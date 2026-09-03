#!/usr/bin/env python3
"""Tests V2.5.1 — Verrouillage Déterministe de l'Orchestrateur.

Preuves physiques (P1 : No Proof, No Marble) de la solution opérationnelle
issue de l'audit du Plan d'Intervention Correctif V2.5.0 :

  Phase 1 — Anti-Usurpation Git (hook 08 + classifieur déterministe)
  Phase 2 — Zero-Middleman / SCD (hook 09 + bibliothèque tesla-scd.sh,
            refactor du hook 07)
  Phase 3 — Pre-Flight Checklist Gate 0 (hook 10)
  Phase 4 — Attestations SLSA / pivot CI-CD (bin/slsa_attestation.py)

Chaque test encode un invariant doctrinal (P2, P3, P4, P9, P10, D-007,
BYPASS-01, A-003). Stdlib uniquement, fail-closed, espaces temporaires.
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


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


git_guard = _load_module("tesla_git_guard_v251", LIB_DIR / "tesla_git_guard.py")
zero_middleman = _load_module("tesla_zero_middleman_v251", LIB_DIR / "tesla_zero_middleman.py")
preflight = _load_module("tesla_preflight_v251", LIB_DIR / "tesla_preflight.py")


def run_hook(script: Path, payload: dict, env_extra: dict | None = None) -> dict:
    """Exécute un hook Antigravity avec un payload JSON, retourne la décision."""
    env = os.environ.copy()
    env.pop("TESLA_AGENT_IDENTITY", None)
    if env_extra:
        env.update(env_extra)
    proc = subprocess.run(
        ["bash", str(script)],
        input=json.dumps(payload),
        capture_output=True, text=True, timeout=60, env=env, check=False)
    if proc.returncode != 0:
        raise AssertionError(
            f"hook {script.name} crashed (exit {proc.returncode}): {proc.stderr}")
    return json.loads(proc.stdout.strip().splitlines()[-1])


def make_transcript(brain: Path, conv_id: str, lines: list[dict]) -> Path:
    transcript_dir = brain / conv_id / ".system_generated" / "logs"
    transcript_dir.mkdir(parents=True, exist_ok=True)
    transcript = transcript_dir / "transcript.jsonl"
    with open(transcript, "w", encoding="utf-8") as handle:
        for line in lines:
            # JSONL compact du runtime Antigravity (sans espaces après ':').
            handle.write(json.dumps(line, ensure_ascii=False,
                                    separators=(",", ":")) + "\n")
    return transcript


def write_capability_probe(root: Path, statuses: dict[str, str] | None = None) -> None:
    statuses = statuses if statuses is not None else {
        "python3": "PASS", "bash": "PASS", "git": "PASS"}
    runtime = root / "runtime"
    runtime.mkdir(parents=True, exist_ok=True)
    (runtime / "capability_health.json").write_text(json.dumps({
        "capabilities": [
            {"capability": name, "status": status}
            for name, status in statuses.items()
        ],
        "verdict_global": "PASS" if all(v == "PASS" for v in statuses.values()) else "UNKNOWN",
    }), encoding="utf-8")


# --------------------------------------------------------------------------- #
# PHASE 1 — Classifieur Git déterministe                                        #
# --------------------------------------------------------------------------- #
class GitClassifierReadTests(unittest.TestCase):
    """Lectures pures : autorisées (l'Orchestrateur doit pouvoir inspecter)."""

    def test_read_verbs_are_allowed(self) -> None:
        for command in ("git status", "git log --oneline", "git diff HEAD~1",
                        "git show abc123", "git rev-parse --show-toplevel",
                        "git ls-files", "git blame README.md"):
            verdict = git_guard.classify_command(command)["verdict"]
            self.assertEqual(verdict, "READ", command)

    def test_global_flags_are_skipped_correctly(self) -> None:
        verdict = git_guard.classify_command(
            "git -C /repo/sub log --oneline")["verdict"]
        self.assertEqual(verdict, "READ")

    def test_git_dir_flag_is_skipped(self) -> None:
        verdict = git_guard.classify_command(
            "git --git-dir=/x/.git --no-pager status")["verdict"]
        self.assertEqual(verdict, "READ")

    def test_read_subverbs_are_allowed(self) -> None:
        for command in ("git stash list", "git remote show origin",
                        "git config --get user.name", "git config --list"):
            verdict = git_guard.classify_command(command)["verdict"]
            self.assertEqual(verdict, "READ", command)

    def test_non_git_commands_are_neutral(self) -> None:
        for command in ("ls -la", "python3 bin/test_runner.py --root .",
                        "echo hello world", "cat notes.txt"):
            self.assertEqual(git_guard.classify_command(command)["verdict"],
                             "NO_GIT", command)

    def test_github_word_is_not_git(self) -> None:
        self.assertEqual(git_guard.classify_command(
            "echo github repository")["verdict"], "NO_GIT")

    def test_gh_read_verbs_are_allowed(self) -> None:
        for command in ("gh pr view 12", "gh pr list", "gh repo view org/repo",
                        "gh run list", "gh release list"):
            self.assertEqual(git_guard.classify_command(command)["verdict"],
                             "READ", command)


class GitClassifierMutationTests(unittest.TestCase):
    """Mutations et obfuscations : BLOQUÉES (P10 fail-closed)."""

    def test_mutating_verbs_are_blocked(self) -> None:
        for command in ("git add .", "git commit -m x", "git push origin main",
                        "git pull", "git merge feature", "git rebase main",
                        "git reset --hard", "git checkout -b new-branch",
                        "git clean -fd", "git rm file.txt", "git mv a b",
                        "git tag v1.0", "git stash push", "git clone url",
                        "git init", "git config user.name X",
                        "git apply patch.diff", "git cherry-pick abc",
                        "git revert abc", "git fetch origin"):
            self.assertEqual(git_guard.classify_command(command)["verdict"],
                             "MUTATING", command)

    def test_mutating_subverbs_are_blocked(self) -> None:
        for command in ("git stash pop", "git remote add origin url",
                        "git config user.email a@b.c", "git notes add -m x",
                        "git worktree add ../wt", "git reflog expire --all"):
            self.assertEqual(git_guard.classify_command(command)["verdict"],
                             "MUTATING", command)

    def test_bare_git_opens_shell_blocked(self) -> None:
        self.assertEqual(git_guard.classify_command("git")["verdict"], "MUTATING")

    def test_unknown_verb_or_alias_blocked(self) -> None:
        # Alias utilisateur possible (git config alias.*) => fail-closed.
        self.assertEqual(git_guard.classify_command("git co -m x")["verdict"],
                         "MUTATING")
        self.assertEqual(git_guard.classify_command("git xyzzy")["verdict"],
                         "MUTATING")

    def test_unknown_global_flag_blocked(self) -> None:
        self.assertEqual(git_guard.classify_command(
            "git --weird-flag status")["verdict"], "MUTATING")

    def test_wrappers_are_unwrapped(self) -> None:
        for command in ("sudo git push", "env GIT_DIR=x git commit -m y",
                        "nohup git pull &", "timeout 30 git push",
                        "/usr/bin/git push"):
            self.assertEqual(git_guard.classify_command(command)["verdict"],
                             "MUTATING", command)

    def test_sh_c_payload_is_recursed(self) -> None:
        self.assertEqual(git_guard.classify_command(
            "sh -c 'git push origin main'")["verdict"], "MUTATING")
        self.assertEqual(git_guard.classify_command(
            "bash -c \"git commit -m leak\"")["verdict"], "MUTATING")

    def test_chained_commands_are_segmented(self) -> None:
        self.assertEqual(git_guard.classify_command(
            "make build && git push")["verdict"], "MUTATING")
        self.assertEqual(git_guard.classify_command(
            "git status; git push")["verdict"], "MUTATING")
        self.assertEqual(git_guard.classify_command(
            "git log | head -5")["verdict"], "READ")

    def test_command_substitution_blocked(self) -> None:
        self.assertEqual(git_guard.classify_command(
            "echo $(git push)")["verdict"], "MUTATING")

    def test_xargs_git_blocked(self) -> None:
        self.assertEqual(git_guard.classify_command(
            "find . -name '*.py' | xargs git add")["verdict"], "MUTATING")

    def test_unparseable_quoting_blocked(self) -> None:
        self.assertEqual(git_guard.classify_command(
            'git commit -m "unbalanced')["verdict"], "UNPARSEABLE")

    def test_unreconciled_git_occurrence_blocked(self) -> None:
        # « git » mentionné dans une chaîne non exécutable : non réconcilié.
        self.assertEqual(git_guard.classify_command(
            "python3 -c \"os.system('git push')\"")["verdict"], "MUTATING")

    def test_git_argument_occurrences_are_accounted(self) -> None:
        # « git » en position d'argument d'une commande non-git : neutre.
        self.assertEqual(git_guard.classify_command(
            "echo git is a tool")["verdict"], "NO_GIT")

    def test_redirection_targets_are_not_commands(self) -> None:
        self.assertEqual(git_guard.classify_command(
            "git log > git")["verdict"], "READ")

    def test_gh_mutations_blocked(self) -> None:
        for command in ("gh pr create --title x", "gh pr merge 12",
                        "gh release create v1", "gh repo delete org/repo",
                        "gh api /repos/x/y", "gh auth login"):
            self.assertEqual(git_guard.classify_command(command)["verdict"],
                             "MUTATING", command)


class Hook08AntiUsurpationTests(unittest.TestCase):
    """Phase 1 — interception end-to-end du hook 08 (payload Antigravity)."""

    HOOK = HOOKS_DIR / "hook_08_anti_usurpation.sh"

    def payload(self, command: str, agent: str | None = None) -> dict:
        args = {"command": command}
        if agent:
            args["agent_id"] = agent
        return {"conversationId": "conv-123",
                "toolCall": {"name": "run_command", "args": args}}

    def test_orchestrator_git_read_is_allowed(self) -> None:
        decision = run_hook(self.HOOK, self.payload("git status"))
        self.assertEqual(decision["decision"], "allow")

    def test_orchestrator_git_mutation_is_denied_exit_81(self) -> None:
        decision = run_hook(self.HOOK, self.payload("git push origin main"))
        self.assertEqual(decision["decision"], "deny")
        self.assertIn("Exit 81", decision["reason"])
        self.assertIn("tesla-github-manager", decision["reason"])

    def test_github_manager_jurisdiction_is_exclusive(self) -> None:
        decision = run_hook(
            self.HOOK, self.payload("git push origin main",
                                    agent="tesla-github-manager"))
        self.assertEqual(decision["decision"], "allow")

    def test_identity_from_env_resolves_jurisdiction(self) -> None:
        decision = run_hook(self.HOOK, self.payload("git commit -m x"),
                            env_extra={"TESLA_AGENT_IDENTITY":
                                       "tesla-github-manager"})
        self.assertEqual(decision["decision"], "allow")

    def test_other_subagents_cannot_git(self) -> None:
        decision = run_hook(self.HOOK, self.payload("git add .",
                                                    agent="tesla-master-code"))
        self.assertEqual(decision["decision"], "deny")

    def test_non_command_tools_are_ignored(self) -> None:
        decision = run_hook(self.HOOK, {
            "conversationId": "conv-123",
            "toolCall": {"name": "write_file",
                         "args": {"path": "src/app.py"}}})
        self.assertEqual(decision["decision"], "allow")

    def test_command_tool_without_command_denied(self) -> None:
        decision = run_hook(self.HOOK, {
            "conversationId": "conv-123",
            "toolCall": {"name": "run_command", "args": {}}})
        self.assertEqual(decision["decision"], "deny")

    def test_obfuscated_mutation_via_sh_c_denied(self) -> None:
        decision = run_hook(self.HOOK,
                            self.payload("sh -c 'git push origin main'"))
        self.assertEqual(decision["decision"], "deny")


# --------------------------------------------------------------------------- #
# PHASE 2 — Zero-Middleman / SCD                                               #
# --------------------------------------------------------------------------- #
class ZeroMiddlemanPathTests(unittest.TestCase):
    def test_security_flag_paths_are_forbidden(self) -> None:
        for path in ("verbal_approval.flag", "runtime/approval.flag",
                     "x/.approval", "secrets.token", "gate2_approval.token"):
            self.assertIsNotNone(
                zero_middleman.is_forbidden_path(path), path)

    def test_authorization_artifacts_are_forbidden(self) -> None:
        for path in ("runtime/subagents/receipt_tesla-arcanis-360.json",
                     "CERTIFICATES/MARBLE_CERTIFICATE_2026.json",
                     "evidence/chain_head.sha256",
                     "runtime/gate2/redemptions.jsonl",
                     "runtime/marble_eligibility.json"):
            self.assertIsNotNone(zero_middleman.is_forbidden_path(path), path)

    def test_security_directories_are_forbidden(self) -> None:
        for path in ("runtime/nonces/abc.lock", "runtime/gate2/anything.json",
                     ".tesla/security/master.key"):
            self.assertIsNotNone(zero_middleman.is_forbidden_path(path), path)

    def test_isolated_runtime_evidence_root_is_forbidden(self) -> None:
        os.environ["TESLA_RUNTIME_EVIDENCE"] = "/opt/evidence"
        try:
            reason = zero_middleman.is_forbidden_path(
                "/opt/evidence/M-1/transcripts/inv-x.json")
            self.assertIsNotNone(reason)
        finally:
            os.environ.pop("TESLA_RUNTIME_EVIDENCE", None)

    def test_path_traversal_is_forbidden(self) -> None:
        self.assertIsNotNone(
            zero_middleman.is_forbidden_path("docs/../../etc/approval.flag"))

    def test_normal_source_files_are_allowed(self) -> None:
        for path in ("src/app.py", "docs/report.md", "OUTPUTS/synthèse.md",
                     "README.md"):
            self.assertIsNone(zero_middleman.is_forbidden_path(path), path)


class Hook09ZeroMiddlemanTests(unittest.TestCase):
    """Phase 2 — l'agent ne peut plus écrire d'artefacts d'autorisation."""

    HOOK = HOOKS_DIR / "hook_09_zero_middleman.sh"

    def payload(self, path: str, tool: str = "write_file") -> dict:
        return {"conversationId": "conv-123",
                "toolCall": {"name": tool, "args": {"path": path}}}

    def test_flag_write_is_denied_exit_81(self) -> None:
        decision = run_hook(self.HOOK, self.payload("runtime/verbal_approval.flag"))
        self.assertEqual(decision["decision"], "deny")
        self.assertIn("Exit 81", decision["reason"])
        self.assertIn("BYPASS-01", decision["reason"])

    def test_token_write_is_denied_even_for_github_manager(self) -> None:
        decision = run_hook(
            self.HOOK,
            {"conversationId": "conv-1",
             "toolCall": {"name": "write_file",
                          "args": {"path": "gate2_approval.token",
                                   "agent_id": "tesla-github-manager"}}})
        self.assertEqual(decision["decision"], "deny")

    def test_receipt_forging_is_denied(self) -> None:
        decision = run_hook(self.HOOK, self.payload(
            "runtime/subagents/receipt_tesla-arcanis-360.json"))
        self.assertEqual(decision["decision"], "deny")

    def test_certificate_write_is_denied(self) -> None:
        decision = run_hook(self.HOOK, self.payload(
            "CERTIFICATES/MARBLE_CERTIFICATE_x.json", tool="edit_file"))
        self.assertEqual(decision["decision"], "deny")

    def test_normal_write_is_allowed(self) -> None:
        decision = run_hook(self.HOOK, self.payload("src/module.py"))
        self.assertEqual(decision["decision"], "allow")

    def test_write_tool_without_path_is_denied(self) -> None:
        decision = run_hook(self.HOOK, {
            "conversationId": "conv-1",
            "toolCall": {"name": "write_file", "args": {"content": "x"}}})
        self.assertEqual(decision["decision"], "deny")

    def test_non_write_tools_are_ignored(self) -> None:
        decision = run_hook(self.HOOK, {
            "conversationId": "conv-1",
            "toolCall": {"name": "run_command",
                         "args": {"command": "ls"}}})
        self.assertEqual(decision["decision"], "allow")

    def test_multi_edit_paths_are_all_checked(self) -> None:
        decision = run_hook(self.HOOK, {
            "conversationId": "conv-1",
            "toolCall": {"name": "apply_patch", "args": {
                "patches": [{"path": "src/ok.py"},
                            {"path": "runtime/approval.flag"}]}}})
        self.assertEqual(decision["decision"], "deny")


class SCDLibraryTests(unittest.TestCase):
    """Phase 2 — bibliothèque Sovereign Chat Directives (universelle)."""

    LIB = LIB_DIR / "tesla-scd.sh"

    def scd(self, script: str, env_extra: dict | None = None) -> tuple[int, str]:
        env = os.environ.copy()
        env.pop("TESLA_BRAIN_ROOT", None)
        if env_extra:
            env.update(env_extra)
        proc = subprocess.run(
            ["bash", "-c", f'source "{self.LIB}"\n{script}'],
            capture_output=True, text=True, timeout=30, env=env, check=False)
        return proc.returncode, (proc.stdout + proc.stderr).strip()

    def test_brain_root_env_override(self) -> None:
        code, out = self.scd('printf "%s" "$(tesla_scd_brain_root)"',
                             {"TESLA_BRAIN_ROOT": "/tmp/custom-brain"})
        self.assertEqual((code, out), (0, "/tmp/custom-brain"))

    def test_transcript_path_rejects_traversal(self) -> None:
        # Le retour 1 (refus) empêche la construction du chemin.
        code, out = self.scd(
            'if tesla_scd_transcript_path "../../etc"; then echo BUILT; else echo REFUSED; fi')
        self.assertEqual(out, "REFUSED")

    def test_valid_directive_phrases(self) -> None:
        for phrase in ("je valide", "Je valide", "JE VALIDE",
                       "je valide l'action", "go", "GO"):
            clean = phrase.lower().replace("'", "")
            code, out = self.scd(
                f'tesla_scd_is_valid_directive "$(printf \'%s\' \'{clean}\' '
                f'| tr -d \'[:punct:]\' | xargs)" && echo YES || echo NO')
            self.assertEqual(out, "YES", phrase)

    def test_invalid_directive_phrases(self) -> None:
        for phrase in ("je valide pas", "ok", "valide", "yes",
                       "je confirme", "c est bon"):
            code, out = self.scd(
                f'tesla_scd_is_valid_directive "$(printf \'%s\' \'{phrase}\' '
                f'| tr -d \'[:punct:]\' | xargs)" && echo YES || echo NO')
            self.assertEqual(out, "NO", phrase)

    def test_consume_is_single_use(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            code, out = self.scd(
                f'tesla_scd_consume 4242 "{tmp}" && echo FIRST-OK; '
                f'tesla_scd_consume 4242 "{tmp}" && echo REPLAY || echo REPLAY-BLOCKED')
            self.assertIn("FIRST-OK", out)
            self.assertIn("REPLAY-BLOCKED", out)
            self.assertFalse((Path(tmp) / "runtime" / "gate2" /
                              "consumed_step_4242.lock").is_dir())


class Hook07SCDRegressionTests(unittest.TestCase):
    """Phase 2 — cérémonie SCD complète via le hook 07 refactoré."""

    HOOK = HOOKS_DIR / "hook_07_gate2_interceptor.sh"

    def payload(self, subagents: int = 3) -> dict:
        return {"conversationId": "conv-abc-123",
                "toolCall": {"name": "invoke_subagent", "args": {
                    "Subagents": [{"id": f"a{i}"} for i in range(subagents)]}}}

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.brain = Path(self._tmp.name) / "brain"
        self.workspace = Path(self._tmp.name) / "workspace"
        (self.workspace / "runtime").mkdir(parents=True)
        make_transcript(self.brain, "conv-abc-123", [
            {"type": "AI_OUTPUT", "content": "je valide", "step_index": 1},
            {"type": "USER_INPUT", "content": "Je valide.", "step_index": 42},
        ])

    def env(self) -> dict:
        return {"TESLA_BRAIN_ROOT": str(self.brain),
                "TESLA_ROOT": str(self.workspace)}

    def test_valid_sovereign_directive_allows(self) -> None:
        decision = run_hook(self.HOOK, self.payload(), self.env())
        self.assertEqual(decision["decision"], "allow")

    def test_replay_of_consumed_directive_is_denied(self) -> None:
        # A-003 : la même directive (step_index) ne peut pas être rejouée.
        first = run_hook(self.HOOK, self.payload(), self.env())
        self.assertEqual(first["decision"], "allow")
        second = run_hook(self.HOOK, self.payload(), self.env())
        self.assertEqual(second["decision"], "deny")
        self.assertIn("Anti-Rejeu", second["reason"])

    def test_invalid_phrase_is_denied(self) -> None:
        make_transcript(self.brain, "conv-abc-123", [
            {"type": "USER_INPUT", "content": "Ça me semble bien.", "step_index": 7}])
        decision = run_hook(self.HOOK, self.payload(), self.env())
        self.assertEqual(decision["decision"], "deny")
        self.assertIn("BYPASS-01", decision["reason"])

    def test_spoofed_type_is_denied(self) -> None:
        # L'IA ne peut pas usurper le canal souverain (type falsifié).
        make_transcript(self.brain, "conv-abc-123", [
            {"type": "AI_OUTPUT", "content": "je valide", "step_index": 9}])
        decision = run_hook(self.HOOK, self.payload(), self.env())
        self.assertEqual(decision["decision"], "deny")

    def test_missing_transcript_is_denied(self) -> None:
        decision = run_hook(self.HOOK, {
            "conversationId": "conv-missing",
            "toolCall": {"name": "invoke_subagent", "args": {
                "Subagents": [{"id": "a"}, {"id": "b"}]}}},
            self.env())
        self.assertEqual(decision["decision"], "deny")

    def test_single_agent_invocation_is_allowed_without_scd(self) -> None:
        decision = run_hook(self.HOOK, self.payload(subagents=1), self.env())
        self.assertEqual(decision["decision"], "allow")

    def test_non_subagent_tool_is_ignored(self) -> None:
        decision = run_hook(self.HOOK, {
            "conversationId": "conv-abc-123",
            "toolCall": {"name": "run_command",
                         "args": {"command": "ls"}}}, self.env())
        self.assertEqual(decision["decision"], "allow")


# --------------------------------------------------------------------------- #
# PHASE 3 — Pre-Flight Checklist Gate 0                                        #
# --------------------------------------------------------------------------- #
class Hook10PreflightTests(unittest.TestCase):
    HOOK = HOOKS_DIR / "hook_10_gate0_preflight.sh"

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.workspace = Path(self._tmp.name) / "workspace"
        self.workspace.mkdir()
        write_capability_probe(self.workspace)

    def env(self, **extra: str) -> dict:
        base = {"TESLA_ROOT": str(self.workspace)}
        base.update(extra)
        return base

    def invoke_payload(self) -> dict:
        return {"conversationId": "conv-1",
                "toolCall": {"name": "invoke_subagent", "args": {
                    "Subagents": [{"id": "a"}, {"id": "b"}, {"id": "c"}]}}}

    def test_invoke_allowed_when_privileges_verified(self) -> None:
        decision = run_hook(self.HOOK, self.invoke_payload(), self.env())
        self.assertEqual(decision["decision"], "allow")

    def test_invoke_blocked_without_capability_probe(self) -> None:
        # P3 : probe absente => UNKNOWN => BLOCKED (jamais un PASS implicite).
        (self.workspace / "runtime" / "capability_health.json").unlink()
        decision = run_hook(self.HOOK, self.invoke_payload(), self.env())
        self.assertEqual(decision["decision"], "deny")
        self.assertIn("Exit 66", decision["reason"])
        self.assertIn("P3", decision["reason"])

    def test_invoke_blocked_when_capability_degraded(self) -> None:
        write_capability_probe(self.workspace, {"python3": "PASS",
                                                "bash": "PASS",
                                                "git": "UNKNOWN-CONFINED"})
        decision = run_hook(self.HOOK, self.invoke_payload(), self.env())
        self.assertEqual(decision["decision"], "deny")
        self.assertIn("P3", decision["reason"])

    def test_invoke_blocked_when_runtime_not_writable(self) -> None:
        (self.workspace / "runtime").chmod(0o555)
        self.addCleanup(lambda: (self.workspace / "runtime").chmod(0o755))
        decision = run_hook(self.HOOK, self.invoke_payload(), self.env())
        self.assertEqual(decision["decision"], "deny")

    def test_transcript_observability_checked_when_brain_configured(self) -> None:
        decision = run_hook(self.HOOK, self.invoke_payload(),
                            self.env(TESLA_BRAIN_ROOT=str(self.workspace / "brain")))
        self.assertEqual(decision["decision"], "deny")
        self.assertIn("transcript", decision["reason"])

    def test_escalation_command_denied_by_default(self) -> None:
        decision = run_hook(self.HOOK, {
            "conversationId": "conv-1",
            "toolCall": {"name": "run_command",
                         "args": {"command": "sudo rm -rf /tmp/x"}}},
            self.env())
        self.assertEqual(decision["decision"], "deny")
        self.assertIn("Exit 81", decision["reason"])

    def test_escalation_allowed_only_with_sovereign_terminal_flag(self) -> None:
        decision = run_hook(self.HOOK, {
            "conversationId": "conv-1",
            "toolCall": {"name": "run_command",
                         "args": {"command": "sudo apt-get update"}}},
            self.env(TESLA_ALLOW_PRIVILEGE_ESCALATION="1"))
        self.assertEqual(decision["decision"], "allow")

    def test_git_mutation_preflight_for_jurisdiction_holder(self) -> None:
        payload = {"conversationId": "conv-1",
                   "toolCall": {"name": "run_command", "args": {
                       "command": "git push origin main",
                       "agent_id": "tesla-github-manager"}}}
        decision = run_hook(self.HOOK, payload, self.env())
        self.assertEqual(decision["decision"], "allow")
        # Sans sonde de capacités : pré-vol bloqué (P3).
        (self.workspace / "runtime" / "capability_health.json").unlink()
        decision = run_hook(self.HOOK, payload, self.env())
        self.assertEqual(decision["decision"], "deny")

    def test_non_sensitive_tools_are_ignored(self) -> None:
        decision = run_hook(self.HOOK, {
            "conversationId": "conv-1",
            "toolCall": {"name": "write_file",
                         "args": {"path": "src/x.py", "command": "ls"}}},
            self.env())
        self.assertEqual(decision["decision"], "allow")


# --------------------------------------------------------------------------- #
# PHASE 4 — Attestations SLSA (pivot CI/CD)                                    #
# --------------------------------------------------------------------------- #
class SLSAAttestationTests(unittest.TestCase):
    TOOL = ROOT / "bin" / "slsa_attestation.py"
    KEY = "control-plane-secret-key-for-tests-0123456789"

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.workspace = Path(self._tmp.name) / "workspace"
        (self.workspace / "artifacts").mkdir(parents=True)
        self.artifact = self.workspace / "artifacts" / "deliverable.json"
        self.artifact.write_text('{"result": "PASS", "tests": 141}\n',
                                 encoding="utf-8")

    def run_tool(self, *args: str, env_extra: dict | None = None) -> tuple[int, str]:
        env = os.environ.copy()
        env.pop("TESLA_CONTROL_PLANE_KEY", None)
        if env_extra:
            env.update(env_extra)
        proc = subprocess.run(
            [sys.executable, str(self.TOOL), *args],
            capture_output=True, text=True, timeout=60, env=env, check=False)
        return proc.returncode, (proc.stdout + proc.stderr).strip()

    def generate(self, sign: bool = True) -> Path:
        out = self.workspace / "attestation.json"
        args = ["generate", "--root", str(self.workspace),
                "--mission", "SGC-EXEC-GOV-03-V251",
                "--subject", str(self.artifact),
                "--gate2-evidence",
                '{"scd": "transcript-unavailable-ci", "mode": "slsa"}',
                "--out", str(out)]
        if sign:
            args.append("--sign")
        code, out_log = self.run_tool(
            *args, env_extra={"TESLA_CONTROL_PLANE_KEY": self.KEY})
        self.assertEqual(code, 0, out_log)
        return out

    def test_generate_and_verify_roundtrip(self) -> None:
        attestation = self.generate()
        code, output = self.run_tool(
            "verify", "--attestation", str(attestation),
            "--root", str(self.workspace),
            "--subject", str(self.artifact),
            env_extra={"TESLA_CONTROL_PLANE_KEY": self.KEY})
        self.assertEqual(code, 0, output)
        verdict = json.loads(output.splitlines()[-1])
        self.assertEqual(verdict["verdict"], "PASS")
        self.assertEqual(verdict["mission_id"], "SGC-EXEC-GOV-03-V251")

    def test_statement_structure_is_intoto_slsa(self) -> None:
        attestation = self.generate()
        envelope = json.loads(attestation.read_text(encoding="utf-8"))
        self.assertEqual(envelope["payloadType"],
                         "application/vnd.in-toto+json")
        import base64
        payload = base64.urlsafe_b64decode(
            envelope["payload"] + "=" * (-len(envelope["payload"]) % 4))
        statement = json.loads(payload)
        self.assertEqual(statement["_type"],
                         "https://in-toto.io/Statement/v0.1")
        self.assertEqual(statement["predicateType"],
                         "https://slsa.dev/provenance/v0.2")
        self.assertEqual(statement["subject"][0]["name"],
                         "artifacts/deliverable.json")
        self.assertEqual(statement["predicate"]["vigilum"]["mission_id"],
                         "SGC-EXEC-GOV-03-V251")

    def test_tampered_subject_fails_closed(self) -> None:
        attestation = self.generate()
        self.artifact.write_text('{"result": "TAMPERED"}\n', encoding="utf-8")
        code, output = self.run_tool(
            "verify", "--attestation", str(attestation),
            "--root", str(self.workspace),
            "--subject", str(self.artifact),
            env_extra={"TESLA_CONTROL_PLANE_KEY": self.KEY})
        self.assertEqual(code, 1)
        self.assertIn("EMPREINTE_DIVERGENTE", output)

    def test_tampered_envelope_fails_closed(self) -> None:
        attestation = self.generate()
        envelope = json.loads(attestation.read_text(encoding="utf-8"))
        import base64
        payload = base64.urlsafe_b64decode(
            envelope["payload"] + "=" * (-len(envelope["payload"]) % 4))
        statement = json.loads(payload)
        statement["predicate"]["builder"]["id"] = "https://evil.example/builder"
        forged = json.dumps(statement, sort_keys=True,
                            separators=(",", ":"), ensure_ascii=False)
        envelope["payload"] = base64.urlsafe_b64encode(
            forged.encode()).decode().rstrip("=")
        attestation.write_text(json.dumps(envelope), encoding="utf-8")
        code, output = self.run_tool(
            "verify", "--attestation", str(attestation),
            "--root", str(self.workspace),
            env_extra={"TESLA_CONTROL_PLANE_KEY": self.KEY})
        self.assertEqual(code, 1)
        self.assertIn("SIGNATURE_INVALIDE", output)

    def test_verification_without_key_is_unknown_not_pass(self) -> None:
        attestation = self.generate()
        code, output = self.run_tool(
            "verify", "--attestation", str(attestation),
            "--root", str(self.workspace))
        self.assertEqual(code, 66)  # P3 : UNKNOWN != PASS
        self.assertIn("P3", output)

    def test_key_inside_workspace_is_refused(self) -> None:
        key_file = self.workspace / "leaked.key"
        key_file.write_text("must-be-refused", encoding="utf-8")
        code, output = self.run_tool(
            "generate", "--root", str(self.workspace),
            "--mission", "M", "--subject", str(self.artifact),
            "--out", str(self.workspace / "a.json"), "--sign",
            env_extra={"TESLA_CONTROL_PLANE_KEY": ""})
        self.assertIn("CLE_", output)

    def test_unattested_subject_fails(self) -> None:
        attestation = self.generate()
        other = self.workspace / "artifacts" / "other.json"
        other.write_text("{}", encoding="utf-8")
        code, output = self.run_tool(
            "verify", "--attestation", str(attestation),
            "--root", str(self.workspace),
            "--subject", str(other),
            env_extra={"TESLA_CONTROL_PLANE_KEY": self.KEY})
        self.assertEqual(code, 1)
        self.assertIn("SUJET_NON_ATTESTE", output)

    def test_verification_with_key_file_outside_workspace(self) -> None:
        attestation = self.generate()
        key_file = Path(self._tmp.name) / "control-plane.key"  # hors workspace
        key_file.write_text(self.KEY, encoding="utf-8")
        code, output = self.run_tool(
            "verify", "--attestation", str(attestation),
            "--root", str(self.workspace),
            "--key-file", str(key_file))
        self.assertEqual(code, 0, output)


if __name__ == "__main__":
    unittest.main()
