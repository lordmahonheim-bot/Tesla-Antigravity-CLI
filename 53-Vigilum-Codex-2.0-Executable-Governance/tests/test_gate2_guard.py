#!/usr/bin/env python3
"""Tests de régression Gate 2 Delegation Guard — SPINOFF-DIAG-GATE2-BYPASS.

Chaque test verrouille une classe de défaillance observée ou corrigée lors de
l'incident du 2026-09-02 (19:14:36, invocation de sous-agents sans validation
humaine du Mission Graph) :

  - reproduction de l'incident : graphe non scellé -> délégation BLOCKED ;
  - P-AGENT-002 : `approved_by` forge par l'agent n'est PAS une autorisation ;
  - le pré-vol est une vérification PURE (aucune consommation de jeton) ;
  - liaison cryptographique jeton <-> (mission, graph_sha256, fenêtre) ;
  - anti-rejeu A-003 : consommation atomique O_CREAT|O_EXCL, usage unique ;
  - grand livre d'échange chaîné SHA-256 (tamper-evident).

Stdlib uniquement, fail-closed, déterministe (--now, --issued-at).
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.orchestration.gate2_guard import (  # noqa: E402
    LOCK_STATE_RESERVED,
    TOKEN_VERSION,
    canonical_bytes,
    gate2_dir,
    pre_flight_delegation_check,
    redeem_delegation_token,
    sign_token,
)
from core.orchestration.orchestration_gate import compute_approval_sha256, load_graph_file  # noqa: E402

GUARD = ROOT / "core" / "orchestration" / "gate2_guard.py"
MISSION = "SPINOFF-DIAG-GATE2-BYPASS"
ISSUED_AT = "2026-09-02T19:00:00Z"
NOW_VALID = "2026-09-02T19:05:00Z"
NOW_LATE = "2026-09-02T19:20:00Z"

GRAPH_TEMPLATE = """mission: {mission}
version: 1.0
nodes:
  - id: N1
    role: {n1_role}
    agents: [tesla-arcanis-360]
    depends_on: []
  - id: N2
    role: Implementation
    agents: [tesla-master-code]
    depends_on: [N1]
"""

APPROVAL_TEMPLATE = """approval:
  approved_by: Lord Mahonheim
  approved_at: 2026-09-02T19:30:00+01:00
  nonce: {nonce}
  approval_sha256: {sha}
"""


class Gate2GuardHarness(unittest.TestCase):
    """Socle commun : workspace éphémère + secret humain hors workspace."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.home = Path(self._tmp.name)
        self.workspace = self.home / "workspace"
        self.workspace.mkdir()
        # Le secret humain vit HORS du workspace agent (~/.tesla simulé).
        self.secret_path = self.home / ".tesla" / "gate2" / "secret.key"
        self.secret_path.parent.mkdir(parents=True, exist_ok=True)
        self.secret_path.write_text("gate2-hmac-secret-0123456789abcdef", encoding="utf-8")
        self.secret_path.chmod(0o600)

    # ------------------------------------------------------------------ #
    def _write_graph(self, *, sealed: bool = False, mission: str = MISSION,
                     n1_role: str = "Audit", nonce: str = "gate2-test-0001",
                     approval_sha: str | None = None,
                     name: str = "mission_graph.yaml") -> Path:
        path = self.workspace / name
        text = GRAPH_TEMPLATE.format(mission=mission, n1_role=n1_role)
        # Le sceau est TOUJOURS calculé sur le texte courant (jamais sur un
        # état périmé du fichier) — c'est exactement la cérémonie humaine.
        path.write_text(text, encoding="utf-8")
        if sealed:
            sha = approval_sha if approval_sha is not None else compute_approval_sha256(load_graph_file(path))
            text += APPROVAL_TEMPLATE.format(nonce=nonce, sha=sha)
            path.write_text(text, encoding="utf-8")
        return path

    def _run(self, *argv: str, **kwargs) -> subprocess.CompletedProcess:
        env = dict(os.environ)
        env.pop("TESLA_GATE2_SECRET", None)  # isolation : jamais le secret du hôte
        env["HOME"] = str(self.home)
        env.update(kwargs.get("env_overrides") or {})
        return subprocess.run([sys.executable, str(GUARD), *argv],
                              capture_output=True, text=True, env=env, check=False)

    def _issue(self, graph: Path, mission: str = MISSION, ttl: str = "900",
               secret: Path | None = None) -> subprocess.CompletedProcess:
        return self._run("issue-token", "--graph", str(graph), "--mission", mission,
                         "--root", str(self.workspace), "--secret-file",
                         str(secret or self.secret_path),
                         "--issued-at", ISSUED_AT, "--ttl-seconds", ttl)

    def _pre_flight(self, graph: Path, mission: str = MISSION,
                    now: str = NOW_VALID) -> subprocess.CompletedProcess:
        return self._run("pre-flight", "--graph", str(graph), "--mission", mission,
                         "--root", str(self.workspace), "--secret-file", str(self.secret_path),
                         "--now", now)

    @staticmethod
    def _json(proc: subprocess.CompletedProcess) -> dict:
        try:
            return json.loads(proc.stdout)
        except json.JSONDecodeError:
            return {"_stdout": proc.stdout, "_stderr": proc.stderr}


