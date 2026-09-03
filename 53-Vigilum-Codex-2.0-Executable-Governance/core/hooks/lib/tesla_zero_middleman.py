#!/usr/bin/env python3
"""Vigilum Codex 2.5.1 — Verrou Zero-Middleman (Phase 2 du plan V2.5.0, audité).

Éradication déterministe de la faille BYPASS-01 (RETEX Session Orchestrateur,
Incident 1) : l'agent — AUCUN agent, y compris tesla-github-manager — ne peut
créer ou modifier par outil d'écriture un ARTEFACT D'AUTORISATION. Les
seules sources légitimes d'autorisation sont :

  1. La directive souveraine lue dans le transcript système (SCD, hook 07) ;
  2. Les jetons signés émis par les outils déterministes du Control Plane
     (``gate2_guard.py issue-token``, ``marble_certificate.py``) invoqués
     hors du canal d'écriture de l'agent ;
  3. La signature biologique du Lord Mahonheim (hors périmètre agent).

L'auto-écriture d'un fichier ``.flag`` / ``.token`` / quittance / certificat
par l'agent est une USURPATION du Plan de Contrôle (P9 — Souveraineté
Humaine ; P2 — Producer != Validator) : décision DENY, Exit 81
(ERR_AGENT_THEATER, D-007/BYPASS-01).

Périmètre bloqué (motifs déterministes, nom de base + répertoires) :
  - fichiers ``*.flag``, ``*.approval``, ``*.token``, ``verbal_approval*`` ;
  - jeton Gate 2 (``gate2_approval.token``), registres de nonces,
    grand livre des rachats (``redemptions*.jsonl``) ;
  - quittances de sous-agents (``receipt_<agent>.json``) et journaux
    transcripts — preuves runtime D-008, jamais auto-attestables (P-AGENT-001) ;
  - certificats de marbre (``MARBLE_CERTIFICATE_*.json``) et ancre de chaîne
    (``chain_head.sha256``) — produits uniquement par ``marble_certificate.py``.

Fail-closed : un outil d'écriture sans chemin extractible est refusé
(la cible ne pouvant être vérifiée, elle ne peut être autorisée — P10).

Contrat : payload JSON Antigravity sur stdin -> décision JSON sur stdout.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from typing import Any

WRITE_TOOLS_DEFAULT = {"write_file", "edit_file", "apply_patch", "create_file",
                       "save_file", "write", "fs_write", "replace_in_file",
                       "multi_edit", "str_replace_editor"}

PATH_FIELDS = ("path", "file_path", "filename", "target", "target_path",
               "file", "filepath", "destination")

# Motifs de NOM DE BASE interdits (artefacts d'autorisation).
FORBIDDEN_BASENAME_PATTERNS: tuple[re.Pattern[str], ...] = tuple(
    re.compile(pattern) for pattern in (
        r".*\.flag$",
        r".*\.approval$",
        r".*\.token$",
        r"verbal_approval.*",
        r"gate2_approval.*",
        r".*_approval\.json$",
        r"redemptions.*\.(jsonl|json)$",
        r"consumed_step_.*\.lock$",
        r"receipt_[A-Za-z0-9_.-]+\.json$",
        r"MARBLE_CERTIFICATE_.*\.json$",
        r"chain_head\.sha256$",
        r"marble_eligibility\.json$",
    )
)

# Suffixes de RÉPERTOIRES (relatifs ou absolus, par segments) interdits en
# écriture : espaces de preuve et de sécurité du runtime.
FORBIDDEN_DIR_SEGMENTS: tuple[tuple[str, ...], ...] = (
    ("runtime", "gate2"),
    ("runtime", "nonces"),
    ("runtime", "subagents", "receipts"),
    ("runtime", "security"),
    ("CERTIFICATES",),
    (".tesla", "security"),
    (".tesla", "gate2"),
)


def _normalize(path: str) -> str:
    return path.strip().replace("\\", "/")


def _segments(path: str) -> list[str]:
    return [seg for seg in _normalize(path).split("/") if seg not in ("", ".")]


def is_forbidden_path(path: str) -> str | None:
    """Retourne la raison du blocage, ou None si l'écriture est permise."""
    normalized = _normalize(path)
    segments = _segments(normalized)
    if not segments:
        return "CHEMIN_VIDE"
    if ".." in segments:
        return "PATH_TRAVERSAL"
    basename = segments[-1]

    # 1. Racine de preuve runtime isolée (hors workspace agent) — jamais
    #    inscriptible via outils d'agent, quel que soit le préfixe.
    env_root = os.environ.get("TESLA_RUNTIME_EVIDENCE", "").strip()
    if env_root:
        root_segments = _segments(os.path.expanduser(env_root))
        if segments[:len(root_segments)] == root_segments:
            return "ESPACE_PREUVE_RUNTIME_ISOLE"

    # 2. Répertoires de sécurité (par segments de fin).
    depth = len(FORBIDDEN_DIR_SEGMENTS[0])
    for forbidden in FORBIDDEN_DIR_SEGMENTS:
        size = len(forbidden)
        for start in range(len(segments) - 1, -1, -1):
            if tuple(segments[start:start + size]) == forbidden:
                return "REPERTOIRE_SECURITE:" + "/".join(forbidden)

    # 3. Noms de base interdits (artefacts d'autorisation).
    for pattern in FORBIDDEN_BASENAME_PATTERNS:
        if pattern.fullmatch(basename):
            return "ARTEFACT_AUTORISATION:" + basename
    return None


