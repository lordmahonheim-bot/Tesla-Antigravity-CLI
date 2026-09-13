#!/usr/bin/env python3
import ast
import sys
from pathlib import Path
from typing import List, Set

DANGEROUS_CALLS: Set[str] = {
    "os.system", "os.popen", "subprocess.run", "subprocess.Popen",
    "subprocess.call", "subprocess.check_call", "subprocess.check_output",
    "exec", "eval", "__import__", "builtins.exec", "builtins.eval"
}

class QuarantineAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.violations: List[str] = []

    def visit_Call(self, node: ast.Call):
        func_name = self._resolve_name(node.func)
        if func_name in DANGEROUS_CALLS or func_name in {"exec", "eval", "__import__"}:
            self.violations.append(f"Ligne {node.lineno} : Appel dangereux détecté -> '{func_name}'")
        self.generic_visit(node)

    def _resolve_name(self, node: ast.expr) -> str:
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            if isinstance(node.value, ast.Name):
                return f"{node.value.id}.{node.attr}"
            return node.attr
        return ""

def analyze_file(filepath: str) -> int:
    try:
        source_code = Path(filepath).read_text(encoding="utf-8")
    except Exception as e:
        print(f"Erreur de lecture {filepath}: {e}", file=sys.stderr)
        return 1

    try:
        tree = ast.parse(source_code, filename=filepath)
    except SyntaxError as e:
        print(f"Erreur de syntaxe dans {filepath} : {e}", file=sys.stderr)
        return 1

    analyzer = QuarantineAnalyzer()
    analyzer.visit(tree)

    if analyzer.violations:
        print(f"[QUARANTAINE] Échec de sécurité pour {filepath} :", file=sys.stderr)
        for violation in analyzer.violations:
            print(f"  - {violation}", file=sys.stderr)
        return 1
    
    print(f"[SAFE] Aucune violation détectée dans {filepath}.")
    return 0

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <fichier_python>", file=sys.stderr)
        sys.exit(1)
    
    exit_code = analyze_file(sys.argv[1])
    sys.exit(exit_code)