class IncidentReproductionTests(Gate2GuardHarness):
    """Reproduction de l'incident du 2026-09-02 19:14:36 (GATE 2 BYPASS)."""

    def test_incident_unsealed_graph_blocks_delegation(self) -> None:
        """19:14:36 rejoué : graphe SANS sceau -> invoke_subagent doit être bloqué."""
        graph = self._write_graph(sealed=False)
        proc = self._pre_flight(graph)
        self.assertEqual(proc.returncode, 1, proc.stdout)
        result = self._json(proc)
        self.assertEqual(result["verdict"], "BLOCKED")
        self.assertEqual(result["reason"], "GRAPH_NOT_APPROVED")
        self.assertEqual(result["stage"], "DAG_VERIFY")

    def test_forged_approved_by_field_is_not_authorization(self) -> None:
        """P-AGENT-002 : écrire approved_by dans le YAML ne constitue PAS une
        validation humaine — même avec un sceau recalculé par l'agent, le
        jeton HMAC (secret hors workspace) manque."""
        # (a) approved_by forgré + sceau invalide (hexadécimal non numérique
        #     pour rester une chaîne YAML et atteindre la vérification du sceau)
        forged = self._write_graph(sealed=True, approval_sha="a" + "0" * 63)
        proc = self._pre_flight(forged)
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(self._json(proc)["reason"], "APPROVAL_SEAL_MISMATCH")
        # (b) approved_by forgré + sceau recalculé par l'agent (forking valide)
        #     -> le sceau n'est qu'une empreinte d'intégrité ; sans jeton signé
        #     par le secret humain, la délégation reste bloquée.
        forged_valid = self._write_graph(sealed=True, nonce="forge-0002")
        proc = self._pre_flight(forged_valid)
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(self._json(proc)["reason"], "GATE2_TOKEN_MISSING")

    def test_pre_flight_blocks_when_token_missing(self) -> None:
        graph = self._write_graph(sealed=True)
        proc = self._pre_flight(graph)
        self.assertEqual(proc.returncode, 1)
        result = self._json(proc)
        self.assertEqual(result["reason"], "GATE2_TOKEN_MISSING")
        self.assertEqual(result["stage"], "TOKEN_LOAD")

    def test_issue_token_refuses_unsealed_graph(self) -> None:
        """Aucun jeton ne peut bénir un graphe non scellé (cérémonie cohérente)."""
        graph = self._write_graph(sealed=False)
        proc = self._issue(graph)
        self.assertEqual(proc.returncode, 1)
        result = self._json(proc)
        self.assertEqual(result["reason"], "GATE2_GRAPH_NOT_SEALABLE")
        self.assertEqual(result["dag"]["reason"], "GRAPH_NOT_APPROVED")


