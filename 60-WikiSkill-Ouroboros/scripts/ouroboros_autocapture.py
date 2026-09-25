#!/usr/bin/env python3
"""ouroboros_autocapture.py - Capture automatique des traces (Phase A Zero-Touch).

V2.1 — FIX CECITE LINGUISTIQUE + ROBUSTESSE + GOUVERNANCE CHECKPOINT

C'est le chainon manquant qui rend Ouroboros autonome : au lieu d'exiger que
l'Orchestrateur (LLM) se souvienne d'appeler trace_writer.py en fin de mission
(gouvernance par le verbe, interdite par Vigilum P4), la capture est effectuee
par du code deterministe STDLIB-ONLY, sans aucun LLM-as-a-judge.

DIAGNOSTIC V2 (corrige ici):
  - Le demon tournait, detectait la session tesla-github-manager (77a304c9...)
    mais loggait: "passe ingestion : 0 trace(s) (inbox=0, scan=0)"
  - Cause racine semantique: STATUS_MAP ne contenait que SUCCESS/PARTIAL/FAILURE
    en anglais strict (\bSUCCESS\b). Les agents francophones disaient
    "Mission accomplie avec succes", "100% Succes", "Termine" -> ignores silencieusement.
  - Pas de [CHECKPOINT CONTRACT] emis (Option B manquante).

CORRECTIONS V2.1 (Option A + B fusionnees + optimisations):
  1. STATUS_MAP multilingue EN+FR avec normalisation sans accents (NFD).
     - SUCCESS: MISSION ACCOMPLIE, SUCCES, REUSSITE, ACCOMPLI, TERMINE, etc.
     - PARTIAL: PARTIEL, INCOMPLET, etc.
     - FAILURE: ECHEC, ERREUR, ECHOUE, etc.
  2. is_completion_entry tolerant:
     - Types contenant RESULT/RESPONSE/DONE/COMPLETED/FINAL
     - Checkpoint Contract EN + FR: [CHECKPOINT CONTRACT], [CONTRAT CHECKPOINT],
       POINT DE CONTROLE, contract_type / type_contrat
     - Si skill d'elite detecte (tesla-github-manager inclus) + texte >80 chars,
       on capture meme sans statut explicite (score 0.0 = unknown, jamais d'inference
       de succes, conforme doctrine).
     - Fallback github/mission/task substantiel
  3. _entry_text elargi: final_answer, answer, response, observation, summary, etc.
  4. Gouvernance: parseur accepte desormais [CHECKPOINT CONTRACT] comme preuve
     primaire, mais ne l'exige plus exclusivement (fail-open capture, fail-closed
     integrity).

Entrees:
  1. Recu JSON (--receipt <fichier>) : produit par le hook post-outil
     (hook_11) ou ecrit manuellement. Format documente dans SKILL.md.
  2. Segment de transcript Antigravity : parse_transcript_segment() detecte
     les executions de sous-agents terminees.

Traitements (tous deterministes):
  - redaction des secrets (secrets_scrubber)
  - extraction des blocs Python et AST quarantine
  - score derive de marqueurs EXPLICITES multilingues uniquement
  - construction ExecutionTrace + ecriture atomique

CLI:
    python3 ouroboros_autocapture.py --receipt <recu.json> [--root <dir>]
    python3 ouroboros_autocapture.py --transcript <t.jsonl> --conversation <id> [--root <dir>]

Code de retour 0 meme si 0 trace produite (ingestion vide != echec).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
import unicodedata
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ast_quarantine import analyze_file as ast_analyze
from schemas import ExecutionTrace
from secrets_scrubber import scrub_text
from trace_writer import resolve_tesla_root, write_trace_bytes

# --- Vocabulaire deterministe --------------------------------------------

#: Types d'entrees de transcript consideres comme "resultat de sous-agent".
COMPLETION_TYPES = frozenset({
    "SUBAGENT_RESULT", "SUBAGENT_RESPONSE", "SUBAGENT_DONE",
    "TOOL_RESULT", "AGENT_RESULT", "TASK_RESULT",
    "SUBAGENT", "TASK_COMPLETED", "MISSION_COMPLETE",
})

#: Agents d'elite connus (attribution deterministe du skill).
KNOWN_SKILLS = (
    "tesla-team-synergy",
    "tesla-arcanis-360",
    "tesla-curator-prime",
    "tesla-web-raider",
    "tesla-master-code",
    "tesla-premortem",
    "tesla-github-manager",
    "tesla-video-director",
    "tesla-code-auditor",
    "tesla-reddit-commander",
    "tesla-writing-skills",
    "tesla-english-tutor",
    "tesla-eye",
    "tesla-wiki-manager",
)

#: Skill -> domaine wiki canonique.
SKILL_DOMAINS = {
    "tesla-team-synergy": "orchestration",
    "tesla-arcanis-360": "research",
    "tesla-curator-prime": "curation",
    "tesla-web-raider": "web-osint",
    "tesla-master-code": "engineering",
    "tesla-premortem": "risk",
    "tesla-github-manager": "github-ops",
    "tesla-video-director": "video",
    "tesla-code-auditor": "audit",
    "tesla-reddit-commander": "social",
    "tesla-writing-skills": "writing",
    "tesla-english-tutor": "language",
    "tesla-eye": "vision",
    "tesla-wiki-manager": "meta",
}

# -------------------------------------------------------------------------
# STATUS MAP V2.1 — Multilingue EN/FR, normalisation sans accents
# Ordre significatif : phrases specifiques d'abord, mots generiques ensuite.
# Tous les keywords sont stockes en clair FR/EN mais compares en forme
# normalisee (sans accents, upper).
# -------------------------------------------------------------------------
STATUS_MAP_RAW = [
    # SUCCESS — FR + EN
    ("MISSION ACCOMPLIE", "success", 1.0),
    ("MISSIONS ACCOMPLIES", "success", 1.0),
    ("MISSION ACCOMPLIE AVEC SUCCES", "success", 1.0),
    ("100% SUCCES", "success", 1.0),
    ("100% SUCCESS", "success", 1.0),
    ("SUCCES TOTAL", "success", 1.0),
    ("SUCCES COMPLET", "success", 1.0),
    ("SUCCES", "success", 1.0),
    ("SUCCESS", "success", 1.0),
    ("REUSSITE", "success", 1.0),
    ("REUSSITES", "success", 1.0),
    ("REUSSI", "success", 1.0),
    ("REUSSIE", "success", 1.0),
    ("ACCOMPLIE", "success", 1.0),
    ("ACCOMPLI", "success", 1.0),
    ("ACHEVEE", "success", 1.0),
    ("ACHEVE", "success", 1.0),
    ("TERMINEE", "success", 1.0),
    ("TERMINE", "success", 1.0),
    ("COMPLETEE", "success", 1.0),
    ("COMPLETE", "success", 1.0),
    ("COMPLETED", "success", 1.0),
    ("VALIDEE", "success", 1.0),
    ("VALIDE", "success", 1.0),
    ("DONE", "success", 1.0),
    ("OK", "success", 1.0),
    # PARTIAL — FR + EN
    ("PARTIELLEMENT REUSSI", "partial", 0.5),
    ("PARTIELLEMENT", "partial", 0.5),
    ("PARTIELLE", "partial", 0.5),
    ("PARTIEL", "partial", 0.5),
    ("PARTIAL", "partial", 0.5),
    ("INCOMPLETE", "partial", 0.5),
    ("INCOMPLET", "partial", 0.5),
    ("DELIVERABLE ONLY", "partial", 0.5),
    ("DELIVERABLE-ONLY", "partial", 0.5),
    ("LIVRABLE PARTIEL", "partial", 0.5),
    # FAILURE — FR + EN
    ("ECHEC CRITIQUE", "failure", 0.0),
    ("ECHEC TOTAL", "failure", 0.0),
    ("ECHEC", "failure", 0.0),
    ("ECHOUEE", "failure", 0.0),
    ("ECHOUE", "failure", 0.0),
    ("ECHOUER", "failure", 0.0),
    ("ERREURS", "failure", 0.0),
    ("ERREUR", "failure", 0.0),
    ("FAILURE", "failure", 0.0),
    ("FAILED", "failure", 0.0),
    ("FAIL", "failure", 0.0),
    ("ERROR", "failure", 0.0),
    ("RATEE", "failure", 0.0),
    ("RATE", "failure", 0.0),
]

# Alias pour compatibilite historique (tests, hook)
STATUS_MAP = STATUS_MAP_RAW

def _strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")

def _normalize_for_match(s: str) -> str:
    return _strip_accents(s).upper()

# Pre-calcule version normalisee sans doublons, en preservant l'ordre
_NORMALIZED_STATUS_MAP: list[tuple[str, str, float]] = []
_seen_norm = set()
for _kw, _out, _sc in STATUS_MAP_RAW:
    _norm_kw = _normalize_for_match(_kw)
    if _norm_kw not in _seen_norm:
        _seen_norm.add(_norm_kw)
        _NORMALIZED_STATUS_MAP.append((_norm_kw, _out, _sc))

OUTCOME_SCORES = {
    "success": 1.0,
    "partial": 0.5,
    "failure": 0.0,
    "deliverable-only": 0.5,
    "unknown": 0.0,
}

MAX_EXCERPT = 2000
MAX_FINAL_ANSWER = 8000

_TASK_ID_RE = re.compile(r"task_id\s*[:=]\s*['\"]?([A-Za-z0-9][A-Za-z0-9_.-]*)", re.IGNORECASE)
_STATUS_RE = re.compile(r"['\"]?status['\"]?\s*[:=]\s*['\"]?([A-Z_]+)['\"]?")
_STEP_RE = re.compile(r"-\s*step:\s*(.+)", re.IGNORECASE)
_CODEBLOCK_RE = re.compile(r"```python\s*(.*?)\s*```", re.DOTALL | re.IGNORECASE)

# Patterns checkpoint multilingues
_CHECKPOINT_PATTERNS = [
    re.compile(r"\[?\s*CHECKPOINT\s*CONTRACT\s*\]?", re.IGNORECASE),
    re.compile(r"\[?\s*CONTRAT\s*CHECKPOINT\s*\]?", re.IGNORECASE),
    re.compile(r"\[?\s*CONTRAT\s*DE\s*CHECKPOINT\s*\]?", re.IGNORECASE),
    re.compile(r"POINT\s+DE\s+CONTROLE", re.IGNORECASE),
    re.compile(r"CHECKPOINT", re.IGNORECASE),
]
_CONTRACT_KEYWORDS = re.compile(r"contract_type|type_contrat|CHECKPOINT|CONTRAT", re.IGNORECASE)


# --- Attribution ----------------------------------------------------------

def attribute_skill(text: str) -> str:
    """Retourne le skill d'elite mentionne, ou 'unknown' (deterministe, tolerant accents)."""
    if not text:
        return "unknown"
    lowered = text.lower()
    norm_lower = _strip_accents(lowered)
    for skill in KNOWN_SKILLS:
        if skill in lowered or skill in norm_lower:
            return skill
    # Heuristiques supplementaires
    if "premortem" in lowered or "premortem" in norm_lower:
        return "tesla-premortem"
    if "github" in lowered and "manager" in lowered:
        return "tesla-github-manager"
    if "github-manager" in lowered or "github_manager" in lowered:
        return "tesla-github-manager"
    if "web-raider" in lowered or "web_raider" in lowered:
        return "tesla-web-raider"
    if "master-code" in lowered or "master_code" in lowered:
        return "tesla-master-code"
    return "unknown"


