#!/usr/bin/env python3
"""intent_formatter.py - Valide les propositions .intent.patch.

Verifie le budget semantique (justification <= 50 mots) et restreint les
modifications aux fichiers WIKI.md / SKILL.md du skill cible.

REFACT Ouroboros Auto-Capture : la logique est exposee via validate_patch()
(retourne un tuple) pour reutilisation par gating_judge.py et
ouroboros_cycle.py. L'interface CLI est inchangee.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

MAX_JUSTIFICATION_WORDS = 50


def validate_patch(patch_file: str) -> tuple[bool, str, dict]:
    """Valide un .intent.patch. Retourne (ok, message, metadata)."""
    if not os.path.isfile(patch_file):
        return False, f"Erreur: Fichier introuvable - {patch_file}", {}

    try:
        with open(patch_file, "r", encoding="utf-8") as fh:
            content = fh.read()
    except OSError as exc:
        return False, f"Erreur de lecture: {exc}", {}

    # 1. Extraction WIKISKILL_METADATA (bloc ```json canonique).
    json_match = re.search(r"```json\s*(.*?)\s*```", content, re.DOTALL)
    if not json_match:
        return False, "Erreur: Bloc JSON metadonnees introuvable.", {}

    try:
        metadata = json.loads(json_match.group(1))
    except json.JSONDecodeError as exc:
        return False, f"Erreur: JSON invalide - {exc}", {}

    if not isinstance(metadata, dict):
        return False, "Erreur: Les metadonnees doivent etre un objet JSON.", {}

    skill_target = metadata.get("skill_target")
    justification = metadata.get("justification", "")

    if not skill_target:
        return False, "Erreur: 'skill_target' manquant.", {}

    # 2. Validation de la Justification (budget semantique).
    word_count = len(str(justification).split())
    if word_count > MAX_JUSTIFICATION_WORDS:
        return False, (
            f"Erreur: Justification trop longue ({word_count} mots). "
            f"Max: {MAX_JUSTIFICATION_WORDS} mots."
        ), {}

    # 3. Extraction et validation du Diff.
    diff_part = content[json_match.end():]
    diff_lines = diff_part.strip().splitlines()

    file_changes: list[str] = []
    for line in diff_lines:
        if line.startswith("--- ") or line.startswith("+++ "):
            parts = line.split(maxsplit=1)
            if len(parts) > 1:
                path = parts[1].split("\t")[0].strip()
                if path.startswith("a/") or path.startswith("b/"):
                    path = path[2:]
                file_changes.append(path)

    if not file_changes:
        return False, "Erreur: Aucun diff unifie trouve.", {}

    valid_paths = {
        f".agents/skills/{skill_target}/WIKI.md",
        f".agents/skills/{skill_target}/SKILL.md",
    }

    for path in file_changes:
        if path == "/dev/null":
            continue
        if path not in valid_paths:
            return False, (
                f"Erreur: Alteration illegale. Le fichier {path} "
                "ne peut pas etre modifie."
            ), {}

    return True, "Validation reussie : budget et securite respectes.", metadata


def main() -> None:
    parser = argparse.ArgumentParser(description="Intent Formatter Validator")
    parser.add_argument("patch_file", type=str, help="Chemin vers le fichier .intent.patch")
    args = parser.parse_args()
    ok, message, _metadata = validate_patch(args.patch_file)
    print(message, file=sys.stderr if not ok else sys.stdout)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
