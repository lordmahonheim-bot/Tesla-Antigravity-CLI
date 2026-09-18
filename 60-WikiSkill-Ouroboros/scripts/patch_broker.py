#!/usr/bin/env python3
"""patch_broker.py - Sas de mediation pour les mutations de prompts (Phase C).

BUGFIX Ouroboros Auto-Capture : le broker rejetait systematiquement les
patches produits par skill_proposer.py / intent_formatter.py car il exigeait
un en-tete JSON brut alors que le format canonique utilise un bloc cloture
```json ... ```. Le broker tolere desormais les deux formes :
    1. bloc ```json ... ``` (canonique, emis par rule_forger.py)
    2. JSON brut (legacy)
Le format du diff (diff --git | --- a/ | --- ./) est inchange.

Usage: python patch_broker.py <path_to_patch>
"""
from __future__ import annotations

import json
import os
import re
import sys


def _strip_fences(json_section: str) -> str:
    """Retire les clotures markdown ```json ... ``` si presentes."""
    text = json_section.strip()
    fence = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
    if fence:
        return fence.group(1).strip()
    # Nettoyage d'un eventuel delimiteur manuel (legacy).
    text = re.sub(r"^---+\s*$", "", text, flags=re.MULTILINE).strip()
    return text


def validate_patch(filepath: str) -> tuple[bool, str, dict]:
    """Valide un patch. Retourne (ok, message, metadata)."""
    if not os.path.exists(filepath):
        return False, f"Error: {filepath} introuvable.", {}

    with open(filepath, "r", encoding="utf-8") as fh:
        content = fh.read()

    # Recherche du point de depart du Unified Diff.
    diff_start_match = re.search(
        r"^(diff --git|--- a/|--- \./)", content, re.MULTILINE)
    if not diff_start_match:
        return False, "Error: Aucune section Unified Diff valide trouvee dans le patch.", {}

    diff_start_idx = diff_start_match.start()
    json_section = _strip_fences(content[:diff_start_idx])

    try:
        metadata = json.loads(json_section)
    except json.JSONDecodeError as exc:
        return False, f"Error: En-tete JSON invalide. {exc}", {}

    if not isinstance(metadata, dict):
        return False, "Error: L'en-tete JSON doit etre un objet.", {}

    required_keys = {"skill_target", "justification", "parent_hash"}
    if not required_keys.issubset(metadata.keys()):
        missing = required_keys - metadata.keys()
        return False, f"Error: Cles JSON manquantes: {sorted(missing)}", {}

    message = (
        "Patch valide avec succes (Structure JSON & format Diff OK).\n"
        f"Target: {metadata['skill_target']}, "
        f"Parent Hash: {metadata['parent_hash']}"
    )
    return True, message, metadata


def process_patch(filepath: str) -> None:
    """Point d'entree historique (CLI). Conserve pour compatibilite."""
    ok, message, _metadata = validate_patch(filepath)
    print(message)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python patch_broker.py <path_to_patch>")
        sys.exit(1)
    process_patch(sys.argv[1])
