#!/usr/bin/env python3
"""sandbox_evaluator.py — Évalue un patch .intent dans un worktree Git détaché.

Correction d'incident : le patch complet (en-tête HTML + diff) était passé à
`git apply`, ce qui provoquait un échec. Seule la portion Unified Diff est
désormais appliquée, et le skill ciblé est transmis au juge de gating.
"""
import argparse
import json
import re
import subprocess
import sys
import os
import uuid

METADATA_RE = re.compile(r"<!--\s*WIKISKILL_METADATA\s*(.*?)\s*-->", re.DOTALL)
DIFF_START_RE = re.compile(r"^(?:diff --git|--- |\+\+\+)", re.MULTILINE)


def extract_skill_target(patch_path: str) -> str:
    with open(patch_path, "r", encoding="utf-8") as f:
        content = f.read()
    m = METADATA_RE.search(content)
    if not m:
        return ""
    try:
        return json.loads(m.group(1)).get("skill_target", "")
    except json.JSONDecodeError:
        return ""


def extract_diff(patch_path: str) -> str:
    with open(patch_path, "r", encoding="utf-8") as f:
        content = f.read()
    m = DIFF_START_RE.search(content)
    if not m:
        raise ValueError("Aucune section Unified Diff valide trouvée dans le patch.")
    return content[m.start():]


def run_evaluation(worktree_path: str, eval_script: str, skill: str) -> int:
    cmd = [sys.executable, eval_script, worktree_path]
    if skill:
        cmd += ["--skill", skill]
    result = subprocess.run(cmd, cwd=worktree_path, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result.returncode


def main() -> int:
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
        return 1

    try:
        diff_content = extract_diff(patch_path)
    except ValueError as e:
        print(f"Erreur : {e}", file=sys.stderr)
        return 1
    skill = extract_skill_target(patch_path)

    hash_id = uuid.uuid4().hex[:8]
    worktree_path = f"/tmp/eval_patch_{hash_id}"

    try:
        print(f"Création du worktree détaché à {worktree_path}...")
        subprocess.run(
            ["git", "worktree", "add", "--detach", worktree_path, "HEAD"],
            cwd=repo_path, check=True, capture_output=True
        )

        with open(os.path.join(worktree_path, "__wikiskill.diff"), "w", encoding="utf-8") as f:
            f.write(diff_content)

        print(f"Application du patch {os.path.basename(patch_path)} dans le worktree...")
        subprocess.run(
            ["git", "apply", os.path.join(worktree_path, "__wikiskill.diff")],
            cwd=worktree_path, check=True, capture_output=True
        )

        print("Exécution de l'évaluation Gating...")
        exit_code = run_evaluation(worktree_path, eval_script, skill)

        if exit_code == 0:
            print("=> Évaluation Sandbox RÉUSSIE.")
        else:
            print("=> Évaluation Sandbox ÉCHOUÉE.", file=sys.stderr)

        return exit_code

    except subprocess.CalledProcessError as e:
        print(f"Erreur fatale lors d'une opération Git : {e}", file=sys.stderr)
        if e.stderr:
            print(e.stderr.decode("utf-8"), file=sys.stderr)
        return 1
    finally:
        if os.path.exists(worktree_path):
            print(f"Nettoyage : Suppression du worktree {worktree_path}...")
            try:
                subprocess.run(
                    ["git", "worktree", "remove", "--force", worktree_path],
                    cwd=repo_path, check=True, capture_output=True
                )
            except subprocess.CalledProcessError as e:
                print(f"Avertissement : Échec de la suppression du worktree : {e}", file=sys.stderr)


if __name__ == "__main__":
    sys.exit(main())
