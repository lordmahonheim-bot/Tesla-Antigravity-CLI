#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys
import os
import re
from typing import Tuple

def extract_metadata_from_patch(patch_path: str) -> Tuple[str, str]:
    """
    Extrait skill_target et justification d'un bloc JSON contenu dans le patch.
    Format attendu dans le patch (.intent.patch) :
    <!-- WIKISKILL_METADATA
    { "skill_target": "tesla-wiki-manager", "justification": "Ajout règle X" }
    -->
    """
    with open(patch_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    match = re.search(r'<!--\s*WIKISKILL_METADATA\s*(.*?)\s*-->', content, re.DOTALL)
    if not match:
        raise ValueError("Bloc WIKISKILL_METADATA introuvable dans le patch.")
        
    json_str = match.group(1)
    try:
        metadata = json.loads(json_str)
        return metadata['skill_target'], metadata['justification']
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON invalide dans le bloc WIKISKILL_METADATA : {e}")
    except KeyError as e:
        raise ValueError(f"Clé manquante dans les métadonnées WIKISKILL : {e}")

def main():
    parser = argparse.ArgumentParser(description="Applique et commit un patch WikiSkill après Gating.")
    parser.add_argument("patch_path", help="Chemin vers le fichier .intent.patch")
    parser.add_argument("--sandbox-script", default="sandbox_evaluator.py", help="Chemin vers sandbox_evaluator.py")
    parser.add_argument("--gating-script", default="gating_judge.py", help="Chemin vers gating_judge.py")
    parser.add_argument("--repo-path", default=".", help="Racine du repository Git")
    args = parser.parse_args()
    
    patch_path = os.path.abspath(args.patch_path)
    sandbox_script = os.path.abspath(args.sandbox_script)
    gating_script = os.path.abspath(args.gating_script)
    repo_path = os.path.abspath(args.repo_path)
    
    print("[Committer] Extraction des métadonnées de l'intention...")
    try:
        skill_target, justification = extract_metadata_from_patch(patch_path)
    except Exception as e:
        print(f"Erreur d'extraction : {e}", file=sys.stderr)
        sys.exit(1)
        
    print(f"Cible : {skill_target} | Justification : {justification}")
    print("[Committer] Invocation du Sandbox de validation...")
    
    # Appel de sandbox_evaluator en sous-processus
    sandbox_result = subprocess.run(
        [sys.executable, sandbox_script, patch_path, 
         "--eval-script", gating_script, 
         "--repo-path", repo_path],
        capture_output=True,
        text=True
    )
    
    if sandbox_result.returncode != 0:
        print("[Committer] Le Gating a rejeté le patch. Annulation du commit.", file=sys.stderr)
        print("--- Sandbox STDERR ---", file=sys.stderr)
        print(sandbox_result.stderr, file=sys.stderr)
        sys.exit(1)
        
    print("[Committer] Gating Sandbox réussi. Intégration du patch au workspace courant...")
    
    try:
        # Application du patch dans le vrai workspace
        subprocess.run(["git", "apply", patch_path], cwd=repo_path, check=True)
        
        # Staging du répertoire de la compétence spécifique
        skill_dir = os.path.join(".agents", "skills", skill_target)
        subprocess.run(["git", "add", skill_dir], cwd=repo_path, check=True)
        
        # Commit de la règle
        commit_msg = f"[WikiSkill] Update {skill_target}: {justification}"
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=repo_path, check=True)
        
        print(f"[Committer] Succès ! Commit créé : {commit_msg}")
        
    except subprocess.CalledProcessError as e:
        print(f"[Committer] Erreur Git lors de l'application ou du commit : {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
