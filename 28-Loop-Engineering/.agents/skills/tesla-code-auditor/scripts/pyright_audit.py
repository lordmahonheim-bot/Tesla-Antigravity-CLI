#!/usr/bin/env python3
import json
import os
import re
import subprocess
import sys
import argparse
import ast

def find_pyright():
    # Search paths
    paths = [
        "/home/lord-mahonheim/bifrost/tesla/.venv/bin/pyright",
        os.path.expanduser("~/bifrost/tesla/.venv/bin/pyright"),
        "pyright"
    ]
    for p in paths:
        if p == "pyright":
            # Check if in PATH
            try:
                subprocess.run(["pyright", "--version"], capture_output=True, check=True)
                return "pyright"
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue
        elif os.path.exists(p):
            return p
    return None

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
    # Look for root_module directory or file at workspace root
    local_dir = os.path.join(workspace_root, root_module)
    local_file = os.path.join(workspace_root, f"{root_module}.py")
    if os.path.isdir(local_dir) or os.path.isfile(local_file):
        return False
        
    # Check if inside any python package directories in workspace
    # e.g., if there's a src/ directory containing the module
    src_dir = os.path.join(workspace_root, "src", root_module)
    src_file = os.path.join(workspace_root, "src", f"{root_module}.py")
    if os.path.isdir(src_dir) or os.path.isfile(src_file):
        return False

    return True

def run_compile_fallback(python_files, workspace_root):
    # Fallback syntax compilation check
    diagnostics = []
    for filepath in python_files:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            compile(content, filepath, "exec")
        except SyntaxError as se:
            diagnostics.append({
                "file": os.path.relpath(filepath, workspace_root),
                "line": se.lineno or 1,
                "severity": "ERROR",
                "code": "SyntaxError",
                "message": f"Syntax Error: {se.msg}"
            })
        except Exception as e:
            diagnostics.append({
                "file": os.path.relpath(filepath, workspace_root),
                "line": 1,
                "severity": "ERROR",
                "code": "CompileError",
                "message": f"Compilation failed: {str(e)}"
            })
    return diagnostics

def parse_pyright_stdout(stdout, workspace_root):
    diagnostics = []
    try:
        data = json.loads(stdout)
        for diag in data.get("generalDiagnostics", []):
            file_abs = diag.get("file", "")
            file_rel = os.path.relpath(file_abs, workspace_root)
            severity = diag.get("severity", "error").upper()
            rule = diag.get("rule", "pyright_error")
            message = diag.get("message", "")
            
            # Convert 0-indexed to 1-indexed line
            line = diag.get("range", {}).get("start", {}).get("line", 0) + 1
            
            diagnostics.append({
                "file": file_rel,
                "line": line,
                "severity": severity,
                "code": rule,
                "message": message
            })
    except Exception as e:
        # Fallback to parsing text-based stdout via regex if JSON fails
        pattern = re.compile(
            r"^(?P<file>.+?):(?P<line>\d+):(?P<col>\d+) - (?P<severity>error|warning): (?P<message>.+?)(?: \((?P<code>\w+)\))?$"
        )
        for line in stdout.splitlines():
            m = pattern.match(line)
            if m:
                file_rel = os.path.relpath(m.group("file"), workspace_root)
                diagnostics.append({
                    "file": file_rel,
                    "line": int(m.group("line")),
                    "severity": m.group("severity").upper(),
                    "code": m.group("code") or "pyright_error",
                    "message": m.group("message")
                })
    return diagnostics

def main():
    parser = argparse.ArgumentParser(description="Pyright Wrapper with Compile Fallback")
    parser.add_argument("targets", nargs="+", help="Files or directories to scan")
    args = parser.parse_args()

    workspace_root = os.getcwd()
    
    # Collect all python files in targets
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

    pyright_bin = find_pyright()
    diagnostics = []
    used_fallback = False
    
    if pyright_bin:
        try:
            cmd = [pyright_bin, "--outputjson"] + python_files
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            diagnostics = parse_pyright_stdout(result.stdout, workspace_root)
        except Exception:
            used_fallback = True
            diagnostics = run_compile_fallback(python_files, workspace_root)
    else:
        used_fallback = True
        diagnostics = run_compile_fallback(python_files, workspace_root)

    # Determine verdict
    # PASS if no errors.
    # BLOCK if there is a missing third-party dependency.
    # DELAY if there are other errors.
    verdict = "PASS"
    has_third_party_block = False
    has_other_errors = False
    
    learning_deltas = []
    
    for diag in diagnostics:
        if diag["severity"] == "ERROR":
            # Check if this is a missing import error
            if diag["code"] == "reportMissingImports":
                if is_third_party_import_error(diag["message"], workspace_root):
                    has_third_party_block = True
                    diag["message"] = f"Missing external dependency: {diag['message']}. Package installation is forbidden in CODE_ONLY mode."
                else:
                    has_other_errors = True
            else:
                has_other_errors = True
        
        learning_deltas.append({
            "file": diag["file"],
            "line": diag["line"],
            "severity": diag["severity"],
            "code": diag["code"],
            "message": diag["message"]
        })
        
    if has_third_party_block:
        verdict = "BLOCK"
    elif has_other_errors:
        verdict = "DELAY"

    output = {
        "verdict": verdict,
        "rung_reached": 2,
        "summary": f"Pyright type verification completed. Found {len(learning_deltas)} diagnostics. Fallback used: {used_fallback}",
        "violations": learning_deltas,
        "learning_deltas": learning_deltas
    }
    
    print(json.dumps(output, indent=2))
    sys.exit(0 if verdict == "PASS" else 1)

if __name__ == "__main__":
    main()
