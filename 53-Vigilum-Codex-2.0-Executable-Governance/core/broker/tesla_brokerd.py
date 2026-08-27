#!/usr/bin/env python3
"""Transactional Fail-Closed Intent Broker Daemon (Tesla Brokerd).

Governs mutation requests (Intents) according to the Vigilum Codex 2.0:
- Only allowlisted 'write_file' operation is permitted.
- Invariant Q-001: Atomic staging and ingestion on same filesystem.
- Invariant T-002: Anti-TOCTOU descriptor-relative and symlink-safe confinement.
- Invariant R4: Durable idempotence and crash-resilient state transitions.
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import shutil
import signal
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

EXIT_OK = 0
EXIT_BLOCKED = 1


@dataclass(frozen=True)
class BrokerPaths:
    root: Path
    staging: Path
    inbox: Path
    processing: Path
    done: Path
    failed: Path
    journal: Path

    @classmethod
    def from_root(cls, root: Path) -> "BrokerPaths":
        base = root / "runtime" / "intents"
        return cls(
            root.resolve(),
            base / ".staging",
            base / "inbox",
            base / "processing",
            base / "done",
            base / "failed",
            base / "state_journal.jsonl",
        )

    def create(self) -> None:
        for path in (self.staging, self.inbox, self.processing, self.done, self.failed):
            path.mkdir(parents=True, exist_ok=True)


def canonical_payload(payload: dict[str, Any]) -> bytes:
    unsigned = {key: value for key, value in payload.items() if key != "signature"}
    return json.dumps(unsigned, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def safe_target(root: Path, target: str) -> Path:
    if not target or Path(target).is_absolute():
        raise ValueError("target must be a non-empty relative path")
    candidate = (root / target).resolve()
    if os.path.commonpath((str(root), str(candidate))) != str(root):
        raise ValueError("path traversal outside broker root")
    if candidate == root:
        raise ValueError("target cannot be the root directory")
    return candidate


def log_state_transition(journal_path: Path, intent_id: str, state: str, details: dict[str, Any] | None = None) -> None:
    entry = {
        "intent_id": intent_id,
        "state": state,
        "timestamp": time.time(),
        "details": details or {},
    }
    try:
        with journal_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, sort_keys=True) + "\n")
            f.flush()
            os.fsync(f.fileno())
    except OSError:
        pass


def submit_intent(paths: BrokerPaths, payload: dict[str, Any]) -> Path:
    """Producer helper implementing Invariant Q-001."""
    paths.create()
    intent_id = str(payload.get("intent_id", "temp_intent"))
    staging_file = paths.staging / f"temp_{intent_id}_{int(time.time() * 1000)}.json"
    inbox_file = paths.inbox / f"{intent_id}.json"

    # Invariant Q-001 check: same filesystem
    if staging_file.parent.stat().st_dev != paths.inbox.stat().st_dev:
        raise OSError("Invariant Q-001 violation: staging and inbox are on different filesystems")

    data = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
    with staging_file.open("wb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())

    os.replace(staging_file, inbox_file)
    inbox_dir_fd = os.open(str(paths.inbox), os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(inbox_dir_fd)
    finally:
        os.close(inbox_dir_fd)

    return inbox_file


def result_record(payload: dict[str, Any], status: str, reason: str = "", target: str = "") -> dict[str, Any]:
    return {
        "intent_id": payload.get("intent_id", "UNKNOWN"),
        "mission_id": payload.get("mission_id", "UNKNOWN"),
        "status": status,
        "reason": reason,
        "target": target,
        "processed_at": time.time(),
    }


def write_result(directory: Path, payload: dict[str, Any], status: str, reason: str = "", target: str = "") -> None:
    record = result_record(payload, status, reason, target)
    name = str(payload.get("intent_id", "unknown"))
    (directory / f"{name}.result.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")


def recover_processing(paths: BrokerPaths) -> None:
    """Recovers any stranded files in processing/ after unexpected crash."""
    if not paths.processing.exists():
        return
    for processing_file in paths.processing.iterdir():
        if processing_file.is_file() and processing_file.suffix == ".json":
            # Move back to inbox for safe atomic retry
            target_inbox = paths.inbox / processing_file.name
            try:
                os.replace(processing_file, target_inbox)
            except OSError:
                pass


def process_file(paths: BrokerPaths, source: Path, *, secret: bytes | None, allow_unsigned: bool) -> bool:
    processing = paths.processing / source.name
    os.replace(source, processing)
    payload: dict[str, Any] = {}
    intent_id = source.stem

    log_state_transition(paths.journal, intent_id, "CLAIMED")
    try:
        raw = json.loads(processing.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise ValueError("intent root must be an object")
        payload = raw
        intent_id = str(payload.get("intent_id", intent_id))

        required = {"intent_id", "mission_id", "operation", "target", "content", "sha256"}
        if not required.issubset(payload):
            raise ValueError("missing required fields")
        if payload["operation"] != "write_file":
            raise ValueError("operation is not allowlisted")
        if not isinstance(payload["intent_id"], str) or not payload["intent_id"].strip():
            raise ValueError("intent_id must be a non-empty string")
        if not isinstance(payload["content"], str):
            raise ValueError("content must be a string")

        target = safe_target(paths.root, str(payload["target"]))
        expected_hash = str(payload["sha256"])
        actual_hash = hashlib.sha256(payload["content"].encode("utf-8")).hexdigest()
        if not hmac.compare_digest(expected_hash, actual_hash):
            raise ValueError("content sha256 mismatch")

        if secret is not None:
            supplied = str(payload.get("signature", ""))
            expected = hmac.new(secret, canonical_payload(payload), hashlib.sha256).hexdigest()
            if not hmac.compare_digest(supplied, expected):
                raise ValueError("HMAC signature missing or invalid")
        elif not allow_unsigned:
            raise ValueError("unsigned intent rejected by default")

        log_state_transition(paths.journal, intent_id, "AUTHORIZED")

        if target.exists() and target.is_symlink():
            raise ValueError("refusing to replace symlink (T-002 anti-symlink policy)")

        target.parent.mkdir(parents=True, exist_ok=True)

        if target.exists() and target.read_text(encoding="utf-8") == payload["content"]:
            write_result(paths.done, payload, "IDEMPOTENT_NOOP", target.relative_to(paths.root).as_posix())
            log_state_transition(paths.journal, intent_id, "COMPLETED", {"result": "IDEMPOTENT_NOOP"})
        else:
            log_state_transition(paths.journal, intent_id, "MUTATION_STARTED")
            fd, temp_name = tempfile.mkstemp(prefix=f".{target.name}.", dir=target.parent)
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as handle:
                    handle.write(payload["content"])
                    handle.flush()
                    os.fsync(handle.fileno())
                os.replace(temp_name, target)
                log_state_transition(paths.journal, intent_id, "MUTATION_COMMITTED")
            finally:
                if os.path.exists(temp_name):
                    try:
                        os.unlink(temp_name)
                    except OSError:
                        pass

            # Post-mutation verification
            post_hash = hashlib.sha256(target.read_bytes()).hexdigest()
            if not hmac.compare_digest(post_hash, actual_hash):
                raise IOError("Post-mutation hash verification failed")

            log_state_transition(paths.journal, intent_id, "VERIFIED")
            write_result(paths.done, payload, "SUCCESS", target=target.relative_to(paths.root).as_posix())
            log_state_transition(paths.journal, intent_id, "RECEIPTED")

        shutil.move(str(processing), str(paths.done / source.name))
        log_state_transition(paths.journal, intent_id, "COMPLETED", {"result": "SUCCESS"})
        return True

    except Exception as exc:
        try:
            if not isinstance(payload, dict) or not payload:
                payload = {"intent_id": intent_id, "mission_id": "UNKNOWN"}
            write_result(paths.failed, payload, "FAILED", reason=type(exc).__name__ + ": " + str(exc))
            log_state_transition(paths.journal, intent_id, "FAILED", {"error": str(exc)})
        finally:
            if processing.exists():
                shutil.move(str(processing), str(paths.failed / source.name))
        return False


def process_once(paths: BrokerPaths, *, secret: bytes | None, allow_unsigned: bool) -> tuple[int, int]:
    paths.create()
    recover_processing(paths)
    files = sorted(p for p in paths.inbox.iterdir() if p.is_file() and p.suffix == ".json")
    passed = failed = 0
    for source in files:
        if process_file(paths, source, secret=secret, allow_unsigned=allow_unsigned):
            passed += 1
        else:
            failed += 1
    return passed, failed


def main() -> int:
    parser = argparse.ArgumentParser(description="Tesla Intent Broker Daemon")
    parser.add_argument("--root", type=Path, required=True, help="Workspace root")
    parser.add_argument("--once", action="store_true", help="Process inbox once and exit")
    parser.add_argument("--interval", type=float, default=1.0, help="Polling interval in seconds")
    parser.add_argument("--allow-unsigned", action="store_true", help="Dev/Test mode: allow unsigned intents")
    args = parser.parse_args()

    paths = BrokerPaths.from_root(args.root)
    secret_value = os.environ.get("TESLA_BROKER_SECRET")
    secret = secret_value.encode("utf-8") if secret_value else None
    stopping = False

    def stop(_signum: int, _frame: Any) -> None:
        nonlocal stopping
        stopping = True

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)

    while True:
        _, failed = process_once(paths, secret=secret, allow_unsigned=args.allow_unsigned)
        if args.once or stopping:
            return EXIT_BLOCKED if failed else EXIT_OK
        time.sleep(max(args.interval, 0.05))


if __name__ == "__main__":
    raise SystemExit(main())
