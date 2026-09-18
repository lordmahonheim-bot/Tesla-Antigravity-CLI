#!/usr/bin/env python3
"""ouroboros_daemon.py - Reconciliateur Zero-Touch (voie garantie).

Tandis que le hook post-outil (hook_11) offre une capture immediate au fil de
l'eau (best-effort), ce demon est la voie GARANTIE : il reconcilie
periodiquement TOUTES les executions terminees, y compris celles manquees
(session fermee brutalement, hook non enregistre, ingestion retroactive).

Chaque passe effectue, dans l'ordre :
  1. INBOX  : draine runtime/ouroboros/inbox/*.json (recus du hook) ;
  2. SCAN   : parcourt les transcripts Antigravity
              ($TESLA_BRAIN_ROOT/*/.system_generated/logs/transcript.jsonl)
              depuis les curseurs persistants, detecte les fins d'execution
              (parse_transcript_segment) et les ingere ;
  3. CYCLE  : execute ouroboros_cycle (distille -> forge -> gate -> commit local).

Au premier demarrage (curseur absent), les transcripts plus anciens que
--backfill-days sont ignores (borne anti-rejeu massif) ; les autres sont
integralement ingeres => ingestion retroactive automatique ("les 3 missions
de ce matin" sont capturees sans aucune action).

Etat sous <root>/runtime/ouroboros/ (gitignore, hygiene Vigilum E5).
Deploiement canonique : service utilisateur systemd (deploy/ouroboros-capture.service),
conformement a la regle Zero-Touch Background Ops (GEMINI.md R8).

CLI :
    python3 ouroboros_daemon.py [--root DIR] [--interval 60] [--once]
                                [--ingest-only] [--cycle-only]
                                [--backfill-days 7] [--no-commit]
"""
from __future__ import annotations

import argparse
import json
import os
import signal
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ouroboros_autocapture import ingest_receipt, parse_transcript_segment  # noqa: E402
from ouroboros_cycle import run_cycle, state_dir  # noqa: E402
from trace_writer import resolve_tesla_root  # noqa: E402

_STOP = False


def _handle_stop(signum, frame):  # noqa: ARG001
    global _STOP
    _STOP = True


def resolve_brain_root(explicit: str | None = None) -> Path | None:
    """Resout la racine des transcripts Antigravity (portable)."""
    candidates = []
    if explicit:
        candidates.append(Path(explicit))
    env = os.environ.get("TESLA_BRAIN_ROOT", "").strip()
    if env:
        candidates.append(Path(env))
    candidates.append(Path.home() / ".gemini" / "antigravity-cli" / "brain")
    candidates.append(Path("/home/lord-mahonheim/.gemini/antigravity-cli/brain"))
    for cand in candidates:
        if cand.is_dir():
            return cand.resolve()
    return None


def ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def log(state: Path, message: str) -> None:
    """Journalise sur stdout + fichier rotatif borne (512 Ko x2)."""
    line = f"[{ts()}] {message}"
    print(line, flush=True)
    try:
        log_file = state / "daemon.log"
        if log_file.exists() and log_file.stat().st_size > 512 * 1024:
            backup = state / "daemon.log.1"
            if backup.exists():
                backup.unlink()
            log_file.replace(backup)
        with open(log_file, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    except OSError:
        pass


def load_cursors(state: Path) -> dict[str, Any]:
    path = state / "cursors.json"
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def save_cursors(state: Path, cursors: dict[str, Any]) -> None:
    (state / "cursors.json").write_text(
        json.dumps(cursors, indent=2, sort_keys=True), encoding="utf-8")


def drain_inbox(root: Path, state: Path) -> int:
    """Ingere les recus deposes par le hook. Retourne le compteur."""
    inbox = state / "inbox"
    done = state / "inbox_done"
    quar = state / "inbox_quarantine"
    inbox.mkdir(parents=True, exist_ok=True)
    done.mkdir(exist_ok=True)
    quar.mkdir(exist_ok=True)
    count = 0
    for receipt_file in sorted(inbox.glob("*.json")):
        try:
            receipt = json.loads(receipt_file.read_text(encoding="utf-8"))
            if not isinstance(receipt, dict):
                raise ValueError("le recu doit etre un objet JSON")
            dest = ingest_receipt(receipt, root)
            log(state, f"inbox: {receipt_file.name} -> {dest.name}")
            receipt_file.replace(done / receipt_file.name)
            count += 1
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            log(state, f"inbox: {receipt_file.name} REJETE ({exc}) -> quarantaine")
            try:
                receipt_file.replace(quar / receipt_file.name)
            except OSError:
                pass
    # Borne inbox_done aux 100 plus recents (hygiene deterministe).
    done_files = sorted(done.glob("*.json"),
                        key=lambda p: p.stat().st_mtime, reverse=True)
    for stale in done_files[100:]:
        try:
            stale.unlink()
        except OSError:
            pass
    return count


def scan_transcripts(root: Path, state: Path, brain: Path | None,
                     backfill_days: int) -> int:
    """Scanne les transcripts depuis les curseurs. Retourne les traces ingerees."""
    cursors = load_cursors(state)
    if brain is None:
        log(state, "scan: aucun cerveau Antigravity resolu (TESLA_BRAIN_ROOT absent) -> passe")
        return 0
    transcripts = sorted(brain.glob("*/.system_generated/logs/transcript.jsonl"))
    if not transcripts:
        log(state, f"scan: aucun transcript sous {brain}")
        return 0
    now = time.time()
    bound_seconds = max(0, backfill_days) * 86400
    count = 0
    for transcript in transcripts:
        key = str(transcript)
        try:
            parts = transcript.parts
            conv_id = parts[-4]  # <brain>/<conv>/.system_generated/logs/transcript.jsonl
        except IndexError:
            conv_id = transcript.parent.name
        try:
            lines = transcript.read_text(encoding="utf-8").splitlines(keepends=True)
        except OSError as exc:
            log(state, f"scan: {conv_id} illisible ({exc})")
            continue
        cursor = cursors.get(key, {})
        read = int(cursor.get("lines", 0) or 0) if isinstance(cursor, dict) else 0
        if len(lines) < read:
            read = 0  # rotation / troncature : on repart de zero
        if read == 0 and key not in cursors:
            age = now - transcript.stat().st_mtime
            if age > bound_seconds:
                log(state, f"scan: {conv_id} ignore (anterieur a la borne backfill "
                           f"{backfill_days}j)")
                cursors[key] = {"lines": len(lines)}
                continue
            log(state, f"scan: {conv_id} backfill initial ({len(lines)} lignes)")
        new_lines = lines[read:]
        if not new_lines:
            cursors[key] = {"lines": len(lines)}
            continue
        receipts = parse_transcript_segment(new_lines, conv_id, base_lineno=read)
        for receipt in receipts:
            try:
                dest = ingest_receipt(receipt, root)
                count += 1
                log(state, f"scan: {conv_id} task={receipt['task_id']} "
                           f"skill={receipt['skill']} -> {dest.name}")
            except ValueError as exc:
                log(state, f"scan: {conv_id} recu ignore ({exc})")
        cursors[key] = {"lines": len(lines)}
    save_cursors(state, cursors)
    return count


def run_pass(root: Path, brain: Path | None, backfill_days: int,
             do_ingest: bool, do_cycle: bool,
             min_hits: int, min_score: float, auto_commit: bool) -> dict[str, Any]:
    """Execute une passe complete. Retourne le resume."""
    state = state_dir(root)
    summary: dict[str, Any] = {"at": ts(), "ingested": 0, "cycle": None}
    if do_ingest:
        inbox_n = drain_inbox(root, state)
        scan_n = scan_transcripts(root, state, brain, backfill_days)
        summary["ingested"] = inbox_n + scan_n
        log(state, f"passe ingestion : {summary['ingested']} trace(s) "
                   f"(inbox={inbox_n}, scan={scan_n})")
    if do_cycle:
        report = run_cycle(root, min_hits, min_score, auto_commit=auto_commit)
        summary["cycle"] = {
            "distilled": len(report["distilled"]),
            "errors": len(report["errors"]),
            "forged": len([f for f in report["forged"] if f.get("forged")]),
            "gated": [(g["proposal"], g["verdict"]) for g in report["gated"]],
        }
        log(state, f"passe cycle : distillees={summary['cycle']['distilled']} "
                   f"forgees={summary['cycle']['forged']} "
                   f"gates={summary['cycle']['gated']}")
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Demon reconciliateur Ouroboros.")
    parser.add_argument("--root", default=None, help="Racine Tesla")
    parser.add_argument("--brain-root", default=None, help="Racine cerveau Antigravity")
    parser.add_argument("--interval", type=int, default=60,
                        help="Secondes entre deux passes (defaut 60)")
    parser.add_argument("--once", action="store_true", help="Une seule passe puis exit")
    parser.add_argument("--ingest-only", action="store_true", help="Sans phase C/D")
    parser.add_argument("--cycle-only", action="store_true", help="Sans ingestion")
    parser.add_argument("--backfill-days", type=int, default=7)
    parser.add_argument("--min-hits", type=int, default=3)
    parser.add_argument("--min-score", type=float, default=0.7)
    parser.add_argument("--no-commit", action="store_true")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve() if args.root else resolve_tesla_root()
    brain = resolve_brain_root(args.brain_root)
    state = state_dir(root)
    signal.signal(signal.SIGTERM, _handle_stop)
    signal.signal(signal.SIGINT, _handle_stop)

    log(state, f"demarrage (root={root}, brain={brain}, interval={args.interval}s)")
    do_ingest = not args.cycle_only
    do_cycle = not args.ingest_only
    while True:
        try:
            run_pass(root, brain, args.backfill_days, do_ingest, do_cycle,
                     args.min_hits, args.min_score,
                     auto_commit=not args.no_commit)
        except Exception as exc:  # noqa: BLE001 - le demon ne doit jamais mourir
            log(state, f"ERREUR de passe (prochaine tentative dans {args.interval}s): {exc}")
        if args.once or _STOP:
            break
        for _ in range(max(1, args.interval)):
            if _STOP:
                break
            time.sleep(1)
        if _STOP:
            break
    log(state, "arret propre")
    return 0


if __name__ == "__main__":
    sys.exit(main())
