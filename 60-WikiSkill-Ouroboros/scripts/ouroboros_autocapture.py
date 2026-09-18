#!/usr/bin/env python3
"""ouroboros_autocapture.py - Capture automatique des traces (Phase A Zero-Touch).

C'est le chainon manquant qui rend Ouroboros autonome : au lieu d'exiger que
l'Orchestrateur (LLM) se souvienne d'appeler trace_writer.py en fin de mission
(gouvernance par le verbe, interdite par Vigilum P4), la capture est effectuee
par du code deterministe STDLIB-ONLY, sans aucun LLM-as-a-judge.

Entrees :
  1. Recu JSON (--receipt <fichier>) : produit par le hook post-outil
     (hook_11) ou ecrit manuellement. Format documente dans SKILL.md.
  2. Segment de transcript Antigravity : parse_transcript_segment() detecte
     les executions de sous-agents terminees (types TOOL_RESULT/SUBAGENT_*,
     blocs [CHECKPOINT CONTRACT], marqueurs de statut explicites).

Traitements (tous deterministes) :
  - redaction des secrets (secrets_scrubber, obligatoire : schemas.py exige
    secrets_scrubbed=True) ;
  - extraction des blocs de code Python et passage au crible AST
    (ast_quarantine) -> statut SAFE / QUARANTINED / NO_CODE ;
  - score derive de marqueurs EXPLICITES uniquement (SUCCESS=1.0,
    PARTIAL=0.5, FAIL/ERROR=0.0, inconnu=0.0) : jamais d'inference, jamais
    de jugement LLM. Un score 0.0 signifie "preuve de succes absente".
  - construction ExecutionTrace (schemas.py) + ecriture atomique
    (trace_writer, deduplication par SHA-256 du contenu).

CLI :
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
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ast_quarantine import analyze_file as ast_analyze  # noqa: E402
from schemas import ExecutionTrace  # noqa: E402
from secrets_scrubber import scrub_text  # noqa: E402
from trace_writer import resolve_tesla_root, write_trace_bytes  # noqa: E402

# --- Vocabulaire deterministe --------------------------------------------

#: Types d'entrees de transcript consideres comme "resultat de sous-agent".
COMPLETION_TYPES = frozenset({
    "SUBAGENT_RESULT", "SUBAGENT_RESPONSE", "SUBAGENT_DONE",
    "TOOL_RESULT", "AGENT_RESULT", "TASK_RESULT",
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
}

#: Statut explicite -> (outcome, score). Ordre de test significatif.
STATUS_MAP = [
    ("SUCCESS", "success", 1.0),
    ("PARTIAL", "partial", 0.5),
    ("FAILURE", "failure", 0.0),
    ("FAILED", "failure", 0.0),
    ("FAIL", "failure", 0.0),
    ("ERROR", "failure", 0.0),
]

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


# --- Attribution ----------------------------------------------------------

def attribute_skill(text: str) -> str:
    """Retourne le skill d'elite mentionne, ou 'unknown' (deterministe)."""
    lowered = text.lower()
    for skill in KNOWN_SKILLS:
        if skill in lowered:
            return skill
    if "premortem" in lowered:
        return "tesla-premortem"
    return "unknown"


def detect_status(text: str) -> tuple[str, float] | None:
    """Detecte un statut EXPLICITE. Retourne (outcome, score) ou None."""
    upper = text.upper()
    for keyword, outcome, score in STATUS_MAP:
        if re.search(rf"\b{keyword}\b", upper):
            return outcome, score
    return None


def is_completion_entry(entry: dict[str, Any], text: str) -> bool:
    """Decide si une entree de transcript est une fin d'execution."""
    entry_type = str(entry.get("type", ""))
    if entry_type in COMPLETION_TYPES:
        return True
    upper = text.upper()
    if "CHECKPOINT" in upper and ("CONTRACT" in upper or "contract_type" in text):
        return True
    if "invoke_subagent" in text or "subagent" in text.lower():
        if detect_status(text) is not None:
            return True
    return False


# --- Parsing de transcript -------------------------------------------------

def _entry_text(entry: dict[str, Any]) -> str:
    parts = []
    for key in ("content", "text", "output", "result", "message", "report"):
        value = entry.get(key)
        if isinstance(value, str) and value.strip():
            parts.append(value)
    return "\n".join(parts)


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
        step_index = entry.get("step_index", lineno)
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
        description="Capture automatique Ouroboros (receipt/transcript -> trace).")
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
