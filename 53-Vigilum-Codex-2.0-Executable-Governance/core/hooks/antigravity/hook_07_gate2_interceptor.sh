#!/bin/bash
# Hook 07 - Gate 2 Interceptor (Direct Sovereign Terminal Validation)
# Architecturally Validated by Curator-Prime.
# Security & Performance Patched by Master-Code & Arcanis-360.
# V2.5.1 — Refactoré sur la bibliothèque SCD (lib/tesla-scd.sh) :
# la lecture du transcript.jsonl devient la méthode UNIVERSELLE et
# EXCLUSIVE de validation des directives souveraines (Phase 2 du plan
# V2.5.0 — protocole Sovereign Chat Directives, Zero-Middleman).
# Racine du cerveau configurable via TESLA_BRAIN_ROOT (portabilité).

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$SCRIPT_DIR/../lib/tesla-scd.sh"

PAYLOAD=$(cat)
TOOL_NAME=$(echo "$PAYLOAD" | jq -r '.toolCall.name // empty')

if [ "$TOOL_NAME" != "invoke_subagent" ]; then
  echo '{"decision": "allow"}'
  exit 0
fi

# 1. Robust Bash Types (Master-Code)
NUM_AGENTS=$(echo "$PAYLOAD" | jq -r '.toolCall.args.Subagents | length? // 0' 2>/dev/null || echo "0")
if [[ ! "$NUM_AGENTS" =~ ^[0-9]+$ ]] || [ "$NUM_AGENTS" -le 1 ]; then
  echo '{"decision": "allow", "reason": "Single agent allowed."}'
  exit 0
fi

# 2. Path Traversal Protection (Arcanis-360) — via lib SCD
CONV_ID=$(echo "$PAYLOAD" | jq -r '.conversationId // empty')
if ! TRANSCRIPT=$(tesla_scd_transcript_path "$CONV_ID"); then
  echo '{"decision": "deny", "reason": "Exit 81: Invalid Conversation ID format."}'
  exit 0
fi

# 3-4. Lecture inverse O(1) + anti-spoofing + extraction typée (lib SCD)
if ! tesla_scd_read_last_directive "$TRANSCRIPT"; then
  echo "{\"decision\": \"deny\", \"reason\": \"Exit 81: $SCD_REASON\"}"
  exit 0
fi

# 5. Strict Semantic Match (Arcanis-360) — formulations canoniques SCD
CLEAN_TEXT=$(tesla_scd_clean_text "$SCD_TEXT")
if ! tesla_scd_is_valid_directive "$CLEAN_TEXT"; then
  echo '{"decision": "deny", "reason": "Exit 81 (BYPASS-01 BLOCKED): La formulation stricte n a pas ete detectee."}'
  exit 0
fi

ROOT_DIR="${TESLA_ROOT:-$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null)}"
if [ -z "$ROOT_DIR" ]; then ROOT_DIR="/home/lord-mahonheim/bifrost/tesla"; fi

# 6. Atomic O_EXCL Anti-Replay (Master-Code) — consommation SCD
if ! tesla_scd_consume "$SCD_STEP_IDX" "$ROOT_DIR"; then
  echo '{"decision": "deny", "reason": "Exit 81: Cette formulation a deja ete consommee (Anti-Rejeu O_EXCL)."}'
  exit 0
fi

echo '{"decision": "allow", "reason": "Validation stricte lue depuis le terminal (O_EXCL)."}'
exit 0