def detect_status(text: str) -> tuple[str, float] | None:
    """Detecte un statut EXPLICITE multilingue (EN+FR, sans accents)."""
    if not text:
        return None
    norm = _normalize_for_match(text)
    # Priorite aux phrases longues deja triees
    for keyword_norm, outcome, score in _NORMALIZED_STATUS_MAP:
        if " " in keyword_norm:
            if keyword_norm in norm:
                # Pour KO et OK, on evite les faux positifs trop courts si seuls
                if keyword_norm in ("OK", "KO") and len(norm) > 500:
                    # Si texte tres long, OK/KO seul est trop faible -> on continue
                    # sauf si marqueur explicite avec ponctuation
                    if not re.search(rf"(?:^|[\s:\[\(]){re.escape(keyword_norm)}(?:[\s:\]\)!.,]|$)", norm):
                        continue
                return outcome, score
        else:
            # Mot isole avec word boundary
            if len(keyword_norm) <= 2:  # OK, KO : exige boundary stricte et contexte court
                if re.search(rf"\b{re.escape(keyword_norm)}\b", norm):
                    # Heuristique : OK/KO doit apparaitre pres d'un indicateur de fin ou en debut
                    # Pour eviter le bruit, on exige que le texte soit <2000 chars ou contienne mission/success
                    if keyword_norm == "OK":
                        if len(norm) < 2000 or any(w in norm for w in ("MISSION", "TACHE", "TASK", "SUCCES", "SUCCESS")):
                            return outcome, score
                    else:
                        return outcome, score
            else:
                if re.search(rf"\b{re.escape(keyword_norm)}\b", norm):
                    return outcome, score
    return None


