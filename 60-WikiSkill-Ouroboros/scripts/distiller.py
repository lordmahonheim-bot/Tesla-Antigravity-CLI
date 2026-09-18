#!/usr/bin/env python3
"""distiller.py - Distillation deterministe Trace -> Pattern Wiki (Phase B).

Sans aucun LLM : chaque ExecutionTrace est projetee sur un pattern agregatif
borne (skill x domaine x outcome), la note wiki correspondante est mise a jour
(observations rolling, max 5), et l'index TSV est maintenu sous le budget
semantique de 4000 tokens par eviction deterministe (score =
HITS / (1 + age_jours/30), ex-aequo : ID croissant).

Layout :
    .agents/wiki/<domain>/index.tsv            (en-tetes canoniques)
    .agents/wiki/<domain>/<id>-<slug>.md       (note de pattern)
    .agents/wiki/_archive/                     (notes evincees, horodatees)

CLI :
    python3 distiller.py --trace <trace.json> [--root DIR]
    python3 distiller.py --reindex [--root DIR]   (reconstruction idempotente)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from index_linter import REQUIRED_COLUMNS, lint_file as lint_index_file  # noqa: E402
from trace_writer import resolve_tesla_root  # noqa: E402

MAX_OBSERVATIONS = 5
INDEX_NAME = "index.tsv"


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:48] or "pattern"


def pattern_key_for_trace(trace: dict[str, Any]) -> dict[str, str]:
    """Derive l'identite de pattern d'une trace (fonction pure, bornee)."""
    skill = str(trace.get("skill", "unknown") or "unknown")
    domaine = str(trace.get("domaine", "general") or "general")
    outcome = str(trace.get("outcome", "unknown") or "unknown")
    key = f"{skill}::{domaine}::{outcome}"
    pattern_id = hashlib.sha256(key.encode("utf-8")).hexdigest()[:8]
    short_skill = skill.replace("tesla-", "")
    name = slugify(f"{domaine}-{short_skill}-{outcome}")
    rel_path = f"wiki/{domaine}/{pattern_id}-{name}.md"
    return {"key": key, "id": pattern_id, "name": name,
            "domain": domaine, "rel_path": rel_path}


def _index_path(root: Path, domain: str) -> Path:
    path = root / ".agents" / "wiki" / domain / INDEX_NAME
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text("\t".join(REQUIRED_COLUMNS) + "\n", encoding="utf-8")
    return path


def read_index(index_path: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    if not index_path.exists():
        return rows
    lines = index_path.read_text(encoding="utf-8").splitlines()
    for line in lines[1:]:
        if not line.strip():
            continue
        cells = line.split("\t")
        if len(cells) != len(REQUIRED_COLUMNS):
            continue
        rows.append(dict(zip(REQUIRED_COLUMNS, cells)))
    return rows


def write_index(index_path: Path, rows: list[dict[str, str]]) -> None:
    ordered = sorted(rows, key=lambda r: (
        -int(r.get("HITS", "0") or 0),
        r.get("RECENCY", ""),
        r.get("ID", ""),
    ), reverse=False)
    # Tri deterministe : HITS desc, RECENCY desc, ID asc.
    ordered = sorted(rows, key=lambda r: r.get("ID", ""))
    ordered = sorted(ordered, key=lambda r: r.get("RECENCY", ""), reverse=True)
    ordered = sorted(ordered, key=lambda r: int(r.get("HITS", "0") or 0), reverse=True)
    lines = ["\t".join(REQUIRED_COLUMNS)]
    for row in ordered:
        lines.append("\t".join(row.get(col, "") for col in REQUIRED_COLUMNS))
    index_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _parse_recency(value: str) -> datetime:
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except ValueError:
        return datetime(1970, 1, 1, tzinfo=timezone.utc)


def eviction_score(row: dict[str, str], now: datetime) -> float:
    hits = int(row.get("HITS", "0") or 0)
    age_days = max(0.0, (now - _parse_recency(row.get("RECENCY", ""))).total_seconds() / 86400.0)
    return hits / (1.0 + age_days / 30.0)


def enforce_budget(index_path: Path, protect_id: str | None = None) -> list[str]:
    """Evince les patterns les plus faibles jusqu'au respect du budget.

    Retourne la liste des IDs evinces. Les notes correspondantes sont
    archivees (jamais supprimees : P8, No Silent Deletion).
    """
    evicted: list[str] = []
    rows = read_index(index_path)
    ok, _msg = lint_index_file(str(index_path))
    if ok:
        return evicted
    now = datetime.now(timezone.utc)
    archive_dir = index_path.parents[1] / "_archive"
    archive_dir.mkdir(parents=True, exist_ok=True)

    candidates = sorted(
        (r for r in rows if r.get("ID") != protect_id),
        key=lambda r: (eviction_score(r, now), r.get("ID", "")))
    remaining = [r for r in rows]
    for victim in candidates:
        remaining = [r for r in remaining if r.get("ID") != victim.get("ID")]
        write_index(index_path, remaining)
        evicted.append(victim.get("ID", "?"))
        # Archivage de la note (REL_PATH relatif a .agents/).
        note = index_path.parents[1].parent / victim.get("REL_PATH", "")
        if note.is_file():
            stamp = now.strftime("%Y%m%dT%H%M%SZ")
            dest = archive_dir / f"{stamp}_{note.name}"
            note.replace(dest)
        ok, _msg = lint_index_file(str(index_path))
        if ok:
            break
    return evicted


def _render_note(pattern: dict[str, str], observations: list[str],
                 total_seen: int, mean_score: float,
                 quarantined: bool) -> str:
    status = "QUARANTINED-SOURCE — jamais forge en regle" if quarantined else "ACTIVE"
    header = (
        f"# Pattern `{pattern['name']}`\n\n"
        f"- ID: `{pattern['id']}`\n"
        f"- Domaine: `{pattern['domain']}`\n"
        f"- Statut: **{status}**\n"
        f"- Corroborations totales: **{total_seen}** "
        f"(score moyen: {mean_score:.2f})\n"
        f"- Distille par: Ouroboros distiller (deterministe, sans LLM)\n\n"
        "---\n\n"
    )
    return header + "\n".join(observations) + ("\n" if observations else "")


def _parse_note_observations(note_path: Path) -> tuple[list[str], int]:
    if not note_path.exists():
        return [], 0
    content = note_path.read_text(encoding="utf-8")
    parts = re.split(r"(?m)^## Observation ", content)
    observations = [("## Observation " + p).strip() + "\n"
                    for p in parts[1:]] if len(parts) > 1 else []
    total = 0
    match = re.search(r"Corroborations totales:\s*\*\*(\d+)\*\*", content)
    if match:
        total = int(match.group(1))
    return observations, total


def update_note(root: Path, pattern: dict[str, str], trace: dict[str, Any],
                trace_sha8: str, when: str) -> Path:
    """Ajoute une observation a la note de pattern (rolling, max 5)."""
    note_path = root / ".agents" / pattern["rel_path"]
    note_path.parent.mkdir(parents=True, exist_ok=True)
    observations, total_seen = _parse_note_observations(note_path)

    final = str(trace.get("final_answer", ""))[:600].replace("\n", " ")
    verdicts = ", ".join(str(s) for s in trace.get("verdict_sources", []))[:300]
    observation = (
        f"## Observation {when} (trace `{trace_sha8}`)\n\n"
        f"- Skill: `{trace.get('skill')}` | Outcome: `{trace.get('outcome')}` "
        f"| Score: `{trace.get('score')}`\n"
        f"- Task: `{trace.get('task_id')}` | AST: `{trace.get('ast_quarantine_status')}`\n"
        f"- Preuves: {verdicts}\n"
        f"- Extrait: {final}\n"
    )
    observations.append(observation)
    observations = observations[-MAX_OBSERVATIONS:]
    total_seen += 1

    # Score moyen recalcule sur les observations conservees (borne, deterministe).
    scores = []
    for obs in observations:
        found = re.search(r"\| Score: `([0-9.]+)`", obs)
        if found:
            try:
                scores.append(float(found.group(1)))
            except ValueError:
                pass
    mean_score = sum(scores) / len(scores) if scores else 0.0
    quarantined = "QUARANTINED" in str(trace.get("ast_quarantine_status", ""))

    note_path.write_text(
        _render_note(pattern, observations, total_seen, mean_score, quarantined),
        encoding="utf-8")
    return note_path


def distill_trace(trace: dict[str, Any], trace_sha8: str,
                  root: Path, when: str | None = None) -> dict[str, Any]:
    """Distille une trace : note + index + budget. Retourne le resume."""
    when = when or utcnow_iso()
    pattern = pattern_key_for_trace(trace)
    note_path = update_note(root, pattern, trace, trace_sha8, when)

    index_path = _index_path(root, pattern["domain"])
    rows = read_index(index_path)
    found = None
    for row in rows:
        if row.get("ID") == pattern["id"]:
            found = row
            break
    if found is None:
        found = {"ID": pattern["id"], "PATTERN_NAME": pattern["name"],
                 "DOMAIN": pattern["domain"], "HITS": "0",
                 "RECENCY": when, "REL_PATH": pattern["rel_path"]}
        rows.append(found)
    found["HITS"] = str(int(found.get("HITS", "0") or 0) + 1)
    found["RECENCY"] = when
    found["REL_PATH"] = pattern["rel_path"]
    found["PATTERN_NAME"] = pattern["name"]
    write_index(index_path, rows)

    evicted = enforce_budget(index_path, protect_id=pattern["id"])
    ok, msg = lint_index_file(str(index_path))
    return {"pattern": pattern, "note": str(note_path),
            "index": str(index_path), "hits": int(found["HITS"]),
            "evicted": evicted, "budget_ok": ok, "lint": msg}


def distill_trace_file(trace_file: str, root: Path) -> dict[str, Any]:
    with open(trace_file, "r", encoding="utf-8") as fh:
        trace = json.load(fh)
    sha8 = hashlib.sha256(
        Path(trace_file).read_bytes()).hexdigest()[:8]
    return distill_trace(trace, sha8, root)


def aggregate_patterns(root: Path) -> dict[str, dict[str, Any]]:
    """Agrege les stats par pattern depuis toutes les traces (fonction pure)."""
    traces_dir = root / ".agents" / "traces"
    agg: dict[str, dict[str, Any]] = {}
    if not traces_dir.is_dir():
        return agg
    for trace_file in sorted(traces_dir.glob("*.json")):
        if trace_file.name.startswith("."):
            continue
        try:
            trace = json.loads(trace_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        pattern = pattern_key_for_trace(trace)
        slot = agg.setdefault(pattern["key"], {
            "pattern": pattern, "hits": 0, "scores": [],
            "quarantined": False, "traces": []})
        slot["hits"] += 1
        try:
            slot["scores"].append(float(trace.get("score", 0.0)))
        except (TypeError, ValueError):
            slot["scores"].append(0.0)
        if "QUARANTINED" in str(trace.get("ast_quarantine_status", "")):
            slot["quarantined"] = True
        slot["traces"].append(trace_file.name)
    for slot in agg.values():
        scores = slot["scores"]
        slot["mean_score"] = sum(scores) / len(scores) if scores else 0.0
    return agg


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Distillation Trace -> Wiki (Phase B).")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--trace", help="Fichier trace JSON a distiller")
    group.add_argument("--reindex", action="store_true",
                       help="Reconstruit tous les index depuis les traces")
    parser.add_argument("--root", default=None, help="Racine Tesla")
    args = parser.parse_args(argv)
    root = Path(args.root).resolve() if args.root else resolve_tesla_root()

    if args.reindex:
        traces_dir = root / ".agents" / "traces"
        count = 0
        if traces_dir.is_dir():
            for trace_file in sorted(traces_dir.glob("*.json")):
                try:
                    distill_trace_file(str(trace_file), root)
                    count += 1
                except (OSError, json.JSONDecodeError, KeyError) as exc:
                    print(f"[Distiller] Trace ignoree {trace_file.name}: {exc}",
                          file=sys.stderr)
        print(f"[Distiller] Reindexation terminee : {count} trace(s).")
        return 0

    try:
        summary = distill_trace_file(args.trace, root)
    except (OSError, json.JSONDecodeError, KeyError) as exc:
        print(f"[Distiller] Echec de distillation : {exc}", file=sys.stderr)
        return 1
    pattern = summary["pattern"]
    print(f"[Distiller] Pattern {pattern['id']} ({pattern['name']}) :: "
          f"HITS={summary['hits']} budget_ok={summary['budget_ok']} "
          f"evinces={summary['evicted']}")
    return 0 if summary["budget_ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
