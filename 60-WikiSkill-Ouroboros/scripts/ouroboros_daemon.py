#!/usr/bin/env python3
"""ouroboros_daemon.py - Reconciliateur Zero-Touch (voie garantie) V2.1.

V2.1 FIX CECITE LINGUISTIQUE + OBSERVABILITE + REPARATION

Tandis que le hook post-outil (hook_11) offre une capture immediate au fil de
l'eau (best-effort), ce demon est la voie GARANTIE : il reconcilie
periodiquement TOUTES les executions terminees, y compris celles manquees
(session fermee brutalement, hook non enregistre, ingestion retroactive).

Chaque passe effectue, dans l'ordre :
  1. INBOX  : draine runtime/ouroboros/inbox/*.json (recus du hook) ;
  2. SCAN   : parcourt les transcripts Antigravity
              ($TESLA_BRAIN_ROOT/*/.system_generated/logs/transcript.jsonl)
              depuis les curseurs persistants, detecte les fins d'execution
              (parse_transcript_segment V2.1 multilingue) et les ingere ;
  3. CYCLE  : execute ouroboros_cycle (distille -> forge -> gate -> commit local).

DIAGNOSTIC V2 corrige:
  - Log "passe ingestion : 0 trace(s) (inbox=0, scan=0)" masquait la cause :
    parseur anglais strict + curseur deja avance + aucun metric detaille.
  - V2.1 ajoute :
    * Logs detailles: lignes scannees, recus detectes, repartition par skill/outcome
    * Option --force-rescan pour reparer les sessions FR ignorees (ex: tesla-github-manager 77a304c9)
    * Resolution brain_root elargie (env, TESLA_ROOT, home, /tmp, etc.)
    * Metriques inbox: succes FR/EN, unknown, etc.
    * Gestion curseur robuste: si fichier tronque ou rotation, re-scan depuis 0 avec log

Etat sous <root>/runtime/ouroboros/ (gitignore, hygiene Vigilum E5).
Deploiement canonique : service utilisateur systemd (deploy/ouroboros-capture.service),
conformement a la regle Zero-Touch Background Ops (GEMINI.md R8).

CLI :
    python3 ouroboros_daemon.py [--root DIR] [--interval 60] [--once]
                                [--ingest-only] [--cycle-only]
                                [--backfill-days 7] [--no-commit]
                                [--force-rescan] [--repair-conv ID]
"""
from __future__ import annotations

import argparse
import json
import os
import signal
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ouroboros_autocapture import ingest_receipt, parse_transcript_segment
from ouroboros_cycle import run_cycle, state_dir
from trace_writer import resolve_tesla_root

_STOP = False


def _handle_stop(signum, frame):
    global _STOP
    _STOP = True


def resolve_brain_root(explicit: str | None = None) -> Path | None:
    """Resout la racine des transcripts Antigravity (portable, V2.1 elargi)."""
    candidates: list[Path] = []
    if explicit:
        candidates.append(Path(explicit))
    # Env var prioritaire
    for env_key in ("TESLA_BRAIN_ROOT", "BRAIN_ROOT", "ANTIGRAVITY_BRAIN_ROOT"):
        env = os.environ.get(env_key, "").strip()
        if env:
            candidates.append(Path(env))
    # TESLA_ROOT relatif
    try:
        tesla_root = resolve_tesla_root()
        candidates.append(tesla_root / ".gemini" / "antigravity-cli" / "brain")
        candidates.append(tesla_root / "runtime" / "brain")
        candidates.append(tesla_root / ".brain")
    except Exception:
        pass
    # Homes standards
    candidates.append(Path.home() / ".gemini" / "antigravity-cli" / "brain")
    candidates.append(Path.home() / ".config" / "antigravity" / "brain")
    candidates.append(Path("/home/lord-mahonheim/.gemini/antigravity-cli/brain"))
    candidates.append(Path("/tmp/antigravity-brain"))
    # Deduplicate
    seen = set()
    uniq = []
    for c in candidates:
        rc = str(c)
        if rc not in seen:
            seen.add(rc)
            uniq.append(c)
    for cand in uniq:
        try:
            if cand.is_dir():
                return cand.resolve()
        except OSError:
            continue
    return None


def ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def log(state: Path, message: str) -> None:
    """Journalise sur stdout + fichier rotatif borne (512 Ko x2) + metrics."""
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
    """Ingere les recus deposes par le hook. Retourne le compteur. V2.1 avec metrics."""
    inbox = state / "inbox"
    done = state / "inbox_done"
    quar = state / "inbox_quarantine"
    inbox.mkdir(parents=True, exist_ok=True)
    done.mkdir(exist_ok=True)
    quar.mkdir(exist_ok=True)
    count = 0
    outcomes = Counter()
    skills = Counter()
    for receipt_file in sorted(inbox.glob("*.json")):
        try:
            receipt = json.loads(receipt_file.read_text(encoding="utf-8"))
            if not isinstance(receipt, dict):
                raise ValueError("le recu doit etre un objet JSON")
            dest = ingest_receipt(receipt, root)
            log(state, f"inbox: {receipt_file.name} -> {dest.name} "
                       f"skill={receipt.get('skill','?')} outcome={receipt.get('outcome','?')}")
            receipt_file.replace(done / receipt_file.name)
            count += 1
            outcomes[str(receipt.get("outcome", "unknown"))] += 1
            skills[str(receipt.get("skill", "unknown"))] += 1
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            log(state, f"inbox: {receipt_file.name} REJETE ({exc}) -> quarantaine")
            try:
                receipt_file.replace(quar / receipt_file.name)
            except OSError:
                pass
    if count > 0:
        log(state, f"inbox metrics: total={count} outcomes={dict(outcomes)} skills={dict(skills)}")
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
                     backfill_days: int, force_rescan: bool = False,
                     repair_conv: str | None = None) -> int:
    """Scanne les transcripts depuis les curseurs. Retourne les traces ingerees.

    V2.1 ameliorations:
    - force_rescan=True ignore les curseurs (reparation FR)
    - repair_conv filtre une conversation specifique (ex: 77a304c9)
    - logs detailles: lignes lues, nouvelles lignes, recus detectes, repartition
    - si 0 recus mais lignes presentes, log un echantillon des types pour diagnostic
    """
    cursors = load_cursors(state)
    if brain is None:
        log(state, "scan: aucun cerveau Antigravity resolu (TESLA_BRAIN_ROOT absent) -> passe. "
                   "Verifiez env TESLA_BRAIN_ROOT ou --brain-root. "
                   "Candidats tentes: home/.gemini/antigravity-cli/brain, etc.")
        return 0
    transcripts = sorted(brain.glob("*/.system_generated/logs/transcript.jsonl"))
    # Fallback: cherche aussi directement *.jsonl sous brain
    if not transcripts:
        transcripts = sorted(brain.glob("**/transcript.jsonl"))
    if not transcripts:
        log(state, f"scan: aucun transcript sous {brain} (glob */.system_generated/logs/transcript.jsonl + **/transcript.jsonl)")
        return 0

    now = time.time()
    bound_seconds = max(0, backfill_days) * 86400
    total_ingested = 0
    total_lines_scanned = 0
    total_new_lines = 0
    total_receipts_detected = 0
    outcomes_global = Counter()
    skills_global = Counter()
    convs_scanned = 0

    for transcript in transcripts:
        key = str(transcript)
        try:
            parts = transcript.parts
            conv_id = parts[-4] if len(parts) >= 4 else transcript.parent.parent.name
        except IndexError:
            conv_id = transcript.parent.name

        # Filtrage repair_conv
        if repair_conv and repair_conv not in conv_id and repair_conv not in key:
            continue

        try:
            content = transcript.read_text(encoding="utf-8")
            lines = content.splitlines(keepends=True)
        except OSError as exc:
            log(state, f"scan: {conv_id} illisible ({exc})")
            continue

        total_lines_scanned += len(lines)
        convs_scanned += 1

        cursor = cursors.get(key, {})
        read = int(cursor.get("lines", 0) or 0) if isinstance(cursor, dict) else 0

        if force_rescan:
            if read != 0:
                log(state, f"scan: {conv_id} force-rescan (ancien curseur {read} -> 0)")
            read = 0
        else:
            if len(lines) < read:
                log(state, f"scan: {conv_id} rotation/troncature detectee (len={len(lines)} < curseur={read}) -> reset 0")
                read = 0

        if read == 0 and key not in cursors:
            try:
                age = now - transcript.stat().st_mtime
            except OSError:
                age = 0
            if age > bound_seconds:
                log(state, f"scan: {conv_id} ignore (anterieur a la borne backfill "
                           f"{backfill_days}j, age={age/86400:.1f}j)")
                cursors[key] = {"lines": len(lines)}
                continue
            log(state, f"scan: {conv_id} backfill initial ({len(lines)} lignes)")

        new_lines = lines[read:]
        total_new_lines += len(new_lines)

        if not new_lines:
            cursors[key] = {"lines": len(lines)}
            continue

        # Diagnostic echantillon si besoin
        receipts = parse_transcript_segment(new_lines, conv_id, base_lineno=read)
        total_receipts_detected += len(receipts)

        if not receipts and len(new_lines) > 0:
            # Log detaille pour comprendre pourquoi 0 trace (ancien bug FR)
            sample_types = Counter()
            sample_texts = []
            for raw in new_lines[-20:]:  # 20 dernieres lignes
                try:
                    e = json.loads(raw)
                    if isinstance(e, dict):
                        sample_types[str(e.get("type", "NO_TYPE"))] += 1
                        # Extrait debut texte
                        for k in ("content", "text", "output", "result", "message"):
                            v = e.get(k)
                            if isinstance(v, str) and len(v.strip()) > 20:
                                sample_texts.append(v[:120].replace("\n", " "))
                                break
                except Exception:
                    continue
            log(state, f"scan: {conv_id} {len(new_lines)} nouvelles lignes mais 0 recus detectes. "
                       f"Types echantillon: {dict(sample_types)}. "
                       f"Exemple texte: {sample_texts[:2]}")

        for receipt in receipts:
            try:
                dest = ingest_receipt(receipt, root)
                total_ingested += 1
                outcomes_global[str(receipt.get("outcome", "unknown"))] += 1
                skills_global[str(receipt.get("skill", "unknown"))] += 1
                log(state, f"scan: {conv_id} task={receipt['task_id']} "
                           f"skill={receipt['skill']} outcome={receipt['outcome']} -> {dest.name}")
            except ValueError as exc:
                log(state, f"scan: {conv_id} recu ignore ({exc}) task={receipt.get('task_id','?')}")

        cursors[key] = {"lines": len(lines)}

    save_cursors(state, cursors)

    # Resume global pour observabilite (corrige le log opaque "0 trace(s)")
    if convs_scanned > 0:
        log(state, f"scan resume: convs={convs_scanned} lignes_totales={total_lines_scanned} "
                   f"nouvelles={total_new_lines} recus_detectes={total_receipts_detected} "
                   f"ingestes={total_ingested} outcomes={dict(outcomes_global)} skills={dict(skills_global)} "
                   f"force_rescan={force_rescan} repair_conv={repair_conv or 'all'}")

    return total_ingested