def is_completion_entry(entry: dict[str, Any], text: str) -> bool:
    """Decide si une entree de transcript est une fin d'execution.

    V2.1 — Beaucoup plus tolerant pour corriger le silent drop francophone:
    - Types canoniques + tout type contenant RESULT/RESPONSE/DONE/COMPLETED/FINAL/OUTPUT
    - Checkpoint Contract EN/FR + POINT DE CONTROLE
    - Skill connu + texte substantiel => capture (unknown score si pas de statut)
    - Mentions github/mission/task longues => capture defensive
    """
    entry_type = str(entry.get("type", "") or "")
    entry_type_up = entry_type.upper()

    if entry_type in COMPLETION_TYPES:
        return True
    if any(tok in entry_type_up for tok in ("RESULT", "RESPONSE", "DONE", "COMPLETED", "FINAL", "OUTPUT", "TASK_RESULT", "MISSION")):
        return True

    if not text or len(text.strip()) < 10:
        return False

    upper = text.upper()
    norm = _normalize_for_match(text)

    # Checkpoint governance (Option B) — EN + FR
    for pat in _CHECKPOINT_PATTERNS:
        if pat.search(text):
            return True
    if _CONTRACT_KEYWORDS.search(text):
        # Si contract_type present avec checkpoint ou status
        if "CHECKPOINT" in upper or "CONTRAT" in upper or "CONTRACT" in upper:
            return True

    # Skill connu => capture si texte substantiel ou statut present
    skill = attribute_skill(
        text + " " + str(entry.get("agent", "")) + " " +
        str(entry.get("agentName", "")) + " " + str(entry.get("skill", ""))
    )
    if skill != "unknown":
        if len(text.strip()) >= 80:
            return True
        if detect_status(text) is not None:
            return True

    lowered = text.lower()
    # Subagent ou tesla- mention + statut ou longueur
    if "invoke_subagent" in text or "subagent" in lowered or "tesla-" in lowered:
        if detect_status(text) is not None:
            return True
        if len(text.strip()) >= 120 and any(w in lowered for w in ("mission", "tache", "task", "github", "pull request", "pr ", "commit", "push", "succes", "success", "accomplie", "termine")):
            return True

    # Dernier filet : si texte contient a la fois une reference de tache et un marqueur de fin FR/EN
    if len(text.strip()) >= 100:
        has_task_hint = any(w in lowered for w in ("task_id", "mission", "tache", "objectif", "livrable"))
        has_end_hint = detect_status(text) is not None
        if has_task_hint and has_end_hint:
            return True

    return False


