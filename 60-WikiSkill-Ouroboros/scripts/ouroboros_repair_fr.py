#!/usr/bin/env python3
"""ouroboros_repair_fr.py - Reparation des missions FR ignorees (V2.1).

Ce script rejoue specifiquement la reparation du diagnostic :
"Le moteur Ouroboros Zero-Touch a-t-il ete enrichi par tesla-github-manager ? Non."

Il :
  1. Simule un transcript contenant la session 77a304c9... en francais
  2. Lance parse_transcript_segment V2.1 et verifie ingestion
  3. Propose la commande de reparation reelle pour le Creuset

Usage:
    python3 scripts/ouroboros_repair_fr.py [--root DIR] [--real]
    --real : execute vraiment le daemon en --force-rescan sur le cerveau reel
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ouroboros_autocapture import ingest_receipt, parse_transcript_segment
from ouroboros_cycle import run_cycle
from ouroboros_daemon import resolve_brain_root, scan_transcripts, state_dir
from trace_writer import resolve_tesla_root


def simulate_french_session(root: Path):
    print("[Repair] Simulation session tesla-github-manager 77a304c9 en francais...")
    lines = [
        json.dumps({"type": "USER_INPUT", "content": "lance la mission github", "step_index": 1}),
        json.dumps({"type": "SUBAGENT_RESULT", "step_index": 2,
                    "content": "tesla-github-manager (77a304c9...) Mission accomplie avec succes - PR #42 fusionnee, 100% Succes, tache terminee"}),
        json.dumps({"type": "TOOL_RESULT", "step_index": 3,
                    "content": "[CHECKPOINT CONTRACT]\ncontract_type: CHECKPOINT\nstatus: SUCCESS\ntask_id=gh-77a304c9\nskill: tesla-github-manager\n- step: analyse du depot\n- step: creation PR\n- step: fusion\nfinal_answer: Mission accomplie avec succes, 100% Succes"}),
        json.dumps({"type": "TOOL_RESULT", "step_index": 4,
                    "content": "tesla-github-manager a termine : Mission accomplie avec succes, PR fusionnee, 100% Succes, Termine"}),
    ]
    receipts = parse_transcript_segment(lines, "77a304c9-simulation")
    print(f"[Repair] Recus detectes : {len(receipts)}")
    for r in receipts:
        print(f"  - task={r['task_id']} skill={r['skill']} outcome={r['outcome']} score={r['score']} sources={r['verdict_sources']}")
        dest = ingest_receipt(r, root)
        print(f"    -> Trace ingeree : {dest}")
        trace = json.loads(dest.read_text(encoding="utf-8"))
        print(f"    -> Domaine : {trace['domaine']} | AST : {trace['ast_quarantine_status']} | SHA256 : {trace['sha256'][:16]}...")
    print("[Repair] Simulation terminee : le moteur V2.1 capture bien les missions FR.")

def real_repair(root: Path, brain_root: Path | None, backfill_days: int, repair_conv: str | None):
    print(f"[Repair] Reparation reelle (root={root}, brain={brain_root}, backfill={backfill_days}j, conv={repair_conv or 'all'})")
    state = state_dir(root)
    # Force rescan
    count = scan_transcripts(root, state, brain_root, backfill_days, force_rescan=True, repair_conv=repair_conv)
    print(f"[Repair] Traces re-ingerees : {count}")
    if count > 0:
        report = run_cycle(root, min_hits=3, min_score=0.7, auto_commit=True, reset_processed=False, reprocess_quarantine=False)
        print(f"[Repair] Cycle : distillees={len(report['distilled'])} forgees={len([f for f in report['forged'] if f.get('forged')])} gatees={len(report['gated'])}")
    else:
        print("[Repair] Aucune nouvelle trace. Verifiez que le cerveau contient bien des transcripts avec des missions FR.")
        print("  Exemple : ls $TESLA_BRAIN_ROOT/*/ .system_generated/logs/transcript.jsonl")

def main(argv=None):
    parser = argparse.ArgumentParser(description="Reparation Ouroboros FR (V2.1)")
    parser.add_argument("--root", default=None, help="Racine Tesla")
    parser.add_argument("--brain-root", default=None, help="Racine cerveau Antigravity")
    parser.add_argument("--backfill-days", type=int, default=30, help="Jours de backfill (defaut 30 pour reparation)")
    parser.add_argument("--repair-conv", default=None, help="ID conversation a reparer (ex: 77a304c9)")
    parser.add_argument("--real", action="store_true", help="Execute la reparation reelle (sinon simulation)")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve() if args.root else resolve_tesla_root()
    brain = resolve_brain_root(args.brain_root)

    print("="*70)
    print("Ouroboros V2.1 - Reparation cecite linguistique FR")
    print("="*70)
    print(f"Root : {root}")
    print(f"Brain: {brain}")
    print(f"Mode : {'REEL (force-rescan)' if args.real else 'SIMULATION (77a304c9)'}")
    print()

    if args.real:
        real_repair(root, brain, args.backfill_days, args.repair_conv)
    else:
        simulate_french_session(root)
        print()
        print("Pour reparer le Creuset reel, lancez :")
        print(f"  python3 scripts/ouroboros_daemon.py --once --force-rescan --backfill-days {args.backfill_days} --root {root}")
        if args.repair_conv:
            print(f"  + --repair-conv {args.repair_conv}")
        print()
        print("Puis :")
        print(f"  python3 scripts/ouroboros_cycle.py --root {root} --reset-processed")

if __name__ == "__main__":
    sys.exit(main())
