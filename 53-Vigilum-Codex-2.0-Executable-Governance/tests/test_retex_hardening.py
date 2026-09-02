#!/usr/bin/env python3
"""Vigilum Codex 2.1 — RETEX Hardening test suite (E1, E2, E3, E4, E7, Gate 2).

Covers: sealed Mission Graph validation (Gate 2), receipt quorum
(anti-usurpation E7), intent guard, strict YAML-subset parser, memory parity
(E3), public staging gate (E2), audit ceiling / SPEC LOCK (E1), and the
universal test runner on dash-decorated paths (E4).
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from bin.audit_cap import cmd_check, cmd_record
from bin.memory_parite import DEFAULT_PILLARS, audit_memory, load_pillars
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
    """D-008 compliant receipt (V2.1.2): runtime attestation fields included."""
    seq = {"tesla-arcanis-360": "01", "tesla-master-code": "02", "tesla-github-manager": "03"}.get(agent_id, "99")
    return {
        "receipt_version": "2.1",
        "agent_id": agent_id,
        "node_id": node_id,
        "mission_id": mission,
        "status": status,
        "output_artifacts": [f"out/{agent_id}.md"],
        "submitted_at": "2026-08-28T21:05:00+01:00",
        "invocation_id": f"inv-550e8400-e29b-41d4-a716-44665544{seq}",
        "started_at": "2026-08-28T21:01:00+01:00",
        "finished_at": "2026-08-28T21:04:00+01:00",
        "exit_code": 0,
        "tool_invocations_count": 3,
        "runtime_event_sha256": "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "output_manifest_sha256": "sha256:ca978112ca1bbdcaf064278e4a1f2c4510594720443035ed1409f0c5ca10e3f8",
        "executor_attestation": "subagent_runtime_v2.1_signed",
        "transcript_ref": f"inv-550e8400-e29b-41d4-a716-44665544{seq}.json",
    }


def write_receipts_with_transcripts(receipts_dir: Path, graph: dict, mission: str) -> None:
    """Write D-008 receipts AND their runtime transcript journals (correlation)."""
    receipts_dir.mkdir(parents=True, exist_ok=True)
    transcripts_dir = receipts_dir.parent / "transcripts"
    transcripts_dir.mkdir(parents=True, exist_ok=True)
    for node in graph["nodes"]:
        for agent in node["agents"]:
            receipt = make_receipt(agent, node["id"], mission)
            write_json(receipts_dir / f"receipt_{agent}.json", receipt)
            ref = receipt["transcript_ref"]
            (transcripts_dir / ref).write_text(
                json.dumps({"invocation_id": ref[:-4], "event": "subagent_invocation"}) + "\n",
                encoding="utf-8")


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
            write_receipts_with_transcripts(receipts_dir, graph, graph["mission"])
            code, result = receipt_quorum(graph, receipts_dir, mission_expected=None)
            self.assertEqual(code, EXIT_PASS, result)
            self.assertEqual(result["agents_receipted"], ["tesla-arcanis-360", "tesla-master-code"])

    def test_receipt_quorum_blocks_missing_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            graph = make_graph()
            receipts_dir = Path(directory) / "subagents"
            write_receipts_with_transcripts(receipts_dir, graph, graph["mission"])
            (receipts_dir / "receipt_tesla-master-code.json").unlink()
            code, result = receipt_quorum(graph, receipts_dir, mission_expected=None)
            self.assertEqual(code, EXIT_BLOCKED)
            self.assertEqual(result["reason"], "RECEIPT_QUORUM_MISSING")
            self.assertIn("tesla-master-code", result["missing"])

    def test_receipt_quorum_blocks_failed_status(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            graph = make_graph()
            receipts_dir = Path(directory) / "subagents"
            write_receipts_with_transcripts(receipts_dir, graph, graph["mission"])
            for agent in ("tesla-arcanis-360", "tesla-master-code"):
                node = "N1" if agent == "tesla-arcanis-360" else "N2"
                write_json(receipts_dir / f"receipt_{agent}.json",
                           make_receipt(agent, node, graph["mission"], status="FAILED"))
            code, result = receipt_quorum(graph, receipts_dir, mission_expected=None)
            self.assertEqual(code, EXIT_BLOCKED)
            self.assertIn("tesla-master-code", result["missing"])

    def test_receipt_quorum_blocks_forged_receipt_missing_attestation(self) -> None:
        """D-008 (V2.1.2): a receipt without the runtime attestation is rejected."""
        with tempfile.TemporaryDirectory() as directory:
            graph = make_graph()
            receipts_dir = Path(directory) / "subagents"
            receipts_dir.mkdir()
            forged = make_receipt("tesla-arcanis-360", "N1", graph["mission"])
            del forged["executor_attestation"]
            forged["invocation_id"] = "written-by-agent"  # not runtime-generated
            write_json(receipts_dir / "receipt_tesla-arcanis-360.json", forged)
            write_json(receipts_dir / "receipt_tesla-master-code.json",
                       make_receipt("tesla-master-code", "N2", graph["mission"]))
            code, result = receipt_quorum(graph, receipts_dir, mission_expected=None)
            self.assertEqual(code, EXIT_BLOCKED)
            self.assertIn("tesla-arcanis-360", result["missing"])

    def test_receipt_quorum_blocks_missing_transcript(self) -> None:
        """D-008: transcript journal exists but the referenced file is absent → BLOCKED."""
        with tempfile.TemporaryDirectory() as directory:
            graph = make_graph()
            receipts_dir = Path(directory) / "subagents"
            write_receipts_with_transcripts(receipts_dir, graph, graph["mission"])
            # Remove one transcript while keeping its receipt
            (receipts_dir.parent / "transcripts" / "inv-550e8400-e29b-41d4-a716-4466554402.json").unlink()
            code, result = receipt_quorum(graph, receipts_dir, mission_expected=None)
            self.assertEqual(code, EXIT_BLOCKED)
            self.assertIn("tesla-master-code", result["missing"])

    def test_receipt_quorum_isolated_runtime_evidence(self) -> None:
        """D-008 V2.1.3 (arbitrage #1): corrélation via TESLA_RUNTIME_EVIDENCE isolé."""
        import os
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as evidence_dir:
            graph = make_graph()
            receipts_dir = Path(directory) / "subagents"
            receipts_dir.mkdir(parents=True)
            for agent, node in (("tesla-arcanis-360", "N1"), ("tesla-master-code", "N2")):
                receipt = make_receipt(agent, node, graph["mission"])
                write_json(receipts_dir / f"receipt_{agent}.json", receipt)
            # Journal isolé hors workspace (aucun miroir local)
            isolated = Path(evidence_dir) / graph["mission"] / "transcripts"
            isolated.mkdir(parents=True)
            for agent in ("tesla-arcanis-360", "tesla-master-code"):
                seq = {"tesla-arcanis-360": "01", "tesla-master-code": "02"}[agent]
                ref = f"inv-550e8400-e29b-41d4-a716-44665544{seq}.json"
                (isolated / ref).write_text(json.dumps({"event": "subagent_invocation"}) + "\n", encoding="utf-8")
            old_env = os.environ.get("TESLA_RUNTIME_EVIDENCE")
            try:
                os.environ["TESLA_RUNTIME_EVIDENCE"] = evidence_dir
                code, result = receipt_quorum(graph, receipts_dir, mission_expected=None)
                self.assertEqual(code, EXIT_PASS, result)
                self.assertEqual(result["agents_receipted"], ["tesla-arcanis-360", "tesla-master-code"])
            finally:
                if old_env is None:
                    os.environ.pop("TESLA_RUNTIME_EVIDENCE", None)
                else:
                    os.environ["TESLA_RUNTIME_EVIDENCE"] = old_env

    def test_receipt_quorum_runtime_evidence_configured_but_unobservable(self) -> None:
        """D-008 V2.1.3: env isolée configurée mais inobservable → BLOCKED (fail-closed)."""
        import os
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as evidence_dir:
            graph = make_graph()
            receipts_dir = Path(directory) / "subagents"
            write_receipts_with_transcripts(receipts_dir, graph, graph["mission"])
            # L'espace isolé existe mais est vide : le miroir local ne peut plus servir de preuve
            (Path(evidence_dir) / graph["mission"] / "transcripts").mkdir(parents=True)
            old_env = os.environ.get("TESLA_RUNTIME_EVIDENCE")
            try:
                os.environ["TESLA_RUNTIME_EVIDENCE"] = evidence_dir
                code, result = receipt_quorum(graph, receipts_dir, mission_expected=None)
                self.assertEqual(code, EXIT_BLOCKED)
                self.assertEqual(result["reason"], "RECEIPT_QUORUM_MISSING")
            finally:
                if old_env is None:
                    os.environ.pop("TESLA_RUNTIME_EVIDENCE", None)
                else:
                    os.environ["TESLA_RUNTIME_EVIDENCE"] = old_env

    def test_transcript_correlation_resolution_order(self) -> None:
        """D-008 V2.1.3: ordre de résolution direct (ref explicite → isolé → miroir)."""
        import os
        from core.orchestration.orchestration_gate import _transcript_correlation
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as evidence_dir:
            graph = make_graph()
            receipts_dir = Path(directory) / "subagents"
            write_receipts_with_transcripts(receipts_dir, graph, graph["mission"])
            receipt = make_receipt("tesla-master-code", "N2", graph["mission"])
            old_env = os.environ.get("TESLA_RUNTIME_EVIDENCE")
            try:
                # a) env absente → miroir local (journal inobservable ≠ FAIL)
                os.environ.pop("TESLA_RUNTIME_EVIDENCE", None)
                self.assertIsNone(_transcript_correlation(receipt, receipts_dir))
                # b) env configurée + répertoire mission absent → UNOBSERVABLE (fail-closed)
                os.environ["TESLA_RUNTIME_EVIDENCE"] = evidence_dir
                self.assertEqual(_transcript_correlation(receipt, receipts_dir),
                                 "RECEIPT_RUNTIME_EVIDENCE_UNOBSERVABLE")
                # c) env configurée + journal présent dans l'espace isolé → corrélé
                isolated = Path(evidence_dir) / graph["mission"] / "transcripts"
                isolated.mkdir(parents=True)
                (isolated / receipt["transcript_ref"]).write_text(
                    json.dumps({"event": "subagent_invocation"}) + "\n", encoding="utf-8")
                self.assertIsNone(_transcript_correlation(receipt, receipts_dir))
                # d) ref explicite absolu prioritaire sur l'isolé
                receipt_abs = dict(receipt)
                receipt_abs["transcript_ref"] = str(isolated / receipt["transcript_ref"])
                self.assertIsNone(_transcript_correlation(receipt_abs, receipts_dir))
            finally:
                if old_env is None:
                    os.environ.pop("TESLA_RUNTIME_EVIDENCE", None)
                else:
                    os.environ["TESLA_RUNTIME_EVIDENCE"] = old_env

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
            path = memory_dir / pillar
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f"content {pillar}\n", encoding="utf-8")

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