class HappyPathTests(Gate2GuardHarness):
    """Le chemin légitime : cérémonie humaine -> pré-vol PASS -> rédemption."""

    def test_valid_ceremony_authorizes_delegation(self) -> None:
        graph = self._write_graph(sealed=True)
        issue = self._issue(graph)
        self.assertEqual(issue.returncode, 0, issue.stdout)
        result = self._json(issue)
        self.assertEqual(result["verdict"], "PASS")
        self.assertEqual(result["authority"], "Lord Mahonheim")

        proc = self._pre_flight(graph)
        self.assertEqual(proc.returncode, 0, proc.stdout)
        pre = self._json(proc)
        self.assertEqual(pre["verdict"], "PASS")
        self.assertEqual(pre["reason"], "GATE2_DELEGATION_AUTHORIZED")
        # La liaison porte l'empreinte exacte du contenu approuvé.
        self.assertEqual(pre["graph_sha256"],
                         compute_approval_sha256(load_graph_file(graph)))

    def test_token_file_permissions_are_0600(self) -> None:
        graph = self._write_graph(sealed=True)
        self.assertEqual(self._issue(graph).returncode, 0)
        token = self.workspace / "runtime" / "gate2" / "gate2_approval.token"
        self.assertTrue(token.is_file())
        self.assertEqual(token.stat().st_mode & 0o077, 0)

    def test_pre_flight_is_pure_and_idempotent(self) -> None:
        """Correction du verrou 1 initial : vérifier NE consomme PAS."""
        graph = self._write_graph(sealed=True)
        self.assertEqual(self._issue(graph).returncode, 0)
        token = self.workspace / "runtime" / "gate2" / "gate2_approval.token"
        secret = self.secret_path.read_bytes().strip()
        moment = datetime(2026, 9, 2, 19, 5, tzinfo=timezone.utc)
        for _ in range(3):
            code, verdict = pre_flight_delegation_check(graph, token, MISSION,
                                                        secret=secret, now=moment,
                                                        root=self.workspace)
            self.assertEqual(code, 0, verdict)
            self.assertEqual(verdict["verdict"], "PASS")
        nonces = self.workspace / "runtime" / "gate2" / "nonces"
        self.assertFalse(nonces.exists() and any(nonces.iterdir()),
                         "un pré-vol pur ne doit créer aucun verrou de nonce")


class BindingTests(Gate2GuardHarness):
    """Liaison cryptographique jeton <-> mission <-> contenu du graphe."""

    def test_token_binding_blocks_foreign_mission(self) -> None:
        graph = self._write_graph(sealed=True)
        self.assertEqual(self._issue(graph, mission="MISSION-A").returncode, 0)
        proc = self._pre_flight(graph, mission="MISSION-B")
        self.assertEqual(proc.returncode, 1)
        result = self._json(proc)
        self.assertEqual(result["reason"], "GATE2_TOKEN_MISSION_MISMATCH")
        self.assertEqual(result["stage"], "TOKEN_BINDING")

    def test_binding_detects_post_seal_tampering(self) -> None:
        """TOCTOU : un graphe modifié APRÈS émission du jeton est rejeté, même
        si l'agent recalcule lui-même le sceau (empreinte) pour passer dag-verify."""
        graph = self._write_graph(sealed=True)
        self.assertEqual(self._issue(graph).returncode, 0)
        # L'agent tente une retouche post-sceau et refait le sceau (forge SHA).
        tampered = self._write_graph(sealed=True, n1_role="Audit-MAJ-RETOUCHE",
                                     nonce="forge-0003")
        self.assertEqual(tampered, graph)  # même chemin, contenu réécrit
        proc = self._pre_flight(graph)
        self.assertEqual(proc.returncode, 1)
        result = self._json(proc)
        self.assertEqual(result["reason"], "GATE2_TOKEN_GRAPH_MISMATCH")

    def test_expired_token_blocks(self) -> None:
        graph = self._write_graph(sealed=True)
        self.assertEqual(self._issue(graph, ttl="300").returncode, 0)
        proc = self._pre_flight(graph, now=NOW_LATE)  # 19:20 > 19:05 (TTL 300s)
        self.assertEqual(proc.returncode, 1)
        result = self._json(proc)
        self.assertEqual(result["reason"], "GATE2_TOKEN_EXPIRED")

    def test_tampered_token_signature_blocks(self) -> None:
        graph = self._write_graph(sealed=True)
        self.assertEqual(self._issue(graph).returncode, 0)
        token = self.workspace / "runtime" / "gate2" / "gate2_approval.token"
        forged = json.loads(token.read_text(encoding="utf-8"))
        forged["authority"] = "Quelqu'un d'Autre"
        token.write_text(json.dumps(forged, indent=2) + "\n", encoding="utf-8")
        proc = self._pre_flight(graph)
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(self._json(proc)["reason"], "GATE2_TOKEN_SIGNATURE_INVALID")

    def test_secret_unavailable_is_unknown_not_pass(self) -> None:
        """P3 : sans secret observable, le verdict est UNKNOWN — jamais PASS."""
        graph = self._write_graph(sealed=True)
        self.assertEqual(self._issue(graph).returncode, 0)
        # HOME vierge : ni TESLA_GATE2_SECRET ni ~/.tesla/gate2/secret.key.
        empty_home = self.home / "empty-home"
        empty_home.mkdir()
        proc = self._run("pre-flight", "--graph", str(graph), "--mission", MISSION,
                         "--root", str(self.workspace), "--now", NOW_VALID,
                         env_overrides={"HOME": str(empty_home)})
        self.assertEqual(proc.returncode, 66, proc.stdout)
        result = self._json(proc)
        self.assertEqual(result["verdict"], "UNKNOWN")
        self.assertEqual(result["reason"], "GATE2_SECRET_UNAVAILABLE")

    def test_secret_file_loose_permissions_fail_closed(self) -> None:
        graph = self._write_graph(sealed=True)
        self.assertEqual(self._issue(graph).returncode, 0)
        loose = self.home / "loose_secret.key"
        loose.write_text("secret-trop-permissif", encoding="utf-8")
        loose.chmod(0o644)
        proc = self._run("pre-flight", "--graph", str(graph), "--mission", MISSION,
                         "--root", str(self.workspace), "--secret-file", str(loose),
                         "--now", NOW_VALID)
        self.assertEqual(proc.returncode, 66)
        self.assertEqual(self._json(proc)["reason"], "GATE2_SECRET_UNSAFE_PERMISSIONS")

    def test_invalid_now_timestamp_is_usage_error(self) -> None:
        graph = self._write_graph(sealed=True)
        proc = self._run("pre-flight", "--graph", str(graph), "--mission", MISSION,
                         "--root", str(self.workspace), "--secret-file", str(self.secret_path),
                         "--now", "pas-une-date")
        self.assertEqual(proc.returncode, 64)
        self.assertEqual(self._json(proc)["reason"], "GATE2_TIMESTAMP_INVALID")


