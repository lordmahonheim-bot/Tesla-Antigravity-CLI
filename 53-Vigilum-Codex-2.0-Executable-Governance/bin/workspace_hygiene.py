#!/usr/bin/env python3
"""Vigilum Codex 2.1.1 — Workspace Hygiene & Quarantine Manager (E5: Encombrement).

Deterministic enforcement of the RETEX corrective action
"Hygiène du Workspace & Quarantaine Atomique" (Invariant H-005): transitory
drafts and ephemeral metrics are quarantined atomically into
``runtime/drafts/archive_<timestamp>/``, guaranteeing a clean working copy
before the final audit phase.

Report mode (default):  verdict BLOCKED (exit 1) when drafts are detected.
Prune mode (--prune):   atomic move (same-filesystem os.replace) into the
                        quarantine archive, then verdict PASS (exit 0).

Canonical finals (LOCKED/FINAL/CANON/SPEC/SEALED/DIAGNOSTIC) are NEVER
quarantined. Structural module directories are never scanned.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

EXIT_PASS = 0
EXIT_BLOCKED = 1
EXIT_USAGE = 64
EXIT_UNKNOWN = 66

CANONICAL_HINTS = ("LOCKED", "FINAL", "CANON", "SPEC", "SEALED", "DIAGNOSTIC")
_VERSIONED_DOC = re.compile(r"_V\d+(?:\.\d+)+\.[Mm][Dd]$")
_EPHEMERAL_EXT = re.compile(r"\.(tmp|bak|orig|swp|swo)$", re.IGNORECASE)
_TRAILING_TILDE = re.compile(r"~$")

# Structural dirs of the governance module that must never be scanned/archived.
_STRUCTURAL = {
    "bin", "core", "tests", "schemas", "docs", "evidence", "examples",
    "manifest", "runtime", ".git", "__pycache__", ".agents", "memory",
}


def _is_canonical(name: str) -> bool:
    return any(hint in name.upper() for hint in CANONICAL_HINTS)


def _is_draft(path: Path) -> bool:
    """Classify a file as a transitory draft (canonical finals excluded)."""
    name = path.name
    if _is_canonical(name):
        return False
    if _VERSIONED_DOC.search(name):
        return True
    if _EPHEMERAL_EXT.search(name):
        return True
    if _TRAILING_TILDE.search(name):
        return True
    parent = path.parent.as_posix()
    if "/capability-health/" in parent and name.endswith(".json"):
        return True
    if path.suffix.lower() in (".tmp", ".bak", ".orig"):
        return True
    return False


def scan_drafts(root: Path, extra_targets: list[str]) -> list[Path]:
    """Discover draft files under OUTPUTS/ + runtime capability-health + extras."""
    targets: list[Path] = []
    for rel in list(extra_targets) + ["OUTPUTS", "runtime/capability-health", ".runtime/capability-health"]:
        candidate = root / rel
        if candidate.is_dir():
            targets.append(candidate)

    drafts: list[Path] = []
    for target in targets:
        for path in sorted(target.rglob("*")):
            if not path.is_file():
                continue
            parts = set(path.relative_to(root).parts[:2] if len(path.relative_to(root).parts) > 1 else path.relative_to(root).parts)
            if parts & _STRUCTURAL and path.parent == root:
                continue
            if _is_draft(path):
                drafts.append(path)
    # De-duplicate while preserving order
    seen: set[str] = set()
    unique: list[Path] = []
    for path in drafts:
        key = str(path.resolve())
        if key not in seen:
            seen.add(key)
            unique.append(path)
    return unique


def quarantine(drafts: list[Path], archive_dir: Path) -> tuple[list[dict[str, Any]], list[str]]:
    """Atomically move drafts into the quarantine archive (same filesystem)."""
    archived: list[dict[str, Any]] = []
    errors: list[str] = []
    for draft in drafts:
        if not draft.is_file():
            continue
        destination = archive_dir / draft.name
        if destination.exists():
            destination = archive_dir / f"{draft.stem}_{int(time.time() * 1000)}{draft.suffix}"
        try:
            if draft.resolve().parent == archive_dir.resolve():
                continue
            os.replace(str(draft), str(destination))
            archived.append({"from": str(draft), "to": str(destination)})
        except OSError as exc:
            errors.append(f"{draft}: {exc}")
    return archived, errors


def run_hygiene(root: Path, prune: bool, extra_targets: list[str]) -> tuple[int, dict[str, Any]]:
    root = root.resolve()
    if not root.is_dir():
        return EXIT_UNKNOWN, {"verdict": "UNKNOWN", "reason": "ROOT_MISSING", "root": str(root)}

    drafts = scan_drafts(root, extra_targets)
    archive_dir = root / "runtime" / "drafts" / f"archive_{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}"

    result: dict[str, Any] = {
        "protocol": "Invariant H-005 — Hygiène & Quarantaine",
        "version": "2.1.1",
        "root": str(root),
        "drafts_detected": [str(p) for p in drafts],
        "drafts_count": len(drafts),
        "prune": prune,
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }

    if not prune:
        if drafts:
            result.update({"verdict": "BLOCKED", "exit_code": EXIT_BLOCKED,
                           "note": "transitory drafts present — run --prune to quarantine"})
            return EXIT_BLOCKED, result
        result.update({"verdict": "PASS", "exit_code": EXIT_PASS})
        return EXIT_PASS, result

    if drafts:
        archive_dir.mkdir(parents=True, exist_ok=True)
        archived, errors = quarantine(drafts, archive_dir)
        result["archived"] = archived
        result["archive_dir"] = str(archive_dir)
        result["errors"] = errors
        if errors:
            result.update({"verdict": "BLOCKED", "exit_code": EXIT_BLOCKED})
            return EXIT_BLOCKED, result
    else:
        result["archived"] = []
        result["archive_dir"] = str(archive_dir)

    result.update({"verdict": "PASS", "exit_code": EXIT_PASS})
    return EXIT_PASS, result


def main() -> int:
    parser = argparse.ArgumentParser(description="Workspace hygiene & quarantine (H-005)")
    parser.add_argument("--root", type=Path, required=True, help="Workspace root")
    parser.add_argument("--prune", action="store_true", help="Quarantine drafts atomically")
    parser.add_argument("--target", action="append", default=[], help="Extra scan target (root-relative)")
    parser.add_argument("--dry-run", action="store_true", help="Report only (same as default)")
    args = parser.parse_args()

    code, result = run_hygiene(args.root, args.prune and not args.dry_run, args.target)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return code


if __name__ == "__main__":
    sys.exit(main())
