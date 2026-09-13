#!/usr/bin/env python3
"""intent_formatter.py — Valide les propositions .intent.patch (budget sémantique + confinement).

Correction d'incident : le validateur lisait un bloc ```json alors que le
proposer écrivait un autre format. Il lit désormais le FORMAT CANONIQUE UNIFIÉ
`<!-- WIKISKILL_METADATA ... -->` (même format que git_committer et patch_broker).
"""
import argparse
import json
import re
import sys
import os

METADATA_RE = re.compile(r"<!--\s*WIKISKILL_METADATA\s*(.*?)\s*-->", re.DOTALL)


def main(argv) -> int:
    parser = argparse.ArgumentParser(description="Intent Formatter Validator")
    parser.add_argument("patch_file", type=str, help="Chemin vers le fichier .intent.patch")
    args = parser.parse_args(argv)

    if not os.path.isfile(args.patch_file):
        print(f"Erreur: Fichier introuvable - {args.patch_file}", file=sys.stderr)
        return 1

    try:
        with open(args.patch_file, "r", encoding="utf-8") as f:
            content = f.read()
    except IOError as e:
        print(f"Erreur de lecture: {e}", file=sys.stderr)
        return 1

    # 1. Extraction WIKISKILL_METADATA (commentaire HTML canonique)
    m = METADATA_RE.search(content)
    if not m:
        print("Erreur: Bloc WIKISKILL_METADATA introuvable (format canonique attendu).", file=sys.stderr)
        return 1

    try:
        metadata = json.loads(m.group(1))
    except json.JSONDecodeError as e:
        print(f"Erreur: JSON invalide - {e}", file=sys.stderr)
        return 1

    skill_target = metadata.get("skill_target")
    justification = metadata.get("justification", "")

    if not skill_target:
        print("Erreur: 'skill_target' manquant.", file=sys.stderr)
        return 1

    # 2. Validation de la Justification (budget sémantique)
    word_count = len(justification.split())
    if word_count > 50:
        print(f"Erreur: Justification trop longue ({word_count} mots). Max: 50 mots.", file=sys.stderr)
        return 1

    # 3. Extraction et validation du Diff
    diff_part = content[m.end():]
    diff_lines = diff_part.strip().splitlines()

    file_changes = []
    for line in diff_lines:
        if line.startswith("--- ") or line.startswith("+++ "):
            parts = line.split(maxsplit=1)
            if len(parts) > 1:
                path = parts[1].split("\t")[0].strip()
                if path.startswith("a/") or path.startswith("b/"):
                    path = path[2:]
                file_changes.append(path)

    if not file_changes:
        print("Erreur: Aucun diff unifié trouvé.", file=sys.stderr)
        return 1

    valid_paths = {
        f".agents/skills/{skill_target}/WIKI.md",
        f".agents/skills/{skill_target}/SKILL.md",
    }

    for path in file_changes:
        if path == "/dev/null":
            continue
        if path not in valid_paths:
            print(f"Erreur: Altération illégale. Le fichier {path} ne peut pas être modifié.", file=sys.stderr)
            return 1

    print("Validation réussie : budget et sécurité respectés.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
