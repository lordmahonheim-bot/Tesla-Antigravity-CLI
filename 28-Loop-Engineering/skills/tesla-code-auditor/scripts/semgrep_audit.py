#!/usr/bin/env python3
import ast
import json
import os
import re
import subprocess
import sys
import argparse

class TeslaASTVisitor(ast.NodeVisitor):
    def __init__(self, filepath, workspace_root):
        self.filepath = filepath
        self.relative_filepath = os.path.relpath(filepath, workspace_root)
        self.violations = []
        self.workspace_root = workspace_root

    def add_violation(self, rule_id, line, severity, message):
        self.violations.append({
            "rule_id": rule_id,
            "file": self.relative_filepath,
            "line": line,
            "severity": severity,
            "message": message
        })

    def _is_path_allowed(self, path_str):
        # Allow paths containing .agents, .runtime, .temp, or tmp/temp in /tmp
        allowed_parts = ['.agents', '.runtime', '.temp', 'tmp']
        # Check absolute path
        abs_path = os.path.abspath(os.path.join(self.workspace_root, path_str))
        if any(part in abs_path for part in allowed_parts):
            return True
        # Check relative path
        rel_path = os.path.relpath(abs_path, self.workspace_root)
        if any(part in rel_path for part in allowed_parts):
            return True
        return False

    def visit_Call(self, node):
        # 1. Dynamic execution: eval, exec, compile
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            if func_name in ('eval', 'exec', 'compile'):
                rule_id = f"python-{func_name}-usage" if func_name in ('eval', 'exec') else "python-dynamic-execution"
                self.add_violation(
                    rule_id=rule_id,
                    line=node.lineno,
                    severity="ERROR",
                    message=f"Use of {func_name}() is strictly forbidden due to arbitrary code execution risks."
                )
            
            # open(...) write check
            elif func_name == 'open' and len(node.args) > 0:
                path_arg = node.args[0]
                if isinstance(path_arg, ast.Constant) and isinstance(path_arg.value, str):
                    # Check write mode
                    is_write = False
                    mode_val = 'r'
                    if len(node.args) > 1:
                        mode_arg = node.args[1]
                        if isinstance(mode_arg, ast.Constant) and isinstance(mode_arg.value, str):
                            mode_val = mode_arg.value
                    for kw in node.keywords:
                        if kw.arg == 'mode' and isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, str):
                            mode_val = kw.value.value
                    
                    if any(char in mode_val for char in ('w', 'a', 'x', '+')):
                        is_write = True
                    
                    if is_write and not self._is_path_allowed(path_arg.value):
                        self.add_violation(
                            rule_id="governance-unauthorized-write",
                            line=node.lineno,
                            severity="ERROR",
                            message=f"Writing to files outside authorized directories: {path_arg.value}"
                        )

        # Attribute calls (os.system, os.popen, subprocess.run, shutil.copy, etc.)
        elif isinstance(node.func, ast.Attribute):
            module_name = ""
            if isinstance(node.func.value, ast.Name):
                module_name = node.func.value.id
            
            func_name = node.func.attr

            # os.system, os.popen
            if module_name == 'os' and func_name in ('system', 'popen'):
                self.add_violation(
                    rule_id="python-command-injection",
                    line=node.lineno,
                    severity="ERROR",
                    message=f"Command execution with os.{func_name} is dangerous and can lead to command injection."
                )
                
                # Check for git push in os.system
                if func_name == 'system' and len(node.args) > 0:
                    cmd_arg = node.args[0]
                    if isinstance(cmd_arg, ast.Constant) and isinstance(cmd_arg.value, str):
                        if "git" in cmd_arg.value and "push" in cmd_arg.value:
                            self.add_violation(
                                rule_id="governance-unauthorized-git-push",
                                line=node.lineno,
                                severity="ERROR",
                                message="Git push operations without explicit authorization flags/approvals are prohibited."
                            )

            # subprocess execution calls
            elif module_name == 'subprocess' and func_name in ('run', 'Popen', 'call', 'check_output', 'check_call'):
                # Check for shell=True
                shell_true = False
                for kw in node.keywords:
                    if kw.arg == 'shell' and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                        shell_true = True
                if shell_true:
                    self.add_violation(
                        rule_id="python-command-injection",
                        line=node.lineno,
                        severity="ERROR",
                        message="Command execution with shell=True is dangerous and can lead to command injection."
                    )
                
                # Check for git push in subprocess args
                if len(node.args) > 0:
                    args_node = node.args[0]
                    is_git_push = False
                    if isinstance(args_node, ast.Constant) and isinstance(args_node.value, str):
                        if "git" in args_node.value and "push" in args_node.value:
                            is_git_push = True
                    elif isinstance(args_node, ast.List):
                        elements = [el.value for el in args_node.elts if isinstance(el, ast.Constant) and isinstance(el.value, str)]
                        if "git" in elements and "push" in elements:
                            is_git_push = True
                    
                    if is_git_push:
                        self.add_violation(
                            rule_id="governance-unauthorized-git-push",
                            line=node.lineno,
                            severity="ERROR",
                            message="Git push operations without explicit authorization flags/approvals are prohibited."
                        )

            # os.chmod insecure permissions
            elif module_name == 'os' and func_name == 'chmod' and len(node.args) > 1:
                mode_arg = node.args[1]
                if isinstance(mode_arg, ast.Constant) and isinstance(mode_arg.value, int):
                    mode_val = mode_arg.value
                    # Check if mode matches 0o777 (511), 0o755 (493), 0o666 (438), or literal numbers 777, 755, 666
                    if mode_val in (0o777, 0o755, 0o666, 777, 755, 666):
                        self.add_violation(
                            rule_id="python-insecure-file-permissions",
                            line=node.lineno,
                            severity="WARNING",
                            message=f"Setting overly permissive file permissions (chmod {oct(mode_val)} / {mode_val}) is forbidden."
                        )

            # Path.write_text, Path.write_bytes
            elif func_name in ('write_text', 'write_bytes'):
                # Extract path string if possible (e.g. Path("file").write_text)
                path_str = None
                if isinstance(node.func.value, ast.Call) and isinstance(node.func.value.func, ast.Name) and node.func.value.func.id == 'Path':
                    if len(node.func.value.args) > 0:
                        p_arg = node.func.value.args[0]
                        if isinstance(p_arg, ast.Constant) and isinstance(p_arg.value, str):
                            path_str = p_arg.value
                
                if path_str and not self._is_path_allowed(path_str):
                    self.add_violation(
                        rule_id="governance-unauthorized-write",
                        line=node.lineno,
                        severity="ERROR",
                        message=f"Writing or modifying files outside authorized directories: {path_str}"
                    )

            # shutil.copy, shutil.move
            elif module_name == 'shutil' and func_name in ('copy', 'copy2', 'move') and len(node.args) > 1:
                dst_arg = node.args[1]
                if isinstance(dst_arg, ast.Constant) and isinstance(dst_arg.value, str):
                    if not self._is_path_allowed(dst_arg.value):
                        self.add_violation(
                            rule_id="governance-unauthorized-write",
                            line=node.lineno,
                            severity="ERROR",
                            message=f"Copying/moving file to unauthorized directory: {dst_arg.value}"
                        )

            # os.remove, os.unlink, Path.unlink log deletion
            elif (module_name == 'os' and func_name in ('remove', 'unlink')) or func_name == 'unlink':
                path_str = None
                if len(node.args) > 0:
                    p_arg = node.args[0]
                    if isinstance(p_arg, ast.Constant) and isinstance(p_arg.value, str):
                        path_str = p_arg.value
                elif func_name == 'unlink':
                    # Path("file.log").unlink()
                    if isinstance(node.func.value, ast.Call) and isinstance(node.func.value.func, ast.Name) and node.func.value.func.id == 'Path':
                        if len(node.func.value.args) > 0:
                            p_arg = node.func.value.args[0]
                            if isinstance(p_arg, ast.Constant) and isinstance(p_arg.value, str):
                                path_str = p_arg.value
                
                if path_str and path_str.endswith('.log'):
                    self.add_violation(
                        rule_id="governance-delete-logs",
                        line=node.lineno,
                        severity="ERROR",
                        message=f"Direct deletion of log file {path_str} is prohibited."
                    )

        self.generic_visit(node)

    def visit_Assign(self, node):
        # 2. Hardcoded secrets
        for target in node.targets:
            var_name = None
            if isinstance(target, ast.Name):
                var_name = target.id
            elif isinstance(target, ast.Attribute):
                var_name = target.attr

            if var_name:
                # Check target name against secrets pattern
                if re.search(r'(api_key|secret|password|token|private_key|passwd)', var_name, re.IGNORECASE):
                    # Check if value is a string constant
                    if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                        # Flag even if empty to match generic $VAR = "..." pattern
                        self.add_violation(
                            rule_id="python-hardcoded-secrets",
                            line=node.lineno,
                            severity="ERROR",
                            message=f"Hardcoded secret assignment detected on variable: {var_name}"
                        )

        self.generic_visit(node)

