#!/usr/bin/env python3
import sys
import os
import tempfile
import ast

# Add the scripts directory to sys.path so we can import modules
sys.path.insert(0, "/home/lord-mahonheim/bifrost/tesla/.agents/skills/tesla-code-auditor/scripts")

try:
    from semgrep_audit import TeslaASTVisitor
    from pyright_audit import is_third_party_import_error
    from policy_engine import parse_frontmatter, check_naming_convention
    import code_auditor
    print("SUCCESS: Imported all modules correctly!")
except ImportError as e:
    print(f"FAILED: Import error: {str(e)}")
    sys.exit(1)

def test_ast_visitor():
    print("Testing TeslaASTVisitor...")
    code = """
import os
import subprocess
from pathlib import Path
import shutil

# 1. Security Violation: eval/exec
eval("1 + 1")
exec("x = 2")

# 2. Security Violation: Command Injection
os.system("echo hello")
subprocess.run("ls", shell=True)

# 3. Security Violation: Hardcoded Secrets
my_api_key = "super_secret_token_123"

# 4. Security Violation: Insecure permissions
os.chmod("file.txt", 0o777)

# 5. Governance: Unauthorized Write
open("unauthorized_file.txt", "w").write("test")
Path("another_bad_file.txt").write_text("hello")
shutil.copy("src.txt", "unauthorized_dest.txt")

# 6. Governance: Unauthorized Git Push
os.system("git push origin master")

# 7. Governance: Log deletion
os.remove("app.log")
"""
    # Create temp file
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as tmp:
        tmp.write(code)
        tmp_name = tmp.name

    try:
        # Run visitor
        workspace_root = os.path.dirname(tmp_name)
        tree = ast.parse(code)
        visitor = TeslaASTVisitor(tmp_name, workspace_root)
        visitor.visit(tree)
        
        violations = visitor.violations
        rule_ids = {v["rule_id"] for v in violations}
        
        expected_rules = {
            "python-eval-usage",
            "python-exec-usage",
            "python-command-injection",
            "python-hardcoded-secrets",
            "python-insecure-file-permissions",
            "governance-unauthorized-write",
            "governance-unauthorized-git-push",
            "governance-delete-logs"
        }
        
        print(f"Detected rule violations: {rule_ids}")
        missing = expected_rules - rule_ids
        if missing:
            print(f"FAILED: AST Visitor missed some violations: {missing}")
            return False
        else:
            print("SUCCESS: AST Visitor correctly identified all security and governance violations!")
            return True
    finally:
        os.unlink(tmp_name)

def test_import_resolver():
    print("Testing is_third_party_import_error...")
    workspace_root = "/home/lord-mahonheim/bifrost/tesla"
    
    # Standard library import
    is_std_err = is_third_party_import_error("Import 'json' could not be resolved", workspace_root)
    # Local module (we know 'core' exists or we can check if it behaves as local)
    is_local_err = is_third_party_import_error("Import 'scripts' could not be resolved", workspace_root)
    # Third party module
    is_3rd_err = is_third_party_import_error("Import 'requests' could not be resolved", workspace_root)
    
    print(f"json (std): is_third_party={is_std_err}")
    print(f"scripts (local): is_third_party={is_local_err}")
    print(f"requests (3rd party): is_third_party={is_3rd_err}")
    
    if is_std_err:
        print("FAILED: Classified standard library import as third-party error.")
        return False
    if is_local_err:
        print("FAILED: Classified local package import as third-party error.")
        return False
    if not is_3rd_err:
        print("FAILED: Failed to identify missing third-party package as third-party error.")
        return False
        
    print("SUCCESS: Third-party import resolver works correctly!")
    return True

def test_frontmatter_parser():
    print("Testing parse_frontmatter...")
    valid_fm = """---
name: my-skill
version: 1.2
status: active
owner: Tesla
---
# Skill Documentation
"""
    metadata = parse_frontmatter(valid_fm)
    print(f"Parsed metadata: {metadata}")
    
    if not metadata or metadata.get("name") != "my-skill" or metadata.get("version") != "1.2" or metadata.get("status") != "active" or metadata.get("owner") != "Tesla":
        print("FAILED: parse_frontmatter failed to parse valid metadata block.")
        return False
        
    invalid_fm = """# Just some markdown
---
name: bad-skill
---
"""
    if parse_frontmatter(invalid_fm) is not None:
        print("FAILED: parse_frontmatter parsed an invalid frontmatter block.")
        return False
        
    print("SUCCESS: Frontmatter parser works correctly!")
    return True

if __name__ == "__main__":
    success = True
    success &= test_ast_visitor()
    success &= test_import_resolver()
    success &= test_frontmatter_parser()
    
    if success:
        print("\nALL TESTS PASSED SUCCESSFULLY!")
        sys.exit(0)
    else:
        print("\nSOME TESTS FAILED!")
        sys.exit(1)
