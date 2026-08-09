#!/usr/bin/env python3
import argparse
import json
import os
import subprocess
import sys
from datetime import datetime

def run_checker(script_path, args, target_files):
    cmd = [sys.executable, script_path] + args + target_files
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            # Crash or bad output fallback
            return {
                "verdict": "BLOCK",
                "summary": f"Checker {os.path.basename(script_path)} crashed or did not return valid JSON.",
                "violations": [{
                    "file": "system",
                    "line": 1,
                    "severity": "CRITICAL",
                    "code": "CheckerCrash",
                    "message": f"Stdout: {result.stdout.strip()[:200]}... Stderr: {result.stderr.strip()[:200]}"
                }],
                "learning_deltas": []
            }
    except Exception as e:
        return {
            "verdict": "BLOCK",
            "summary": f"Failed to execute checker: {str(e)}",
            "violations": [{
                "file": "system",
                "line": 1,
                "severity": "CRITICAL",
                "code": "ExecutionFailure",
                "message": str(e)
            }],
            "learning_deltas": []
        }

def get_code_snippet(filepath, line_num):
    if not os.path.isfile(filepath):
        return None
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
        if 0 < line_num <= len(lines):
            return lines[line_num - 1].strip()
    except Exception:
        pass
    return None

def generate_markdown_report(verdict, rung_results, learning_deltas, workspace_root):
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    md = []
    md.append("# Code Auditor Execution Report")
    md.append(f"**Timestamp**: {timestamp} (UTC)")
    md.append(f"**Consolidated Verdict**: `{verdict}`")
    md.append("")
    md.append("## Executive Summary")
    md.append("")
    md.append("| Rung / Checker | Verdict | Summary |")
    md.append("| :--- | :--- | :--- |")
    
    for name, res in rung_results.items():
        md.append(f"| {name} | `{res.get('verdict', 'UNKNOWN')}` | {res.get('summary', '')} |")
        
    md.append("")
    md.append("---")
    md.append("")
    md.append("## Learning Deltas & Violations")
    md.append("")
    
    if not learning_deltas:
        md.append("🟢 **No violations found! All checks passed successfully.**")
    else:
        md.append(f"Found {len(learning_deltas)} violations that need to be addressed:")
        md.append("")
        for idx, delta in enumerate(learning_deltas, 1):
            file_path = delta.get("file", "unknown")
            line = delta.get("line", 1)
            code = delta.get("code", "violation")
            severity = delta.get("severity", "ERROR")
            message = delta.get("message", "")
            
            md.append(f"### {idx}. [{severity}] {code} in `{file_path}`:line {line}")
            md.append(f"> {message}")
            
            # Try to get code snippet
            snippet = get_code_snippet(os.path.join(workspace_root, file_path), line)
            if snippet:
                md.append("")
                md.append("```python")
                md.append(f"# Line {line}")
                md.append(snippet)
                md.append("```")
                
            md.append("")
            
            # Suggestion based on code
            suggestion = "Review the rule documentation and correct the code segment."
            if "eval" in message or "exec" in message:
                suggestion = "Refactor using safe parsing libraries (e.g. json, ast.literal_eval) instead of eval/exec."
            elif "shell=True" in message or "os.system" in message:
                suggestion = "Pass command arguments as a list of strings instead of raw shell command strings, and set shell=False."
            elif "secret" in message or "key" in message:
                suggestion = "Load secrets from environment variables or a configuration file instead of hardcoding."
            elif "chmod" in message:
                suggestion = "Restrict file permissions using standard secure octal modes (e.g. 0o600 or 0o640)."
            elif "outside authorized" in message:
                suggestion = "Ensure all writes are directed only to authorized directories (.agents/, .runtime/, .temp/, /tmp/)."
            elif "git push" in message:
                suggestion = "Bypass git push command calls. All pushes must go through approved operator commands."
            elif "deletion of log" in message:
                suggestion = "Do not delete log files programmatically. Use standard log rotation configs."
            elif "missing external dependency" in message.lower():
                suggestion = "Unresolved package import. Third-party installation is forbidden in CODE_ONLY mode. Consult operator."
                
            md.append(f"**Actionable Suggestion**: {suggestion}")
            md.append("")
            
    md.append("---")
    md.append("")
    md.append("## Developer Feedback Instructions (LLM-Readable)")
    md.append("")
    if verdict == "PASS":
        md.append("Code is ready to commit. Proceed to transition/merge.")
    else:
        md.append("Please address all issues listed in 'Learning Deltas & Violations' before running the auditor again.")
        md.append("Follow the actionable suggestions provided. Do not use prohibited tools or package installs.")
        
    return "\n".join(md)