def run_ast_fallback(filepath, workspace_root):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        tree = ast.parse(content, filename=filepath)
        visitor = TeslaASTVisitor(filepath, workspace_root)
        visitor.visit(tree)
        return visitor.violations
    except Exception as e:
        return [{
            "rule_id": "ast-parse-error",
            "file": os.path.relpath(filepath, workspace_root),
            "line": 1,
            "severity": "ERROR",
            "message": f"Failed to parse AST for file {filepath}: {str(e)}"
        }]

def run_semgrep(config_path, target_paths, workspace_root):
    # Try running semgrep executable
    try:
        # Check if semgrep is available
        subprocess.run(["semgrep", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Semgrep not found
        return None

    # Run semgrep with config and json output
    violations = []
    for target in target_paths:
        try:
            cmd = ["semgrep", "--config", config_path, "--json", target]
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            if result.returncode not in (0, 1):
                # Semgrep failed or crashed
                return None
            
            data = json.loads(result.stdout)
            for item in data.get("results", []):
                violations.append({
                    "rule_id": item.get("check_id"),
                    "file": os.path.relpath(item.get("path"), workspace_root),
                    "line": item.get("start", {}).get("line", 1),
                    "severity": item.get("extra", {}).get("severity", "ERROR"),
                    "message": item.get("extra", {}).get("message", "")
                })
        except Exception:
            return None
    return violations

def main():
    parser = argparse.ArgumentParser(description="Semgrep Audit Wrapper with AST Fallback")
    parser.add_argument("--config", required=True, help="Path to Semgrep custom rules YAML")
    parser.add_argument("targets", nargs="+", help="Files or directories to audit")
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
    
    violations = run_semgrep(args.config, python_files, workspace_root)
    
    used_fallback = False
    if violations is None:
        # Fallback to AST engine
        used_fallback = True
        violations = []
        for filepath in python_files:
            violations.extend(run_ast_fallback(filepath, workspace_root))
            
    # Determine verdict
    # Block on ERROR, Delay on WARNING
    verdict = "PASS"
    has_error = False
    has_warning = False
    
    for v in violations:
        if v["severity"] == "ERROR":
            has_error = True
        elif v["severity"] == "WARNING":
            has_warning = True
            
    if has_error:
        verdict = "BLOCK"
    elif has_warning:
        verdict = "DELAY"

    output = {
        "verdict": verdict,
        "rung_reached": 2,
        "summary": f"SemGrep audit completed. Found {len(violations)} violations. Fallback used: {used_fallback}",
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
    
    # Exit code matches verdict style: 0 for PASS, 1 for violations
    sys.exit(0 if verdict == "PASS" else 1)

if __name__ == "__main__":
    main()