class AntiReplayLedgerTests(Gate2GuardHarness):
    """Consommation atomique (A-003) & grand livre d'échange chaîné."""

    def test_consume_is_single_use_anti_replay(self) -> None:
        graph = self._write_graph(sealed=True)
        self.assertEqual(self._issue(graph).returncode, 0)
        first = self._run("consume", "--graph", str(graph), "--mission", MISSION,
                          "--root", str(self.workspace), "--secret-file", str(self.secret_path),
                          "--now", NOW_VALID)
        self.assertEqual(first.returncode, 0, first.stdout)
        consumed = self._json(first)
        self.assertEqual(consumed["reason"], "GATE2_DELEGATION_REDEEMED")
        lock = self.workspace / "runtime" / "gate2" / "nonces" / f"{consumed['nonce']}.lock"
        self.assertTrue(lock.is_file())
        # Rejeu (A-003) : le même jeton ne délègue jamais deux fois.
        replay = self._run("consume", "--graph", str(graph), "--mission", MISSION,
                           "--root", str(self.workspace), "--secret-file", str(self.secret_path),
                           "--now", NOW_VALID)
        self.assertEqual(replay.returncode, 1)
        result = self._json(replay)
        self.assertIn(result["reason"],
                      ("GATE2_TOKEN_ALREADY_CONSUMED", "GATE2_TOKEN_REPLAY_DETECTED"))

    def test_pre_flight_after_consume_reports_already_consumed(self) -> None:
        graph = self._write_graph(sealed=True)
        self.assertEqual(self._issue(graph).returncode, 0)
        consume = self._run("consume", "--graph", str(graph), "--mission", MISSION,
                            "--root", str(self.workspace), "--secret-file", str(self.secret_path),
                            "--now", NOW_VALID)
        self.assertEqual(consume.returncode, 0)
        proc = self._pre_flight(graph)
        self.assertEqual(proc.returncode, 1)
        result = self._json(proc)
        self.assertEqual(result["reason"], "GATE2_TOKEN_ALREADY_CONSUMED")
        self.assertEqual(result["stage"], "NONCE_REGISTRY")

    def test_redemption_ledger_chain_verifiable(self) -> None:
        """Le grand livre d'échange est chaîné SHA-256 : toute falsification
        ultérieure est détectable par recalcul indépendant."""
        graph_a = self._write_graph(sealed=True, nonce="chain-0001", name="graph_a.yaml")
        graph_b = self._write_graph(sealed=True, nonce="chain-0002", name="graph_b.yaml")
        self.assertEqual(self._issue(graph_a).returncode, 0)
        self.assertEqual(self._run("consume", "--graph", str(graph_a), "--mission", MISSION,
                                   "--root", str(self.workspace), "--secret-file", str(self.secret_path),
                                   "--now", NOW_VALID).returncode, 0)
        self.assertEqual(self._issue(graph_b).returncode, 0)
        self.assertEqual(self._run("consume", "--graph", str(graph_b), "--mission", MISSION,
                                   "--root", str(self.workspace), "--secret-file", str(self.secret_path),
                                   "--now", NOW_VALID).returncode, 0)

        ledger = self.workspace / "runtime" / "gate2" / "redemptions.jsonl"
        lines = [json.loads(line) for line in ledger.read_text(encoding="utf-8").splitlines() if line.strip()]
        self.assertEqual(len(lines), 2)
        prev = "0" * 64
        for entry in lines:
            self.assertEqual(entry["prev_hash"], prev)
            payload = {k: v for k, v in entry.items() if k != "entry_hash"}
            expected = hashlib.sha256(canonical_bytes(payload)).hexdigest()
            self.assertEqual(entry["entry_hash"], expected)
            prev = entry["entry_hash"]
        head = (self.workspace / "runtime" / "gate2" / "chain_head.sha256").read_text().strip()
        self.assertEqual(head, prev)


