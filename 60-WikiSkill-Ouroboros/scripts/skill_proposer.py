#!/usr/bin/env python3
"""
skill_proposer.py - Simule le Moteur d'Inférence pour WikiSkill.
Génère un fichier .intent.patch avec métadonnées JSON et Diff unifié.
"""
import argparse
import json
import os
import uuid
import sys

def main() -> None:
    parser = argparse.ArgumentParser(description="Skill Proposer (Inference Engine Simulator)")
    parser.add_argument("skill_target", type=str, help="Le skill ciblé (ex: tesla-master-code)")
    args = parser.parse_args()

    proposal_dir = os.path.join(".agents", "skills", "tesla-wiki-manager", "proposals")
    try:
        os.makedirs(proposal_dir, exist_ok=True)
    except OSError as e:
        print(f"Erreur lors de la création du répertoire : {e}", file=sys.stderr)
        sys.exit(1)

    proposal_id = str(uuid.uuid4())
    patch_filename = f"{proposal_id}.intent.patch"
    patch_filepath = os.path.join(proposal_dir, patch_filename)

    metadata = {
        "skill_target": args.skill_target,
        "justification": "Ajout d'une règle de sécurité critique pour l'exécution de code. "
                         "Cette règle permet de garantir la stabilité et d'empêcher les régressions silencieuses.",
        "parent_hash": "a1b2c3d4e5f67890"
    }

    # Diff factice, modifiant WIKI.md
    diff_content = f"""--- .agents/skills/{args.skill_target}/WIKI.md
+++ .agents/skills/{args.skill_target}/WIKI.md
@@ -10,3 +10,7 @@
 - Respecter les standards de code.
 - Documenter les fonctions complexes.
 - Utiliser le typage strict.
+
+## Règles de Sécurité
+- Ne jamais exécuter de commandes destructrices sans confirmation.
+- Valider les entrées (Gating) avant chaque exécution.
"""

    try:
        with open(patch_filepath, "w", encoding="utf-8") as f:
            f.write("```json\n")
            f.write(json.dumps(metadata, indent=4) + "\n")
            f.write("```\n\n")
            f.write(diff_content)
        print(f"Proposition générée avec succès : {patch_filepath}")
    except IOError as e:
        print(f"Erreur d'écriture du fichier : {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
