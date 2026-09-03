#!/bin/bash
# Hook 07 - Gate 2 Interceptor (Direct Sovereign Terminal Validation)
# Architecturally Validated by Curator-Prime.
# Security & Performance Patched by Master-Code & Arcanis-360.

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

# 2. Path Traversal Protection (Arcanis-360)
CONV_ID=$(echo "$PAYLOAD" | jq -r '.conversationId // empty')
if [[ ! "$CONV_ID" =~ ^[a-zA-Z0-9-]+$ ]]; then
  echo '{"decision": "deny", "reason": "Exit 81: Invalid Conversation ID format."}'
  exit 0
fi

TRANSCRIPT="/home/lord-mahonheim/.gemini/antigravity-cli/brain/$CONV_ID/.system_generated/logs/transcript.jsonl"
if [ ! -f "$TRANSCRIPT" ]; then
  echo '{"decision": "deny", "reason": "Exit 81: Transcript systeme inaccessible."}'
  exit 0
fi

# 3. O(1) Performance & Anti-Spoofing (Master-Code & Arcanis-360)
# tac reads backwards, stops at first match. jq verifies actual JSON type.
LAST_USER_INPUT=$(tac "$TRANSCRIPT" | grep -m 1 '"type":"USER_INPUT"')
if [ -z "$LAST_USER_INPUT" ]; then
  echo '{"decision": "deny", "reason": "Exit 81: Aucun input utilisateur trouve."}'
  exit 0
fi

IS_VALID_TYPE=$(echo "$LAST_USER_INPUT" | jq -r 'if .type == "USER_INPUT" then "true" else "false" end')
if [ "$IS_VALID_TYPE" != "true" ]; then
  echo '{"decision": "deny", "reason": "Exit 81: Tentative de spoofing IA detectee."}'
  exit 0
fi

USER_TEXT=$(echo "$LAST_USER_INPUT" | jq -r '.content // empty' | tr '[:upper:]' '[:lower:]' | xargs)
STEP_IDX=$(echo "$LAST_USER_INPUT" | jq -r '.step_index // empty')

if [[ ! "$STEP_IDX" =~ ^[0-9]+$ ]]; then
  echo '{"decision": "deny", "reason": "Exit 81: Step Index invalide."}'
  exit 0
fi

# 4. Strict Semantic Match (Arcanis-360)
CLEAN_TEXT=$(echo "$USER_TEXT" | tr -d '[:punct:]')
if [ "$CLEAN_TEXT" != "je valide" ] && [ "$CLEAN_TEXT" != "je valide laction" ] && [ "$CLEAN_TEXT" != "go" ]; then
  echo '{"decision": "deny", "reason": "Exit 81 (BYPASS-01 BLOCKED): La formulation stricte n a pas ete detectee."}'
  exit 0
fi

ROOT_DIR="$(git -C "$(dirname "${BASH_SOURCE[0]}")" rev-parse --show-toplevel 2>/dev/null)"
if [ -z "$ROOT_DIR" ]; then ROOT_DIR="/home/lord-mahonheim/bifrost/tesla"; fi

# 5. Atomic O_EXCL Anti-Replay (Master-Code)
STATE_FILE="$ROOT_DIR/runtime/gate2/consumed_step_${STEP_IDX}.lock"
mkdir -p "$(dirname "$STATE_FILE")"

if ! (set -C; echo "$STEP_IDX" > "$STATE_FILE") 2>/dev/null; then
  echo '{"decision": "deny", "reason": "Exit 81: Cette formulation a deja ete consommee (Anti-Rejeu O_EXCL)."}'
  exit 0
fi

echo '{"decision": "allow", "reason": "Validation stricte lue depuis le terminal (O_EXCL)."}'
exit 0
