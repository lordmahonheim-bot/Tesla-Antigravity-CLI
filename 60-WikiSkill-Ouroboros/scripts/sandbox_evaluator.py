#!/usr/bin/env python3
import argparse
import subprocess
import uuid
import sys
import os
from typing import Optional

def run_evaluation(worktree_path: str, eval_script: str) -> int:
    """Exécute le script d'évaluation à l'intérieur du worktree."""
    try:
        # On suppose que eval_script est un exécutable ou un script Python
        result = subprocess.run(
            [sys.executable, eval_script, worktree_path],
            cwd=worktree_path,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        return result.returncode
    except Exception as e:
        print(f"Erreur lors de l'exécution de l'évaluation : {e}", file=sys.stderr)
        return 1

def main():
    parser = argparse.ArgumentParser(description="Évalue un patch .intent dans un worktree (sandbox).")
    parser.add_argument("patch_path", help="Chemin vers le fichier .intent.patch")
    parser.add_argument("--eval-script", default="gating_judge.py", help="Chemin vers le script d'évaluation")
    parser.add_argument("--repo-path", default=".", help="Chemin vers la racine du repo Git")
    
    args = parser.parse_args()
    
    patch_path = os.path.abspath(args.patch_path)
    eval_script = os.path.abspath(args.eval_script)
    repo_path = os.path.abspath(args.repo_path)
    
    if not os.path.exists(patch_path):
        print(f"Erreur : Le patch {patch_path} n'existe pas.", file=sys.stderr)
        sys.exit(1)
        
    hash_id = uuid.uuid4().hex[:8]
    worktree_path = f"/tmp/eval_patch_{hash_id}"
    
    try:
        print(f"Création du worktree détaché à {worktree_path}...")
        subprocess.run(
            ["git", "worktree", "add", "--detach", worktree_path, "HEAD"],
            cwd=repo_path,
            check=True,
            capture_output=True
        )
        
        print(f"Application du patch {os.path.basename(patch_path)} dans le worktree...")
        subprocess.run(
            ["git", "apply", patch_path],
            cwd=worktree_path,
            check=True,
            capture_output=True
        )
        
        print("Exécution de l'évaluation Gating...")
        exit_code = run_evaluation(worktree_path, eval_script)
        
        if exit_code == 0:
            print("=> Évaluation Sandbox RÉUSSIE.")
        else:
            print("=> Évaluation Sandbox ÉCHOUÉE.", file=sys.stderr)
            
        sys.exit(exit_code)
        
    except subprocess.CalledProcessError as e:
        print(f"Erreur fatale lors d'une opération Git : {e}", file=sys.stderr)
        if e.stderr:
            print(e.stderr.decode('utf-8'), file=sys.stderr)
        sys.exit(1)
    finally:
        # Nettoyage systématique
        if os.path.exists(worktree_path):
            print(f"Nettoyage : Suppression du worktree {worktree_path}...")
            try:
                subprocess.run(
                    ["git", "worktree", "remove", "--force", worktree_path],
                    cwd=repo_path,
                    check=True,
                    capture_output=True
                )
            except subprocess.CalledProcessError as e:
                print(f"Avertissement : Échec de la suppression du worktree : {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
