#!/usr/bin/env python3
import json
import os
import re
import sys
import argparse

def parse_frontmatter(content):
    lines = content.splitlines()
    if not lines or lines[0].strip() != '---':
        return None
    fm_lines = []
    found_end = False
    for line in lines[1:]:
        if line.strip() == '---':
            found_end = True
            break
        fm_lines.append(line)
    if not found_end:
        return None
    
    metadata = {}
    for line in fm_lines:
        if not line.strip() or line.strip().startswith('#'):
            continue
        match = re.match(r"^\s*([a-zA-Z0-9_-]+)\s*:\s*(.*)$", line)
        if match:
            key = match.group(1).strip()
            val = match.group(2).strip()
            if val.startswith('"') and val.endswith('"'):
                val = val[1:-1]
            elif val.startswith("'") and val.endswith("'"):
                val = val[1:-1]
            metadata[key] = val
    return metadata

def check_naming_convention(filepath, workspace_root, violations):
    file_rel = os.path.relpath(filepath, workspace_root)
    parts = file_rel.split(os.path.sep)
    filename = parts[-1]
    
    # 1. Path Boundary Check for .agents/ folder
    # Executable/binary files forbidden in .agents/ unless they are inside .agents/skills/
    if '.agents' in parts:
        is_in_skills = '.agents/skills/' in file_rel.replace(os.path.sep, '/')
        _, ext = os.path.splitext(filename)
        ext = ext.lower()
        if not is_in_skills and ext in ('.py', '.sh', '.pl', '.db', '.exe', '.bin', '.so', '.dll'):
            violations.append({
                "rule_id": "policy-agents-boundary",
                "file": file_rel,
                "line": 1,
                "severity": "CRITICAL",
                "message": f"Forbidden executable or binary file found in .agents/ folder: {file_rel}"
            })

    # 2. Python File Suffix/Naming
    if filename.endswith('.py'):
        is_test = filename.startswith('test_') or 'tests' in parts or 'test' in parts
        if is_test:
            # Test files must follow ^test_[a-z0-9_]+\.py$
            if not re.match(r"^test_[a-z0-9_]+\.py$", filename):
                violations.append({
                    "rule_id": "policy-test-naming",
                    "file": file_rel,
                    "line": 1,
                    "severity": "WARNING",
                    "message": f"Test file does not follow snake_case prefixed by test_: {filename}"
                })
        else:
            # Non-test files must follow ^[a-z0-9_]+\.py$
            if not re.match(r"^[a-z0-9_]+\.py$", filename):
                violations.append({
                    "rule_id": "policy-file-naming",
                    "file": file_rel,
                    "line": 1,
                    "severity": "WARNING",
                    "message": f"Python source file does not follow strict snake_case naming: {filename}"
                })

    # 3. Markdown Naming
    elif filename.endswith('.md'):
        if not re.match(r"^[a-z0-9_-]+\.md$", filename):
            violations.append({
                "rule_id": "policy-markdown-naming",
                "file": file_rel,
                "line": 1,
                "severity": "WARNING",
                "message": f"Markdown documentation file does not follow snake_case/kebab-case: {filename}"
            })

    # 4. Forbidden/Temporary Files
    forbidden_names = {'temp.md', 'tmp.txt', 'output.txt', 'debug.log'}
    forbidden_extensions = {'.bak', '.tmp'}
    _, ext = os.path.splitext(filename)
    if filename in forbidden_names or ext in forbidden_extensions:
        violations.append({
            "rule_id": "policy-forbidden-file",
            "file": file_rel,
            "line": 1,
            "severity": "WARNING",
            "message": f"Transient or forbidden file detected: {filename}"
        })

def check_metadata(filepath, workspace_root, violations):
    file_rel = os.path.relpath(filepath, workspace_root)
    parts = file_rel.split(os.path.sep)
    filename = parts[-1]

    # Frontmatter is required for Markdown files inside .agents/ or skill directories
    is_markdown = filename.endswith('.md')
    is_in_agents = '.agents' in parts
    
    if is_markdown and is_in_agents:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            violations.append({
                "rule_id": "policy-metadata-read",
                "file": file_rel,
                "line": 1,
                "severity": "WARNING",
                "message": f"Unable to read file for metadata verification: {str(e)}"
            })
            return

        metadata = parse_frontmatter(content)
        if not metadata:
            violations.append({
                "rule_id": "policy-metadata-missing",
                "file": file_rel,
                "line": 1,
                "severity": "WARNING",
                "message": f"Metadata frontmatter is missing or invalid in Markdown file: {file_rel}"
            })
            return

        # Check for specific files
        if filename == 'SKILL.md':
            required_keys = ['name', 'description', 'version', 'status', 'owner']
        elif filename in ('analysis.md', 'handoff.md'):
            required_keys = ['version', 'status', 'date']
        else:
            required_keys = ['version', 'status']

        for key in required_keys:
            if key not in metadata:
                violations.append({
                    "rule_id": "policy-metadata-schema",
                    "file": file_rel,
                    "line": 1,
                    "severity": "WARNING",
                    "message": f"Required metadata key '{key}' is missing in {file_rel}"
                })

        # Schema value checks
        if 'status' in metadata:
            valid_statuses = {'concept', 'active', 'stable', 'production', 'deprecated'}
            if metadata['status'] not in valid_statuses:
                violations.append({
                    "rule_id": "policy-metadata-status",
                    "file": file_rel,
                    "line": 1,
                    "severity": "WARNING",
                    "message": f"Invalid status '{metadata['status']}' in {file_rel}. Must be one of: {', '.join(valid_statuses)}"
                })

        if 'version' in metadata:
            if not re.match(r"^\d+(\.\d+)*$", metadata['version']):
                violations.append({
                    "rule_id": "policy-metadata-version",
                    "file": file_rel,
                    "line": 1,
                    "severity": "WARNING",
                    "message": f"Invalid version format '{metadata['version']}' in {file_rel}. Must be semantic (e.g. 1.0)."
                })

