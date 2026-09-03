#!/usr/bin/env bash
# Hook 08 — Anti-Usurpation Git (Phase 1 du Plan d'Intervention Correctif V2.5.0)
# Vigilum Codex 2.5.1 — audité & implémenté en verrou déterministe.
#
# Interception OBLIGATOIRE de toutes les requêtes vers l'outil natif
# `run_command`. Toute commande Git qui n'est pas une lecture pure
# (status/log/diff/show/rev-parse...) est BLOQUÉE (Exit 81 — ERR_AGENT_THEATER,
# D-007) sauf pour l'appelant `tesla-github-manager`, seul titulaire de la
# juridiction Git (Règle Absolue N°4 : AGENTS délègue, il ne réimplémente pas).
#
# Extension V2.5.1 (audit) : la juridiction couvre aussi GitHub CLI (`gh`)
# et la lecture pure est explicitement autorisée — l'Orchestrateur doit
# pouvoir inspecter l'état (git status) pour la Gravure sur Marbre sans
# pouvoir muter le dépôt. Fail-closed : tout « git » non classé = rejet.
#
# Identité de l'appelant : TESLA_AGENT_IDENTITY (runtime) > champ payload
# agent_id > défaut "orchestrator" (moindre privilège).
#
# Performances : un seul processus Python, O(n) sur la commande, zéro I/O
# disque, zéro réseau.
set -euo pipefail

HOOK_LIB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../lib" && pwd)"
exec python3 "$HOOK_LIB_DIR/tesla_git_guard.py" --mode hook
