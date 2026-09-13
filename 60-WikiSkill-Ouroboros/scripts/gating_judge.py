#!/usr/bin/env python3
"""gating_judge.py — Juge d'évaluation Double-Split (fail-closed, sans simulation).

Correction d'incident : l'ancienne implémentation retournait un score factice de
1.0 ("100% de réussite simulée"), ce qui violait la Règle Zéro "NO PROOF, NO PASS".
Désormais :
  * les datasets sont chargés depuis des fichiers réels (JSONL) ;
  * si un dataset est absent, le Gating REFUSE la validation (exit 1) au lieu de
    simuler un succès ;
  * l'évaluation est déterministe : chaque entrée déclare un fichier attendu et un
    contenu obligatoire dans le worktree. Le jeton `{skill}` est substitué par la
    valeur de --skill.

Format JSONL (une entrée par ligne) :
    {"file": ".agents/skills/{skill}/SKILL.md", "must_contain": "{skill}", "reason": "identité"}

Exit codes :
    0 : double-split validé (train >= 0.9 et holdout >= 0.9)
    1 : échec de validation ou simulation refusée (fail-closed)
"""
import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional


def default_dataset_dir() -> Path:
    # Relatif au script : 60-WikiSkill-Ouroboros/tests/datasets
    return Path(__file__).resolve().parent.parent / "tests" / "datasets"


def load_dataset(dataset_path: str) -> Optional[List[dict]]:
    p = Path(dataset_path)
    if not p.is_file():
        print(f"[Judge] REFUS : dataset introuvable {p} (simulation interdite).", file=sys.stderr)
        return None
    entries = []
    with open(p, "r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"[Judge] JSONL invalide {p}:{lineno} : {e}", file=sys.stderr)
                sys.exit(1)
    if not entries:
        print(f"[Judge] REFUS : dataset vide {p} (simulation interdite).", file=sys.stderr)
        return None
    return entries


def check_entry(worktree: Path, entry: dict, skill: str) -> bool:
    rel = entry.get("file", "").replace("{skill}", skill)
    must_contain = entry.get("must_contain", "").replace("{skill}", skill)
    reason = entry.get("reason", "contrôle structurel")
    target = worktree / rel
    if not target.is_file():
        print(f"  [KO] fichier attendu absent : {rel} ({reason})")
        return False
    content = target.read_text(encoding="utf-8", errors="replace")
    if must_contain and must_contain not in content:
        print(f"  [KO] contenu absent ({must_contain!r}) dans {rel} ({reason})")
        return False
    print(f"  [OK] {rel} ({reason})")
    return True


def evaluate_skill(worktree_path: str, dataset: List[dict], skill: str) -> float:
    worktree = Path(worktree_path)
    passed = sum(1 for entry in dataset if check_entry(worktree, entry, skill))
    return passed / len(dataset)


def main(argv) -> int:
    parser = argparse.ArgumentParser(description="Double-Split Gating (Juge d'évaluation, fail-closed).")
    parser.add_argument("worktree_path", help="Chemin du worktree à évaluer")
    parser.add_argument("--skill", default="", help="Nom du skill évalué (substitue {skill} dans le dataset).")
    parser.add_argument("--dataset-dir", default="", help="Répertoire contenant train_val.jsonl et holdout.jsonl.")
    args = parser.parse_args(argv)

    worktree_path = str(Path(args.worktree_path).resolve())
    ds_dir = Path(args.dataset_dir) if args.dataset_dir else default_dataset_dir()

    print("Démarrage du Gating Judge (Double-Split, fail-closed)...")

    train_dataset = load_dataset(str(ds_dir / "train_val.jsonl"))
    if train_dataset is None:
        return 1
    holdout_dataset = load_dataset(str(ds_dir / "holdout.jsonl"))
    if holdout_dataset is None:
        return 1

    print("[Judge] Validation sur D_train_val ...")
    train_score = evaluate_skill(worktree_path, train_dataset, args.skill)
    if train_score < 0.9:
        print(f"[Judge] Échec sur D_train_val (Score: {train_score:.2f}). Régression majeure.", file=sys.stderr)
        return 1

    print("[Judge] Validation sur D_holdout ...")
    holdout_score = evaluate_skill(worktree_path, holdout_dataset, args.skill)
    if holdout_score < 0.9:
        print(f"[Judge] Échec sur D_holdout (Score: {holdout_score:.2f}). Overfitting détecté.", file=sys.stderr)
        return 1

    print(f"[Judge] Toutes les validations sont passées (train={train_score:.2f}, holdout={holdout_score:.2f}).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
