#!/usr/bin/env python3
"""Vigilum Codex 2.1 — RETEX Hardening test suite (E1, E2, E3, E4, E7, Gate 2).

Covers: sealed Mission Graph validation (Gate 2), receipt quorum
(anti-usurpation E7), intent guard, strict YAML-subset parser, memory parity
(E3), public staging gate (E2), audit ceiling / SPEC LOCK (E1), and the
universal test runner on dash-decorated paths (E4).
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from bin.audit_cap import cmd_check, cmd_record
from bin.memory_parite import DEFAULT_PILLARS, audit_memory
from bin.staging_gate import cmd_next_milestone, cmd_verify
from core.orchestration.orchestration_gate import (  # noqa: E402
    EXIT_BLOCKED,
    EXIT_PASS,
    EXIT_UNKNOWN,
    compute_approval_sha256,
    dag_verify,
    intent_guard,
    receipt_quorum,
    verify_approval_seal,
)
from core.orchestration.yaml_mini import YamlMiniError, load_file  # noqa: E402


def make_graph(*, sealed: bool = True, tamper: bool = False, cyclic: bool = False,
               mission: str = "SGC-EXEC-GOV-03-R3") -> dict:
    nodes = [
        {"id": "N1", "role": "Audit", "agents": ["tesla-arcanis-360"], "depends_on": []},
        {"id": "N2", "role": "Implementation", "agents": ["tesla-master-code"], "depends_on": ["N1"]},
    ]
    if cyclic:
        nodes[1]["depends_on"] = ["N1"]
        nodes[0]["depends_on"] = ["N2"]
    graph: dict = {"mission": mission, "version": "1.0", "nodes": nodes}
    if sealed:
        seal = compute_approval_sha256(graph)
        if tamper:
            seal = "0" * 64
        graph["approval"] = {
            "approved_by": "Lord Mahonheim",
            "approved_at": "2026-08-28T21:00:00+01:00",
            "nonce": "test-nonce-1",
            "approval_sha256": seal,
        }
    return graph


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_graph(path: Path, graph: dict) -> None:
    path.write_text(json.dumps(graph, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def make_receipt(agent_id: str, node_id: str, mission: str, status: str = "SUCCESS") -> dict:
    return {
        "agent_id": agent_id,
        "node_id": node_id,
        "mission_id": mission,
        "status": status,
        "output_artifacts": [f"out/{agent_id}.md"],
        "submitted_at": "2026-08-28T21:05:00+01:00",
    }


class OrchestrationGateTests(unittest.TestCase):
    def test_dag_verify_accepts_sealed_graph(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            graph_path = Path(directory) / "mission_graph.json"
            write_graph(graph_path, make_graph())
            # Library path
            code, result = dag_verify(graph_path)
            self.assertEqual(code, EXIT_PASS, result)
            self.assertEqual(result["verdict"], "PASS")
            # CLI path (E4-safe invocation: absolute script path)
            proc = subprocess.run(
                [sys.executable, str(ROOT / "core/orchestration/orchestration_gate.py"),
                 "dag-verify", "--graph", str(graph_path)],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn('"verdict": "PASS"', proc.stdout)

    def test_dag_verify_rejects_unsealed_graph(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            graph_path = Path(directory) / "mission_graph.json"
            write_graph(graph_path, make_graph(sealed=False))
            code, result = dag_verify(graph_path)
            self.assertEqual(code, EXIT_BLOCKED)
            self.assertEqual(result["reason"], "GRAPH_NOT_APPROVED")

    def test_dag_verify_rejects_tampered_seal(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            graph_path = Path(directory) / "mission_graph.json"
            write_graph(graph_path, make_graph(tamper=True))
            code, result = dag_verify(graph_path)
            self.assertEqual(code, EXIT_BLOCKED)
            self.assertEqual(result["reason"], "APPROVAL_SEAL_MISMATCH")

    def test_dag_verify_rejects_cyclic_graph(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            graph_path = Path(directory) / "mission_graph.json"
            write_graph(graph_path, make_graph(cyclic=True))
            code, result = dag_verify(graph_path)
            self.assertEqual(code, EXIT_BLOCKED)
            self.assertIn("GRAPH_CYCLE_DETECTED", result["violations"])

    def test_receipt_quorum_passes_with_complete_receipts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            graph = make_graph()
            receipts_dir = Path(directory) / "subagents"
            receipts_dir.mkdir()
            for agent, node in (("tesla-arcanis-360", "N1"), ("tesla-master-code", "N2")):
                write_json(receipts_dir / f"receipt_{agent}.json",
                           make_receipt(agent, node, graph["mission"]))
            code, result = receipt_quorum(graph, receipts_dir, mission_expected=None)
            self.assertEqual(code, EXIT_PASS, result)
            self.assertEqual(result["agents_receipted"], ["tesla-arcanis-360", "tesla-master-code"])

    def test_receipt_quorum_blocks_missing_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            graph = make_graph()
            receipts_dir = Path(directory) / "subagents"
            receipts_dir.mkdir()
            write_json(receipts_dir / "receipt_tesla-arcanis-360.json",
                       make_receipt("tesla-arcanis-360", "N1", graph["mission"]))
            code, result = receipt_quorum(graph, receipts_dir, mission_expected=None)
            self.assertEqual(code, EXIT_BLOCKED)
            self.assertEqual(result["reason"], "RECEIPT_QUORUM_MISSING")
            self.assertIn("tesla-master-code", result["missing"])

    def test_receipt_quorum_blocks_failed_status(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            graph = make_graph()
            receipts_dir = Path(directory) / "subagents"
            receipts_dir.mkdir()
            for agent, node in (("tesla-arcanis-360", "N1"), ("tesla-master-code", "N2")):
                status = "SUCCESS" if agent == "tesla-arcanis-360" else "FAILED"
                write_json(receipts_dir / f"receipt_{agent}.json",
                           make_receipt(agent, node, graph["mission"], status=status))
            code, result = receipt_quorum(graph, receipts_dir, mission_expected=None)
            self.assertEqual(code, EXIT_BLOCKED)
            self.assertIn("tesla-master-code", result["missing"])

    def test_intent_guard_blocks_team_synergy_without_quorum(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "OUTPUTS" / "synth.md"
            target.parent.mkdir(parents=True)
            target.write_text("---\nx-vigilum-team-synergy: true\n---\n# Synthèse\n", encoding="utf-8")
            code, result = intent_guard(root, [target], graph_override=None, receipts_override=None)
            self.assertEqual(code, EXIT_BLOCKED)
            self.assertEqual(result["reason"], "MISSION_GRAPH_NOT_DECLARED")

    def test_intent_guard_passes_with_sealed_graph_and_quorum(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            graph_path = root / "runtime" / "orchestration" / "mission_graph.json"
            graph_path.parent.mkdir(parents=True)
            graph = make_graph()
            write_graph(graph_path, graph)
            (root / "runtime" / "orchestration" / "active_mission.json").write_text(json.dumps({
                "mission_id": graph["mission"],
                "mission_graph": "runtime/orchestration/mission_graph.json",
                "activated_by": "Lord Mahonheim",
            }) + "\n", encoding="utf-8")
            receipts_dir = root / "runtime" / "subagents"
            receipts_dir.mkdir(parents=True)
            for agent, node in (("tesla-arcanis-360", "N1"), ("tesla-master-code", "N2")):
                write_json(receipts_dir / f"receipt_{agent}.json",
                           make_receipt(agent, node, graph["mission"]))
            target = root / "OUTPUTS" / "synth.md"
            target.parent.mkdir(parents=True)
            target.write_text("---\nteam_synergy: true\n---\n# Synthèse\n", encoding="utf-8")
            code, result = intent_guard(root, [target], graph_override=None, receipts_override=None)
            self.assertEqual(code, EXIT_PASS, result)
            self.assertEqual(result["reason"], "TEAM_SYNERGY_SYNTHESIS_AUTHORIZED")


class YamlSubsetParserTests(unittest.TestCase):
    def test_parser_handles_canonical_mission_graph_example(self) -> None:
        example = ROOT.parent / "29-Tesla-Team-Synergy" / "examples" / "mission_graph.yaml"
        self.assertTrue(example.is_file(), f"missing example: {example}")
        data = load_file(str(example))
        self.assertIsInstance(data, dict)
        self.assertEqual(len(data["nodes"]), 6)
        self.assertEqual(data["nodes"][0]["id"], "N1")
        self.assertEqual(data["nodes"][0]["agents"], ["tesla-arcanis-360", "tesla-curator-prime"])
        self.assertEqual(data["scheduler"]["critical_path"], ["N1", "N2", "N2b", "N3", "N4", "N5"])
        # Round-trip through gate validation: structurally valid, but unsealed -> BLOCKED
        code, result = dag_verify(example)
        self.assertEqual(code, EXIT_BLOCKED)
        self.assertEqual(result["reason"], "GRAPH_NOT_APPROVED")

    def test_parser_rejects_duplicate_keys(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "dup.yaml"
            path.write_text("mission: A\nmission: B\n", encoding="utf-8")
            with self.assertRaises(YamlMiniError):
                load_file(str(path))

    def test_parser_rejects_tab_indentation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tab.yaml"
            path.write_text("mission: A\n\tnodes:\n", encoding="utf-8")
            with self.assertRaises(YamlMiniError):
                load_file(str(path))


class MemoryParityTests(unittest.TestCase):
    def _make_memory(self, root: Path, count: int) -> None:
        memory_dir = root / "memory"
        memory_dir.mkdir(parents=True, exist_ok=True)
        for pillar in DEFAULT_PILLARS[:count]:
            (memory_dir / pillar).write_text(f"content {pillar}\n", encoding="utf-8")

    def test_memory_parity_passes_13_13(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._make_memory(root, len(DEFAULT_PILLARS))
            code, result = audit_memory(root, DEFAULT_PILLARS, {})
            self.assertEqual(code, 0, result)
            self.assertEqual(result["verdict"], "PASS")
            self.assertEqual(result["pillars_total"], 13)
            self.assertEqual(result["pillars_passed"], 13)

    def test_memory_parity_blocks_missing_pillar(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._make_memory(root, 12)
            code, result = audit_memory(root, DEFAULT_PILLARS, {})
            self.assertEqual(code, 1)
            self.assertEqual(result["verdict"], "BLOCKED")
            self.assertEqual(len(result["missing"]), 1)

    def test_memory_parity_unknown_without_memory_dir(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            code, result = audit_memory(Path(directory), DEFAULT_PILLARS, {})
            self.assertEqual(code, EXIT_UNKNOWN)
            self.assertEqual(result["verdict"], "UNKNOWN")

    def test_memory_parity_stale_state_on_baseline_drift(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._make_memory(root, len(DEFAULT_PILLARS))
            baseline = {DEFAULT_PILLARS[0]: "0" * 64}
            code, result = audit_memory(root, DEFAULT_PILLARS, baseline)
            self.assertEqual(code, 2)
            self.assertEqual(result["verdict"], "STALE_STATE")
            self.assertIn(DEFAULT_PILLARS[0], result["drifted"])


class StagingGateTests(unittest.TestCase):
    def test_next_milestone_computes_n_plus_1(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            registry = Path(directory) / "MVP-GITHUB"
            registry.mkdir()
            (registry / "07-Foo").mkdir()
            (registry / "12-Bar").mkdir()
            code, result = cmd_next_milestone(registry)
            self.assertEqual(code, EXIT_PASS)
            self.assertEqual(result["last_milestone"], 12)
            self.assertEqual(result["next_milestone"], 13)

    def test_staging_verify_passes_with_canonical_readme(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            registry = Path(directory) / "MVP-GITHUB"
            module = registry / "53-Vigilum-Codex-2.0-Executable-Governance"
            (module / "bin").mkdir(parents=True)
            (module / "README.md").write_text(
                "![Status](https://img.shields.io/badge/Status-MVP-blue)\n"
                "## Objective\nBuild the engine.\n## Installation\npip install.\n"
                "## Security\nFail-closed.\n", encoding="utf-8")
            code, result = cmd_verify(registry, 53)
            self.assertEqual(code, EXIT_PASS, result)
            self.assertEqual(result["verdict"], "PASS")

    def test_staging_verify_blocks_missing_readme(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            registry = Path(directory) / "MVP-GITHUB"
            (registry / "53-Broken").mkdir(parents=True)
            code, result = cmd_verify(registry, 53)
            self.assertEqual(code, EXIT_BLOCKED)
            self.assertIn("README_MISSING", result["violations"])


class AuditCapTests(unittest.TestCase):
    def test_audit_cap_spec_lock_at_max(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            code, _ = cmd_record(root, "SPEC-V3.6.2", 3, now=1000.0)
            self.assertEqual(code, 0)
            code, _ = cmd_record(root, "SPEC-V3.6.2", 3, now=1001.0)
            self.assertEqual(code, 0)
            code, result = cmd_record(root, "SPEC-V3.6.2", 3, now=1002.0)
            self.assertEqual(code, 80, result)
            self.assertEqual(result["verdict"], "SPEC_LOCK_CREATED")
            # Any further textual audit pass is refused
            code, result = cmd_record(root, "SPEC-V3.6.2", 3, now=1003.0)
            self.assertEqual(code, 80)
            self.assertEqual(result["verdict"], "SPEC_LOCK")
            # check agrees
            code, result = cmd_check(root, "SPEC-V3.6.2", 3)
            self.assertEqual(code, 80)
            self.assertEqual(result["verdict"], "SPEC_LOCK")

    def test_audit_cap_below_ceiling(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            code, result = cmd_check(root, "SPEC-V3.6.2", 3)
            self.assertEqual(code, 0)
            self.assertEqual(result["verdict"], "BELOW_CEILING")
            code, result = cmd_record(root, "SPEC-V3.6.2", 3, now=2000.0)
            self.assertEqual(code, 0)
            self.assertEqual(result["remaining"], 2)


class UniversalRunnerTests(unittest.TestCase):
    def test_universal_runner_runs_suites_in_dash_directory(self) -> None:
        """E4 regression: unittest discovery must work under a dash-decorated path."""
        with tempfile.TemporaryDirectory() as directory:
            module = Path(directory) / "53-Suite.Retrofit-Tests"
            tests_dir = module / "tests"
            tests_dir.mkdir(parents=True)
            (tests_dir / "test_sample.py").write_text(
                "import unittest\n"
                "class Sample(unittest.TestCase):\n"
                "    def test_ok(self): self.assertTrue(True)\n", encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(ROOT / "bin/test_runner.py"),
                 "--root", str(module), "--mission", "E4-REGRESSION", "--skip-bash"],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            ledger = list((module / "evidence").glob("test_runner_E4-REGRESSION_*.json"))
            self.assertEqual(len(ledger), 1)
            summary = json.loads(ledger[0].read_text(encoding="utf-8"))
            self.assertEqual(summary["verdict_global"], "PASS")
            self.assertEqual(summary["suites"][0]["verdict"], "PASS")


if __name__ == "__main__":
    unittest.main()
