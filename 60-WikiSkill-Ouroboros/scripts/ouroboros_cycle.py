#!/usr/bin/env python3
"""ouroboros_cycle.py - Moteur du cycle complet Trace -> Index -> Patch -> Gate.

C'est le "moteur qui tourne" sans l'Orchestrateur : un seul appel execute
deterministiquement les 4 phases Ouroboros sur toutes les traces non traitees :

  Phase A (Capture)  : verifie l'integrite SHA-256 de chaque trace (.agents/traces/) ;
                       corrompue -> quarantine/ (+ journal), saine -> suite.
  Phase B (Distill)  : distiller.distill_trace -> note wiki + index.tsv (budget 4000).
  Phase C (Mutate)   : rule_forger.forge_all_eligible -> proposals/*.intent.patch.
  Phase D (Gate)     : git_committer (sandbox + gating_judge V2) sur chaque
                       proposition ouverte -> PASS : commit LOCAL + accepted/ ;
                       FAIL : verdict sidecar, 3 tentatives max puis quarantine/.

Etat : <root>/runtime/ouroboros/processed.json + last_cycle.json (runtime/ est
gitignore, hygiene Vigilum E5). JAMAIS de push distant (prerogative souveraine).

CLI :
    python3 ouroboros_cycle.py [--root DIR] [--min-hits 3] [--min-score 0.7]
                               [--no-commit] [--max-attempts 3]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
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


def phase_ab(root: Path, processed: dict[str, Any]) -> tuple[list[dict], list[dict]]:
    """Phase A (verification) + B (distillation) des traces non traitees."""
    distilled: list[dict] = []
    errors: list[dict] = []
    traces_dir = root / ".agents" / "traces"
    if not traces_dir.is_dir():
        return distilled, errors
    for trace_file in sorted(traces_dir.glob("*.json")):
        sha = trace_file.stem
        if sha in processed:
            continue
        ok, reason, trace = verify_trace_file(trace_file)
        if not ok:
            quar = traces_dir / "quarantine" / trace_file.name
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
                          "at": utcnow_iso()}
        distilled.append({"trace": trace_file.name,
                          "pattern": summary["pattern"]["id"],
                          "hits": summary["hits"],
                          "budget_ok": summary["budget_ok"]})
    return distilled, errors


def phase_c(root: Path, min_hits: int, min_score: float) -> list[dict]:
    """Phase C (mutation) : forge les regles eligibles."""
    return forge_all_eligible(root, min_hits, min_score)


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
        return gated

    is_git = (root / ".git").is_dir()
    for proposal in open_props:
        verdict = _read_verdict(proposal)
        attempts = int(verdict.get("attempts", 0) or 0)
        if attempts >= max_attempts:
            quar = pdir / "quarantine" / proposal.name
            proposal.replace(quar)
            _write_verdict(quar, {**verdict, "verdict": "EXHAUSTED",
                                  "moved_to": "quarantine", "at": utcnow_iso()})
            gated.append({"proposal": proposal.name, "verdict": "EXHAUSTED"})
            continue
        if not auto_commit:
            gated.append({"proposal": proposal.name, "verdict": "STAGED",
                          "reason": "--no-commit : gating differe"})
            continue
        if not is_git:
            gated.append({"proposal": proposal.name, "verdict": "SKIPPED",
                          "reason": "racine non-git : sandbox impossible"})
            continue

        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "git_committer.py"), str(proposal),
             "--sandbox-script", str(SCRIPTS_DIR / "sandbox_evaluator.py"),
             "--gating-script", str(SCRIPTS_DIR / "gating_judge.py"),
             "--repo-path", str(root)],
            capture_output=True, text=True)
        attempts += 1
        if result.returncode == 0:
            dest = pdir / "accepted" / proposal.name
            if proposal.exists():
                proposal.replace(dest)
            _write_verdict(dest, {"verdict": "PASS", "attempts": attempts,
                                  "committed_at": utcnow_iso(),
                                  "log": result.stdout[-2000:]})
            gated.append({"proposal": proposal.name, "verdict": "PASS",
                          "committed": True})
        else:
            _write_verdict(proposal, {"verdict": "FAIL", "attempts": attempts,
                                      "at": utcnow_iso(),
                                      "log": (result.stdout + result.stderr)[-2000:]})
            gated.append({"proposal": proposal.name, "verdict": "FAIL",
                          "attempts": attempts})
    return gated


def run_cycle(root: Path, min_hits: int = 3, min_score: float = 0.7,
              auto_commit: bool = True, max_attempts: int = 3) -> dict[str, Any]:
    """Execute un cycle complet. Retourne le rapport (ecrit aussi sur disque)."""
    started = utcnow_iso()
    processed = load_processed(root)
    distilled, errors = phase_ab(root, processed)
    save_processed(root, processed)
    forged = phase_c(root, min_hits, min_score)
    gated = phase_d(root, auto_commit, max_attempts)
    report = {"started_at": started, "finished_at": utcnow_iso(),
              "distilled": distilled, "errors": errors,
              "forged": forged, "gated": gated}
    (state_dir(root) / "last_cycle.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8")
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Moteur de cycle Ouroboros (A->D).")
    parser.add_argument("--root", default=None, help="Racine Tesla")
    parser.add_argument("--min-hits", type=int, default=3)
    parser.add_argument("--min-score", type=float, default=0.7)
    parser.add_argument("--no-commit", action="store_true",
                        help="Distille + forge sans gater/commiter")
    parser.add_argument("--max-attempts", type=int, default=3)
    args = parser.parse_args(argv)
    root = Path(args.root).resolve() if args.root else resolve_tesla_root()

    report = run_cycle(root, args.min_hits, args.min_score,
                       auto_commit=not args.no_commit,
                       max_attempts=args.max_attempts)
    print(f"[Cycle] Distillees: {len(report['distilled'])} | "
          f"Erreurs: {len(report['errors'])} | "
          f"Forgees: {len([f for f in report['forged'] if f.get('forged')])} | "
          f"Gatees: {len(report['gated'])}")
    for gate in report["gated"]:
        print(f"[Cycle]   {gate['proposal']} -> {gate['verdict']}")
    for err in report["errors"]:
        print(f"[Cycle]   ERREUR {err['trace']} :: {err['error']}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
