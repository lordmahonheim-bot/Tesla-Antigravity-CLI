#!/usr/bin/env python3
"""git_committer.py — Applique et commit un patch WikiSkill après Gating.

Corrections d'incident :
  * lit le FORMAT CANONIQUE UNIFIÉ `<!-- WIKISKILL_METADATA ... -->` ;
  * extrait UNIQUEMENT la portion Unified Diff avant `git apply` (l'ancien flux
    passait le fichier entier, en-tête HTML inclus, à git apply -> échec) ;
  * conserve l'ordre Sandbox -> Gating -> apply -> commit (fail-closed).
"""
import argparse
import json
import re
import subprocess
import sys
import os
import tempfile
from typing import Tuple

METADATA_RE = re.compile(r"<!--\s*WIKISKILL_METADATA\s*(.*?)\s*-->", re.DOTALL)
DIFF_START_RE = re.compile(r"^(?:diff --git|--- |\+\+\+)", re.MULTILINE)


def extract_metadata_from_patch(patch_path: str) -> Tuple[str, str]:
    with open(patch_path, "r", encoding="utf-8") as f:
        content = f.read()

    m = METADATA_RE.search(content)
    if not m:
        raise ValueError("Bloc WIKISKILL_METADATA introuvable dans le patch.")

    try:
        metadata = json.loads(m.group(1))
        return metadata["skill_target"], metadata["justification"]
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON invalide dans le bloc WIKISKILL_METADATA : {e}")
    except KeyError as e:
        raise ValueError(f"Clé manquante dans les métadonnées WIKISKILL : {e}")


def extract_diff(patch_path: str) -> str:
    with open(patch_path, "r", encoding="utf-8") as f:
        content = f.read()
    m = DIFF_START_RE.search(content)
    if not m:
        raise ValueError("Aucune section Unified Diff valide trouvée dans le patch.")
    return content[m.start():]


def main() -> int:
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
        return 1

    print(f"Cible : {skill_target} | Justification : {justification}")
    print("[Committer] Invocation du Sandbox de validation...")

    sandbox_result = subprocess.run(
        [sys.executable, sandbox_script, patch_path,
         "--eval-script", gating_script,
         "--repo-path", repo_path],
        capture_output=True,
        text=True
    )

    if sandbox_result.returncode != 0:
        print("[Committer] Le Gating a rejeté le patch. Annulation du commit.", file=sys.stderr)
        print("--- Sandbox STDOUT ---", file=sys.stderr)
        print(sandbox_result.stdout, file=sys.stderr)
        print("--- Sandbox STDERR ---", file=sys.stderr)
        print(sandbox_result.stderr, file=sys.stderr)
        return 1

    print("[Committer] Gating Sandbox réussi. Intégration du patch au workspace courant...")

    try:
        diff_content = extract_diff(patch_path)
        with tempfile.NamedTemporaryFile(mode="w", suffix=".diff", delete=False, encoding="utf-8") as tmp:
            tmp.write(diff_content)
            diff_path = tmp.name

        try:
            subprocess.run(["git", "apply", diff_path], cwd=repo_path, check=True)
            skill_dir = os.path.join(".agents", "skills", skill_target)
            subprocess.run(["git", "add", skill_dir], cwd=repo_path, check=True)
            commit_msg = f"[WikiSkill] Update {skill_target}: {justification}"
            subprocess.run(["git", "commit", "-m", commit_msg], cwd=repo_path, check=True)
            print(f"[Committer] Succès ! Commit créé : {commit_msg}")
        finally:
            if os.path.exists(diff_path):
                os.remove(diff_path)

    except subprocess.CalledProcessError as e:
        print(f"[Committer] Erreur Git lors de l'application ou du commit : {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"[Committer] Erreur de patch : {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
