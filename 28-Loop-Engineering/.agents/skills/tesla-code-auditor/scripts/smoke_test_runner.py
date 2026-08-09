#!/usr/bin/env python3
import json
import os
import re
import subprocess
import sys
import argparse

def is_third_party_import_error(message, workspace_root):
    # Extract the module name between quotes
    match = re.search(r"['\"]([^'\"]+)['\"]", message)
    if not match:
        return False
    
    full_module = match.group(1)
    root_module = full_module.split('.')[0]
    
    # Check standard library
    if hasattr(sys, 'stdlib_module_names') and root_module in sys.stdlib_module_names:
        return False
    if root_module in sys.builtin_module_names:
        return False
        
    # Check local modules in workspace
    local_dir = os.path.join(workspace_root, root_module)
    local_file = os.path.join(workspace_root, f"{root_module}.py")
    if os.path.isdir(local_dir) or os.path.isfile(local_file):
        return False
        
    # Check src/ folder as well
    src_dir = os.path.join(workspace_root, "src", root_module)
    src_file = os.path.join(workspace_root, "src", f"{root_module}.py")
    if os.path.isdir(src_dir) or os.path.isfile(src_file):
        return False

    return True

def parse_traceback(stderr, workspace_root):
    lines = [line.rstrip() for line in stderr.splitlines() if line.strip()]
    if not lines:
        return []
    
    # Find the last line that matches our exception format
    exc_line = lines[-1]
    exc_match = re.match(r"^([a-zA-Z0-9_]+):\s*(.*)$", exc_line)
    exc_class = exc_match.group(1) if exc_match else "RuntimeError"
    exc_msg = exc_line
    
    file_path = "unknown"
    line_num = 1
    
    file_pattern = re.compile(r'File "([^"]+)", line (\d+), in (.+)')
    for line in reversed(lines[:-1]):
        m = file_pattern.search(line)
        if m:
            file_path = m.group(1)
            line_num = int(m.group(2))
            break
            
    if os.path.isabs(file_path):
        file_rel = os.path.relpath(file_path, workspace_root)
    else:
        file_rel = file_path
        
    return [{
        "file": file_rel,
        "line": line_num,
        "severity": "ERROR",
        "code": exc_class,
        "message": exc_msg
    }]

def check_file(filepath, workspace_root):
    # Determine the test mode
    # Read the file content to check for if __name__ == "__main__":
    is_executable = False
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        if '__name__' in content and '__main__' in content:
            is_executable = True
    except Exception:
        pass

    # Build environment with SMOKE_TEST_MODE=1
    test_env = {
        **os.environ,
        "SMOKE_TEST_MODE": "1",
        "PYTHONPATH": workspace_root + (os.pathsep + os.environ.get("PYTHONPATH", "") if os.environ.get("PYTHONPATH") else "")
    }

    if is_executable:
        # Run help mode
        cmd = [sys.executable, filepath, "--help"]
        mode_str = "Help Dry-Run Check (--help)"
    else:
        # Run import mode
        # Convert path to module dotted path
        rel_path = os.path.relpath(filepath, workspace_root)
        module_path = os.path.splitext(rel_path)[0].replace(os.path.sep, '.')
        cmd = [sys.executable, "-c", f"import sys; sys.path.insert(0, '{workspace_root}'); import {module_path}"]
        mode_str = f"Import Verification Check (import {module_path})"

    try:
        # Enforce strict 10 second timeout ceiling
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10,
            env=test_env,
            cwd=workspace_root
        )
        
        if result.returncode == 0:
            return {
                "verdict": "PASS",
                "message": f"Smoke check passed: {mode_str} succeeded."
            }
        else:
            # Parse traceback
            violations = parse_traceback(result.stderr, workspace_root)
            return {
                "verdict": "FAILED",
                "message": f"Smoke check failed: {mode_str} returned exit code {result.returncode}.",
                "violations": violations
            }
            
    except subprocess.TimeoutExpired:
        return {
            "verdict": "TIMEOUT",
            "message": f"Smoke check blocked: {mode_str} timed out after 10 seconds.",
            "violations": [{
                "file": os.path.relpath(filepath, workspace_root),
                "line": 1,
                "severity": "CRITICAL",
                "code": "TimeoutExpired",
                "message": f"Process hang or infinite loop detected during smoke check of {filepath}."
            }]
        }
    except Exception as e:
        return {
            "verdict": "FAILED",
            "message": f"Smoke check error: {str(e)}",
            "violations": [{
                "file": os.path.relpath(filepath, workspace_root),
                "line": 1,
                "severity": "ERROR",
                "code": "SmokeTestError",
                "message": f"Unexpected execution failure: {str(e)}"
            }]
        }

def main():
    parser = argparse.ArgumentParser(description="Smoke Test Runner")
    parser.add_argument("targets", nargs="+", help="Files or directories to smoke test")
    args = parser.parse_args()

    workspace_root = os.getcwd()
    python_files = []
    for target in args.targets:
        if os.path.isfile(target):
            if target.endswith('.py'):
                python_files.append(target)
        elif os.path.isdir(target):
            for root, _, files in os.walk(target):
                for f in files:
                    if f.endswith('.py'):
                        python_files.append(os.path.join(root, f))

    all_violations = []
    verdict = "PASS"
    
    # We do NOT run smoke tests on test files themselves (files named test_*.py or in tests/ folder)
    # as smoke testing test files directly might run them or fail due to import framework issues.
    target_files = []
    for filepath in python_files:
        basename = os.path.basename(filepath)
        if basename.startswith('test_') or 'tests' in filepath.split(os.path.sep):
            continue
        target_files.append(filepath)

    for filepath in target_files:
        res = check_file(filepath, workspace_root)
        if res["verdict"] != "PASS":
            violations = res.get("violations", [])
            all_violations.extend(violations)
            
            # Map failed to BLOCK or DELAY
            if res["verdict"] == "TIMEOUT":
                verdict = "BLOCK"
            else:
                # Check if any violation is due to missing third-party import
                for v in violations:
                    if v["code"] in ("ModuleNotFoundError", "ImportError"):
                        if is_third_party_import_error(v["message"], workspace_root):
                            verdict = "BLOCK"
                            v["message"] = f"Missing external dependency: {v['message']}. Package installation is forbidden in CODE_ONLY mode."
                            break
                if verdict != "BLOCK":
                    verdict = "DELAY"

    output = {
        "verdict": verdict,
        "rung_reached": 3,
        "summary": f"Smoke verification completed with verdict: {verdict}",
        "violations": all_violations,
        "learning_deltas": all_violations
    }

    print(json.dumps(output, indent=2))
    sys.exit(0 if verdict == "PASS" else 1)

if __name__ == "__main__":
    main()
