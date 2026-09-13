#!/usr/bin/env python3
"""skill_proposer.py — Moteur d'Inférence (simulateur) de WikiSkill.

Génère un fichier .intent.patch au FORMAT CANONIQUE UNIFIÉ :
  * en-tête métadonnées dans un commentaire HTML `<!-- WIKISKILL_METADATA ... -->`
    (toléré par les outils de diff, lisible par git_committer / intent_formatter /
    patch_broker — correction d'incident : les 4 consommateurs du patch
    s'accordaient sur 3 formats incompatibles) ;
  * puis un Unified Diff modifiant uniquement WIKI.md / SKILL.md du skill ciblé.
"""
import argparse
import json
import os
import sys
import uuid


def build_patch(skill_target: str) -> str:
    metadata = {
        "skill_target": skill_target,
        "justification": "Ajout d'une règle de sécurité critique pour l'exécution de code. "
                         "Cette règle permet de garantir la stabilité et d'empêcher les régressions silencieuses.",
        "parent_hash": "a1b2c3d4e5f67890",
    }

    diff_content = (
        f"--- a/.agents/skills/{skill_target}/WIKI.md\n"
        f"+++ b/.agents/skills/{skill_target}/WIKI.md\n"
        "@@ -10,3 +10,7 @@\n"
        " - Respecter les standards de code.\n"
        " - Documenter les fonctions complexes.\n"
        " - Utiliser le typage strict.\n"
        "+\n"
        "+## Règles de Sécurité\n"
        "+- Ne jamais exécuter de commandes destructrices sans confirmation.\n"
        "+- Valider les entrées (Gating) avant chaque exécution.\n"
    )

    return (
        "<!-- WIKISKILL_METADATA\n"
        + json.dumps(metadata, indent=2, ensure_ascii=False)
        + "\n-->\n\n"
        + diff_content
    )


def main(argv) -> int:
    parser = argparse.ArgumentParser(description="Skill Proposer (Inference Engine Simulator)")
    parser.add_argument("skill_target", type=str, help="Le skill ciblé (ex: tesla-master-code)")
    parser.add_argument("--proposal-dir", default="", help="Répertoire de sortie (défaut : .agents/skills/tesla-wiki-manager/proposals)")
    args = parser.parse_args(argv)

    proposal_dir = args.proposal_dir or os.path.join(".agents", "skills", "tesla-wiki-manager", "proposals")
    try:
        os.makedirs(proposal_dir, exist_ok=True)
    except OSError as e:
        print(f"Erreur lors de la création du répertoire : {e}", file=sys.stderr)
        return 1

    proposal_id = str(uuid.uuid4())
    patch_filename = f"{proposal_id}.intent.patch"
    patch_filepath = os.path.join(proposal_dir, patch_filename)

    try:
        with open(patch_filepath, "w", encoding="utf-8") as f:
            f.write(build_patch(args.skill_target))
        print(f"Proposition générée avec succès : {patch_filepath}")
    except IOError as e:
        print(f"Erreur d'écriture du fichier : {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