def check_log_integrity(log_path, workspace_root, violations):
    file_rel = os.path.relpath(log_path, workspace_root)
    
    # Check for empty/truncated logs
    try:
        size = os.path.getsize(log_path)
        if size == 0:
            violations.append({
                "rule_id": "policy-log-truncation",
                "file": file_rel,
                "line": 1,
                "severity": "CRITICAL",
                "message": f"Log file is empty or has been truncated: {file_rel}"
            })
            return
    except Exception:
        return

    # Check formatting and monotonicity
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        violations.append({
            "rule_id": "policy-log-read",
            "file": file_rel,
            "line": 1,
            "severity": "WARNING",
            "message": f"Failed to read log file: {str(e)}"
        })
        return

    log_pattern = re.compile(
        r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?) \[(INFO|WARNING|ERROR)\] \[([a-zA-Z0-9_-]+)\] (.*)$"
    )
    
    prev_timestamp = None
    
    for idx, line in enumerate(lines, 1):
        m = log_pattern.match(line)
        if not m:
            violations.append({
                "rule_id": "policy-log-format",
                "file": file_rel,
                "line": idx,
                "severity": "WARNING",
                "message": f"Log line does not match standard pattern: {line.strip()}"
            })
            continue
            
        timestamp_str = m.group(1)
        # Check monotonicity
        if prev_timestamp and timestamp_str < prev_timestamp:
            violations.append({
                "rule_id": "policy-log-monotonicity",
                "file": file_rel,
                "line": idx,
                "severity": "CRITICAL",
                "message": f"Log timestamp is not chronologically sequential. Current: {timestamp_str}, Previous: {prev_timestamp}"
            })
        prev_timestamp = timestamp_str

def main():
    parser = argparse.ArgumentParser(description="Policy Engine Auditor")
    parser.add_argument("targets", nargs="*", help="Files or directories to audit")
    args = parser.parse_args()

    workspace_root = os.getcwd()
    
    # Resolve all files to audit
    files_to_check = []
    if args.targets:
        for target in args.targets:
            if os.path.isfile(target):
                files_to_check.append(target)
            elif os.path.isdir(target):
                for root, _, files in os.walk(target):
                    for f in files:
                        files_to_check.append(os.path.join(root, f))
    else:
        # Default to entire workspace (excluding virtual environments, git etc.)
        for root, dirs, files in os.walk(workspace_root):
            # Prune directories
            dirs[:] = [d for d in dirs if d not in ('.git', '.venv', 'venv', '__pycache__', 'node_modules')]
            for f in files:
                files_to_check.append(os.path.join(root, f))

    violations = []
    
    for filepath in files_to_check:
        check_naming_convention(filepath, workspace_root, violations)
        check_metadata(filepath, workspace_root, violations)
        # If it is a log file in .runtime/
        if '.runtime' in filepath.split(os.path.sep) and filepath.endswith('.log'):
            check_log_integrity(filepath, workspace_root, violations)

    # Automatically check .runtime/ folder if it exists in the workspace
    runtime_dir = os.path.join(workspace_root, '.runtime')
    if os.path.isdir(runtime_dir):
        for f in os.listdir(runtime_dir):
            if f.endswith('.log'):
                log_path = os.path.join(runtime_dir, f)
                # Avoid double checking if already in files_to_check
                if log_path not in files_to_check:
                    check_log_integrity(log_path, workspace_root, violations)

    # Determine verdict
    # CRITICAL -> BLOCK
    # WARNING -> DELAY
    verdict = "PASS"
    has_critical = False
    has_warning = False
    
    for v in violations:
        if v["severity"] == "CRITICAL":
            has_critical = True
        elif v["severity"] == "WARNING":
            has_warning = True

    if has_critical:
        verdict = "BLOCK"
    elif has_warning:
        verdict = "DELAY"

    output = {
        "verdict": verdict,
        "rung_reached": 4,
        "summary": f"Policy engine check completed. Found {len(violations)} violations.",
        "violations": violations,
        "learning_deltas": [
            {
                "file": v["file"],
                "line": v["line"],
                "severity": v["severity"],
                "code": v["rule_id"],
                "message": v["message"]
            } for v in violations
        ]
    }

    print(json.dumps(output, indent=2))
    sys.exit(0 if verdict == "PASS" else 1)

if __name__ == "__main__":
    main()