# --- Parsing de transcript -------------------------------------------------

def _entry_text(entry: dict[str, Any]) -> str:
    """Extrait le texte utile d'une entree transcript (tolerant, multilingue)."""
    parts: list[str] = []
    primary_keys = (
        "content", "text", "output", "result", "message", "report",
        "final_answer", "finalAnswer", "final", "answer", "response",
        "observation", "summary", "body", "description", "conclusion",
        "mission", "resultat", "reponse", "output_text", "result_text"
    )
    for key in primary_keys:
        value = entry.get(key)
        if isinstance(value, str) and value.strip():
            parts.append(value)
        elif isinstance(value, dict):
            for subk in primary_keys:
                sv = value.get(subk)
                if isinstance(sv, str) and sv.strip():
                    parts.append(sv)
                    break
        elif isinstance(value, list):
            # Liste de blocs (ex: content blocks)
            for item in value:
                if isinstance(item, str) and item.strip():
                    parts.append(item)
                elif isinstance(item, dict):
                    for subk in primary_keys:
                        sv = item.get(subk)
                        if isinstance(sv, str) and sv.strip():
                            parts.append(sv)
                            break

    if not parts:
        # Fallback : toutes les valeurs string substantielles
        for k, v in entry.items():
            if isinstance(v, str) and len(v.strip()) >= 30:
                if k.lower() in ("id", "conversationid", "type", "timestamp"):
                    continue
                parts.append(v)
    # Deduplicate tout en preservant l'ordre, borne
    seen = set()
    uniq_parts = []
    for p in parts:
        h = hash(p[:200])
        if h not in seen:
            seen.add(h)
            uniq_parts.append(p)
    return "\n".join(uniq_parts)


