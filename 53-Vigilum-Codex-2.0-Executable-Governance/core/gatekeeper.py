#!/usr/bin/env python3
"""Fail-closed validation of a local mission lock (Gatekeeper).

The validator is intentionally dependency-free and deterministic.
It never grants permission based on a missing, expired, malformed, or mismatched lock.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

EXIT_PASS = 0
EXIT_BLOCKED = 1
EXIT_USAGE = 64
EXIT_MISSING = 66


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a Synergy mission lock")
    parser.add_argument("--lock", type=Path, required=True, help="Path to lock JSON file")
    parser.add_argument("--mission", required=True, help="Mission ID expected")
    parser.add_argument("--operation", required=True, help="Operation requested")
    parser.add_argument("--root", type=Path, required=True, help="Target workspace root")
    parser.add_argument("--now", type=float, default=None, help="Unix timestamp override for deterministic testing")
    return parser.parse_args()


def fail(reason: str, *, lock: str, mission: str) -> int:
    print(json.dumps({
        "verdict": "BLOCKED",
        "reason": reason,
        "lock": lock,
        "mission_id": mission
    }, sort_keys=True))
    return EXIT_BLOCKED


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    lock_path = args.lock.resolve()

    if not root.is_dir():
        return fail("ROOT_MISSING", lock=str(lock_path), mission=args.mission)
    if not lock_path.is_file():
        print(json.dumps({
            "verdict": "UNKNOWN",
            "reason": "LOCK_MISSING",
            "lock": str(lock_path),
            "mission_id": args.mission
        }, sort_keys=True))
        return EXIT_MISSING

    try:
        payload: dict[str, Any] = json.loads(lock_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return fail("LOCK_INVALID_JSON", lock=str(lock_path), mission=args.mission)

    required = {"mission_id", "root", "allowed_operations", "issued_at", "expires_at", "nonce"}
    if not required.issubset(payload):
        return fail("LOCK_MISSING_FIELDS", lock=str(lock_path), mission=args.mission)
    if payload.get("mission_id") != args.mission:
        return fail("MISSION_MISMATCH", lock=str(lock_path), mission=args.mission)

    try:
        declared_root = Path(str(payload["root"])).expanduser().resolve()
        issued_at = float(payload["issued_at"])
        expires_at = float(payload["expires_at"])
    except (TypeError, ValueError, OSError):
        return fail("LOCK_FIELDS_INVALID", lock=str(lock_path), mission=args.mission)

    if declared_root != root:
        return fail("ROOT_MISMATCH", lock=str(lock_path), mission=args.mission)
    if not isinstance(payload["allowed_operations"], list) or args.operation not in payload["allowed_operations"]:
        return fail("OPERATION_NOT_ALLOWED", lock=str(lock_path), mission=args.mission)

    now = time.time() if args.now is None else args.now
    if expires_at <= issued_at or now < issued_at or now >= expires_at:
        return fail("LOCK_EXPIRED_OR_NOT_YET_VALID", lock=str(lock_path), mission=args.mission)
    if not str(payload["nonce"]).strip():
        return fail("NONCE_EMPTY", lock=str(lock_path), mission=args.mission)

    digest = hashlib.sha256(lock_path.read_bytes()).hexdigest()
    print(json.dumps({
        "verdict": "PASS",
        "mission_id": args.mission,
        "operation": args.operation,
        "lock_sha256": digest,
        "root": str(root),
        "expires_at": expires_at,
        "pid": os.getpid(),
    }, sort_keys=True))
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
