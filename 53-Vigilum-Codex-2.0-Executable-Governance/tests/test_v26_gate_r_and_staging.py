#!/usr/bin/env python3
"""Tests V2.6.1 — Deltas admissibles du plan V2.6.0 (audit & verdict).

Preuves physiques (P1) des incréments implémentés à la suite du verdict
d'audit du PLAN D'INTERVENTION DE HAUT NIVEAU V2.6.0 :

  Phase 2 (corrigée) — usurpation de staging par transfert de fichiers
      (cp/mv/install/rsync vers destinations de gouvernance) ;
  Phase 3 (étendue)  — le registre de vérité mission_truth.json et les
      contrats runtime/contracts/ sont inaccessibles à l'écriture agent ;
  Phase 5 (P11)      — Gate R « Evidence Reconciliation » : manifeste ↔
      ledger ↔ signature Control Plane, registre émis par l'outil
      déterministe (jamais par l'agent), fail-closed 0/50/66.

Stdlib uniquement, espaces temporaires, fail-closed.
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIB_DIR = ROOT / "core" / "hooks" / "lib"
HOOKS_DIR = ROOT / "core" / "hooks" / "antigravity"
SLSA_TOOL = ROOT / "bin" / "slsa_attestation.py"
GATE_R_TOOL = ROOT / "bin" / "gate_r.py"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


git_guard = _load_module("tesla_git_guard_v261", LIB_DIR / "tesla_git_guard.py")
zero_middleman = _load_module("tesla_zero_middleman_v261", LIB_DIR / "tesla_zero_middleman.py")


def run_hook(script: Path, payload: dict, env_extra: dict | None = None) -> dict:
    env = os.environ.copy()
    env.pop("TESLA_AGENT_IDENTITY", None)
    if env_extra:
        env.update(env_extra)
    proc = subprocess.run(
        ["bash", str(script)], input=json.dumps(payload),
        capture_output=True, text=True, timeout=60, env=env, check=False)
    if proc.returncode != 0:
        raise AssertionError(
            f"hook {script.name} crashed (exit {proc.returncode}): {proc.stderr}")
    return json.loads(proc.stdout.strip().splitlines()[-1])


# --------------------------------------------------------------------------- #
# Phase 2 (corrigée) — transferts vers espaces de gouvernance                  #
# --------------------------------------------------------------------------- #
class StagingTransferClassifierTests(unittest.TestCase):
    """Le blocage est CIBLÉ PAR DESTINATION — jamais aveugle (correction
    d'audit : un cp/mv global casserait l'opérabilité de l'Orchestrateur)."""

    def test_transfers_to_governance_paths_are_mutating(self) -> None:
        for command in (
                "cp core/x.py MVP-GITHUB/53-Vigilum/x.py",       # RETEX Incident 3
                "cp -r src MVP-GITHUB/53-/",
                "mv out.json evidence/result.json",
                "mv draft.md CERTIFICATES/draft.md",
                "cp token runtime/gate2/gate2_approval.token",
                "cp truth.json runtime/contracts/mission_truth.json",
                "cp a.lock .git/hooks/pre-commit",
                "install -m 644 x.sh MVP-GITHUB/53-/",
                "rsync -a build/ MVP-GITHUB/53-/"):
            self.assertEqual(git_guard.classify_command(command)["verdict"],
                             "MUTATING", command)

    def test_explicit_target_directory_flag_is_honored(self) -> None:
        self.assertEqual(git_guard.classify_command(
            "cp -t MVP-GITHUB/53- file.py")["verdict"], "MUTATING")
        self.assertEqual(git_guard.classify_command(
            "mv --target-directory=evidence file.json")["verdict"],
            "MUTATING")

    def test_wrapped_transfers_are_unwrapped(self) -> None:
        self.assertEqual(git_guard.classify_command(
            "sudo cp x MVP-GITHUB/y")["verdict"], "MUTATING")
        self.assertEqual(git_guard.classify_command(
            "sh -c 'cp x evidence/y'")["verdict"], "MUTATING")

    def test_transfers_to_workspace_paths_are_neutral(self) -> None:
        for command in ("cp notes.txt archive.txt",
                        "mv draft.md OUTPUTS/final.md",
                        "cp -r src backup_src",
                        "rsync -a src/ dst/",
                        "install -m 755 tool.sh bin/tool.sh"):
            verdict = git_guard.classify_command(command)["verdict"]
            self.assertIn(verdict, ("NO_GIT", "READ"), command)

    def test_combined_git_and_staging_mutation(self) -> None:
        self.assertEqual(git_guard.classify_command(
            "cp x MVP-GITHUB/y && git add MVP-GITHUB/y")["verdict"],
            "MUTATING")


class Hook08StagingTests(unittest.TestCase):
    HOOK = HOOKS_DIR / "hook_08_anti_usurpation.sh"

    def payload(self, command: str, agent: str | None = None) -> dict:
        args = {"command": command}
        if agent:
            args["agent_id"] = agent
        return {"conversationId": "conv-1",
                "toolCall": {"name": "run_command", "args": args}}

    def test_orchestrator_staging_copy_denied(self) -> None:
        decision = run_hook(self.HOOK, self.payload(
            "cp core/x.py MVP-GITHUB/53-Vigilum/x.py"))
        self.assertEqual(decision["decision"], "deny")
        self.assertIn("Exit 81", decision["reason"])
        self.assertIn("gouvernance", decision["reason"])

    def test_github_manager_staging_copy_allowed(self) -> None:
        decision = run_hook(self.HOOK, self.payload(
            "cp core/x.py MVP-GITHUB/53-Vigilum/x.py",
            agent="tesla-github-manager"))
        self.assertEqual(decision["decision"], "allow")

    def test_normal_copy_allowed(self) -> None:
        decision = run_hook(self.HOOK, self.payload("cp a.txt b.txt"))
        self.assertEqual(decision["decision"], "allow")


class IdentitySpoofDetectionTests(unittest.TestCase):
    """V2.6.2 (plan consolidé V2.6.1, Phase 1) : « blocage de toute
    usurpation détectée » — l'identité runtime contredit l'identité
    déclarée => refus immédiat (Exit 81), avant toute évaluation de
    juridiction. L'identité injectée par le runtime fait foi."""

    HOOK = HOOKS_DIR / "hook_08_anti_usurpation.sh"

    def payload(self, command: str, agent: str | None = None) -> dict:
        args = {"command": command}
        if agent:
            args["agent_id"] = agent
        return {"conversationId": "conv-1",
                "toolCall": {"name": "run_command", "args": args}}

    def test_env_payload_contradiction_denies_despite_claimed_jurisdiction(self) -> None:
        # L'agent tesla-master-code (runtime) tente de se faire passer pour
        # le titulaire de la juridiction Git dans le payload => usurpation.
        decision = run_hook(
            self.HOOK,
            self.payload("git push origin main", agent="tesla-github-manager"),
            env_extra={"TESLA_AGENT_IDENTITY": "tesla-master-code"})
        self.assertEqual(decision["decision"], "deny")
        self.assertIn("Exit 81", decision["reason"])
        self.assertIn("usurpation d'identite", decision["reason"])
        self.assertIn("tesla-master-code", decision["reason"])

    def test_consistent_runtime_and_payload_identity_allowed(self) -> None:
        decision = run_hook(
            self.HOOK,
            self.payload("git push origin main", agent="tesla-github-manager"),
            env_extra={"TESLA_AGENT_IDENTITY": "tesla-github-manager"})
        self.assertEqual(decision["decision"], "allow")

    def test_payload_only_identity_still_resolves(self) -> None:
        # Sans identité runtime, la voie payload reste l'unique signal
        # (compatibilité V2.5.1 préservée).
        decision = run_hook(
            self.HOOK,
            self.payload("git push origin main", agent="tesla-github-manager"))
        self.assertEqual(decision["decision"], "allow")

    def test_spoof_check_runs_even_for_reads(self) -> None:
        # La détection d'usurpation précède TOUTE évaluation — même une
        # lecture pure est refusée si l'identité est falsifiée (P10).
        decision = run_hook(
            self.HOOK,
            self.payload("git status", agent="tesla-github-manager"),
            env_extra={"TESLA_AGENT_IDENTITY": "tesla-curator-prime"})
        self.assertEqual(decision["decision"], "deny")
        self.assertIn("usurpation d'identite", decision["reason"])

    def test_detect_identity_spoof_unit(self) -> None:
        import os as _os
        old = _os.environ.get("TESLA_AGENT_IDENTITY")
        try:
            _os.environ.pop("TESLA_AGENT_IDENTITY", None)
            # Pas d'identité runtime => rien à contredire.
            self.assertIsNone(git_guard.detect_identity_spoof(self.payload("ls")))
            _os.environ["TESLA_AGENT_IDENTITY"] = "tesla-arcanis-360"
            # Identité runtime sans déclaration payload => cohérent.
            self.assertIsNone(git_guard.detect_identity_spoof(self.payload("ls")))
            # Contradiction => raison d'usurpation.
            reason = git_guard.detect_identity_spoof(
                self.payload("ls", agent="tesla-github-manager"))
            self.assertIsNotNone(reason)
            self.assertIn("IDENTITY_SPOOF", reason)
        finally:
            if old is None:
                _os.environ.pop("TESLA_AGENT_IDENTITY", None)
            else:
                _os.environ["TESLA_AGENT_IDENTITY"] = old


# --------------------------------------------------------------------------- #
# Phase 3 (étendue) — mission_truth.json hors d'atteinte agent                 #
# --------------------------------------------------------------------------- #
class ZeroMiddlemanV26Tests(unittest.TestCase):
    HOOK = HOOKS_DIR / "hook_09_zero_middleman.sh"

    def test_mission_truth_registry_is_agent_unwritable(self) -> None:
        reason = zero_middleman.is_forbidden_path(
            "runtime/contracts/mission_truth.json")
        self.assertIsNotNone(reason)
        decision = run_hook(self.HOOK, {
            "conversationId": "c1",
            "toolCall": {"name": "write_file",
                         "args": {"path": "runtime/contracts/mission_truth.json"}}})
        self.assertEqual(decision["decision"], "deny")

    def test_runtime_contracts_directory_is_forbidden(self) -> None:
        self.assertIsNotNone(
            zero_middleman.is_forbidden_path("runtime/contracts/anything.json"))

    def test_normal_contract_documentation_is_allowed(self) -> None:
        # Un document de contrat métier (OUTPUTS) reste légitime.
        self.assertIsNone(
            zero_middleman.is_forbidden_path("OUTPUTS/contrat_client.md"))


# --------------------------------------------------------------------------- #
# Phase 5 — Gate R : Evidence Reconciliation (P11)                             #
# --------------------------------------------------------------------------- #
class GateRTests(unittest.TestCase):
    MISSION = "V261-GATE-R-TEST"
    KEY = "gate-r-control-plane-test-key-0123456789abcdef"

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name) / "module"
        (self.root / "manifest").mkdir(parents=True)
        (self.root / "evidence").mkdir(parents=True)
        (self.root / "manifest" / "test_manifest_v2.1.yaml").write_text(
            "# Manifeste synthétique V2.6.1 (tests Gate R)\n"
            "manifest_version: \"2.6.1\"\n"
            "suites:\n"
            "  - name: python-unittest-discovery\n"
            "    command: \"python3 -m unittest discover -s tests\"\n"
            "    expected_tests: 2\n"
            "    critical: true\n"
            "  - name: bash-hooks-suite\n"
            "    command: \"bash tests/test_hooks_suite.sh\"\n"
            "    expected_tests: 1\n"
            "    critical: true\n"
            "total_tests: 3\n",
            encoding="utf-8")
        self.ledger = self.root / "evidence" / (
            f"test_runner_{self.MISSION}_20260903-000000-000001.json")
        self.ledger.write_text(json.dumps(self.make_ledger()), encoding="utf-8")

    def make_ledger(self, verdict: str = "PASS", python_tests: int = 2,
                    bash_tests: int = 1, skipped: int = 0,
                    disclose_skips: bool = True) -> dict:
        suites = []
        for name, count in (("python-unittest-discovery", python_tests),
                            ("bash-hooks-suite", bash_tests)):
            suite = {"name": name, "exit_code": 0 if verdict == "PASS" else 1,
                     "verdict": "PASS" if verdict == "PASS" else "FAIL",
                     "tests_reported": count}
            if name.startswith("python") and skipped:
                suite["tests_skipped"] = skipped
                if disclose_skips:
                    suite["p3_disclosure"] = "confinement documenté (P3)"
            suites.append(suite)
        return {"runner": "Universal Test Runner", "mission_id": self.MISSION,
                "verdict_global": verdict, "suites": suites}

    def rewrite_ledger(self, **kwargs) -> None:
        self.ledger.write_text(
            json.dumps(self.make_ledger(**kwargs)), encoding="utf-8")

    def sign_ledger(self) -> Path:
        attestation = (self.root / "evidence" /
                       f"gate_r_{self.MISSION}.attestation.json")
        proc = subprocess.run(
            [sys.executable, str(SLSA_TOOL), "generate",
             "--root", str(self.root), "--mission", self.MISSION,
             "--subject", str(self.ledger), "--sign",
             "--out", str(attestation)],
            capture_output=True, text=True, timeout=60, check=False,
            env={**os.environ, "TESLA_CONTROL_PLANE_KEY": self.KEY})
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        return attestation

    def gate_r(self, *extra: str, key: str | None = None,
               mission: str | None = None) -> tuple[int, dict]:
        """key=None → clé de test ; key='' → AUCUNE clé (mode P3)."""
        mission = mission or self.MISSION
        key = self.KEY if key is None else key
        env = {**os.environ, "PYTHONPATH": str(ROOT)}
        env.pop("TESLA_CONTROL_PLANE_KEY", None)
        if key:
            env["TESLA_CONTROL_PLANE_KEY"] = key
        proc = subprocess.run(
            [sys.executable, str(GATE_R_TOOL), "reconcile",
             "--root", str(self.root), "--mission", mission, *extra],
            capture_output=True, text=True, timeout=120, check=False, env=env)
        try:
            # La Gate R imprime un verdict JSON multi-lignes (indent=2).
            verdict = json.loads(proc.stdout)
        except json.JSONDecodeError:
            verdict = {"raw": (proc.stdout + proc.stderr)[:400]}
        return proc.returncode, verdict

    def test_happy_path_reconciles_and_writes_truth_contract(self) -> None:
        self.sign_ledger()
        code, verdict = self.gate_r()
        self.assertEqual(code, 0, verdict)
        self.assertEqual(verdict["verdict"], "RECONCILED")
        contract = self.root / "runtime" / "contracts" / "mission_truth.json"
        self.assertTrue(contract.is_file())
        truth = json.loads(contract.read_text(encoding="utf-8"))
        self.assertEqual(truth["verdict"], "RECONCILED")
        self.assertIn("sha256", truth["manifest"])
        self.assertIn("sha256", truth["ledger"])
        self.assertEqual(truth["attestation"]["signed_by"],
                         "vigilum-control-plane-hmac-2026")

    def test_missing_ledger_is_unknown(self) -> None:
        self.ledger.unlink()
        code, verdict = self.gate_r()
        self.assertEqual(code, 66)  # P3 : inobservable
        self.assertIn("LEDGER", verdict.get("reason", ""))

    def test_ledger_verdict_fail_blocks(self) -> None:
        self.rewrite_ledger(verdict="FAIL")
        self.sign_ledger()
        code, verdict = self.gate_r()
        self.assertEqual(code, 50)
        self.assertIn("P11", verdict["reason"])

    def test_declared_tests_not_executed_blocks(self) -> None:
        self.rewrite_ledger(python_tests=1)
        self.sign_ledger()
        code, verdict = self.gate_r()
        self.assertEqual(code, 50)
        self.assertIn("COMPTE_INSUFFISANT", verdict["reason"])

    def test_missing_suite_blocks(self) -> None:
        ledger = self.make_ledger()
        ledger["suites"] = [s for s in ledger["suites"]
                            if s["name"] != "bash-hooks-suite"]
        self.ledger.write_text(json.dumps(ledger), encoding="utf-8")
        self.sign_ledger()
        code, verdict = self.gate_r()
        self.assertEqual(code, 50)
        self.assertIn("SUITE_NON_EXECUTEE", verdict["reason"])

    def test_undisclosed_skips_block(self) -> None:
        self.rewrite_ledger(skipped=3, disclose_skips=False)
        self.sign_ledger()
        code, verdict = self.gate_r()
        self.assertEqual(code, 50)
        self.assertIn("SKIP_NON_DIVULGUE", verdict["reason"])

    def test_disclosed_skips_are_admissible(self) -> None:
        self.rewrite_ledger(skipped=3, disclose_skips=True)
        self.sign_ledger()
        code, verdict = self.gate_r()
        self.assertEqual(code, 0, verdict)

    def test_missing_attestation_blocks(self) -> None:
        code, verdict = self.gate_r()
        self.assertEqual(code, 50)
        self.assertIn("ATTESTATION_ABSENTE", verdict["reason"])

    def test_unsigned_envelope_blocks(self) -> None:
        # Enveloppe non signée (statement brut) : pas une preuve (P11).
        attestation = (self.root / "evidence" /
                       f"gate_r_{self.MISSION}.attestation.json")
        attestation.write_text(json.dumps({"statement": {"_type": "x"}}),
                               encoding="utf-8")
        code, verdict = self.gate_r()
        self.assertEqual(code, 50)
        self.assertIn("ATTESTATION_INVALIDE", verdict["reason"])

    def test_tampered_ledger_after_signing_blocks(self) -> None:
        self.sign_ledger()
        # Falsification du ledger APRÈS signature : l'empreinte diverge.
        self.rewrite_ledger(python_tests=99)
        code, verdict = self.gate_r()
        self.assertEqual(code, 50)
        self.assertIn("ATTESTATION_INVALIDE", verdict["reason"])

    def test_no_key_is_unknown_not_pass(self) -> None:
        self.sign_ledger()
        code, verdict = self.gate_r(key="")  # aucune clé → P3
        self.assertEqual(code, 66)  # P3 : UNKNOWN != PASS
        self.assertIn("P3", json.dumps(verdict))

    def test_explicit_ledger_override(self) -> None:
        self.sign_ledger()
        code, verdict = self.gate_r("--ledger", str(self.ledger))
        self.assertEqual(code, 0, verdict)

    def test_check_only_does_not_write_contract(self) -> None:
        self.sign_ledger()
        code, verdict = self.gate_r("--no-write")
        self.assertEqual(code, 0, verdict)
        self.assertFalse(
            (self.root / "runtime" / "contracts" / "mission_truth.json").is_file())


if __name__ == "__main__":
    unittest.main()
