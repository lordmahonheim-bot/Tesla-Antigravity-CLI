#!/usr/bin/env python3
import argparse
import sys
import os
from typing import List, Dict

def load_dataset(dataset_name: str) -> List[Dict[str, str]]:
    """Simule le chargement d'un dataset (train_val ou holdout)."""
    print(f"[Judge] Chargement du dataset : {dataset_name}...")
    # Dans la vraie implémentation : charger un JSONL depuis tests/datasets/
    return [{"input": "Tâche de test complexe", "expected": "Validation OK"}]

def evaluate_skill(worktree_path: str, dataset: List[Dict[str, str]]) -> float:
    """
    Exécute les tests sur la compétence présente dans le worktree.
    Retourne un score de succès entre 0.0 et 1.0.
    """
    print(f"[Judge] Évaluation des performances dans : {worktree_path}...")
    # Simulation d'un test LSP/Unitaire (ex: pytest, ou appel LLM as code)
    # Si le WIKI.md contient une syntaxe invalide ou fait échouer l'agent, le score baisse.
    return 1.0 # 100% de réussite simulée

def main():
    parser = argparse.ArgumentParser(description="Double-Split Gating (Juge d'évaluation).")
    parser.add_argument("worktree_path", help="Chemin du worktree à évaluer")
    args = parser.parse_args()
    
    worktree_path = os.path.abspath(args.worktree_path)
    print("Démarrage du Gating Judge (Double-Split)...")
    
    # 1. Validation sur D_train_val (cas normaux et historiques)
    d_train_val = load_dataset("D_train_val")
    train_score = evaluate_skill(worktree_path, d_train_val)
    
    if train_score < 0.9:
        print("[Judge] Échec de la validation sur D_train_val (Score: {:.2f}). Régression majeure.".format(train_score), file=sys.stderr)
        sys.exit(1)
        
    # 2. Validation sur D_holdout (cas extrêmes / tests de généralisation)
    d_holdout = load_dataset("D_holdout")
    holdout_score = evaluate_skill(worktree_path, d_holdout)
    
    if holdout_score < 0.9:
        print("[Judge] Échec de la validation sur D_holdout (Score: {:.2f}). Overfitting de la règle détecté.".format(holdout_score), file=sys.stderr)
        sys.exit(1)
        
    print("[Judge] Toutes les validations sont passées. Le patch est robuste.")
    sys.exit(0)

if __name__ == "__main__":
    main()
