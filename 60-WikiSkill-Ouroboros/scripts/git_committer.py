#!/usr/bin/env python3
"""git_committer.py - Applique et commit un patch WikiSkill apres Gating.

BUGFIX Ouroboros Auto-Capture (2 correctifs) :
  1. Le committer exigeait un 3e format de metadonnees (<!-- WIKISKILL_METADATA
     -->) incompatible avec skill_proposer.py (```json) et patch_broker.py
     (JSON brut). Il accepte desormais le format canonique ```json en
     priorite, puis le JSON brut, puis le commentaire HTML (legacy).
  2. Le committer invoquait `git apply` directement sur le fichier .intent.patch
     dont l'en-tete JSON faisait echouer l'application ("unrecognized input").
     La section diff est desormais extraite vers un fichier temporaire avant
     application (memes correctif applique a sandbox_evaluator.py).

Interface CLI inchangee. JAMAIS de push distant (prerogative souveraine,
contrat d'execution AGENTS.md) : commit local uniquement.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile

DIFF_START_RE = re.compile(r"^(diff --git|--- a/|--- \./|--- \.agents/)", re.MULTILINE)


def extract_diff_section(patch_path: str) -> str:
    """Extrait la section Unified Diff d'un .intent.patch (sans l'en-tete)."""
    with open(patch_path, "r", encoding="utf-8") as fh:
        content = fh.read()
    match = DIFF_START_RE.search(content)
    if not match:
        raise ValueError("Aucune section Unified Diff trouvee dans le patch.")
    return content[match.start():]


def _parse_metadata_object(raw: str) -> tuple[str, str]:
    try:
        metadata = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"JSON invalide dans les metadonnees : {exc}") from exc
    try:
        return metadata["skill_target"], metadata["justification"]
    except (KeyError, TypeError) as exc:
        raise ValueError(f"Cle manquante dans les metadonnees WIKISKILL : {exc}") from exc


def extract_metadata_from_patch(patch_path: str) -> tuple[str, str]:
    """Extrait (skill_target, justification) d'un .intent.patch.

    Formats acceptes, par ordre de priorite :
      1. bloc canonique ```json ... ``` (emis par rule_forger.py)
      2. en-tete JSON brut (legacy patch_broker)
      3. <!-- WIKISKILL_METADATA { ... } --> (legacy committer)
    """
    with open(patch_path, "r", encoding="utf-8") as fh:
        content = fh.read()

    fenced = re.search(r"```json\s*(.*?)\s*```", content, re.DOTALL)
    if fenced:
        return _parse_metadata_object(fenced.group(1).strip())

    html = re.search(r"<!--\s*WIKISKILL_METADATA\s*(.*?)\s*-->", content, re.DOTALL)
    if html:
        return _parse_metadata_object(html.group(1).strip())

    diff_match = DIFF_START_RE.search(content)
    header = content[:diff_match.start()].strip() if diff_match else content.strip()
    header = re.sub(r"^---+\s*$", "", header, flags=re.MULTILINE).strip()
    if header:
        return _parse_metadata_object(header)

    raise ValueError("Bloc de metadonnees introuvable dans le patch.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Applique et commit un patch WikiSkill apres Gating.")
    parser.add_argument("patch_path", help="Chemin vers le fichier .intent.patch")
    parser.add_argument("--sandbox-script", default="sandbox_evaluator.py",
                        help="Chemin vers sandbox_evaluator.py")
    parser.add_argument("--gating-script", default="gating_judge.py",
                        help="Chemin vers gating_judge.py")
    parser.add_argument("--repo-path", default=".", help="Racine du repository Git")
    args = parser.parse_args()

    patch_path = os.path.abspath(args.patch_path)
    sandbox_script = os.path.abspath(args.sandbox_script)
    gating_script = os.path.abspath(args.gating_script)
    repo_path = os.path.abspath(args.repo_path)

    print("[Committer] Extraction des metadonnees de l'intention...")
    try:
        skill_target, justification = extract_metadata_from_patch(patch_path)
    except Exception as exc:  # noqa: BLE001 - message d'erreur CLI
        print(f"Erreur d'extraction : {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"Cible : {skill_target} | Justification : {justification}")
    print("[Committer] Invocation du Sandbox de validation...")

    sandbox_result = subprocess.run(
        [sys.executable, sandbox_script, patch_path,
         "--eval-script", gating_script,
         "--repo-path", repo_path],
        capture_output=True,
        text=True,
    )

    if sandbox_result.returncode != 0:
        print("[Committer] Le Gating a rejete le patch. Annulation du commit.", file=sys.stderr)
        print("--- Sandbox STDERR ---", file=sys.stderr)
        print(sandbox_result.stderr, file=sys.stderr)
        sys.exit(1)

    print("[Committer] Gating Sandbox reussi. Integration du patch au workspace courant...")

    try:
        diff_only = extract_diff_section(patch_path)
    except ValueError as exc:
        print(f"[Committer] Patch inapplicable : {exc}", file=sys.stderr)
        sys.exit(1)

    tmp_patch = None
    try:
        with tempfile.NamedTemporaryFile(
                mode="w", suffix=".diff", prefix="wikiskill_",
                delete=False, encoding="utf-8") as fh:
            fh.write(diff_only)
            tmp_patch = fh.name

        subprocess.run(["git", "apply", "--check", tmp_patch],
                       cwd=repo_path, check=True, capture_output=True, text=True)
        subprocess.run(["git", "apply", tmp_patch], cwd=repo_path, check=True)

        skill_dir = os.path.join(".agents", "skills", skill_target)
        subprocess.run(["git", "add", skill_dir], cwd=repo_path, check=True)

        commit_msg = f"[WikiSkill] Update {skill_target}: {justification}"
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=repo_path, check=True)

        print(f"[Committer] Succes ! Commit cree : {commit_msg}")

    except subprocess.CalledProcessError as exc:
        print(f"[Committer] Erreur Git lors de l'application ou du commit : {exc}",
              file=sys.stderr)
        if exc.stderr:
            print(exc.stderr, file=sys.stderr)
        sys.exit(1)
    finally:
        if tmp_patch and os.path.exists(tmp_patch):
            os.remove(tmp_patch)


if __name__ == "__main__":
    main()