class Bypass04AuthorityTests(Gate2GuardHarness):
    """BYPASS-04 : un jeton ne peut ni être émis ni être accepté sans autorité."""

    def test_issue_token_refuses_empty_authority(self) -> None:
        graph = self._write_graph(sealed=True)
        proc = self._run("issue-token", "--graph", str(graph), "--mission", MISSION,
                         "--root", str(self.workspace), "--secret-file", str(self.secret_path),
                         "--authority", "   ", "--issued-at", ISSUED_AT)
        self.assertEqual(proc.returncode, 1)
        result = self._json(proc)
        self.assertEqual(result["reason"], "GATE2_TOKEN_AUTHORITY_MISSING")

    def test_pre_flight_rejects_signed_token_with_empty_authority(self) -> None:
        """Défense en profondeur : même un jeton bien signé mais à autorité vide
        est rejeté en liaison (pré-vol), jamais un PASS implicite."""
        graph = self._write_graph(sealed=True)
        secret = self.secret_path.read_bytes().strip()
        payload = {
            "token_version": TOKEN_VERSION,
            "mission_id": MISSION,
            "graph_sha256": compute_approval_sha256(load_graph_file(graph)),
            "authority": "",
            "issued_at": ISSUED_AT,
            "expires_at": "2026-09-02T19:30:00Z",
            "nonce": "empty-authority-0001",
        }
        token = dict(payload)
        token["hmac"] = sign_token(payload, secret)
        token_path = self.workspace / "runtime" / "gate2" / "gate2_approval.token"
        token_path.parent.mkdir(parents=True, exist_ok=True)
        token_path.write_text(json.dumps(token, indent=2) + "\n", encoding="utf-8")

        proc = self._pre_flight(graph)
        self.assertEqual(proc.returncode, 1)
        result = self._json(proc)
        self.assertEqual(result["reason"], "GATE2_TOKEN_AUTHORITY_MISSING")
        self.assertEqual(result["stage"], "TOKEN_BINDING")


