#!/usr/bin/env python3
"""ouroboros_cycle.py - Moteur du cycle complet Trace -> Index -> Patch -> Gate V2.1.

V2.1 FIX + OPTIMISATION + OBSERVABILITE

C'est le "moteur qui tourne" sans l'Orchestrateur : un seul appel execute
deterministiquement les 4 phases Ouroboros sur toutes les traces non traitees :

  Phase A (Capture)  : verifie l'integrite SHA-256 de chaque trace (.agents/traces/) ;
                       corrompue -> quarantine/ (+ journal), saine -> suite.
  Phase B (Distill)  : distiller.distill_trace -> note wiki + index.tsv (budget 4000).
  Phase C (Mutate)   : rule_forger.forge_all_eligible -> proposals/*.intent.patch.
  Phase D (Gate)     : git_committer (sandbox + gating_judge V2) sur chaque
                       proposition ouverte -> PASS : commit LOCAL + accepted/ ;
                       FAIL : verdict sidecar, 3 tentatives max puis quarantine/.

Ameliorations V2.1:
  - Logs detailles par skill/domaine/outcome (inclut github-ops FR)
  - Option --reset-processed pour rejouer toutes les traces (reparation FR)
  - Option --reprocess-quarantine pour tenter de recuperer les traces en quarantaine
  - Metrics de performance (duree par phase)
  - Hygiene: processed.json borne, last_cycle.json enrichi
  - Optimisation: tri stable, evite re-lecture inutile, batch

Etat : <root>/runtime/ouroboros/processed.json + last_cycle.json (runtime/ est
gitignore, hygiene Vigilum E5). JAMAIS de push distant (prerogative souveraine).

CLI :
    python3 ouroboros_cycle.py [--root DIR] [--min-hits 3] [--min-score 0.7]
                               [--no-commit] [--max-attempts 3]
                               [--reset-processed] [--reprocess-quarantine]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from distiller import distill_trace  # noqa: E402
from rule_forger import forge_all_eligible, proposals_dir  # noqa: E402
from schemas import ExecutionTrace  # noqa: E402
from trace_writer import resolve_tesla_root  # noqa: E402

SCRIPTS_DIR = Path(__file__).resolve().parent


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def state_dir(root: Path) -> Path:
    path = root / "runtime" / "ouroboros"
    path.mkdir(parents=True, exist_ok=True)
    return path


def load_processed(root: Path) -> dict[str, Any]:
    path = state_dir(root) / "processed.json"
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def save_processed(root: Path, data: dict[str, Any]) -> None:
    path = state_dir(root) / "processed.json"
    # Hygiene: borne a 5000 entrees max (evite bloat), garde les plus recents
    if len(data) > 5000:
        # Trie par at desc, garde 4000 plus recents
        sorted_items = sorted(data.items(), key=lambda kv: kv[1].get("at", ""), reverse=True)
        data = dict(sorted_items[:4000])
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def verify_trace_file(trace_file: Path) -> tuple[bool, str, dict[str, Any]]:
    """Verifie nom==SHA(contenu) + schema + hash interne. Retourne (ok, motif, trace)."""
    try:
        raw = trace_file.read_bytes()
        trace = json.loads(raw.decode("utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        return False, f"illisible : {exc}", {}
    content_sha = hashlib.sha256(raw).hexdigest()
    if trace_file.stem != content_sha:
        return False, "nom de fichier != SHA-256 du contenu (corruption?)", {}
    try:
        instance = ExecutionTrace(**trace)
        instance.validate()
    except (TypeError, ValueError) as exc:
        return False, f"schema invalide : {exc}", {}
    if trace.get("sha256") and instance.compute_hash() != trace["sha256"]:
        return False, "champ sha256 incoherent (trace falsifiee?)", {}
    return True, "ok", trace


def phase_ab(root: Path, processed: dict[str, Any], reprocess_quarantine: bool = False) -> tuple[list[dict], list[dict]]:
    """Phase A (verification) + B (distillation) des traces non traitees. V2.1 avec metrics."""
    distilled: list[dict] = []
    errors: list[dict] = []
    traces_dir = root / ".agents" / "traces"
    if not traces_dir.is_dir():
        return distilled, errors

    # Option reprocess quarantine: tente de revalider les traces en quarantaine
    if reprocess_quarantine:
        quar_dir = traces_dir / "quarantine"
        if quar_dir.is_dir():
            for q_file in sorted(quar_dir.glob("*.json")):
                try:
                    raw = q_file.read_bytes()
                    trace = json.loads(raw.decode("utf-8"))
                    # Si le fichier a ete corrige (ex: FR maintenant supporte), on le remet
                    # On recalcule son SHA et on le deplace vers traces_dir si valide
                    ok, reason, _ = verify_trace_file(q_file)
                    # verify_trace_file attend que le nom == SHA contenu, mais en quarantaine le nom peut deja etre SHA
                    # Donc on tente aussi de reconstruire via ExecutionTrace
                    if not ok and "nom de fichier" in reason:
                        # Recalcule destination
                        new_sha = hashlib.sha256(raw).hexdigest()
                        dest = traces_dir / f"{new_sha}.json"
                        if not dest.exists():
                            q_file.replace(dest)
                except Exception:
                    continue

    skill_counter = Counter()
    outcome_counter = Counter()
    domain_counter = Counter()

    for trace_file in sorted(traces_dir.glob("*.json")):
        sha = trace_file.stem
        if sha in processed:
            continue
        ok, reason, trace = verify_trace_file(trace_file)
        if not ok:
            quar = traces_dir / "quarantine" / trace_file.name
            quar.parent.mkdir(parents=True, exist_ok=True)
            try:
                trace_file.replace(quar)
            except OSError:
                pass
            errors.append({"trace": trace_file.name, "error": reason,
                           "action": "quarantaine"})
            processed[sha] = {"status": "quarantined", "reason": reason,
                              "at": utcnow_iso()}
            continue
        try:
            summary = distill_trace(trace, sha[:8], root)
        except (OSError, KeyError, ValueError) as exc:
            errors.append({"trace": trace_file.name, "error": str(exc),
                           "action": "retry-later"})
            continue
        processed[sha] = {"status": "distilled",
                          "pattern": summary["pattern"]["id"],
                          "skill": trace.get("skill", "unknown"),
                          "outcome": trace.get("outcome", "unknown"),
                          "at": utcnow_iso()}
        distilled.append({"trace": trace_file.name,
                          "pattern": summary["pattern"]["id"],
                          "skill": trace.get("skill", "unknown"),
                          "domain": summary["pattern"]["domain"],
                          "outcome": trace.get("outcome", "unknown"),
                          "hits": summary["hits"],
                          "budget_ok": summary["budget_ok"]})
        skill_counter[str(trace.get("skill", "unknown"))] += 1
        outcome_counter[str(trace.get("outcome", "unknown"))] += 1
        domain_counter[str(summary["pattern"]["domain"])] += 1

    if distilled:
        print(f"[Cycle AB] Metrics skills={dict(skill_counter)} outcomes={dict(outcome_counter)} domains={dict(domain_counter)}")

    return distilled, errors


def phase_c(root: Path, min_hits: int, min_score: float) -> list[dict]:
    """Phase C (mutation) : forge les regles eligibles."""
    start = time.time()
    result = forge_all_eligible(root, min_hits, min_score)
    elapsed = time.time() - start
    forged = [r for r in result if r.get("forged")]
    print(f"[Cycle C] Forge {len(forged)}/{len(result)} en {elapsed:.2f}s "
          f"(min_hits={min_hits}, min_score={min_score})")
    for f in forged:
        print(f"[Cycle C]   FORGE {f['pattern_key']} -> {f.get('proposal','?')} "
              f"skill={f.get('skill')} HITS justif={f.get('justification','')[:80]}")
    return result


def _read_verdict(proposal: Path) -> dict[str, Any]:
    sidecar = proposal.with_name(proposal.stem + ".verdict.json")
    if sidecar.exists():
        try:
            data = json.loads(sidecar.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}
        except (OSError, json.JSONDecodeError):
            return {}
    return {}


def _write_verdict(proposal: Path, verdict: dict[str, Any]) -> None:
    sidecar = proposal.with_name(proposal.stem + ".verdict.json")
    sidecar.write_text(json.dumps(verdict, indent=2), encoding="utf-8")


def phase_d(root: Path, auto_commit: bool, max_attempts: int) -> list[dict]:
    """Phase D (gating) : evalue chaque proposition ouverte, commit si PASS."""
    gated: list[dict] = []
    pdir = proposals_dir(root)
    open_props = sorted(pdir.glob("*.intent.patch"))
    if not open_props:
        print("[Cycle D] Aucune proposition ouverte")
        return gated

    is_git = (root / ".git").is_dir()
    for proposal in open_props:
        verdict = _read_verdict(proposal)
        attempts = int(verdict.get("attempts", 0) or 0)
        if attempts >= max_attempts:
            quar = pdir / "quarantine" / proposal.name
            quar.parent.mkdir(parents=True, exist_ok=True)
            try:
                proposal.replace(quar)
            except OSError:
                pass
            _write_verdict(quar, {**verdict, "verdict": "EXHAUSTED",
                                  "moved_to": "quarantine", "at": utcnow_iso()})
            gated.append({"proposal": proposal.name, "verdict": "EXHAUSTED"})
            print(f"[Cycle D] {proposal.name} -> EXHAUSTED (quarantaine apres {attempts} tentatives)")
            continue
        if not auto_commit:
            gated.append({"proposal": proposal.name, "verdict": "STAGED",
                          "reason": "--no-commit : gating differe"})
            print(f"[Cycle D] {proposal.name} -> STAGED (--no-commit)")
            continue
        if not is_git:
            gated.append({"proposal": proposal.name, "verdict": "SKIPPED",
                          "reason": "racine non-git : sandbox impossible"})
            print(f"[Cycle D] {proposal.name} -> SKIPPED (non-git)")
            continue

        print(f"[Cycle D] Gating {proposal.name} (tentative {attempts+1}/{max_attempts})...")
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "git_committer.py"), str(proposal),
             "--sandbox-script", str(SCRIPTS_DIR / "sandbox_evaluator.py"),
             "--gating-script", str(SCRIPTS_DIR / "gating_judge.py"),
             "--repo-path", str(root)],
            capture_output=True, text=True)
        attempts += 1
        if result.returncode == 0:
            dest = pdir / "accepted" / proposal.name
            dest.parent.mkdir(parents=True, exist_ok=True)
            if proposal.exists():
                proposal.replace(dest)
            _write_verdict(dest, {"verdict": "PASS", "attempts": attempts,
                                  "committed_at": utcnow_iso(),
                                  "log": result.stdout[-2000:]})
            gated.append({"proposal": proposal.name, "verdict": "PASS",
                          "committed": True})
            print(f"[Cycle D] {proposal.name} -> PASS (commit local)")
        else:
            _write_verdict(proposal, {"verdict": "FAIL", "attempts": attempts,
                                      "at": utcnow_iso(),
                                      "log": (result.stdout + result.stderr)[-2000:]})
            gated.append({"proposal": proposal.name, "verdict": "FAIL",
                          "attempts": attempts})
            print(f"[Cycle D] {proposal.name} -> FAIL (attempt {attempts})")
            print(f"[Cycle D]   log: {(result.stdout + result.stderr)[-500:]}")
    return gated


def run_cycle(root: Path, min_hits: int = 3, min_score: float = 0.7,
              auto_commit: bool = True, max_attempts: int = 3,
              reset_processed: bool = False,
              reprocess_quarantine: bool = False) -> dict[str, Any]:
    """Execute un cycle complet. Retourne le rapport (ecrit aussi sur disque)."""
    started = utcnow_iso()
    start_ts = time.time()

    if reset_processed:
        print("[Cycle] --reset-processed : efface processed.json (reparation FR)")
        try:
            (state_dir(root) / "processed.json").unlink(missing_ok=True)
        except TypeError:
            # Python <3.8 fallback
            p = state_dir(root) / "processed.json"
            if p.exists():
                p.unlink()

    processed = load_processed(root)

    print(f"[Cycle] Demarrage (root={root}, processed={len(processed)} traces deja traitees, "
          f"min_hits={min_hits}, min_score={min_score}, auto_commit={auto_commit})")

    t_ab_start = time.time()
    distilled, errors = phase_ab(root, processed, reprocess_quarantine=reprocess_quarantine)
    t_ab = time.time() - t_ab_start
    save_processed(root, processed)

    t_c_start = time.time()
    forged = phase_c(root, min_hits, min_score)
    t_c = time.time() - t_c_start

    t_d_start = time.time()
    gated = phase_d(root, auto_commit, max_attempts)
    t_d = time.time() - t_d_start

    total_elapsed = time.time() - start_ts

    report = {
        "started_at": started,
        "finished_at": utcnow_iso(),
        "elapsed_seconds": round(total_elapsed, 2),
        "timings": {"AB": round(t_ab, 2), "C": round(t_c, 2), "D": round(t_d, 2)},
        "distilled": distilled,
        "errors": errors,
        "forged": forged,
        "gated": gated,
        "metrics": {
            "processed_total": len(processed),
            "distilled_now": len(distilled),
            "errors_now": len(errors),
            "forged_now": len([f for f in forged if f.get("forged")]),
            "gated_now": len(gated),
        }
    }
    (state_dir(root) / "last_cycle.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"[Cycle] Termine en {total_elapsed:.2f}s : "
          f"distillees={len(distilled)} erreurs={len(errors)} "
          f"forgees={len([f for f in forged if f.get('forged')])} gatees={len(gated)}")

    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Moteur de cycle Ouroboros (A->D) V2.1.")
    parser.add_argument("--root", default=None, help="Racine Tesla")
    parser.add_argument("--min-hits", type=int, default=3)
    parser.add_argument("--min-score", type=float, default=0.7)
    parser.add_argument("--no-commit", action="store_true",
                        help="Distille + forge sans gater/commiter")
    parser.add_argument("--max-attempts", type=int, default=3)
    parser.add_argument("--reset-processed", action="store_true",
                        help="Rejoue toutes les traces (reparation FR, ignore processed.json)")
    parser.add_argument("--reprocess-quarantine", action="store_true",
                        help="Tente de recuperer les traces en quarantaine")
    args = parser.parse_args(argv)
    root = Path(args.root).resolve() if args.root else resolve_tesla_root()

    report = run_cycle(root, args.min_hits, args.min_score,
                       auto_commit=not args.no_commit,
                       max_attempts=args.max_attempts,
                       reset_processed=args.reset_processed,
                       reprocess_quarantine=args.reprocess_quarantine)
    print(f"[Cycle] Distillees: {len(report['distilled'])} | "
          f"Erreurs: {len(report['errors'])} | "
          f"Forgees: {len([f for f in report['forged'] if f.get('forged')])} | "
          f"Gatees: {len(report['gated'])} | "
          f"Duree: {report.get('elapsed_seconds', '?')}s")
    for gate in report["gated"]:
        print(f"[Cycle]   {gate['proposal']} -> {gate['verdict']}")
    for err in report["errors"]:
        print(f"[Cycle]   ERREUR {err['trace']} :: {err['error']}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
