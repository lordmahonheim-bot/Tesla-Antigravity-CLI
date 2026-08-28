#!/usr/bin/env python3
"""Vigilum Codex 2.1 — Memory Parity Loop (E3: Amnésie Mémorielle Partielle).

Deterministic enforcement of the RETEX corrective action
"Bouclage des 13 Piliers Mémoire": no mission closure is acceptable without
the 13/13 SHA-256 matrix report and exit code 0.

Behavior (fail-closed, Invariants P1/P3/P7):
  - Memory directory missing          -> UNKNOWN (exit 66): an unobservable
                                          state is never a PASS.
  - Pillar missing or empty           -> BLOCKED (exit 1), never synthesized.
  - --baseline hashes declared and a
    pillar drifted                    -> STALE_STATE (exit 2).

Usage
-----
  python3 bin/memory_parite.py --root <TESLA_ROOT> [--mission <ID>]
                               [--manifest <json-list>] [--baseline <json-map>]
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

EXIT_PASS = 0
EXIT_BLOCKED = 1
EXIT_STALE = 2
EXIT_USAGE = 64
EXIT_UNKNOWN = 66

# Canonical 13 pillars (Source de Vérité, AGENTS.md Rule 14 / Loi de Parité).
DEFAULT_PILLARS: list[str] = [
    "PROJECT_STATE.md",                      # Ancrage à court terme
    "SESSION_LOG.md",                        # Historique chronologique
    "liste_projets_antigravity_BASE.md",     # Taxonomie canonique des projets
    "TESLA.json",                            # Registre des capacités
    "FORCE_TOOLING.md",                      # Policy Registry & lifecycle
    "ENGINE.md",                             # Moteurs cognitifs
    "SOUL.md",                               # Identité constitutionnelle
    "AGENTS.md",                             # Gouvernance opérationnelle
    "SETTINGS.json",                         # Configuration de l'écosystème
    "GEMINI.md",                             # Contrat de modèle (Gemini)
    "knowledge_graph.json",                  # Graphe relationnel canonique
    "TELEGRAM_SYNAPSE.md",                   # Synapse de canal (Telegram)
    "CLAUDE.md",                             # Contrat de modèle (Claude)
]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def resolve_root(args_root: str | None) -> Path | None:
    import os
    env_root = os.environ.get("TESLA_ROOT")
    if args_root:
        candidate = Path(args_root).expanduser()
        return candidate.resolve() if candidate.is_dir() else None
    if env_root:
        candidate = Path(env_root).expanduser()
        return candidate.resolve() if candidate.is_dir() else None
    return None


def load_pillars(args_manifest: str | None) -> list[str]:
    if not args_manifest:
        return list(DEFAULT_PILLARS)
    manifest = Path(args_manifest).expanduser()
    if not manifest.is_file():
        raise SystemExit(f"usage: manifest not found: {manifest}")
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"usage: manifest is not valid JSON: {exc}") from exc
    if isinstance(data, list):
        pillars = [str(p) for p in data]
    elif isinstance(data, dict) and isinstance(data.get("pillars"), list):
        pillars = [str(p) for p in data["pillars"]]
    else:
        raise SystemExit("usage: manifest must be a list or {pillars: [...]}")
    if not pillars:
        raise SystemExit("usage: manifest pillar list is empty")
    return pillars


def load_baseline(args_baseline: str | None) -> dict[str, str]:
    if not args_baseline:
        return {}
    baseline = Path(args_baseline).expanduser()
    if not baseline.is_file():
        raise SystemExit(f"usage: baseline not found: {baseline}")
    try:
        data = json.loads(baseline.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"usage: baseline is not valid JSON: {exc}") from exc
    return {str(k): str(v) for k, v in data.items()}


def audit_memory(root: Path, pillars: list[str], baseline: dict[str, str]) -> tuple[int, dict[str, Any]]:
    memory_dir = root / "memory"
    if not memory_dir.is_dir():
        return EXIT_UNKNOWN, {
            "verdict": "UNKNOWN",
            "reason": "MEMORY_DIR_UNOBSERVABLE",
            "note": "Invariant P3 (UNKNOWN != PASS): no memory parity can be certified "
                    "without the memory/ directory.",
            "memory_dir": str(memory_dir),
        }

    rows: list[dict[str, Any]] = []
    passed = 0
    missing: list[str] = []
    drifted: list[str] = []

    for pillar in pillars:
        path = memory_dir / pillar
        row: dict[str, Any] = {"file": pillar}
        if not path.is_file():
            row.update({"verdict": "MISSING", "note": "pillar file is absent"})
            missing.append(pillar)
        else:
            raw = path.read_bytes()
            if not raw.strip():
                row.update({"verdict": "EMPTY", "note": "pillar file is empty"})
                missing.append(pillar)
            else:
                digest = sha256_bytes(raw)
                expected = baseline.get(pillar)
                if expected is not None and not hmac.compare_digest(expected.lower(), digest.lower()):
                    row.update({"verdict": "DRIFT", "sha256": digest, "expected_sha256": expected})
                    drifted.append(pillar)
                else:
                    row.update({"verdict": "PASS", "sha256": digest})
                    passed += 1
        rows.append(row)

    total = len(pillars)
    verdict = "PASS"
    exit_code = EXIT_PASS
    if drifted:
        verdict = "STALE_STATE"
        exit_code = EXIT_STALE
    elif missing:
        verdict = "BLOCKED"
        exit_code = EXIT_BLOCKED

    result: dict[str, Any] = {
        "protocol": "Bouclage des 13 Piliers Mémoire",
        "version": "2.1.0",
        "verdict": verdict,
        "exit_code": exit_code,
        "pillars_total": total,
        "pillars_passed": passed,
        "missing": missing,
        "drifted": drifted,
        "matrix": rows,
        "memory_dir": str(memory_dir),
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    return exit_code, result


def main() -> int:
    parser = argparse.ArgumentParser(description="Memory parity loop (13 piliers)")
    parser.add_argument("--root", default=None, help="TESLA_ROOT (default: $TESLA_ROOT or CWD)")
    parser.add_argument("--mission", default="SGC-EXEC-GOV-03", help="Mission ID (informational)")
    parser.add_argument("--manifest", default=None, help="JSON list of pillar filenames (default: 13 canoniques)")
    parser.add_argument("--baseline", default=None, help="JSON map {pillar: sha256} for stale-state detection")
    args = parser.parse_args()

    root = resolve_root(args.root)
    if root is None:
        print(json.dumps({
            "verdict": "UNKNOWN",
            "reason": "TESLA_ROOT_UNRESOLVED",
            "note": "no --root, no $TESLA_ROOT, and CWD does not resolve to a workspace root",
        }, indent=2, ensure_ascii=False))
        return EXIT_UNKNOWN

    pillars = load_pillars(args.manifest)
    baseline = load_baseline(args.baseline)
    exit_code, result = audit_memory(root, pillars, baseline)
    result["mission_id"] = args.mission
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
