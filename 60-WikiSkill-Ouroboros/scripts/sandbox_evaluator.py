#!/usr/bin/env python3
"""sandbox_evaluator.py - Evalue un patch .intent dans un worktree isole.

BUGFIX Ouroboros Auto-Capture : `git apply` etait invoque directement sur le
fichier .intent.patch dont l'en-tete JSON faisait echouer l'application
("unrecognized input"). La section diff est desormais extraite vers un
fichier temporaire avant application dans le worktree.

Interface CLI inchangee :
    python3 sandbox_evaluator.py <patch> [--eval-script X] [--repo-path R]
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import tempfile
import uuid

DIFF_START_RE = re.compile(r"^(diff --git|--- a/|--- \./|--- \.agents/)", re.MULTILINE)


def extract_diff_section(patch_path: str) -> str:
    """Extrait la section Unified Diff d'un .intent.patch (sans l'en-tete)."""
    with open(patch_path, "r", encoding="utf-8") as fh:
        content = fh.read()
    match = DIFF_START_RE.search(content)
    if not match:
        raise ValueError("Aucune section Unified Diff trouvee dans le patch.")
    return content[match.start():]


def run_evaluation(worktree_path: str, eval_script: str) -> int:
    """Execute le script d'evaluation a l'interieur du worktree."""
    try:
        result = subprocess.run(
            [sys.executable, eval_script, worktree_path],
            cwd=worktree_path,
            capture_output=True,
            text=True,
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        return result.returncode
    except Exception as exc:  # noqa: BLE001 - robustesse du runner
        print(f"Erreur lors de l'execution de l'evaluation : {exc}", file=sys.stderr)
        return 1


def main() -> None:
    parser = argparse.ArgumentParser(description="Evalue un patch .intent dans un worktree (sandbox).")
    parser.add_argument("patch_path", help="Chemin vers le fichier .intent.patch")
    parser.add_argument("--eval-script", default="gating_judge.py",
                        help="Chemin vers le script d'evaluation")
    parser.add_argument("--repo-path", default=".", help="Chemin vers la racine du repo Git")

    args = parser.parse_args()

    patch_path = os.path.abspath(args.patch_path)
    eval_script = os.path.abspath(args.eval_script)
    repo_path = os.path.abspath(args.repo_path)

    if not os.path.exists(patch_path):
        print(f"Erreur : Le patch {patch_path} n'existe pas.", file=sys.stderr)
        sys.exit(1)

    try:
        diff_only = extract_diff_section(patch_path)
    except ValueError as exc:
        print(f"Erreur : Patch inapplicable : {exc}", file=sys.stderr)
        sys.exit(1)

    hash_id = uuid.uuid4().hex[:8]
    worktree_path = f"/tmp/eval_patch_{hash_id}"
    tmp_patch = None
    try:
        with tempfile.NamedTemporaryFile(
                mode="w", suffix=".diff", prefix="wikiskill_sbx_",
                delete=False, encoding="utf-8") as fh:
            fh.write(diff_only)
            tmp_patch = fh.name

        print(f"Creation du worktree detache a {worktree_path}...")
        subprocess.run(
            ["git", "worktree", "add", "--detach", worktree_path, "HEAD"],
            cwd=repo_path,
            check=True,
            capture_output=True,
        )

        print(f"Application du patch {os.path.basename(patch_path)} dans le worktree...")
        subprocess.run(
            ["git", "apply", tmp_patch],
            cwd=worktree_path,
            check=True,
            capture_output=True,
        )

        print("Execution de l'evaluation Gating...")
        exit_code = run_evaluation(worktree_path, eval_script)

        if exit_code == 0:
            print("=> Evaluation Sandbox REUSSIE.")
        else:
            print("=> Evaluation Sandbox ECHOUEE.", file=sys.stderr)

        sys.exit(exit_code)

    except subprocess.CalledProcessError as exc:
        print(f"Erreur fatale lors d'une operation Git : {exc}", file=sys.stderr)
        if exc.stderr:
            try:
                print(exc.stderr.decode("utf-8"), file=sys.stderr)
            except Exception:  # noqa: BLE001
                print(exc.stderr, file=sys.stderr)
        sys.exit(1)
    finally:
        if tmp_patch and os.path.exists(tmp_patch):
            os.remove(tmp_patch)
        if os.path.exists(worktree_path):
            print(f"Nettoyage : Suppression du worktree {worktree_path}...")
            try:
                subprocess.run(
                    ["git", "worktree", "remove", "--force", worktree_path],
                    cwd=repo_path,
                    check=True,
                    capture_output=True,
                )
            except subprocess.CalledProcessError as exc:
                print(f"Avertissement : Echec de la suppression du worktree : {exc}",
                      file=sys.stderr)


if __name__ == "__main__":
    main()