def parse_transcript_segment(
    lines: list[str],
    conversation_id: str,
    base_lineno: int = 0,
) -> list[dict[str, Any]]:
    """Convertit des lignes JSONL en recus (0..n). Fonction pure."""
    receipts: list[dict[str, Any]] = []
    for offset, raw in enumerate(lines):
        lineno = base_lineno + offset
        line = raw.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(entry, dict):
            continue
        text = _entry_text(entry)
        if not text or not is_completion_entry(entry, text):
            continue

        detected = detect_status(text)
        outcome = detected[0] if detected else "unknown"
        score = detected[1] if detected else 0.0
        step_index = entry.get("step_index", entry.get("stepIndex", lineno))
        task_match = _TASK_ID_RE.search(text)
        task_id = task_match.group(1) if task_match else f"{conversation_id}#{step_index}"
        skill = attribute_skill(
            text + " " + str(entry.get("agent", "")) + " "
            + str(entry.get("agentName", "")) + " " + str(entry.get("skill", "")))

        steps: list[dict[str, Any]] = []
        for idx, found in enumerate(_STEP_RE.findall(text)):
            steps.append({"index": idx, "type": "checkpoint-evidence",
                          "summary": found.strip()[:500]})
        steps.append({"index": len(steps),
                      "type": str(entry.get("type", "transcript")),
                      "summary": text[:MAX_EXCERPT]})

        verdict_sources = [f"transcript:{conversation_id}:{step_index}"]
        if detected:
            verdict_sources.append(f"marker:{outcome.upper()}")
            # Pour audit : on garde aussi le keyword normalise detecte
            norm = _normalize_for_match(text)
            for kw_norm, out, _sc in _NORMALIZED_STATUS_MAP:
                if out == outcome and kw_norm in norm:
                    verdict_sources.append(f"kw:{kw_norm}")
                    break
        verdict_sources.append(f"agent:{skill}")

        receipts.append({
            "skill": skill,
            "task_id": task_id,
            "model": str(entry.get("model", "antigravity-cli")),
            "outcome": outcome,
            "score": score,
            "verdict_sources": verdict_sources,
            "steps": steps,
            "final_answer": text[:MAX_FINAL_ANSWER],
        })
    return _merge_receipts(receipts)


