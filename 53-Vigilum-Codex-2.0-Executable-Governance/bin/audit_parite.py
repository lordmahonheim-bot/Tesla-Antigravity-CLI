#!/usr/bin/env python3
"""Deterministic, file-by-file audit and parity validator (Loi de Parité Absolue)."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REQUIRED_COMPONENTS = [
    "core/gatekeeper.py",
    "core/broker/tesla_brokerd.py",
    "schemas/intent_v3.1.schema.json",
    "core/hooks/lib/tesla-exit-codes.sh",
    "core/hooks/lib/tesla-logging.sh",
    "core/hooks/pre-commit/tesla-pre-commit-main.sh",
    "core/hooks/pre-push/tesla-pre-push-main.sh",
    "tests/test_hooks_suite.sh",
    "tests/test_governance.py",
    "docs/AUDIT_REPORT.md",
    "docs/protocol_mapping.md",
    "bin/audit_parite.py",
    "bin/audit_parite.sh",
    "bin/audit_cap.py",
    "bin/memory_parite.py",
    "bin/staging_gate.py",
    "bin/test_runner.py",
    "bin/workspace_hygiene.py",
    "bin/probe_capabilities.py",
    "bin/mission_controller.py",
    "bin/marble_certificate.py",
    "core/orchestration/orchestration_gate.py",
    "core/orchestration/yaml_mini.py",
    "core/hooks/pre-commit/04-project-state-check.sh",
    "core/hooks/pre-commit/07-orchestration-gate.sh",
    "core/hooks/pre-commit/08-draft-artifact-guard.sh",
    "schemas/receipt_v1.0.schema.json",
    "schemas/mission_graph_v2.0.schema.json",
    "schemas/memory_pillars_v2.1.schema.json",
    "manifest/memory_manifest_v2.1.yaml",
    "manifest/test_manifest_v2.1.yaml",
    "tests/test_retex_hardening.py",
    "docs/RETEX_HARDENING_2.1.md",
    "OUTPUTS/Synergy_Gouvernance_Executable_V3.6_LOCKED.md",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fingerprint(root: Path) -> str:
    paths = sorted(
        p for p in root.rglob("*")
        if p.is_file()
        and "evidence" not in p.parts
        and "__pycache__" not in p.parts
        and ".git" not in p.parts
        and ".venv" not in p.parts
        and "node_modules" not in p.parts
        and "runtime" not in p.parts
    )
    digest = hashlib.sha256()
    for path in paths:
        rel = path.relative_to(root).as_posix()
        digest.update(rel.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def check_file(root: Path, rel: str, verdict: str = "PASS", note: str = "") -> dict[str, Any]:
    path = root / rel
    item: dict[str, Any] = {"file": rel}
    if not path.is_file():
        item.update({"verdict": "MISSING", "note": "required file is absent"})
        return item
    item.update({"verdict": verdict, "sha256": sha256(path)})
    if note:
        item["note"] = note
    return item


def build_checks(root: Path) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    checks: list[dict[str, Any]] = []
    failures: list[str] = []

    for rel in REQUIRED_COMPONENTS:
        item = check_file(root, rel)
        checks.append(item)
        if item["verdict"] != "PASS":
            failures.append(rel)

    return checks, failures, []


def main() -> int:
    parser = argparse.ArgumentParser(description="Deterministic parity auditor")
    parser.add_argument("--id", default="COMP-PARITY-01", help="Component ID")
    parser.add_argument("--type", default="TOOLING", help="Component Type")
    parser.add_argument("--root", type=Path, required=True, help="Root directory")
    parser.add_argument("--mission", required=True, help="Mission ID")
    parser.add_argument("--baseline", default="", help="Expected baseline fingerprint")
    args = parser.parse_args()

    root = args.root.resolve()
    current = fingerprint(root)
    stale = bool(args.baseline and args.baseline.removeprefix("sha256:") != current)
    checks, failures, _ = build_checks(root)

    verdict = "STALE_STATE" if stale else ("BLOCKED" if failures else "PASS")
    exit_code = 2 if stale else (1 if failures else 0)

    # V2.1.3 (arbitrage #6) — classification du sceau :
    #  - evidence/chain_head.sha256 (local, vérifiable par re-calcul) = TAMPER_EVIDENT
    #  - certificat de marbre ancré côté distant (POST_PUB_VERIFIED) = IMMUTABLE
    chain_head_path = root / "evidence" / "chain_head.sha256"
    seal_classification = {
        "evidence_chain_head": str(chain_head_path) if chain_head_path.is_file() else "ABSENT",
        "classification": "TAMPER_EVIDENT" if chain_head_path.is_file() else "UNSEALED",
        "immutable": "IMMUTABLE (ancrage distant POST_PUB_VERIFIED — certificat de marbre)",
        "note": "preuve locale vérifiable par re-calcul ; l'immutabilité définitive est établie "
                "côté distant après publication vérifiée (jamais auto-attestée).",
    }

    ledger = {
        "protocol": "Loi-Parite-Absolue",
        "version": "2.1.3",
        "mission_id": args.mission,
        "seal_classification": seal_classification,
        "component_id": args.id,
        "component_type": args.type,
        "tesla_root": str(root),
        "baseline_fingerprint": f"sha256:{args.baseline.removeprefix('sha256:')}" if args.baseline else "UNSPECIFIED",
        "current_fingerprint": f"sha256:{current}",
        "stale_state": stale,
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "verdict_global": verdict,
        "exit_code": exit_code,
        "checks": checks,
        "failures": failures,
        "orphans": [],
        "ghosts": [],
        "self_heal_iterations": 0,
    }

    evidence = root / "evidence"
    evidence.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-%f")
    path = evidence / f"parity_{args.mission}_{stamp}.json"
    path.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({
        "verdict": verdict,
        "exit_code": exit_code,
        "ledger": str(path),
        "failures": failures
    }, ensure_ascii=False, indent=2))

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