class Bypass06LedgerTamperingTests(Gate2GuardHarness):
    """BYPASS-06 : toute falsification du grand livre rompt la chaîne (détection)."""

    def test_tampered_ledger_blocks_further_redemptions(self) -> None:
        secret = self.secret_path.read_bytes().strip()
        moment = datetime(2026, 9, 2, 19, 5, tzinfo=timezone.utc)
        graph_a = self._write_graph(sealed=True, nonce="ledger-0001", name="g1.yaml")
        graph_b = self._write_graph(sealed=True, nonce="ledger-0002", name="g2.yaml")
        token_path = self.workspace / "runtime" / "gate2" / "gate2_approval.token"

        self.assertEqual(self._issue(graph_a).returncode, 0)
        code, verdict = redeem_delegation_token(graph_a, token_path, MISSION,
                                                secret, now=moment, root=self.workspace)
        self.assertEqual(code, 0, verdict)

        self.assertEqual(self._issue(graph_b).returncode, 0)

        # Falsification d'une entrée existante (autorité usurpée rétrospectivement).
        ledger = self.workspace / "runtime" / "gate2" / "redemptions.jsonl"
        lines = ledger.read_text(encoding="utf-8").splitlines()
        forged = json.loads(lines[0])
        forged["authority"] = "Faux Mahonheim"
        lines[0] = json.dumps(forged, sort_keys=True, ensure_ascii=False)
        ledger.write_text("\n".join(lines) + "\n", encoding="utf-8")

        code, verdict = redeem_delegation_token(graph_b, token_path, MISSION,
                                                secret, now=moment, root=self.workspace)
        self.assertEqual(code, 1)
        self.assertEqual(verdict["reason"], "GATE2_LEDGER_CHAIN_BROKEN")


class SafeSpawnTransactionTests(Gate2GuardHarness):
    """A-7 : transaction RESERVE -> SPAWN -> OBSERVE (quatre issues fermées)."""

    def _delegate(self, graph: Path, spawn: list[str], timeout: str = "120") -> subprocess.CompletedProcess:
        return self._run("delegate", "--graph", str(graph), "--mission", MISSION,
                         "--root", str(self.workspace), "--secret-file", str(self.secret_path),
                         "--now", NOW_VALID, "--spawn-timeout", timeout,
                         "--spawn-command", *spawn)

    def test_delegate_success_commits_nonce(self) -> None:
        graph = self._write_graph(sealed=True)
        self.assertEqual(self._issue(graph).returncode, 0)
        proc = self._delegate(graph, ["true"])
        self.assertEqual(proc.returncode, 0, proc.stdout)
        result = self._json(proc)
        self.assertEqual(result["reason"], "GATE2_DELEGATION_SPAWN_SUCCEEDED")
        self.assertEqual(result["stage"], "OBSERVE")
        # Le nonce est définitivement consommé : tout retry est un rejeu.
        replay = self._delegate(graph, ["true"])
        self.assertEqual(replay.returncode, 1)
        self.assertIn(self._json(replay)["reason"],
                      ("GATE2_TOKEN_REPLAY_DETECTED", "GATE2_TOKEN_ALREADY_CONSUMED"))

    def test_delegate_spawn_failure_consumes_nonce(self) -> None:
        """COMMIT_FAILURE : spawn démarré puis échoué -> nonce brûlé, pas de rejeu."""
        graph = self._write_graph(sealed=True)
        self.assertEqual(self._issue(graph).returncode, 0)
        proc = self._delegate(graph, ["false"])
        self.assertEqual(proc.returncode, 1)
        result = self._json(proc)
        self.assertEqual(result["reason"], "GATE2_DELEGATION_SPAWN_FAILED")
        self.assertEqual(result["spawn_exit_code"], 1)
        replay = self._delegate(graph, ["true"])
        self.assertEqual(replay.returncode, 1)
        self.assertIn(self._json(replay)["reason"],
                      ("GATE2_TOKEN_REPLAY_DETECTED", "GATE2_TOKEN_ALREADY_CONSUMED"))

    def test_delegate_launch_failure_aborts_safe_and_releases_nonce(self) -> None:
        """ABORT_SAFE : échec de lancement CERTAIN -> nonce libéré et réutilisable."""
        graph = self._write_graph(sealed=True)
        self.assertEqual(self._issue(graph).returncode, 0)
        proc = self._delegate(graph, ["/nonexistent/vigilum-spawn-xyz"])
        self.assertEqual(proc.returncode, 1)
        result = self._json(proc)
        self.assertEqual(result["reason"], "GATE2_SPAWN_NOT_STARTED_ABORT_SAFE")
        nonces = self.workspace / "runtime" / "gate2" / "nonces"
        self.assertFalse(any(nonces.iterdir()), "ABORT_SAFE doit libérer le verrou")
        # Le nonce est à nouveau jouable (spawn certainement jamais démarré).
        proc2 = self._delegate(graph, ["true"])
        self.assertEqual(proc2.returncode, 0, proc2.stdout)
        self.assertEqual(self._json(proc2)["reason"], "GATE2_DELEGATION_SPAWN_SUCCEEDED")

    def test_delegate_timeout_confines_unknown_and_forbids_retry(self) -> None:
        """BYPASS-09 : timeout -> UNKNOWN_CONFINED, nonce brûlé, zéro retry."""
        graph = self._write_graph(sealed=True)
        self.assertEqual(self._issue(graph).returncode, 0)
        proc = self._delegate(graph, ["sleep", "5"], timeout="1")
        self.assertEqual(proc.returncode, 66, proc.stdout)
        result = self._json(proc)
        self.assertEqual(result["reason"], "GATE2_SPAWN_UNKNOWN_CONFINED")
        # L'état d'incertitude interdit la remise en jeu automatique du nonce :
        # le pré-vol bloque en registre (état terminal non-RESERVED = consommé).
        retry = self._delegate(graph, ["true"])
        self.assertEqual(retry.returncode, 1)
        self.assertEqual(self._json(retry)["reason"], "GATE2_TOKEN_ALREADY_CONSUMED")
        # Le verrou porte l'état terminal d'incertitude (inspectable).
        lock = self.workspace / "runtime" / "gate2" / "nonces" / f"{result['nonce']}.lock"
        self.assertEqual(json.loads(lock.read_text(encoding="utf-8"))["state"],
                         "UNKNOWN_CONFINED")


