#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from core.broker.tesla_brokerd import BrokerPaths, process_once, submit_intent  # noqa: E402


class GatekeeperAndParityTests(unittest.TestCase):
    def test_gatekeeper_accepts_valid_lock(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            lock = root / "lock.json"
            lock.write_text(json.dumps({
                "mission_id": "M-1",
                "root": str(root),
                "allowed_operations": ["write_file"],
                "issued_at": 100.0,
                "expires_at": 200.0,
                "nonce": "nonce-1",
            }), encoding="utf-8")
            result = subprocess.run([
                sys.executable, str(ROOT / "core/gatekeeper.py"),
                "--lock", str(lock), "--mission", "M-1", "--operation", "write_file",
                "--root", str(root), "--now", "150",
            ], capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('"verdict": "PASS"', result.stdout)

    def test_gatekeeper_blocks_expired_lock(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            lock = root / "lock.json"
            lock.write_text(json.dumps({
                "mission_id": "M-1", "root": str(root), "allowed_operations": ["write_file"],
                "issued_at": 100.0, "expires_at": 110.0, "nonce": "nonce-1",
            }), encoding="utf-8")
            result = subprocess.run([
                sys.executable, str(ROOT / "core/gatekeeper.py"),
                "--lock", str(lock), "--mission", "M-1", "--operation", "write_file",
                "--root", str(root), "--now", "150",
            ], capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 1)
            self.assertIn("LOCK_EXPIRED_OR_NOT_YET_VALID", result.stdout)

    def test_gatekeeper_blocks_missing_lock(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            lock = root / "non_existent_lock.json"
            result = subprocess.run([
                sys.executable, str(ROOT / "core/gatekeeper.py"),
                "--lock", str(lock), "--mission", "M-1", "--operation", "write_file",
                "--root", str(root), "--now", "150",
            ], capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 66)
            self.assertIn("LOCK_MISSING", result.stdout)


class IntentAndBrokerTests(unittest.TestCase):
    def test_schema_is_valid_json_and_restricts_operation(self) -> None:
        schema = json.loads((ROOT / "schemas/intent_v3.1.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(schema["properties"]["operation"]["const"], "write_file")
        self.assertTrue(schema["additionalProperties"] is False)

    def test_broker_staging_submission_and_execution(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = BrokerPaths.from_root(root)
            content = "alpha content\n"
            payload = {
                "intent_id": "intent-stage-1",
                "mission_id": "SGC-EXEC-GOV-03",
                "operation": "write_file",
                "target": "governed/output.txt",
                "content": content,
                "sha256": hashlib.sha256(content.encode()).hexdigest(),
            }
            inbox_file = submit_intent(paths, payload)
            self.assertTrue(inbox_file.is_file())
            passed, failed = process_once(paths, secret=None, allow_unsigned=True)
            self.assertEqual(passed, 1)
            self.assertEqual(failed, 0)
            target_path = root / "governed/output.txt"
            self.assertEqual(target_path.read_text(encoding="utf-8"), content)
            self.assertIn("SUCCESS", (paths.done / "intent-stage-1.result.json").read_text(encoding="utf-8"))

    def test_broker_idempotence_noop(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = BrokerPaths.from_root(root)
            content = "identical content\n"
            payload = {
                "intent_id": "intent-idempotent",
                "mission_id": "SGC-EXEC-GOV-03",
                "operation": "write_file",
                "target": "out/idempotent.txt",
                "content": content,
                "sha256": hashlib.sha256(content.encode()).hexdigest(),
            }
            submit_intent(paths, payload)
            process_once(paths, secret=None, allow_unsigned=True)
            # Resubmit same intent
            submit_intent(paths, payload)
            passed, failed = process_once(paths, secret=None, allow_unsigned=True)
            self.assertEqual(passed, 1)
            self.assertEqual(failed, 0)
            self.assertIn("IDEMPOTENT_NOOP", (paths.done / "intent-idempotent.result.json").read_text(encoding="utf-8"))

    def test_broker_rejects_path_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = BrokerPaths.from_root(root)
            content = "malicious payload\n"
            payload = {
                "intent_id": "intent-escape",
                "mission_id": "SGC-EXEC-GOV-03",
                "operation": "write_file",
                "target": "../outside.txt",
                "content": content,
                "sha256": hashlib.sha256(content.encode()).hexdigest(),
            }
            submit_intent(paths, payload)
            passed, failed = process_once(paths, secret=None, allow_unsigned=True)
            self.assertEqual(passed, 0)
            self.assertEqual(failed, 1)
            self.assertIn("FAILED", (paths.failed / "intent-escape.result.json").read_text(encoding="utf-8"))

    def test_broker_recovers_stranded_processing_on_startup(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = BrokerPaths.from_root(root)
            paths.create()
            content = "recovered content\n"
            payload = {
                "intent_id": "intent-crash-recovery",
                "mission_id": "SGC-EXEC-GOV-03",
                "operation": "write_file",
                "target": "out/recovered.txt",
                "content": content,
                "sha256": hashlib.sha256(content.encode()).hexdigest(),
            }
            # Simulate crash: file left in processing/
            stranded = paths.processing / "intent-crash-recovery.json"
            stranded.write_text(json.dumps(payload), encoding="utf-8")

            passed, failed = process_once(paths, secret=None, allow_unsigned=True)
            self.assertEqual(passed, 1)
            self.assertEqual(failed, 0)
            self.assertEqual((root / "out/recovered.txt").read_text(encoding="utf-8"), content)


if __name__ == "__main__":
    unittest.main()
