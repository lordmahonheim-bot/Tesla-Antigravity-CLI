#!/usr/bin/env python3
"""Vigilum Codex 2.5.1 — Pre-Flight Checklist Gate 0 (Phase 3 du plan V2.5.0, audité).

Éradication déterministe du réflexe « Shoot-First » (RETEX Session
Orchestrateur, Incident 4) : avant l'exécution d'un OUTIL SENSIBLE, les
privilèges physiques sont vérifiés PROACTIVEMENT. L'audit du plan V2.5.0 a
corrigé la proposition initiale : « injecter une routine dans le Moteur
Cognitif » serait un retour à la gouvernance par le verbe, précisément ce
que le Codex interdit (P4). L'implémentation canonique est donc un
intercepteur déterministe au niveau du runtime (hook), pas un prompt.

Outils sensibles et vérifications (toutes O(1), fail-closed, Exit 66 = P3) :
  invoke_subagent :
    R1. racine de workspace résoluble (TESLA_ROOT > git rev-parse) ;
    R2. répertoire runtime/ inscriptible (verrous d'état) ;
    R3. sonde de capacités présente et PASS sur {python3, bash, git}
        (U-006 : fichier runtime/capability_health.json — absent => UNKNOWN
        => BLOCKED, jamais un PASS implicite) ;
    R4. transcript SCD lisible lorsque le cerveau est configuré
        (TESLA_BRAIN_ROOT) — la preuve Gate 2 doit être physiquement
        observable AVANT le vol, pas après.
  run_command :
    R5. commandes d'élévation de privilèges (sudo, doas, pkexec, su)
        refusées sauf TESLA_ALLOW_PRIVILEGE_ESCALATION=1 posé par le
        Souverain dans le terminal hôte (jamais négociable dans le chat) ;
    R6. mutation Git (via le classifieur hook 08) : pré-vol de privilèges
        pour le titulaire de la juridiction (tesla-github-manager) —
        runtime inscriptible + capacité git PASS.

Sorties : décision JSON Antigravity. Codes sémantiques : 66 (P3 UNKNOWN),
81 (D-007 usurpation). Performances : un processus, zéro réseau, lectures
fichier bornées.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tesla_git_guard import (  # noqa: E402
    GIT_JURISDICTION_AGENT,
    classify_command,
    extract_command,
    resolve_caller,
)

ESCALATION_RE = re.compile(
    r"(^|[\s;&|(])(sudo|doas|pkexec|su)(\s|$)")

REQUIRED_CAPABILITIES = ("python3", "bash", "git")
CAPABILITY_FILE_REL = ("runtime", "capability_health.json")


def _deny(reason: str) -> dict[str, Any]:
    return {"decision": "deny", "reason": reason}


def _allow(reason: str) -> dict[str, Any]:
    return {"decision": "allow", "reason": reason}


def resolve_workspace_root() -> Path | None:
    env_root = os.environ.get("TESLA_ROOT", "").strip()
    if env_root and Path(env_root).is_dir():
        return Path(env_root).resolve()
    try:
        out = subprocess.run(
            ["git", "-C", str(Path(__file__).resolve().parents[3]),
             "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=10, check=False)
        if out.returncode == 0 and out.stdout.strip():
            return Path(out.stdout.strip()).resolve()
    except (OSError, subprocess.SubprocessError):
        pass
    return None


def capability_status(root: Path) -> tuple[dict[str, str], str | None]:
    """Retourne (statuts, erreur). Erreur non None => fail-closed (P3)."""
    probe_file = root.joinpath(*CAPABILITY_FILE_REL)
    if not probe_file.is_file():
        return {}, "CAPABILITY_PROBE_ABSENT (P3: UNKNOWN != PASS — executer bin/probe_capabilities.py)"
    try:
        data = json.loads(probe_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {}, f"CAPABILITY_PROBE_ILLISIBLE:{exc}"
    statuses: dict[str, str] = {}
    capabilities = data.get("capabilities")
    if not isinstance(capabilities, list):
        return {}, "CAPABILITY_PROBE_MALFORME (cle 'capabilities' absente)"
    for entry in capabilities:
        if isinstance(entry, dict) and isinstance(entry.get("capability"), str):
            statuses[entry["capability"]] = str(entry.get("status", "UNKNOWN-CONFINED"))
    missing = [cap for cap in REQUIRED_CAPABILITIES if cap not in statuses]
    if missing:
        return statuses, f"CAPABILITIES_NON_SONDEES:{','.join(missing)}"
    not_pass = [cap for cap in REQUIRED_CAPABILITIES if statuses[cap] != "PASS"]
    if not_pass:
        return statuses, ("CAPABILITIES_DEGRADEES:" + ",".join(
            f"{cap}={statuses[cap]}" for cap in not_pass) + " (P3: UNKNOWN != PASS)")
    return statuses, None


def preflight_invoke_subagent(payload: dict[str, Any]) -> dict[str, Any]:
    root = resolve_workspace_root()
    if root is None:
        return _deny("Exit 66 (P3): racine de workspace non resoluble "
                     "(pre-flight impossible).")
    if not (root / "runtime").is_dir() or not os.access(root / "runtime", os.W_OK):
        return _deny("Exit 66 (P3): repertoire runtime/ non inscriptible "
                     "(verrous d'etat inutilisables).")
    _statuses, error = capability_status(root)
    if error is not None:
        return _deny(f"Exit 66 (P3): {error}")

    # R4 : observabilité de la preuve SCD (Gate 2) AVANT le vol.
    brain_root = os.environ.get("TESLA_BRAIN_ROOT", "").strip()
    conv_id = str(payload.get("conversationId") or "").strip()
    if brain_root:
        if not re.fullmatch(r"[a-zA-Z0-9-]+", conv_id):
            return _deny("Exit 66 (P3): conversationId invalide — preuve "
                         "SCD non observable (anti path-traversal).")
        transcript = (Path(brain_root) / conv_id /
                      ".system_generated" / "logs" / "transcript.jsonl")
        if not transcript.is_file() or not os.access(transcript, os.R_OK):
            return _deny("Exit 66 (P3): transcript SCD non lisible — "
                         "la validation Gate 2 serait inobservable.")
    return _allow("Pre-Flight Checklist Gate 0: privileges physiques "
                  "verifies (runtime, capacites, preuve SCD observable).")


def preflight_run_command(payload: dict[str, Any]) -> dict[str, Any]:
    command = extract_command(payload)
    if command is None:
        return _deny("Exit 66 (P3): commande non extractible (fail-closed).")

    # R5 : élévation de privilèges — refus par défaut.
    if ESCALATION_RE.search(command):
        if os.environ.get("TESLA_ALLOW_PRIVILEGE_ESCALATION", "").strip() != "1":
            return _deny("Exit 81 (D-007): elevation de privileges (sudo/su/"
                         "pkexec/doas) refusee — autorisation souveraine "
                         "requise dans le terminal hote "
                         "(TESLA_ALLOW_PRIVILEGE_ESCALATION=1).")
        return _allow("Elevation autorisee par le terminal souverain.")

    # R6 : pré-vol pour mutation Git (juridiction github-manager uniquement —
    # l'usurpation par d'autres appelants est bloquée par le hook 08).
    classification = classify_command(command)
    if classification["verdict"] in ("MUTATING", "UNPARSEABLE"):
        caller = resolve_caller(payload)
        if caller != GIT_JURISDICTION_AGENT:
            # Redondance défensive : hook 08 est le verrou primaire.
            return _deny("Exit 81 (D-007): mutation Git hors juridiction "
                         f"({caller} != {GIT_JURISDICTION_AGENT}).")
        root = resolve_workspace_root()
        if root is None:
            return _deny("Exit 66 (P3): racine de workspace non resoluble "
                         "avant mutation Git (pre-flight).")
        runtime_dir = root / "runtime"
        if not runtime_dir.is_dir() or not os.access(runtime_dir, os.W_OK):
            return _deny("Exit 66 (P3): runtime non inscriptible avant "
                         "mutation Git (pre-flight).")
        statuses, error = capability_status(root)
        if error is not None:
            return _deny(f"Exit 66 (P3): {error}")
        if statuses.get("git") != "PASS":
            return _deny("Exit 66 (P3): capacite git non PASS avant mutation.")
    return _allow("Pre-Flight Checklist Gate 0: rien a verifier pour cette "
                  "commande.")


def evaluate_hook(payload: dict[str, Any]) -> dict[str, Any]:
    tool_call = payload.get("toolCall") or {}
    tool_name = tool_call.get("name") or payload.get("tool_name") or ""
    if tool_name == "invoke_subagent":
        return preflight_invoke_subagent(payload)
    if tool_name in ("run_command", "bash", "shell", "execute_command",
                     "terminal"):
        return preflight_run_command(payload)
    return _allow("Outil non sensible: pre-flight non requis.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Vigilum Codex 2.5.1 — Pre-Flight Checklist Gate 0")
    parser.add_argument("--mode", choices=("hook",), default="hook")
    args = parser.parse_args(argv)
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(json.dumps({"decision": "deny",
                          "reason": f"Exit 10 (SCHEMA): payload invalide: {exc}"}))
        return 0
    print(json.dumps(evaluate_hook(payload), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
