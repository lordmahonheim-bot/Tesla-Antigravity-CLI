#!/usr/bin/env bash
# Hook 10 — Pre-Flight Checklist Gate 0 (Phase 3 du Plan V2.5.0)
# Vigilum Codex 2.5.1 — audité & implémenté en verrou déterministe.
#
# Éradication du « Shoot-First » : vérification PROACTIVE des privilèges
# physiques AVANT l'exécution d'un outil sensible.
#   - invoke_subagent  : racine workspace, runtime inscriptible, sonde de
#     capacités PASS (U-006/P3 : probe absente => UNKNOWN => BLOCKED),
#     transcript SCD lisible si cerveau configuré.
#   - run_command      : élévation de privilèges (sudo/su/pkexec/doas)
#     refusée sauf autorisation posée dans le terminal hôte ; pré-vol de
#     privilèges avant toute mutation Git du titulaire de juridiction.
#
# Note d'audit (V2.5.1) : la version du plan V2.5.0 proposait « d'injecter
# la routine dans le Moteur Cognitif ». Cela aurait été un retour à la
# gouvernance par le verbe (violation P4). L'implémentation canonique est
# cet intercepteur déterministe au niveau du runtime.
set -euo pipefail

HOOK_LIB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../lib" && pwd)"
exec python3 "$HOOK_LIB_DIR/tesla_preflight.py" --mode hook
