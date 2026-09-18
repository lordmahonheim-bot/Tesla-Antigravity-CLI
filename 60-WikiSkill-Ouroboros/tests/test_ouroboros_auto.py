#!/usr/bin/env python3
"""Tests Ouroboros Auto-Capture (STDLIB unittest, zero dependance).

Lancement :
    cd 60-WikiSkill-Ouroboros && python3 -m unittest discover -s tests -v

Couverture : scrubber, trace_writer (portabilite), autocapture (recu +
transcript), distiller (budget/eviction), rule_forger (eligibilite),
compatibilite des validateurs (regression des 3 formats), gating_judge V2
(controles negatifs), daemon (curseurs/backfill/inbox) et cycle E2E
"prime the pump" jusqu'au commit local.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from distiller import distill_trace, enforce_budget  # noqa: E402
from gating_judge import _check_holdout, _check_train_val  # noqa: E402
from index_linter import REQUIRED_COLUMNS, lint_file  # noqa: E402
from intent_formatter import validate_patch as validate_intent  # noqa: E402
from ouroboros_autocapture import (  # noqa: E402
    build_trace,
    ingest_receipt,
    parse_transcript_segment,
)
from ouroboros_cycle import run_cycle  # noqa: E402
from ouroboros_daemon import drain_inbox, resolve_brain_root, scan_transcripts  # noqa: E402
from patch_broker import validate_patch as validate_broker  # noqa: E402
from rule_forger import forge_pattern  # noqa: E402
from schemas import ExecutionTrace  # noqa: E402
from secrets_scrubber import REDACTED, scrub_text  # noqa: E402
from trace_writer import write_trace_bytes  # noqa: E402


class IsolatedRoot(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="ouroboros_test_")
        self.root = Path(self.tmp.name) / "tesla"
        self.root.mkdir()
        self._old_env = os.environ.get("TESLA_ROOT")
        os.environ["TESLA_ROOT"] = str(self.root)
        self.addCleanup(self._restore)

    def _restore(self):
        if self._old_env is None:
            os.environ.pop("TESLA_ROOT", None)
        else:
            os.environ["TESLA_ROOT"] = self._old_env
        self.tmp.cleanup()


def make_receipt(skill="tesla-web-raider", outcome="success", task="t1",
                 final="Extraction OK. American navy ships tracked."):
    score = {"success": 1.0, "partial": 0.5, "failure": 0.0}.get(outcome, 0.0)
    return {
        "skill": skill, "task_id": task, "model": "antigravity-cli",
        "outcome": outcome, "score": score,
        "verdict_sources": ["transcript:test:1", f"marker:{outcome.upper()}"],
        "steps": [{"index": 0, "type": "test", "summary": "collecte puis synthese"}],
        "final_answer": final,
    }


class SecretsScrubberTest(unittest.TestCase):
    def test_known_tokens(self):
        raw = "key ghp_abcdefghijklmnop123456 and sk-proj-ABCDEF1234567890 visit"
        clean, count = scrub_text(raw)
        self.assertNotIn("ghp_", clean)
        self.assertNotIn("sk-proj-", clean)
        self.assertGreaterEqual(count, 2)

    def test_url_password_and_kv(self):
        raw = "https://bot:s3cr3t-pass@github.com/x.git with api_key = 'ZZZ12345'"
        clean, count = scrub_text(raw)
        self.assertNotIn("s3cr3t-pass", clean)
        self.assertNotIn("ZZZ12345", clean)
        self.assertIn(REDACTED, clean)
        self.assertGreaterEqual(count, 2)

    def test_pem_and_idempotence(self):
        pem = "-----BEGIN RSA PRIVATE KEY-----\nMIIB\n-----END RSA PRIVATE KEY-----"
        once, _n = scrub_text(pem)
        self.assertNotIn("MIIB", once)
        twice, n2 = scrub_text(once)
        self.assertEqual(once, twice)
        self.assertEqual(n2, 0)


class TraceWriterTest(IsolatedRoot):
    def test_write_and_dedup(self):
        payload = json.dumps({"hello": "world"}).encode("utf-8")
        first = write_trace_bytes(payload, self.root)
        second = write_trace_bytes(payload, self.root)
        self.assertEqual(first, second)
        self.assertTrue(str(first).startswith(str(self.root / ".agents" / "traces")))
        self.assertTrue((self.root / ".agents" / "traces" / ".staging").is_dir())
        self.assertTrue((self.root / ".agents" / "traces" / "quarantine").is_dir())

    def test_invalid_json_rejected(self):
        with self.assertRaises(ValueError):
            write_trace_bytes(b"not json", self.root)


class AutocaptureTest(IsolatedRoot):
    def test_receipt_to_valid_trace(self):
        receipt = make_receipt(final="Done. Token ghp_abcdefghijklmnop123456 inside.")
        dest = ingest_receipt(receipt, self.root)
        trace = json.loads(dest.read_text(encoding="utf-8"))
        instance = ExecutionTrace(**trace)
        self.assertTrue(instance.validate())
        self.assertTrue(instance.verify_hash())
        self.assertTrue(trace["secrets_scrubbed"])
        self.assertNotIn("ghp_", trace["final_answer"])
        self.assertIn(REDACTED, trace["final_answer"])
        self.assertEqual(trace["ast_quarantine_status"], "NO_CODE")
        self.assertEqual(trace["domaine"], "web-osint")

    def test_quarantine_triggers_on_dangerous_code(self):
        evil = "Result:\n```python\nimport os\nos.system('rm -rf /')\n```"
        receipt = make_receipt(final=evil)
        dest = ingest_receipt(receipt, self.root)
        trace = json.loads(dest.read_text(encoding="utf-8"))
        self.assertEqual(trace["ast_quarantine_status"], "QUARANTINED")

    def test_safe_code_passes(self):
        clean = "Result:\n```python\ndef add(a, b):\n    return a + b\n```"
        receipt = make_receipt(final=clean)
        dest = ingest_receipt(receipt, self.root)
        trace = json.loads(dest.read_text(encoding="utf-8"))
        self.assertEqual(trace["ast_quarantine_status"], "SAFE")

    def test_transcript_segment_parsing(self):
        lines = [
            json.dumps({"type": "USER_INPUT", "content": "lance la mission", "step_index": 1}),
            json.dumps({"type": "SUBAGENT_RESULT", "step_index": 2,
                        "content": "tesla-web-raider mission done SUCCESS task_id=raid-7"}),
            "not json at all",
            json.dumps({"type": "CHATTER", "content": "simple discussion sans marqueur"}),
            json.dumps({"type": "TOOL_RESULT", "step_index": 5,
                        "content": "[CHECKPOINT CONTRACT]\ncontract_type: CHECKPOINT\n"
                                   "status: SUCCESS\ntask_id=raid-7\n"
                                   "- step: collecte\n- step: synthese"}),
        ]
        receipts = parse_transcript_segment(lines, "conv-abc")
        # Fusion par task_id : raid-7 (checkpoint+resultat) = 1 recu.
        self.assertEqual(len(receipts), 1)
        receipt = receipts[0]
        self.assertEqual(receipt["task_id"], "raid-7")
        self.assertEqual(receipt["skill"], "tesla-web-raider")
        self.assertEqual(receipt["outcome"], "success")
        self.assertEqual(receipt["score"], 1.0)
        self.assertGreaterEqual(len(receipt["steps"]), 2)

    def test_unknown_status_scores_zero(self):
        lines = [json.dumps({"type": "SUBAGENT_RESULT", "step_index": 3,
                             "content": "tesla-master-code a termine, resultat ambigu"})]
        receipts = parse_transcript_segment(lines, "conv-x")
        self.assertEqual(len(receipts), 1)
        self.assertEqual(receipts[0]["outcome"], "unknown")
        self.assertEqual(receipts[0]["score"], 0.0)


class DistillerTest(IsolatedRoot):
    def test_hits_increment_and_index_valid(self):
        for idx in range(3):
            receipt = make_receipt(task=f"raid-{idx}")
            dest = ingest_receipt(receipt, self.root)
            trace = json.loads(dest.read_text(encoding="utf-8"))
            summary = distill_trace(trace, dest.stem[:8], self.root)
        self.assertEqual(summary["hits"], 3)
        self.assertTrue(summary["budget_ok"])
        ok, _msg = lint_file(summary["index"])
        self.assertTrue(ok)
        note = Path(summary["note"])
        self.assertTrue(note.is_file())
        self.assertIn("Corroborations totales", note.read_text(encoding="utf-8"))

    def test_eviction_is_deterministic_and_archives(self):
        index_path = self.root / ".agents" / "wiki" / "general" / "index.tsv"
        index_path.parent.mkdir(parents=True, exist_ok=True)
        rows = ["\t".join(REQUIRED_COLUMNS)]
        for idx in range(300):
            rows.append(f"v{idx:04d}\tpattern-{idx}\tgeneral\t1\t"
                        f"2020-01-01T00:00:00Z\tnote-{idx}.md")
        rows.append("KEEP0001\tkeep-me\tgeneral\t50\t2026-09-18T00:00:00Z\tkeep.md")
        index_path.write_text("\n".join(rows) + "\n", encoding="utf-8")
        ok_before, _msg = lint_file(str(index_path))
        self.assertFalse(ok_before)
        evicted = enforce_budget(index_path, protect_id="KEEP0001")
        ok_after, _msg = lint_file(str(index_path))
        self.assertTrue(ok_after)
        self.assertGreater(len(evicted), 0)
        remaining = index_path.read_text(encoding="utf-8")
        self.assertIn("KEEP0001", remaining)


class RuleForgerTest(IsolatedRoot):
    def _ingest_successes(self, skill, count, task_prefix="ok"):
        for idx in range(count):
            ingest_receipt(make_receipt(skill=skill, task=f"{task_prefix}-{idx}"),
                           self.root)

    def test_forge_success_pattern(self):
        self._ingest_successes("tesla-web-raider", 3)
        outcome = forge_pattern("tesla-web-raider::web-osint::success", self.root)
        self.assertTrue(outcome["forged"], outcome.get("reason"))
        proposal = Path(outcome["proposal"])
        self.assertTrue(proposal.is_file())
        ok_b, _msg_b, _m1 = validate_broker(str(proposal))
        ok_i, _msg_i, _m2 = validate_intent(str(proposal))
        self.assertTrue(ok_b, _msg_b)
        self.assertTrue(ok_i, _msg_i)

    def test_failure_never_forged(self):
        for idx in range(5):
            ingest_receipt(make_receipt(outcome="failure", task=f"ko-{idx}"), self.root)
        outcome = forge_pattern("tesla-web-raider::web-osint::failure", self.root)
        self.assertFalse(outcome["forged"])
        self.assertIn("succes", outcome["reason"])

    def test_quarantined_never_forged(self):
        evil = "```python\nimport os\nos.system('x')\n```"
        for idx in range(3):
            receipt = make_receipt(task=f"q-{idx}", final=evil)
            ingest_receipt(receipt, self.root)
        outcome = forge_pattern("tesla-web-raider::web-osint::success", self.root)
        self.assertFalse(outcome["forged"])
        self.assertIn("QUARANTINED", outcome["reason"])

    def test_insufficient_hits_skipped(self):
        self._ingest_successes("tesla-master-code", 2)
        outcome = forge_pattern("tesla-master-code::engineering::success", self.root)
        self.assertFalse(outcome["forged"])
        self.assertIn("HITS=2", outcome["reason"])


class GatingJudgeTest(unittest.TestCase):
    def test_holdout_negative_controls_all_reject(self):
        results = _check_holdout()
        self.assertEqual(len(results), 4)
        for name, ok, detail in results:
            self.assertTrue(ok, f"{name} :: {detail}")

    def test_train_val_passes_on_healthy_worktree(self):
        with tempfile.TemporaryDirectory(prefix="gate_tv_") as tmp:
            work = Path(tmp)
            idx = work / ".agents" / "wiki" / "web-osint" / "index.tsv"
            idx.parent.mkdir(parents=True, exist_ok=True)
            idx.write_text("\t".join(REQUIRED_COLUMNS) + "\n"
                           "a1b2c3d4\tpat\tweb-osint\t3\t"
                           "2026-09-18T00:00:00Z\tnote.md\n", encoding="utf-8")
            wiki = work / ".agents" / "skills" / "tesla-web-raider" / "WIKI.md"
            wiki.parent.mkdir(parents=True, exist_ok=True)
            wiki.write_text("# WIKI\n\nRegles.\n", encoding="utf-8")
            results = _check_train_val(work)
            for name, ok, detail in results:
                self.assertTrue(ok, f"{name} :: {detail}")

    def test_train_val_fails_on_corrupt_index(self):
        with tempfile.TemporaryDirectory(prefix="gate_bad_") as tmp:
            work = Path(tmp)
            idx = work / ".agents" / "wiki" / "x" / "index.tsv"
            idx.parent.mkdir(parents=True, exist_ok=True)
            idx.write_text("BAD\tHEADER\n1\t2\n", encoding="utf-8")
            results = _check_train_val(work)
            self.assertTrue(any(not ok for _n, ok, _d in results))


class DaemonIngestTest(IsolatedRoot):
    def _write_transcript(self, brain: Path, conv: str, entries: list[dict]) -> Path:
        path = brain / conv / ".system_generated" / "logs" / "transcript.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(json.dumps(e) for e in entries) + "\n",
                        encoding="utf-8")
        return path

    def test_scan_ingests_once_then_cursor(self):
        brain = self.root / "brain"
        self._write_transcript(brain, "conv-1", [
            {"type": "SUBAGENT_RESULT", "step_index": 4,
             "content": "tesla-curator-prime audit SUCCESS task_id=audit-1"},
        ])
        from ouroboros_cycle import state_dir
        state = state_dir(self.root)
        first = scan_transcripts(self.root, state, brain, backfill_days=7)
        self.assertEqual(first, 1)
        traces = list((self.root / ".agents" / "traces").glob("*.json"))
        self.assertEqual(len(traces), 1)
        second = scan_transcripts(self.root, state, brain, backfill_days=7)
        self.assertEqual(second, 0)

    def test_backfill_bound_skips_ancient(self):
        brain = self.root / "brain"
        path = self._write_transcript(brain, "conv-old", [
            {"type": "SUBAGENT_RESULT", "step_index": 1,
             "content": "tesla-eye scan SUCCESS task_id=old-1"},
        ])
        ancient = time.time() - 30 * 86400
        os.utime(path, (ancient, ancient))
        from ouroboros_cycle import state_dir
        state = state_dir(self.root)
        count = scan_transcripts(self.root, state, brain, backfill_days=7)
        self.assertEqual(count, 0)

    def test_inbox_drain_and_quarantine(self):
        from ouroboros_cycle import state_dir
        state = state_dir(self.root)
        inbox = state / "inbox"
        inbox.mkdir(parents=True, exist_ok=True)
        (inbox / "good.json").write_text(json.dumps(make_receipt(task="inbox-1")),
                                         encoding="utf-8")
        (inbox / "bad.json").write_text("not json", encoding="utf-8")
        count = drain_inbox(self.root, state)
        self.assertEqual(count, 1)
        self.assertTrue((state / "inbox_done" / "good.json").exists())
        self.assertTrue((state / "inbox_quarantine" / "bad.json").exists())

    def test_resolve_brain_root_prefers_env(self):
        brain = self.root / "custom-brain"
        brain.mkdir()
        os.environ["TESLA_BRAIN_ROOT"] = str(brain)
        self.addCleanup(os.environ.pop, "TESLA_BRAIN_ROOT", None)
        self.assertEqual(resolve_brain_root(), brain.resolve())


class CycleEndToEndTest(IsolatedRoot):
    """Amorcage de la pompe : recu -> trace -> index -> patch -> gate -> commit."""

    def _init_git(self):
        subprocess.run(["git", "init"], cwd=self.root, check=True,
                       capture_output=True)
        subprocess.run(["git", "config", "user.email", "ouroboros@test.local"],
                       cwd=self.root, check=True)
        subprocess.run(["git", "config", "user.name", "Ouroboros Test"],
                       cwd=self.root, check=True)
        (self.root / "README.md").write_text("# test\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=self.root, check=True,
                       capture_output=True)

    def test_prime_the_pump(self):
        self._init_git()
        for idx in range(3):
            ingest_receipt(make_receipt(task=f"pump-{idx}"), self.root)
        report = run_cycle(self.root, min_hits=3, min_score=0.7,
                           auto_commit=True, max_attempts=3)
        self.assertEqual(len(report["distilled"]), 3, report["errors"])
        forged = [f for f in report["forged"] if f.get("forged")]
        self.assertEqual(len(forged), 1)
        self.assertEqual(len(report["gated"]), 1)
        self.assertEqual(report["gated"][0]["verdict"], "PASS")

        log = subprocess.run(["git", "log", "--oneline"], cwd=self.root,
                             capture_output=True, text=True, check=True)
        self.assertIn("[WikiSkill]", log.stdout)
        wiki = self.root / ".agents" / "skills" / "tesla-web-raider" / "WIKI.md"
        self.assertTrue(wiki.is_file())
        self.assertIn("Auto-learned Rules (Ouroboros)", wiki.read_text(encoding="utf-8"))

        # Idempotence : second cycle, rien de nouveau (pas de doublon).
        report2 = run_cycle(self.root, min_hits=3, min_score=0.7,
                            auto_commit=True, max_attempts=3)
        self.assertEqual(len(report2["distilled"]), 0)
        self.assertEqual(len([f for f in report2["forged"] if f.get("forged")]), 0)


if __name__ == "__main__":
    unittest.main()