class MemoryManifestTests(unittest.TestCase):
    def test_shipped_manifest_is_canonical_13(self) -> None:
        """Plan V2.1.1 Étape 8: manifest/memory_manifest_v2.1.yaml governs the 13 pillars."""
        manifest = ROOT / "manifest" / "memory_manifest_v2.1.yaml"
        self.assertTrue(manifest.is_file(), f"missing manifest: {manifest}")
        data = load_file(str(manifest))
        self.assertEqual(data["manifest_version"], "2.1.1")
        pillars = data["required_pillars"]
        self.assertEqual(len(pillars), 13)
        self.assertEqual(pillars[0]["path"], "PROJECT_STATE.md")
        nested = [p["path"] for p in pillars]
        self.assertIn("PROTOCOLES/GRAVURE-SUR-MARBRE.md", nested)
        self.assertIn("Le_Conducteur_Absolu_v3.2.1.md", nested)

    def test_memory_parite_uses_manifest_paths(self) -> None:
        """M-014: audit resolves pillars from the manifest, incl. nested PROTOCOLES/."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = root / "memory"
            (memory / "PROTOCOLES").mkdir(parents=True)
            for pillar in DEFAULT_PILLARS:
                path = memory / pillar
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(f"content {pillar}\n", encoding="utf-8")
            pillars = load_pillars(None, root)
            self.assertEqual(len(pillars), 13)
            code, result = audit_memory(root, pillars, {})
            self.assertEqual(code, 0, result)
            self.assertEqual(result["verdict"], "PASS")
            self.assertEqual(result["pillars_passed"], 13)


class WorkspaceHygieneTests(unittest.TestCase):
    def test_report_blocks_on_drafts(self) -> None:
        from bin.workspace_hygiene import run_hygiene
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            outputs = root / "OUTPUTS"
            outputs.mkdir()
            (outputs / "Synergy_Gouvernance_Executable_V3.4.md").write_text("draft\n", encoding="utf-8")
            code, result = run_hygiene(root, prune=False, extra_targets=[])
            self.assertEqual(code, 1)
            self.assertEqual(result["verdict"], "BLOCKED")
            self.assertEqual(result["drafts_count"], 1)

    def test_prune_quarantines_and_respects_canonical(self) -> None:
        from bin.workspace_hygiene import run_hygiene
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            outputs = root / "OUTPUTS"
            outputs.mkdir()
            draft = outputs / "Synergy_Gouvernance_Executable_V3.4.md"
            draft.write_text("draft\n", encoding="utf-8")
            canonical = outputs / "Synergy_Gouvernance_Executable_V3.6_LOCKED.md"
            canonical.write_text("locked\n", encoding="utf-8")
            code, result = run_hygiene(root, prune=True, extra_targets=[])
            self.assertEqual(code, 0, result)
            self.assertEqual(result["verdict"], "PASS")
            self.assertFalse(draft.exists())
            self.assertTrue(canonical.exists(), "canonical final must never be quarantined")
            self.assertEqual(len(result["archived"]), 1)
            archive = Path(result["archive_dir"])
            self.assertTrue(list(archive.glob("Synergy_Gouvernance_Executable_V3.4.md")))

    def test_hygiene_clean_workspace_passes_without_prune(self) -> None:
        from bin.workspace_hygiene import run_hygiene
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "OUTPUTS").mkdir()
            (root / "OUTPUTS" / "Rapport_FINAL_2026.md").write_text("canonical\n", encoding="utf-8")
            code, result = run_hygiene(root, prune=False, extra_targets=[])
            self.assertEqual(code, 0, result)
            self.assertEqual(result["verdict"], "PASS")


class ProbeCapabilitiesTests(unittest.TestCase):
    def test_probe_pass_with_required_tools(self) -> None:
        from bin.probe_capabilities import probe_set
        tools = [
            {"name": "python3", "cmd": "python3", "probe": ["-c", "import sys"]},
            {"name": "bash", "cmd": "bash", "probe": ["--version"]},
        ]
        code, result = probe_set(tools, [])
        self.assertEqual(code, 0, result)
        self.assertEqual(result["verdict"], "PASS")
        self.assertTrue(all(c["status"] == "PASS" for c in result["capabilities"]))

    def test_probe_unknown_confined_when_absent(self) -> None:
        from bin.probe_capabilities import probe_set
        tools = [{"name": "tesla-nonexistent-tool-xyz", "cmd": "tesla-nonexistent-tool-xyz", "probe": ["--version"]}]
        code, result = probe_set(tools, [])
        self.assertEqual(code, 66)
        self.assertEqual(result["verdict"], "UNKNOWN")
        self.assertEqual(result["capabilities"][0]["status"], "UNKNOWN-CONFINED")
        self.assertIn("jamais", result["capabilities"][0]["note"].lower())

    def test_probe_fail_when_tool_broken(self) -> None:
        from bin.probe_capabilities import probe_set
        with tempfile.TemporaryDirectory() as directory:
            fake = Path(directory) / "fake-tool"
            fake.write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
            fake.chmod(0o755)
            import os
            old_path = os.environ.get("PATH", "")
            try:
                os.environ["PATH"] = f"{directory}:{old_path}"
                tools = [{"name": "fake-tool", "cmd": "fake-tool", "probe": ["--version"]}]
                code, result = probe_set(tools, [])
            finally:
                os.environ["PATH"] = old_path
            self.assertEqual(code, 1)
            self.assertEqual(result["verdict"], "FAIL")
            self.assertEqual(result["capabilities"][0]["status"], "FAIL")


class MissionControllerTests(unittest.TestCase):
    """V2.1.2 : Mission Closure Controller (13 niveaux) + MARBLE_ELIGIBILITY."""

    def _build_eligible_workspace(self, directory: str) -> Path:
        root = Path(directory)
        # Mémoire 13 piliers
        memory = root / "memory"
        (memory / "PROTOCOLES").mkdir(parents=True)
        for pillar in DEFAULT_PILLARS:
            path = memory / pillar
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f"content {pillar}\n", encoding="utf-8")
        # Contrat machine
        contracts = root / "runtime" / "contracts"
        contracts.mkdir(parents=True)
        (contracts / "mission_contract.json").write_text(json.dumps({
            "mission_id": "SGC-EXEC-GOV-03-R3",
            "closure_profile": "internal-only",
            "required_nodes": ["N1", "N2"],
            "required_agents": ["tesla-arcanis-360", "tesla-master-code"],
            "max_documentation_rounds": 3,
        }) + "\n", encoding="utf-8")
        # DAG scellé + registre
        orch = root / "runtime" / "orchestration"
        orch.mkdir(parents=True)
        graph = make_graph()
        write_graph(orch / "mission_graph.json", graph)
        (orch / "active_mission.json").write_text(json.dumps({
            "mission_id": graph["mission"],
            "mission_graph": "runtime/orchestration/mission_graph.json",
            "activated_by": "Lord Mahonheim",
        }) + "\n", encoding="utf-8")
        # Quittances D-008 corrélées (répertoire canonical receipts/)
        write_receipts_with_transcripts(root / "runtime" / "subagents" / "receipts", graph, graph["mission"])
        # Ledger test runner (WORK_VALIDATED)
        evidence = root / "evidence"
        evidence.mkdir(exist_ok=True)
        (evidence / "test_runner_SGC-EXEC-GOV-03-R3_FINAL.json").write_text(json.dumps({
            "mission_id": "SGC-EXEC-GOV-03-R3",
            "verdict_global": "PASS",
            "exit_code": 0,
            "timestamp": "2026-08-28T22:00:00Z",
        }) + "\n", encoding="utf-8")
        # Sonde tri-state (PROBE_VALID)
        probe_dir = root / "runtime"
        (probe_dir / "capability_health.json").write_text(json.dumps({
            "verdict": "PASS",
            "required": ["python3", "bash", "git"],
            "evidence": "runtime/capability_health.json",
            "capabilities": [
                {"capability": "python3", "status": "PASS"},
                {"capability": "bash", "status": "PASS"},
                {"capability": "git", "status": "PASS"},
                {"capability": "pyright", "status": "UNKNOWN-CONFINED"},
            ],
        }) + "\n", encoding="utf-8")
        # Workspace propre
        (root / "OUTPUTS").mkdir(exist_ok=True)
        return root

    def test_controller_marble_eligible_internal_only(self) -> None:
        from bin.mission_controller import evaluate
        with tempfile.TemporaryDirectory() as directory:
            root = self._build_eligible_workspace(directory)
            code, result = evaluate(root, "SGC-EXEC-GOV-03-R3", "internal-only",
                                    registry=None, milestone=None, graph_override=None,
                                    receipts_override=None, authorized=False)
            self.assertEqual(code, 0, result)
            self.assertTrue(result["marble_eligible"])
            self.assertEqual(result["state"], "MARBLE_ELIGIBLE")
            self.assertTrue(all(term["pass"] for term in result["equation_terms"].values()))
            self.assertTrue((root / "runtime" / "marble_eligibility.json").is_file())
            self.assertTrue((root / "runtime" / "state.json").is_file())

    def test_controller_blocks_when_receipts_missing(self) -> None:
        from bin.mission_controller import evaluate
        with tempfile.TemporaryDirectory() as directory:
            root = self._build_eligible_workspace(directory)
            import shutil
            shutil.rmtree(root / "runtime" / "subagents")
            code, result = evaluate(root, "SGC-EXEC-GOV-03-R3", "internal-only",
                                    registry=None, milestone=None, graph_override=None,
                                    receipts_override=None, authorized=False)
            self.assertEqual(code, 1, result)
            self.assertFalse(result["marble_eligible"])
            self.assertFalse(result["equation_terms"]["RECEIPTS_CORRELATED"]["pass"])
            self.assertIn(result["state"], ("WORK_VALIDATED", "EVIDENCE_VALIDATED"))

    def test_controller_human_authorized_transition(self) -> None:
        from bin.mission_controller import evaluate
        with tempfile.TemporaryDirectory() as directory:
            root = self._build_eligible_workspace(directory)
            code, result = evaluate(root, "SGC-EXEC-GOV-03-R3", "internal-only",
                                    registry=None, milestone=None, graph_override=None,
                                    receipts_override=None, authorized=True)
            self.assertEqual(code, 0, result)
            self.assertTrue(result["marble_eligible"])
            self.assertEqual(result["state"], "HUMAN_AUTHORIZED")

    def test_probe_valid_contextualized_from_contract(self) -> None:
        """V2.1.3 (arbitrage #4): PROBE_VALID piloté par required_capabilities du contrat."""
        from bin.mission_controller import evaluate
        with tempfile.TemporaryDirectory() as directory:
            root = self._build_eligible_workspace(directory)
            # Contrat exigeant python3 + bash : le prédicat REQUIS est piloté
            # par le contrat, pas par le défaut codé en dur
            contract_path = root / "runtime" / "contracts" / "mission_contract.json"
            contract = json.loads(contract_path.read_text(encoding="utf-8"))
            contract["required_capabilities"] = ["python3", "bash"]
            contract_path.write_text(json.dumps(contract) + "\n", encoding="utf-8")
            code, result = evaluate(root, "SGC-EXEC-GOV-03-R3", "internal-only",
                                    registry=None, milestone=None, graph_override=None,
                                    receipts_override=None, authorized=False)
            self.assertEqual(code, 0, result)
            self.assertTrue(result["marble_eligible"])
            self.assertTrue(result["equation_terms"]["PROBE_VALID"]["pass"])
            self.assertEqual(result["equation_terms"]["PROBE_VALID"]["detail"]["required_set"],
                             ["python3", "bash"])

    def test_probe_valid_blocks_on_contract_missing_capability(self) -> None:
        """V2.1.3: capacité requise par le contrat absente → PROBE_VALID false (fail-closed)."""
        from bin.mission_controller import evaluate
        with tempfile.TemporaryDirectory() as directory:
            root = self._build_eligible_workspace(directory)
            contract_path = root / "runtime" / "contracts" / "mission_contract.json"
            contract = json.loads(contract_path.read_text(encoding="utf-8"))
            contract["required_capabilities"] = ["python3", "tesla-nonexistent-capability-xyz"]
            contract_path.write_text(json.dumps(contract) + "\n", encoding="utf-8")
            code, result = evaluate(root, "SGC-EXEC-GOV-03-R3", "internal-only",
                                    registry=None, milestone=None, graph_override=None,
                                    receipts_override=None, authorized=False)
            self.assertEqual(code, 1, result)
            self.assertFalse(result["marble_eligible"])
            self.assertFalse(result["equation_terms"]["PROBE_VALID"]["pass"])


class ExitCodeLibraryTests(unittest.TestCase):
    """V2.1.3 (arbitrage #3) : codes POSIX uniques — les alias 71/72/73 sont bannis."""

    def test_exit_code_library_has_no_numeric_aliases(self) -> None:
        """Seuls les 12 codes canoniques sont exportés numériquement."""
        lib = (ROOT / "core" / "hooks" / "lib" / "tesla-exit-codes.sh").read_text(encoding="utf-8")
        exported: dict[str, str] = {}
        for line in lib.splitlines():
            match = re.match(r"^export\s+(\w+)=(\d+)\s*$", line)
            if match:
                exported[match.group(1)] = match.group(2)
        values = sorted(exported.values())
        self.assertEqual(values, ["0", "10", "20", "30", "40", "50", "60", "66", "70", "80", "81", "90"])
        self.assertNotIn("71", values)
        self.assertNotIn("72", values)
        self.assertNotIn("73", values)

    def test_exit_code_library_semantic_ids_present(self) -> None:
        """Les identifiants sémantiques documentent les codes, sans export numérique."""
        lib = (ROOT / "core" / "hooks" / "lib" / "tesla-exit-codes.sh").read_text(encoding="utf-8")
        self.assertIn("ERR_SPEC_LOCKED", lib)
        self.assertIn("ERR_AGENT_THEATER", lib)
        self.assertIn("ERR_PUBLIC_STAGING_MISSING", lib)
        self.assertIn("80", lib)  # ERR_SPEC_LOCKED → 80
        self.assertIn("81", lib)  # ERR_AGENT_THEATER → 81


class TestManifestTests(unittest.TestCase):
    """V2.1.3 (arbitrage #5) : comptes déclarés au manifeste, jamais hardcodés."""

    def _module_with_manifest(self, directory: str, declared_python: int) -> Path:
        module = Path(directory) / "53-Manifest-Tests"
        tests_dir = module / "tests"
        tests_dir.mkdir(parents=True)
        (tests_dir / "test_sample.py").write_text(
            "import unittest\nclass Sample(unittest.TestCase):\n"
            "    def test_ok(self): self.assertTrue(True)\n", encoding="utf-8")
        manifest_dir = module / "manifest"
        manifest_dir.mkdir(parents=True)
        (manifest_dir / "test_manifest_v2.1.yaml").write_text(
            "manifest_version: \"2.1.3\"\n"
            "suites:\n"
            "  - name: python-unittest-discovery\n"
            "    expected_tests: {}\n"
            "total_tests: {}\n".format(declared_python, declared_python), encoding="utf-8")
        # Chaque module déployé embarque son propre parseur (stdlib-only)
        parser_src = ROOT / "core" / "orchestration" / "yaml_mini.py"
        parser_dst = module / "core" / "orchestration" / "yaml_mini.py"
        parser_dst.parent.mkdir(parents=True, exist_ok=True)
        parser_dst.write_text(parser_src.read_text(encoding="utf-8"), encoding="utf-8")
        return module

    def test_runner_passes_when_manifest_matches(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            module = self._module_with_manifest(directory, 1)
            proc = subprocess.run(
                [sys.executable, str(ROOT / "bin/test_runner.py"),
                 "--root", str(module), "--mission", "MANIFEST-OK", "--skip-bash"],
                capture_output=True, text=True, check=False)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertIn('"test_manifest"', proc.stdout)
            self.assertIn('"verdict": "PASS"', proc.stdout)

    def test_runner_fails_when_manifest_declares_more(self) -> None:
        """Fail-closed: le runner refuse si les tests exécutés < tests déclarés."""
        with tempfile.TemporaryDirectory() as directory:
            module = self._module_with_manifest(directory, 5)
            proc = subprocess.run(
                [sys.executable, str(ROOT / "bin/test_runner.py"),
                 "--root", str(module), "--mission", "MANIFEST-FAIL", "--skip-bash"],
                capture_output=True, text=True, check=False)
            self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
            summary = json.loads(proc.stdout)
            self.assertEqual(summary["verdict_global"], "FAIL")
            self.assertEqual(summary["test_manifest"]["verdict"], "FAIL")
            self.assertTrue(any("declared 5" in m for m in summary["test_manifest"]["mismatches"]))
            self.assertTrue(any("total: declared 5" in m for m in summary["test_manifest"]["mismatches"]))


class MarbleCertificateTests(unittest.TestCase):
    def test_certificate_sealed_after_eligibility(self) -> None:
        from bin.marble_certificate import build_certificate
        from bin.mission_controller import evaluate
        with tempfile.TemporaryDirectory() as directory:
            root = MissionControllerTests()._build_eligible_workspace(directory)
            code, _ = evaluate(root, "SGC-EXEC-GOV-03-R3", "internal-only",
                               registry=None, milestone=None, graph_override=None,
                               receipts_override=None, authorized=True)
            self.assertEqual(code, 0)
            code, result = build_certificate(root, "SGC-EXEC-GOV-03-R3",
                                             remote_commit=None, out_dir=None, graph_override=None)
            self.assertEqual(code, 0, result)
            self.assertEqual(result["verdict"], "SEALED")
            cert_path = Path(result["certificate"])
            self.assertTrue(cert_path.is_file())
            anchors = result["anchors"]
            # V2.1.3 (arbitrage #6) : classification TAMPER_EVIDENT explicite
            self.assertEqual(anchors["status"], "SEALED_TAMPER_EVIDENT")
            self.assertEqual(anchors["seal_class"], "TAMPER_EVIDENT")
            self.assertEqual(anchors["authority"], "Lord Mahonheim (Biological Gate)")
            self.assertIn("dag_sha256", anchors)
            self.assertIn("receipts_manifest_sha256", anchors)
            self.assertTrue(anchors["receipts_manifest_sha256"] not in ("UNSEALED", ""))
            self.assertIn("sha256:", anchors["evidence_chain_head"])
            mode = cert_path.stat().st_mode & 0o777
            self.assertEqual(mode, 0o444, "certificate must be sealed read-only (0444)")

    def test_certificate_remote_anchor_is_immutable(self) -> None:
        """V2.1.3 (arbitrage #6) : ancre distante → IMMUTABLE, jamais auto-attesté."""
        from bin.marble_certificate import build_certificate
        from bin.mission_controller import evaluate
        with tempfile.TemporaryDirectory() as directory:
            root = MissionControllerTests()._build_eligible_workspace(directory)
            code, _ = evaluate(root, "SGC-EXEC-GOV-03-R3", "internal-only",
                               registry=None, milestone=None, graph_override=None,
                               receipts_override=None, authorized=True)
            self.assertEqual(code, 0)
            code, result = build_certificate(root, "SGC-EXEC-GOV-03-R3",
                                             remote_commit="f053432deadbeef", out_dir=None,
                                             graph_override=None)
            self.assertEqual(code, 0, result)
            anchors = result["anchors"]
            self.assertEqual(anchors["status"], "SEALED_IMMUTABLE")
            self.assertEqual(anchors["seal_class"], "IMMUTABLE")
            self.assertEqual(anchors["remote_commit_sha"], "f053432deadbeef")
            self.assertIn("POST_PUB_VERIFIED", anchors["seal_note"])

    def test_certificate_refused_without_eligibility(self) -> None:
        from bin.marble_certificate import build_certificate
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            code, result = build_certificate(root, "SGC-EXEC-GOV-03-R3",
                                             remote_commit=None, out_dir=None, graph_override=None)
            self.assertEqual(code, 1)
            self.assertEqual(result["reason"], "MARBLE_ELIGIBILITY_NOT_RECORDED")


if __name__ == "__main__":
    unittest.main()
