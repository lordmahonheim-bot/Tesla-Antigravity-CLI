#!/usr/bin/env python3
"""Vigilum Codex 2.1.2 — Cryptographic Marble Certificate (Sceau de Marbre).

Deterministic issuance of the immutability certificate (V2.1.2 arbitrage #3):
a full cryptographic anchor — local_commit_sha, remote_commit_sha,
evidence_chain_head, dag_sha256, receipts_manifest_sha256 — sealed in mode
0444 (tamper-evident). Refuses to issue unless the Mission Closure Controller
recorded MARBLE_ELIGIBLE (runtime/marble_eligibility.json).

Output: CERTIFICATES/MARBLE_CERTIFICATE_<mission>_<ts>.json (hook-05 compatible).

Usage
-----
  python3 bin/marble_certificate.py --root <dir> --mission <id>
      [--remote-commit <sha>] [--out <dir>]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.orchestration.orchestration_gate import _default_receipts_dir  # noqa: E402

EXIT_PASS = 0
EXIT_BLOCKED = 1


def _local_commit_sha(root: Path) -> str:
    try:
        proc = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(root),
                              capture_output=True, text=True, check=False, timeout=15)
        if proc.returncode == 0 and proc.stdout.strip():
            return proc.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        pass
    return "UNCOMMITTED"


def _chain_head(root: Path) -> str:
    path = root / "evidence" / "chain_head.sha256"
    if path.is_file():
        content = path.read_text(encoding="utf-8").strip()
        if content:
            return content
    return "UNSEALED"


def _dag_sha256(root: Path, graph_override: str | None) -> str:
    if graph_override:
        candidate = Path(graph_override)
        if not candidate.is_absolute():
            candidate = root / candidate
        if candidate.is_file():
            return hashlib.sha256(candidate.read_bytes()).hexdigest()
    registry = root / "runtime" / "orchestration" / "active_mission.json"
    if registry.is_file():
        try:
            data = json.loads(registry.read_text(encoding="utf-8"))
            ref = data.get("mission_graph")
            if isinstance(ref, str) and ref:
                candidate = Path(ref)
                if not candidate.is_absolute():
                    candidate = root / candidate
                if candidate.is_file():
                    return hashlib.sha256(candidate.read_bytes()).hexdigest()
        except (OSError, json.JSONDecodeError):
            return "UNRESOLVED"
    return "UNRESOLVED"


def _receipts_manifest_sha256(root: Path) -> str:
    receipts_dir = _default_receipts_dir(root)
    if not receipts_dir.is_dir():
        return "UNSEALED"
    digest = hashlib.sha256()
    files = sorted(receipts_dir.glob("receipt_*.json"))
    if not files:
        return "UNSEALED"
    for path in files:
        digest.update(path.name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def build_certificate(root: Path, mission: str, remote_commit: str | None,
                      out_dir: Path | None, graph_override: str | None) -> tuple[int, dict[str, Any]]:
    root = root.resolve()
    eligibility = root / "runtime" / "marble_eligibility.json"
    if not eligibility.is_file():
        return EXIT_BLOCKED, {"verdict": "BLOCKED", "reason": "MARBLE_ELIGIBILITY_NOT_RECORDED",
                              "note": "Issue the certificate only after the Mission Closure "
                                      "Controller records marble_eligible=true."}
    try:
        ledger = json.loads(eligibility.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return EXIT_BLOCKED, {"verdict": "BLOCKED", "reason": "MARBLE_ELIGIBILITY_UNPARSEABLE"}
    if ledger.get("marble_eligible") is not True:
        return EXIT_BLOCKED, {"verdict": "BLOCKED", "reason": "MARBLE_NOT_ELIGIBLE",
                              "state": ledger.get("state")}

    certificate: dict[str, Any] = {
        "certificate_type": "MARBLE_CERTIFICATE",
        "doctrine": "Vigilum Codex 2.1 — Sovereign Shield",
        "status": "SEALED_IMMUTABLE",
        "mission_id": mission,
        "closure_profile": ledger.get("closure_profile"),
        "state_at_issuance": ledger.get("state"),
        "local_commit_sha": _local_commit_sha(root),
        "remote_commit_sha": remote_commit or "PENDING_AUTHORIZATION",
        "evidence_chain_head": _chain_head(root),
        "dag_sha256": _dag_sha256(root, graph_override),
        "receipts_manifest_sha256": _receipts_manifest_sha256(root),
        "authority": "Lord Mahonheim (Biological Gate)",
        "issued_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "integrity_classification": {
            "local_integrity": "TAMPER_EVIDENT",
            "external_anchor": "NOT_IMPLEMENTED",
            "immutability_scope": "LOCAL_POSIX_0444",
        },
    }

    target_dir = (out_dir or root / "CERTIFICATES").resolve()
    target_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-%f")
    target = target_dir / f"MARBLE_CERTIFICATE_{mission}_{stamp}.json"
    target.write_text(json.dumps(certificate, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    try:
        os.chmod(target, 0o444)  # tamper-evident: read-only seal
    except OSError:
        pass

    return EXIT_PASS, {"verdict": "SEALED", "certificate": str(target),
                       "mode": "0444", "anchors": certificate}


def main() -> int:
    parser = argparse.ArgumentParser(description="Cryptographic Marble Certificate (Sceau 0444)")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--mission", required=True)
    parser.add_argument("--remote-commit", default=None)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--graph", default=None)
    args = parser.parse_args()

    code, result = build_certificate(args.root, args.mission, args.remote_commit, args.out, args.graph)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return code


if __name__ == "__main__":
    sys.exit(main())
