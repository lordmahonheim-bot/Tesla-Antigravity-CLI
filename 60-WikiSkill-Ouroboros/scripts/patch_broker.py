#!/usr/bin/env python3
"""patch_broker.py — Courtier de patchs .intent.patch (structure & confinement).

Correction d'incident : lit désormais le FORMAT CANONIQUE UNIFIÉ
`<!-- WIKISKILL_METADATA ... -->` (identique à git_committer et intent_formatter).
"""
import sys
import json
import re
import os

METADATA_RE = re.compile(r"<!--\s*WIKISKILL_METADATA\s*(.*?)\s*-->", re.DOTALL)


def process_patch(filepath: str) -> int:
    if not os.path.exists(filepath):
        print(f"Error: {filepath} introuvable.")
        return 1

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    m = METADATA_RE.search(content)
    if not m:
        print("Error: Bloc WIKISKILL_METADATA introuvable.")
        return 1

    try:
        metadata = json.loads(m.group(1))
    except json.JSONDecodeError as e:
        print(f"Error: JSON invalide dans les métadonnées. {e}")
        return 1

    required_keys = {"skill_target", "justification", "parent_hash"}
    if not required_keys.issubset(metadata.keys()):
        missing = required_keys - metadata.keys()
        print(f"Error: Clés JSON manquantes: {missing}")
        return 1

    # Vérification de la présence d'une section Unified Diff valide
    diff_start_match = re.search(r"^(?:diff --git|--- |\+\+\+)", content, re.MULTILINE)
    if not diff_start_match:
        print("Error: Aucune section Unified Diff valide trouvée dans le patch.")
        return 1

    print("Patch validé avec succès (Structure JSON & format Diff OK).")
    print(f"Target: {metadata['skill_target']}, Parent Hash: {metadata['parent_hash']}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <path_to_patch>", file=sys.stderr)
        sys.exit(1)
    sys.exit(process_patch(sys.argv[1]))
