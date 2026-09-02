#!/usr/bin/env python3
"""Vigilum Codex 2.1 — Audit Ceiling & SPEC LOCK (E1: Paralysie Documentaire).

Deterministic enforcement of the RETEX corrective action
"Plafond d'Audit Théorique (Max 3)": the theoretical audit cycle of a SPEC is
automatically frozen at the 3rd pass (SPEC LOCK) and the mission is forced
towards executable code. No textual refinement may exceed the ceiling.

Mechanism
---------
State lives under ``<root>/runtime/audit/``:
  audit_cap_<SPEC>.json         pass ledger (count + history)
  SPEC_LOCK_<SPEC>.json         atomic O_CREAT|O_EXCL lock (anti-replay, A-003 style)

Actions
-------
--check     Report status: BELOW_CEILING (0) | AT_CEILING (80) | BLOCKED (1)
--record    Register one audit pass; at the ceiling, atomically create the
            SPEC LOCK and refuse any further pass (exit 80).
--reset     Open a new audit cycle for a NEW spec version (explicit, safe).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import uuid
from pathlib import Path

EXIT_PASS = 0
EXIT_BLOCKED = 1
EXIT_USAGE = 64
EXIT_LOCKED = 80  # matches TESLA_EXIT_LOCK in core/hooks/lib/tesla-exit-codes.sh


def state_paths(root: Path, spec: str) -> tuple[Path, Path]:
    audit_dir = root / "runtime" / "audit"
    return audit_dir / f"audit_cap_{spec}.json", audit_dir / f"SPEC_LOCK_{spec}.json"


def load_state(root: Path, spec: str, default_max: int) -> tuple[dict, Path]:
    state_file, lock_file = state_paths(root, spec)
    state: dict = {"spec": spec, "max": default_max, "passes": [], "locked": False}
    if state_file.is_file():
        try:
            loaded = json.loads(state_file.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                state.update(loaded)
        except (OSError, json.JSONDecodeError):
            return {"spec": spec, "max": default_max, "passes": [], "locked": False,
                    "corrupt": str(state_file)}, state_file
    if lock_file.is_file():
        state["locked"] = True
    return state, state_file


def save_state(state: dict, state_file: Path) -> None:
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def create_lock(root: Path, spec: str, state: dict) -> dict:
    _, lock_file = state_paths(root, spec)
    lock_file.parent.mkdir(parents=True, exist_ok=True)
    lock = {
        "spec": spec,
        "type": "SPEC_LOCK",
        "locked_at": time.time(),
        "nonce": uuid.uuid4().hex,
        "max_audit_passes": state.get("max"),
        "directive": "SPEC LOCK — audit textuel gelé, bascule forcée vers le code exécutable.",
    }
    try:
        fd = os.open(str(lock_file), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(json.dumps(lock, indent=2) + "\n")
    except FileExistsError:
        lock["note"] = "lock already present (replay-safe)"
    return lock


def cmd_check(root: Path, spec: str, max_passes: int) -> tuple[int, dict]:
    state, state_file = load_state(root, spec, max_passes)
    count = len(state.get("passes", []))
    locked = bool(state.get("locked"))
    if locked:
        return EXIT_LOCKED, {"verdict": "SPEC_LOCK", "spec": spec, "passes": count, "max": max_passes,
                             "state": str(state_file)}
    if count >= max_passes:
        return EXIT_BLOCKED, {"verdict": "AT_CEILING_UNLOCKED", "spec": spec, "passes": count, "max": max_passes,
                              "note": "inconsistent state: ceiling reached but no lock — run --record to seal"}
    return EXIT_PASS, {"verdict": "BELOW_CEILING", "spec": spec, "passes": count, "max": max_passes,
                       "remaining": max_passes - count}


def cmd_record(root: Path, spec: str, max_passes: int, now: float | None) -> tuple[int, dict]:
    state, state_file = load_state(root, spec, max_passes)
    count = len(state.get("passes", []))
    if state.get("locked"):
        return EXIT_LOCKED, {"verdict": "SPEC_LOCK", "spec": spec, "passes": count, "max": max_passes,
                             "note": "locked: further textual audit passes are forbidden"}
    if count >= max_passes:
        # Sealing pass: reach the ceiling AND atomically lock
        state["passes"].append({"ts": now if now is not None else time.time()})
        state["locked"] = True
        save_state(state, state_file)
        lock = create_lock(root, spec, state)
        return EXIT_LOCKED, {"verdict": "SPEC_LOCK_CREATED", "spec": spec, "passes": len(state["passes"]),
                             "max": max_passes, "lock": lock}
    state["passes"].append({"ts": now if now is not None else time.time()})
    save_state(state, state_file)
    new_count = len(state["passes"])
    if new_count >= max_passes:
        state["locked"] = True
        save_state(state, state_file)
        lock = create_lock(root, spec, state)
        return EXIT_LOCKED, {"verdict": "SPEC_LOCK_CREATED", "spec": spec, "passes": new_count,
                             "max": max_passes, "lock": lock}
    return EXIT_PASS, {"verdict": "BELOW_CEILING", "spec": spec, "passes": new_count, "max": max_passes,
                       "remaining": max_passes - new_count}


def cmd_reset(root: Path, spec: str, max_passes: int) -> tuple[int, dict]:
    state_file, lock_file = state_paths(root, spec)
    removed = []
    for path in (state_file, lock_file):
        try:
            if path.is_file():
                path.unlink()
                removed.append(str(path))
        except OSError:
            pass
    return EXIT_PASS, {"verdict": "RESET", "spec": spec, "removed": removed,
                       "note": "new audit cycle opened — only valid for a NEW spec version (e.g. V3.7)"}


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit ceiling & SPEC LOCK (max 3 passes)")
    parser.add_argument("--root", type=Path, required=True, help="Workspace root")
    parser.add_argument("--spec", default="SGC-EXEC-GOV-03", help="SPEC identifier (e.g. V3.6.2)")
    parser.add_argument("--max", type=int, default=3, help="Audit ceiling (default 3)")
    parser.add_argument("--check", action="store_true", help="Report current status")
    parser.add_argument("--record", action="store_true", help="Register one audit pass")
    parser.add_argument("--reset", action="store_true", help="Open a new cycle (explicit)")
    parser.add_argument("--now", type=float, default=None, help="Timestamp override (deterministic tests)")
    args = parser.parse_args()

    if args.max < 1:
        print(json.dumps({"verdict": "USAGE", "reason": "--max must be >= 1"}))
        return EXIT_USAGE

    if args.reset:
        code, result = cmd_reset(args.root, args.spec, args.max)
    elif args.record:
        code, result = cmd_record(args.root, args.spec, args.max, args.now)
    else:
        code, result = cmd_check(args.root, args.spec, args.max)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return code


if __name__ == "__main__":
    sys.exit(main())