def extract_paths(payload: dict[str, Any]) -> list[str] | None:
    """Extrait les chemins ciblés par l'outil d'écriture (tous champs connus).

    Retourne None si aucun chemin n'est extractible (fail-closed).
    """
    tool_call = payload.get("toolCall") or {}
    args = tool_call.get("args") or {}
    found: list[str] = []
    if isinstance(args, dict):
        for field in PATH_FIELDS:
            value = args.get(field)
            if isinstance(value, str) and value.strip():
                found.append(value)
        # Éditions multiples (multi_edit / apply_patch : liste de corrections).
        edits = args.get("edits") or args.get("patches") or args.get("changes")
        if isinstance(edits, list):
            for edit in edits:
                if isinstance(edit, dict):
                    for field in PATH_FIELDS:
                        if isinstance(edit.get(field), str) and edit[field].strip():
                            found.append(edit[field])
    return found if found else None


def evaluate_hook(payload: dict[str, Any]) -> dict[str, Any]:
    tool_call = payload.get("toolCall") or {}
    tool_name = tool_call.get("name") or payload.get("tool_name") or ""
    tools = {t.strip() for t in
             os.environ.get("TESLA_WRITE_TOOLS", "").split(",") if t.strip()}
    tools = tools or WRITE_TOOLS_DEFAULT
    if tool_name not in tools:
        return {"decision": "allow"}

    # AUCUNE exemption d'agent : les artefacts d'autorisation ne sont jamais
    # négociables par écriture d'agent (P2/P9 — y compris github-manager).
    paths = extract_paths(payload)
    if paths is None:
        return {"decision": "deny",
                "reason": "Exit 81 (BYPASS-01/ZERO-MIDDLEMAN): outil "
                          "d'ecriture sans chemin verifiable (fail-closed)."}

    for path in paths:
        reason = is_forbidden_path(path)
        if reason is not None:
            return {"decision": "deny",
                    "reason": f"Exit 81 (BYPASS-01/ZERO-MIDDLEMAN): ecriture "
                              f"d'artefact d'autorisation interdite ({reason}) "
                              f"— la validation souveraine passe exclusivement "
                              f"par le transcript (SCD, hook 07) ou les "
                              f"outils du Control Plane."}
    return {"decision": "allow"}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Vigilum Codex 2.5.1 — Verrou Zero-Middleman (hook + CLI)")
    parser.add_argument("--mode", choices=("hook", "check"), default="hook")
    parser.add_argument("--path", help="chemin à vérifier (mode check)")
    args = parser.parse_args(argv)

    if args.mode == "check":
        reason = is_forbidden_path(args.path or "")
        print(json.dumps({"path": args.path, "forbidden": reason is not None,
                          "reason": reason}, ensure_ascii=False))
        return 0

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
