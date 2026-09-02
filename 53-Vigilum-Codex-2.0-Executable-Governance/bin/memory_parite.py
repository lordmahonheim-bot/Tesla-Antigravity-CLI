#!/usr/bin/env python3
"""Vigilum Codex 2.1.1 — Memory Parity Scrutator (E3: Amnésie Mémorielle Partielle).

Deterministic enforcement of the RETEX corrective action
"Bouclage des Piliers Mémoire" (Invariant M-014): no mission closure is
acceptable without the N/N SHA-256 matrix report and exit code 0, where N is
governed by a DECLARATIVE manifest (never hardcoded at runtime).

Manifest resolution order (first hit wins):
  1. --manifest <file>                       (explicit; JSON or YAML-subset)
  2. <TESLA_ROOT>/memory/MEMORY_MANIFEST.yaml
  3. <module>/manifest/memory_manifest_v2.1.yaml   (canonical shipped 13)
  4. built-in DEFAULT_PILLARS                      (fallback, 13 canoniques)

Exit codes (fail-closed, Invariants P1/P3/P7):
  0 PASS           matrix N/N all present and matching baseline (if any)
  1 BLOCKED        at least one pillar missing or empty
  2 STALE_STATE    baseline hashes declared and a pillar drifted
  66 UNKNOWN       memory/ directory unobservable (UNKNOWN != PASS)
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

# Script-execution shim: allow `python3 bin/memory_parite.py` from any CWD
# while keeping package imports (E4-compliant absolute resolution).
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.orchestration.yaml_mini import YamlMiniError, load_file  # noqa: E402

EXIT_PASS = 0
EXIT_BLOCKED = 1
EXIT_STALE = 2
EXIT_USAGE = 64
EXIT_UNKNOWN = 66

# Fallback canonique (utilisé uniquement si aucun manifeste n'est trouvé).
DEFAULT_PILLARS: list[str] = [
    "PROJECT_STATE.md",
    "SESSION_LOG.md",
    "liste_projets_antigravity_BASE.md",
    "AGENTS.md",
    "GEMINI.md",
    "ENGINE.md",
    "FORCE_TOOLING.md",
    "SOUL.md",
    "TESLA.json",
    "settings.json",
    "Le_Conducteur_Absolu_v3.2.1.md",
    "PROTOCOLES/GRAVURE-SUR-MARBRE.md",
    "PROTOCOLES/LOI-DE-PARITE-ABSOLUE.md",
]

SHIPPED_MANIFEST = Path(__file__).resolve().parent.parent / "manifest" / "memory_manifest_v2.1.yaml"


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


def _extract_pillars(data: Any) -> list[str] | None:
    """Extract pillar paths from a manifest payload (JSON or YAML-subset dict)."""
    if isinstance(data, list):
        if all(isinstance(item, str) for item in data):
            return [str(item) for item in data]
        if all(isinstance(item, dict) for item in data):
            paths = [item.get("path") for item in data]
            if all(isinstance(p, str) and p for p in paths):
                return [str(p) for p in paths]
        return None
    if isinstance(data, dict):
        required = data.get("required_pillars")
        if isinstance(required, list) and all(isinstance(item, dict) for item in required):
            paths = [item.get("path") for item in required]
            if all(isinstance(p, str) and p for p in paths):
                return [str(p) for p in paths]
        if isinstance(required, list) and all(isinstance(item, str) for item in required):
            return [str(item) for item in required]
        if isinstance(data.get("pillars"), list) and all(isinstance(item, str) for item in data["pillars"]):
            return [str(item) for item in data["pillars"]]
    return None


def load_pillars(args_manifest: str | None, root: Path | None) -> list[str]:
    """Resolve the pillar list from the manifest resolution order (fail-closed)."""
    candidates: list[Path] = []
    if args_manifest:
        candidates.append(Path(args_manifest).expanduser())
    else:
        if root is not None:
            candidates.append(root / "memory" / "MEMORY_MANIFEST.yaml")
        candidates.append(SHIPPED_MANIFEST)

    for candidate in candidates:
        if not candidate.is_file():
            continue
        try:
            if candidate.suffix.lower() in (".yaml", ".yml"):
                data = load_file(str(candidate))
            else:
                data = json.loads(candidate.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, YamlMiniError) as exc:
            if args_manifest:
                raise SystemExit(f"usage: manifest unparsable: {candidate}: {exc}") from exc
            continue
        pillars = _extract_pillars(data)
        if pillars:
            return pillars
        if args_manifest:
            raise SystemExit(f"usage: manifest structure unsupported: {candidate}")

    return list(DEFAULT_PILLARS)


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
        "protocol": "Invariant M-014 — Piliers Mémoire (Manifeste Déclaratif)",
        "version": "2.1.1",
        "verdict": verdict,
        "exit_code": exit_code,
        "manifest_source": str(SHIPPED_MANIFEST),
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
    parser = argparse.ArgumentParser(description="Memory parity scrutator (manifest-driven, M-014)")
    parser.add_argument("--root", default=None, help="TESLA_ROOT (default: $TESLA_ROOT or CWD)")
    parser.add_argument("--mission", default="SGC-EXEC-GOV-03", help="Mission ID (informational)")
    parser.add_argument("--manifest", default=None, help="Manifest override (JSON or YAML subset)")
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

    pillars = load_pillars(args.manifest, root)
    baseline = load_baseline(args.baseline)
    exit_code, result = audit_memory(root, pillars, baseline)
    result["mission_id"] = args.mission
    result["pillars"] = pillars
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
