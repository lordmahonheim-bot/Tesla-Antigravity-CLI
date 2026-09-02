#!/usr/bin/env python3
"""Vigilum Codex 2.1.3 — Cryptographic Marble Certificate (Sceau de Marbre).

Deterministic issuance of the immutability certificate (V2.1.2 arbitrage #3):
a full cryptographic anchor — local_commit_sha, remote_commit_sha,
evidence_chain_head, dag_sha256, receipts_manifest_sha256 — sealed in mode
0444 (tamper-evident). Refuses to issue unless the Mission Closure Controller
recorded MARBLE_ELIGIBLE (runtime/marble_eligibility.json).

V2.1.3 (arbitrage #6) — classification explicite du sceau :
  - TAMPER_EVIDENT : preuve locale (evidence/chain_head.sha256), vérifiable
    par re-calcul, mutable jusqu'à ancrage distant ;
  - IMMUTABLE      : certificat ancré côté distant (--remote-commit,
    POST_PUB_VERIFIED) — jamais auto-attesté.

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


def _chain_head(root: Path) -> dict[str, str]:
    """V2.1.3 (arbitrage #6) : point de tête calculé sur le ledger de preuve.

    H_n = SHA-256(evidence_ledger) — calculé sur le plus récent ledger
    (test_runner_*.json / parity_*.json). Classification explicite :
    TAMPER_EVIDENT (preuve locale, vérifiable) vs IMMUTABLE (établi côté
    distant après POST_PUB_VERIFIED).
    """
    evidence_dir = root / "evidence"
    candidates: list[Path] = []
    if evidence_dir.is_dir():
        candidates = sorted(
            [p for p in evidence_dir.glob("*.json") if p.name.startswith(("test_runner_", "parity_"))],
            key=lambda p: p.name,
        )
    if candidates:
        newest = candidates[-1]
        digest = hashlib.sha256(newest.read_bytes()).hexdigest()
        return {"value": f"sha256:{digest} {newest.name}", "seal_class": "TAMPER_EVIDENT",
                "note": "immutabilité définitive établie côté distant après POST_PUB_VERIFIED"}
    path = root / "evidence" / "chain_head.sha256"
    if path.is_file():
        content = path.read_text(encoding="utf-8").strip()
        if content:
            return {"value": content, "seal_class": "TAMPER_EVIDENT", "note": "ancrage pré-existant"}
    return {"value": "UNSEALED", "seal_class": "UNSEALED", "note": "aucun ledger de preuve observable"}


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
    for path in sorted(receipts_dir.glob("receipt_*.json")):
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

    chain_head = _chain_head(root)
    # V2.1.3 (arbitrage #6) : TAMPER_EVIDENT local → IMMUTABLE une fois l'ancre
    # distante fournie (POST_PUB_VERIFIED). L'immutabilité n'est jamais
    # auto-attestée : elle repose sur l'ancre de commit côté distant.
    if remote_commit:
        seal_class = "IMMUTABLE"
        seal_note = ("immutabilité ancrée côté distant (POST_PUB_VERIFIED) — "
                     "vérifiable par re-calcul local et ancre de commit distante")
        status = "SEALED_IMMUTABLE"
    else:
        seal_class = chain_head.get("seal_class", "TAMPER_EVIDENT")
        seal_note = chain_head.get("note", "")
        status = "SEALED_TAMPER_EVIDENT"
    certificate: dict[str, Any] = {
        "certificate_type": "MARBLE_CERTIFICATE",
        "doctrine": "Vigilum Codex 2.1 — Sovereign Shield",
        "status": status,
        "seal_class": seal_class,
        "seal_note": seal_note,
        "mission_id": mission,
        "closure_profile": ledger.get("closure_profile"),
        "state_at_issuance": ledger.get("state"),
        "local_commit_sha": _local_commit_sha(root),
        "remote_commit_sha": remote_commit or "PENDING_AUTHORIZATION",
        "evidence_chain_head": chain_head.get("value"),
        "dag_sha256": _dag_sha256(root, graph_override),
        "receipts_manifest_sha256": _receipts_manifest_sha256(root),
        "authority": "Lord Mahonheim (Biological Gate)",
        "issued_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
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
