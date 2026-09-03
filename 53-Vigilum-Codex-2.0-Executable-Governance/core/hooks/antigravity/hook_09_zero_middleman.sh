#!/usr/bin/env bash
# Hook 09 — Zero-Middleman (Phase 2 du Plan d'Intervention Correctif V2.5.0)
# Vigilum Codex 2.5.1 — audité & implémenté en verrou déterministe.
#
# Standardisation Sovereign Chat Directives (SCD) : l'IA est destituée de
# son rôle d'intermédiaire pour toutes les validations de sécurité.
# Interception de tout outil d'écriture (write_file, edit_file,
# apply_patch...) : la création ou modification d'un ARTEFACT
# D'AUTORISATION (.flag, .token, .approval, quittances de sous-agents,
# certificats de marbre, registres de nonces) est BLOQUÉE pour tous les
# agents (Exit 81 — ERR_AGENT_THEATER / BYPASS-01).
#
# La validation souveraine passe EXCLUSIVEMENT par :
#   - le transcript système lu par le Hook 07 (SCD) ;
#   - les outils déterministes du Control Plane (gate2_guard.py,
#     marble_certificate.py), invoqués hors canal d'écriture agent.
#
# Fail-closed (P10) : outil d'écriture sans chemin vérifiable => refus.
set -euo pipefail

HOOK_LIB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../lib" && pwd)"
exec python3 "$HOOK_LIB_DIR/tesla_zero_middleman.py" --mode hook
