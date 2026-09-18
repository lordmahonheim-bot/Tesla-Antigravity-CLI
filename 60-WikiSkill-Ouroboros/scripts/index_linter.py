#!/usr/bin/env python3
"""index_linter.py - Gardien du budget semantique de l'index Wiki (4000 tokens).

REFACT Ouroboros Auto-Capture : la logique est exposee via lint_file()
(retourne un tuple au lieu de sys.exit) pour permettre sa reutilisation
par distiller.py et gating_judge.py. L'interface CLI est inchangee :
    python3 index_linter.py <path_to_index.tsv>
"""
from __future__ import annotations

import os
import sys

MAX_TOKENS = 4000
CHAR_PER_TOKEN = 4
REQUIRED_COLUMNS = ["ID", "PATTERN_NAME", "DOMAIN", "HITS", "RECENCY", "REL_PATH"]


def lint_file(filepath: str) -> tuple[bool, str]:
    """Valide un index TSV. Retourne (ok, message_detaille)."""
    if not os.path.exists(filepath):
        return False, f"Error: {filepath} n'existe pas."

    try:
        with open(filepath, "r", encoding="utf-8") as fh:
            content = fh.read()
    except OSError as exc:
        return False, f"Error: lecture impossible de {filepath}: {exc}"

    lines = [line for line in content.split("\n") if line.strip()]
    if not lines:
        return False, "Error: Le fichier index est vide."

    header_cleaned = [h.strip() for h in lines[0].split("\t")]
    if header_cleaned != REQUIRED_COLUMNS:
        return False, (
            "Error: En-tetes TSV invalides.\n"
            f"Attendu: {REQUIRED_COLUMNS}\nRecu: {header_cleaned}"
        )

    char_count = len(content)
    approx_tokens = char_count / CHAR_PER_TOKEN
    stats = f"Index stats: {char_count} chars, ~{approx_tokens:.0f} tokens."
    if approx_tokens > MAX_TOKENS:
        return False, (
            f"{stats}\n"
            f"Error: Limite de tokens depassee ({approx_tokens:.0f} > {MAX_TOKENS})."
        )
    return True, f"{stats}\nLinting passe avec succes."


def lint_index(filepath: str) -> None:
    """Point d'entree historique (CLI). Conserve pour compatibilite."""
    ok, message = lint_file(filepath)
    print(message)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python index_linter.py <path_to_index.tsv>")
        sys.exit(1)
    lint_index(sys.argv[1])