def _merge_receipts(receipts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Fusionne les recus partageant le meme task_id (checkpoint + resultat)."""
    grouped: dict[str, dict[str, Any]] = {}
    order: list[str] = []
    for receipt in receipts:
        key = receipt["task_id"]
        if key not in grouped:
            grouped[key] = receipt
            order.append(key)
            continue
        base = grouped[key]
        # Le meilleur outcome documente gagne (success > partial > failure > unknown).
        rank = {"success": 3, "partial": 2, "failure": 1, "unknown": 0,
                "deliverable-only": 2}
        if rank.get(receipt["outcome"], 0) > rank.get(base["outcome"], 0):
            base["outcome"] = receipt["outcome"]
            base["score"] = receipt["score"]
        base["steps"].extend(receipt["steps"])
        for src in receipt["verdict_sources"]:
            if src not in base["verdict_sources"]:
                base["verdict_sources"].append(src)
        if len(receipt["final_answer"]) > len(base["final_answer"]):
            base["final_answer"] = receipt["final_answer"]
        if base["skill"] == "unknown" and receipt["skill"] != "unknown":
            base["skill"] = receipt["skill"]
    return [grouped[key] for key in order]


# --- Construction de trace -------------------------------------------------

def _quarantine_status(texts: list[str]) -> str:
    """Passe les blocs Python extraits au crible AST. Deterministe."""
    blocks = []
    for text in texts:
        blocks.extend(_CODEBLOCK_RE.findall(text))
    if not blocks:
        return "NO_CODE"
    combined = "\n\n".join(blocks)
    tmp = None
    try:
        with tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", prefix="ouroboros_ast_",
                delete=False, encoding="utf-8") as fh:
            fh.write(combined)
            tmp = fh.name
        # analyze_file imprime sur stdout/stderr ; on neutralise pour le daemon.
        import contextlib
        import io
        with contextlib.redirect_stdout(io.StringIO()), \
                contextlib.redirect_stderr(io.StringIO()):
            code = ast_analyze(tmp)
        return "SAFE" if code == 0 else "QUARANTINED"
    finally:
        if tmp and os.path.exists(tmp):
            os.remove(tmp)


def build_trace(receipt: dict[str, Any]) -> ExecutionTrace:
    """Construit une ExecutionTrace valide depuis un recu (scrub inclus)."""
    skill = str(receipt.get("skill", "unknown") or "unknown")
    if skill == "unknown":
        # Repli deterministe : attribution par mention explicite d'agent.
        haystacks = [str(receipt.get("final_answer", ""))]
        for step in receipt.get("steps", []):
            if isinstance(step, dict):
                haystacks.append(str(step.get("summary", "")))
        skill = attribute_skill(" ".join(haystacks))
    domaine = str(receipt.get("domaine")
                   or SKILL_DOMAINS.get(skill, "general"))
    task_id = str(receipt.get("task_id", "untracked") or "untracked")
    model = str(receipt.get("model", "antigravity-cli") or "antigravity-cli")
    outcome = str(receipt.get("outcome", "unknown") or "unknown")
    if outcome not in OUTCOME_SCORES:
        outcome = "unknown"

    raw_score = receipt.get("score")
    if isinstance(raw_score, (int, float)) and 0.0 <= raw_score <= 1.0:
        score = float(raw_score)
    else:
        score = OUTCOME_SCORES[outcome]

    verdict_sources = [str(s) for s in receipt.get("verdict_sources", [])]
    if not verdict_sources:
        verdict_sources = ["receipt:manual"]

    scrubbed_steps: list[dict[str, Any]] = []
    for idx, step in enumerate(receipt.get("steps", [])):
        if isinstance(step, dict):
            summary = str(step.get("summary", ""))[:MAX_EXCERPT]
            stype = str(step.get("type", "step"))
        else:
            summary = str(step)[:MAX_EXCERPT]
            stype = "step"
        clean, _n = scrub_text(summary)
        scrubbed_steps.append({"index": idx, "type": stype, "summary": clean})
    if not scrubbed_steps:
        scrubbed_steps = [{"index": 0, "type": "receipt",
                           "summary": "aucun detail de pas fourni"}]

    final_answer, _n = scrub_text(str(receipt.get("final_answer", ""))[:MAX_FINAL_ANSWER])

    quarantine = _quarantine_status(
        [final_answer] + [s["summary"] for s in scrubbed_steps])

    fingerprint = f"{skill}|{task_id}|{final_answer[:512]}"
    trace_id = "auto-" + hashlib.sha256(fingerprint.encode("utf-8")).hexdigest()[:16]

    trace = ExecutionTrace(
        trace_id=trace_id,
        skill=skill,
        domaine=domaine,
        task_id=task_id,
        model=model,
        outcome=outcome,
        score=score,
        verdict_sources=verdict_sources,
        ast_quarantine_status=quarantine,
        steps=scrubbed_steps,
        final_answer=final_answer,
        secrets_scrubbed=True,
    )
    trace.validate()
    return trace


def ingest_receipt(receipt: dict[str, Any], root: Path | None = None) -> Path:
    """Construit et ecrit atomiquement la trace d'un recu. Retourne le chemin."""
    trace = build_trace(receipt)
    return write_trace_bytes(trace.to_json().encode("utf-8"), root)


# --- CLI -------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Capture automatique Ouroboros (receipt/transcript -> trace) V2.1 multilingue.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--receipt", help="Chemin vers le recu JSON")
    group.add_argument("--transcript", help="Chemin vers le transcript JSONL")
    parser.add_argument("--conversation", default="cli",
                        help="Identifiant de conversation (mode transcript)")
    parser.add_argument("--root", default=None,
                        help="Racine Tesla (defaut: resolution automatique)")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve() if args.root else resolve_tesla_root()

    if args.receipt:
        try:
            with open(args.receipt, "r", encoding="utf-8") as fh:
                receipt = json.load(fh)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"[Autocapture] Recu illisible : {exc}", file=sys.stderr)
            return 1
        if not isinstance(receipt, dict):
            print("[Autocapture] Le recu doit etre un objet JSON.", file=sys.stderr)
            return 1
        try:
            dest = ingest_receipt(receipt, root)
        except ValueError as exc:
            print(f"[Autocapture] Recu invalide : {exc}", file=sys.stderr)
            return 1
        print(f"[Autocapture] Trace ingeree : {dest}")
        return 0

    try:
        with open(args.transcript, "r", encoding="utf-8") as fh:
            lines = fh.readlines()
    except OSError as exc:
        print(f"[Autocapture] Transcript illisible : {exc}", file=sys.stderr)
        return 1
    receipts = parse_transcript_segment(lines, args.conversation)
    count = 0
    for receipt in receipts:
        try:
            dest = ingest_receipt(receipt, root)
        except ValueError as exc:
            print(f"[Autocapture] Recu ignore (invalide) : {exc}", file=sys.stderr)
            continue
        print(f"[Autocapture] Trace ingeree : {dest}")
        count += 1
    print(f"[Autocapture] {count} trace(s) ingeree(s) depuis {args.transcript}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