def run_pass(root: Path, brain: Path | None, backfill_days: int,
             do_ingest: bool, do_cycle: bool,
             min_hits: int, min_score: float, auto_commit: bool,
             force_rescan: bool = False, repair_conv: str | None = None) -> dict[str, Any]:
    """Execute une passe complete. Retourne le resume."""
    state = state_dir(root)
    summary: dict[str, Any] = {"at": ts(), "ingested": 0, "cycle": None}
    if do_ingest:
        inbox_n = drain_inbox(root, state)
        scan_n = scan_transcripts(root, state, brain, backfill_days,
                                  force_rescan=force_rescan, repair_conv=repair_conv)
        summary["ingested"] = inbox_n + scan_n
        summary["inbox"] = inbox_n
        summary["scan"] = scan_n
        log(state, f"passe ingestion : {summary['ingested']} trace(s) "
                   f"(inbox={inbox_n}, scan={scan_n}) force_rescan={force_rescan}")
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
    parser = argparse.ArgumentParser(description="Demon reconciliateur Ouroboros V2.1 (multilingue + repair).")
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
    parser.add_argument("--force-rescan", action="store_true",
                        help="Ignore les curseurs et re-scanne tout (reparation FR, ex: tesla-github-manager)")
    parser.add_argument("--repair-conv", default=None,
                        help="Ne re-scanne que les conversations contenant cet ID (ex: 77a304c9)")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve() if args.root else resolve_tesla_root()
    brain = resolve_brain_root(args.brain_root)
    state = state_dir(root)
    signal.signal(signal.SIGTERM, _handle_stop)
    signal.signal(signal.SIGINT, _handle_stop)

    log(state, f"demarrage V2.1 (root={root}, brain={brain}, interval={args.interval}s, "
               f"force_rescan={args.force_rescan}, repair_conv={args.repair_conv})")
    do_ingest = not args.cycle_only
    do_cycle = not args.ingest_only
    first_pass = True
    while True:
        try:
            # force_rescan seulement sur premiere passe si --once, sinon a chaque passe si demande
            fr = args.force_rescan if (first_pass or not args.once) else False
            # Si --once + --force-rescan, on le fait une seule fois puis on l'enleve pour boucle
            run_pass(root, brain, args.backfill_days, do_ingest, do_cycle,
                     args.min_hits, args.min_score,
                     auto_commit=not args.no_commit,
                     force_rescan=fr,
                     repair_conv=args.repair_conv)
            first_pass = False
            # Si force_rescan en mode once, on ne le repete pas
            if args.once and args.force_rescan:
                # Apres une passe force, on pourrait vouloir garder les curseurs a jour
                pass
        except Exception as exc:  # noqa: BLE001 - le demon ne doit jamais mourir
            log(state, f"ERREUR de passe (prochaine tentative dans {args.interval}s): {exc}")
            import traceback
            log(state, f"traceback: {traceback.format_exc()[:1000]}")
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
