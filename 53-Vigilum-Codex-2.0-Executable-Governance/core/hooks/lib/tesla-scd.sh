#!/usr/bin/env bash
# Vigilum Codex 2.5.1 — Bibliothèque SCD (Sovereign Chat Directives).
#
# Phase 2 du Plan d'Intervention Correctif V2.5.0 : la lecture du
# `transcript.jsonl` système (via `tac`) devient LA méthode universelle et
# EXCLUSIVE de validation des directives souveraines. Aucun jeton de
# sécurité n'est négociable par fichier `.flag` écrit par l'agent
# (verrou complémentaire : hook_09_zero_middleman).
#
# Principe (P9 — Souveraineté Humaine) : la preuve d'autorisation vit dans
# le canal terminal de l'humain, hors du périmètre d'écriture de l'agent.
# L'agent ne peut ni forger ni rejouer une directive (anti-rejeu O_EXCL).
#
# Portabilité V2.5.1 (audit) : la racine du cerveau Antigravity est
# résolue dans cet ordre :
#   1. TESLA_BRAIN_ROOT (variable d'environnement)
#   2. /home/lord-mahonheim/.gemini/antigravity-cli/brain (défaut historique)
# Fail-closed : transcript absent ou illisible => refus.

# Racine du cerveau (transcripts système Antigravity).
tesla_scd_brain_root() {
  if [ -n "${TESLA_BRAIN_ROOT:-}" ]; then
    printf '%s' "$TESLA_BRAIN_ROOT"
  else
    printf '%s' "/home/lord-mahonheim/.gemini/antigravity-cli/brain"
  fi
}

# Chemin canonique du transcript pour un identifiant de conversation.
# Retour 1 si l'ID est malformé (protection path traversal).
tesla_scd_transcript_path() {
  local conv_id="$1"
  if [[ ! "$conv_id" =~ ^[a-zA-Z0-9-]+$ ]]; then
    return 1
  fi
  printf '%s/%s/.system_generated/logs/transcript.jsonl' "$(tesla_scd_brain_root)" "$conv_id"
}

# Dernière directive souveraine (type USER_INPUT) lue en O(queue) depuis la
# fin du transcript (tac | grep -m 1). Exporte SCD_TEXT et SCD_STEP_IDX.
# Retour 0 = directive lue et typée ; 1 = refus (raison dans SCD_REASON).
tesla_scd_read_last_directive() {
  local transcript="$1"
  SCD_REASON=""
  if [ ! -f "$transcript" ]; then
    SCD_REASON="Transcript systeme inaccessible."
    return 1
  fi
  local last_input
  last_input=$(tac "$transcript" 2>/dev/null | grep -m 1 '"type":"USER_INPUT"')
  if [ -z "$last_input" ]; then
    SCD_REASON="Aucun input utilisateur trouve."
    return 1
  fi
  local is_valid_type
  is_valid_type=$(echo "$last_input" | jq -r 'if .type == "USER_INPUT" then "true" else "false" end')
  if [ "$is_valid_type" != "true" ]; then
    SCD_REASON="Tentative de spoofing IA detectee."
    return 1
  fi
  SCD_TEXT=$(echo "$last_input" | jq -r '.content // empty' | tr '[:upper:]' '[:lower:]' | xargs)
  SCD_STEP_IDX=$(echo "$last_input" | jq -r '.step_index // empty')
  if [[ ! "$SCD_STEP_IDX" =~ ^[0-9]+$ ]]; then
    SCD_REASON="Step Index invalide."
    return 1
  fi
  return 0
}

# Normalisation stricte (ponctuation retirée, minuscules, trim).
tesla_scd_clean_text() {
  printf '%s' "$1" | tr -d '[:punct:]' | xargs
}

# Formulations souveraines canoniques EXHAUSTIVES (matching strict après
# normalisation ; toute autre formulation est rejetée — anti-spoofing).
tesla_scd_is_valid_directive() {
  local clean="$1"
  case "$clean" in
    "je valide"|"je valide laction"|"go") return 0 ;;
    *) return 1 ;;
  esac
}

# Consommation anti-rejeu d'une directive (Invariant A-003 : O_CREAT|O_EXCL).
# Retour 0 = consommée ; 1 = déjà consommée (rejeu détecté).
tesla_scd_consume() {
  local step_idx="$1" root="$2"
  local state_file="$root/runtime/gate2/consumed_step_${step_idx}.lock"
  mkdir -p "$(dirname "$state_file")"
  if (set -C; echo "$step_idx" > "$state_file") 2>/dev/null; then
    return 0
  fi
  return 1
}
