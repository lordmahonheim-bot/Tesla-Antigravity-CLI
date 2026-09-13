#!/usr/bin/env python3
"""
intent_formatter.py - Valide les propositions .intent.patch.
Vérifie le budget sémantique et restreint les modifications de fichiers.
"""
import argparse
import json
import re
import sys
import os

def main() -> None:
    parser = argparse.ArgumentParser(description="Intent Formatter Validator")
    parser.add_argument("patch_file", type=str, help="Chemin vers le fichier .intent.patch")
    args = parser.parse_args()

    if not os.path.isfile(args.patch_file):
        print(f"Erreur: Fichier introuvable - {args.patch_file}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(args.patch_file, "r", encoding="utf-8") as f:
            content = f.read()
    except IOError as e:
        print(f"Erreur de lecture: {e}", file=sys.stderr)
        sys.exit(1)

    # 1. Extraction WIKISKILL_METADATA
    json_match = re.search(r"```json\s*(.*?)\s*```", content, re.DOTALL)
    if not json_match:
        print("Erreur: Bloc JSON métadonnées introuvable.", file=sys.stderr)
        sys.exit(1)

    try:
        metadata = json.loads(json_match.group(1))
    except json.JSONDecodeError as e:
        print(f"Erreur: JSON invalide - {e}", file=sys.stderr)
        sys.exit(1)

    skill_target = metadata.get("skill_target")
    justification = metadata.get("justification", "")

    if not skill_target:
        print("Erreur: 'skill_target' manquant.", file=sys.stderr)
        sys.exit(1)

    # 2. Validation de la Justification
    word_count = len(justification.split())
    if word_count > 50:
        print(f"Erreur: Justification trop longue ({word_count} mots). Max: 50 mots.", file=sys.stderr)
        sys.exit(1)

    # 3. Extraction et validation du Diff
    diff_part = content[json_match.end():]
    diff_lines = diff_part.strip().splitlines()
    
    file_changes = []
    for line in diff_lines:
        if line.startswith("--- ") or line.startswith("+++ "):
            parts = line.split(maxsplit=1)
            if len(parts) > 1:
                # Nettoyage des préfixes Git potentiels (a/, b/)
                path = parts[1].split("\t")[0].strip()
                if path.startswith("a/") or path.startswith("b/"):
                    path = path[2:]
                file_changes.append(path)

    if not file_changes:
        print("Erreur: Aucun diff unifié trouvé.", file=sys.stderr)
        sys.exit(1)

    valid_paths = {
        f".agents/skills/{skill_target}/WIKI.md",
        f".agents/skills/{skill_target}/SKILL.md"
    }

    for path in file_changes:
        if path == "/dev/null":
            continue
        if path not in valid_paths:
            print(f"Erreur: Altération illégale. Le fichier {path} ne peut pas être modifié.", file=sys.stderr)
            sys.exit(1)

    print("Validation réussie : budget et sécurité respectés.")
    sys.exit(0)

if __name__ == "__main__":
    main()
