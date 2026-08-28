#!/usr/bin/env python3
"""Vigilum Codex 2.1 — Universal Test Runner (E4: Faille d'Invocation Python).

Deterministic enforcement of the RETEX corrective action
"Universal Test Runner": EXCLUSIVE use of launchers resolving ``sys.path`` and
using discovery ``-s <directory> -t <root>``. Direct invocation of
``python3 -m unittest <path-with-dashes>`` is forbidden (ModuleNotFoundError
on decorated paths such as ``MVP-GITHUB/53-Vigilum-Codex-2.0-...``).

Suites executed
---------------
  1. Python unit tests    python3 -m unittest discover -s tests -t <root>
  2. Bash hook suite      bash tests/test_hooks_suite.sh
  3. RETEX orchestration  covered by suite 1 (tests/test_retex_hardening.py)
  4. Parity audit         opt-in (--run-parity): bin/audit_parite.sh

Evidence: writes evidence/test_runner_<mission>_<ts>.json
Exit: 0 only when every executed suite passed (fail-closed aggregate).
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

EXIT_PASS = 0
EXIT_FAIL = 1
EXIT_UNKNOWN = 66

MANIFEST_NAME = "test_manifest_v2.1.yaml"


def load_test_manifest(root: Path) -> tuple[Path | None, dict | None, str | None]:
    """Load the declarative test manifest (YAML-subset or JSON). Returns (path, data, error).

    Path-agnostic (E4) : le runner est invocable depuis n'importe quel CWD,
    donc la racine du module est ajoutée à ``sys.path`` avant l'import du
    parseur ``core.orchestration.yaml_mini``.
    """
    path = root / "manifest" / MANIFEST_NAME
    if not path.is_file():
        return None, None, None
    try:
        root_str = str(root)
        if root_str not in sys.path:
            sys.path.insert(0, root_str)
        if path.suffix.lower() in (".yaml", ".yml"):
            from core.orchestration.yaml_mini import load_file
            data = load_file(str(path))
        else:
            data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # P3 : manifeste illisible => jamais un PASS implicite
        return path, None, f"TEST_MANIFEST_UNPARSEABLE:{exc}"
    if not isinstance(data, dict):
        return path, None, "TEST_MANIFEST_ROOT_NOT_OBJECT"
    return path, data, None


def manifest_mismatches(suites: list[dict[str, Any]], manifest: dict) -> list[str]:
    """Compare executed suite counts against the declared manifest (fail-closed)."""
    problems: list[str] = []
    actual = {s["name"]: s.get("tests_reported") for s in suites}
    for entry in manifest.get("suites", []):
        if not isinstance(entry, dict):
            continue
        name = entry.get("name")
        declared = entry.get("expected_tests")
        executed = actual.get(name)
        if not isinstance(declared, int):
            continue
        if not isinstance(executed, int) or executed < declared:
            problems.append(f"{name}: declared {declared}, executed {executed if executed is not None else 'SKIPPED'}")
    declared_total = manifest.get("total_tests")
    executed_total = sum(v for v in actual.values() if isinstance(v, int))
    if isinstance(declared_total, int) and executed_total < declared_total:
        problems.append(f"total: declared {declared_total}, executed {executed_total}")
    return problems


def run_command(cmd: list[str], cwd: Path) -> tuple[int, str]:
    try:
        proc = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True,
                              timeout=600, check=False)
    except (OSError, subprocess.SubprocessError) as exc:
        return EXIT_UNKNOWN, f"launch error: {exc}"
    tail = "\n".join((proc.stdout + proc.stderr).splitlines()[-40:])
    return proc.returncode, tail


def run_python_suite(root: Path) -> dict[str, Any]:
    # E4-compliant: discovery with explicit start dir (`-s tests`), top-level
    # defaults to the start dir so the dash-decorated module path never becomes
    # an import name. `-t <root>` is forbidden: it requires an importable
    # top-level dir and breaks under `53-Vigilum-Codex-2.0-...` (E4).
    cmd = [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"]
    code, output = run_command(cmd, root)
    passed = 0
    failed = 0
    for line in output.splitlines():
        if line.startswith("Ran "):
            try:
                passed = int(line.split()[1])
            except (IndexError, ValueError):
                pass
        if line.startswith("FAILED"):
            failed = 1
    return {
        "name": "python-unittest-discovery",
        "command": " ".join(cmd),
        "exit_code": code,
        "verdict": "PASS" if code == 0 else "FAIL",
        "tests_reported": passed,
        "output_tail": output,
    }


def run_bash_suite(root: Path) -> dict[str, Any]:
    cmd = ["bash", "tests/test_hooks_suite.sh"]
    code, output = run_command(cmd, root)
    import re
    match = re.search(r"All (\d+) tests OK", output)
    tests_reported = int(match.group(1)) if match else None
    return {
        "name": "bash-hooks-suite",
        "command": " ".join(cmd),
        "exit_code": code,
        "verdict": "PASS" if code == 0 else "FAIL",
        "tests_reported": tests_reported,
        "output_tail": output,
    }


def run_parity_suite(root: Path, mission: str) -> dict[str, Any]:
    cmd = ["bash", "bin/audit_parite.sh", "--root", str(root), "--mission", mission]
    code, output = run_command(cmd, root)
    return {
        "name": "parity-audit",
        "command": " ".join(cmd),
        "exit_code": code,
        "verdict": "PASS" if code == 0 else "FAIL",
        "output_tail": output,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Universal Test Runner (Vigilum Codex 2.1)")
    parser.add_argument("--root", type=Path, default=None,
                        help="Module root (default: parent of this script's directory)")
    parser.add_argument("--mission", default="SGC-EXEC-GOV-03-R3", help="Mission ID for the evidence ledger")
    parser.add_argument("--skip-python", action="store_true")
    parser.add_argument("--skip-bash", action="store_true")
    parser.add_argument("--run-parity", action="store_true",
                        help="Also execute bin/audit_parite.sh (opt-in: N/A on public clones)")
    parser.add_argument("--no-evidence", action="store_true")
    args = parser.parse_args()

    root = (args.root or Path(__file__).resolve().parent.parent).resolve()
    if not (root / "tests").is_dir():
        print(json.dumps({"verdict": "UNKNOWN", "reason": "TESTS_DIR_MISSING", "root": str(root)}, indent=2))
        return EXIT_UNKNOWN

    suites: list[dict[str, Any]] = []
    if not args.skip_python:
        suites.append(run_python_suite(root))
    if not args.skip_bash:
        suites.append(run_bash_suite(root))
    if args.run_parity:
        suites.append(run_parity_suite(root, args.mission))

    executed = [s for s in suites if s["exit_code"] != EXIT_UNKNOWN]
    global_verdict = "PASS" if executed and all(s["exit_code"] == 0 for s in executed) else "FAIL"
    if not executed:
        global_verdict = "UNKNOWN"

    # V2.1.3 (arbitrage #5) : validation contre le manifeste déclaratif des tests
    manifest_path, manifest, manifest_error = load_test_manifest(root)
    manifest_check: dict[str, Any] = {"manifest": str(manifest_path) if manifest_path else None}
    if manifest_error:
        manifest_check.update({"verdict": "FAIL", "reason": manifest_error})
        global_verdict = "FAIL"
    elif manifest is not None:
        problems = manifest_mismatches(suites, manifest)
        manifest_check.update({
            "verdict": "PASS" if not problems else "FAIL",
            "mismatches": problems,
        })
        if problems:
            global_verdict = "FAIL"

    summary: dict[str, Any] = {
        "runner": "Universal Test Runner",
        "version": "2.1.3",
        "mission_id": args.mission,
        "module_root": str(root),
        "verdict_global": global_verdict,
        "exit_code": 0 if global_verdict == "PASS" else 1,
        "suites": suites,
        "test_manifest": manifest_check,
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }

    if not args.no_evidence:
        evidence_dir = root / "evidence"
        evidence_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-%f")
        ledger_path = evidence_dir / f"test_runner_{args.mission}_{stamp}.json"
        ledger_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        summary["evidence_ledger"] = str(ledger_path)

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if global_verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