def get_git_diff_files(diff_spec):
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", diff_spec],
            capture_output=True,
            text=True,
            check=True
        )
        files = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        return [f for f in files if os.path.exists(f)]
    except Exception as e:
        print(f"Error getting git diff: {str(e)}", file=sys.stderr)
        return []

def main():
    parser = argparse.ArgumentParser(description="Tesla Code Auditor Master Orchestrator")
    parser.add_argument("--files", nargs="+", help="Specific files to audit")
    parser.add_argument("--diff", help="Git commit or branch spec to get modified files to audit")
    parser.add_argument("--output-json", help="Path to save the consolidated JSON report")
    parser.add_argument("--output-md", help="Path to save the consolidated Markdown report")
    parser.add_argument("targets", nargs="*", help="Directories or files to scan (if --files or --diff not specified)")
    args = parser.parse_args()

    workspace_root = os.getcwd()
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    skill_dir = os.path.dirname(scripts_dir)

    # 1. Resolve files/directories to scan
    target_files = []
    if args.files:
        target_files = args.files
    elif args.diff:
        target_files = get_git_diff_files(args.diff)
    elif args.targets:
        target_files = args.targets
    else:
        # Default to entire workspace (excluding git, venv, etc.)
        target_files = ["."]

    # Resolve paths
    target_files = [os.path.abspath(f) for f in target_files]

    # Rule path
    config_path = os.path.join(skill_dir, "rules", "tesla_custom_rules.yaml")

    # Runner paths
    semgrep_script = os.path.join(scripts_dir, "semgrep_audit.py")
    pyright_script = os.path.join(scripts_dir, "pyright_audit.py")
    smoke_script = os.path.join(scripts_dir, "smoke_test_runner.py")
    policy_script = os.path.join(scripts_dir, "policy_engine.py")

    rung_results = {}

    # Run checkers in sequence (non-fail-fast)
    print("Executing Rung 1 & 2: SemGrep SAST Audit...")
    rung_results["SemGrep Audit"] = run_checker(semgrep_script, ["--config", config_path], target_files)

    print("Executing Rung 2: Pyright Type Check...")
    rung_results["Pyright Audit"] = run_checker(pyright_script, [], target_files)

    print("Executing Rung 3: Smoke Test Runner...")
    rung_results["Smoke Audit"] = run_checker(smoke_script, [], target_files)

    print("Executing Rung 4: Policy Engine Check...")
    rung_results["Policy Audit"] = run_checker(policy_script, [], target_files)

    # Consolidate verdicts
    # Precedence: BLOCK > DELAY > PASS
    final_verdict = "PASS"
    has_block = False
    has_delay = False

    for name, res in rung_results.items():
        v = res.get("verdict", "PASS")
        if v == "BLOCK":
            has_block = True
        elif v == "DELAY" or v == "FAILED": # FAILED maps to DELAY for compilation/runtime
            has_delay = True

    if has_block:
        final_verdict = "BLOCK"
    elif has_delay:
        final_verdict = "DELAY"

    # Consolidate learning deltas
    consolidated_deltas = []
    for name, res in rung_results.items():
        for delta in res.get("learning_deltas", []):
            # Annotate delta with the source checker
            delta["source"] = name
            consolidated_deltas.append(delta)

    # Build outputs
    output_payload = {
        "verdict": final_verdict,
        "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "rungs": rung_results,
        "learning_deltas": consolidated_deltas
    }

    # Write output files if requested
    if args.output_json:
        try:
            with open(args.output_json, "w", encoding="utf-8") as f:
                json.dump(output_payload, f, indent=2)
            print(f"JSON report written to: {args.output_json}")
        except Exception as e:
            print(f"Failed to write JSON report: {str(e)}", file=sys.stderr)

    md_report = generate_markdown_report(final_verdict, rung_results, consolidated_deltas, workspace_root)
    
    if args.output_md:
        try:
            with open(args.output_md, "w", encoding="utf-8") as f:
                f.write(md_report)
            print(f"Markdown report written to: {args.output_md}")
        except Exception as e:
            print(f"Failed to write Markdown report: {str(e)}", file=sys.stderr)

    print("\n================ AUDITOR VERDICT ================")
    print(f"Verdict: {final_verdict}")
    print(f"Total Violations: {len(consolidated_deltas)}")
    print("=================================================")

    # Exit code: 0 if PASS, 1 if DELAY or BLOCK
    sys.exit(0 if final_verdict == "PASS" else 1)

if __name__ == "__main__":
    main()