class ReservedNonceRecoveryTests(Gate2GuardHarness):
    """Crash entre RESERVE et SPAWN : fail-closed + release manuel signé."""

    def test_reserved_unobserved_blocks_then_manual_release_restores(self) -> None:
        graph = self._write_graph(sealed=True)
        self.assertEqual(self._issue(graph).returncode, 0)
        token_path = self.workspace / "runtime" / "gate2" / "gate2_approval.token"
        nonce = json.loads(token_path.read_text(encoding="utf-8"))["nonce"]

        # Simulation du crash : verrou RESERVED sans observation (BYPASS-09).
        lock = self.workspace / "runtime" / "gate2" / "nonces" / f"{nonce}.lock"
        lock.parent.mkdir(parents=True, exist_ok=True)
        lock.write_text(json.dumps({"nonce": nonce, "state": LOCK_STATE_RESERVED}) + "\n",
                        encoding="utf-8")

        proc = self._pre_flight(graph)
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(self._json(proc)["reason"], "GATE2_TOKEN_RESERVED_UNOBSERVED")

        # Release manuel signé (autorité humaine) — ledgeré.
        rel = self._run("release", "--nonce", nonce, "--root", str(self.workspace),
                        "--secret-file", str(self.secret_path))
        self.assertEqual(rel.returncode, 0, rel.stdout)
        self.assertEqual(self._json(rel)["reason"], "GATE2_NONCE_RELEASED_MANUAL")

        # Le pré-vol redevient PASS : le nonce est à nouveau présentable.
        proc = self._pre_flight(graph)
        self.assertEqual(proc.returncode, 0, proc.stdout)

    def test_release_refuses_terminal_nonce(self) -> None:
        graph = self._write_graph(sealed=True)
        self.assertEqual(self._issue(graph).returncode, 0)
        consume = self._run("consume", "--graph", str(graph), "--mission", MISSION,
                            "--root", str(self.workspace), "--secret-file", str(self.secret_path),
                            "--now", NOW_VALID)
        self.assertEqual(consume.returncode, 0)
        token_path = self.workspace / "runtime" / "gate2" / "gate2_approval.token"
        nonce = json.loads(token_path.read_text(encoding="utf-8"))["nonce"]
        rel = self._run("release", "--nonce", nonce, "--root", str(self.workspace),
                        "--secret-file", str(self.secret_path))
        self.assertEqual(rel.returncode, 1)
        self.assertEqual(self._json(rel)["reason"], "GATE2_NONCE_LOCK_TERMINAL")


if __name__ == "__main__":
    unittest.main()
