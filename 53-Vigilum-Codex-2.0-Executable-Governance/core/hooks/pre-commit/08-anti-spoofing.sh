#!/usr/bin/env bash
# Vigilum Codex 2.1 — Guardrail 08 : Anti-Spoofing & Command Jurisdiction
# Enforces C1/C2 honesty: TESLA_AGENT_IDENTITY == agent_id payload.
set -eu

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$SCRIPT_DIR/../lib/tesla-exit-codes.sh"
. "$SCRIPT_DIR/../lib/tesla-logging.sh"

agent_env="${TESLA_AGENT_IDENTITY:-orchestrator}"
agent_payload="${TESLA_AGENT_PAYLOAD_ID:-$agent_env}"

# Anti-Spoofing Strict Check (Exit 81)
if [ "$agent_env" != "$agent_payload" ]; then
    tesla_log ERROR "Anti-Spoofing Triggered: Env identity ($agent_env) != Payload identity ($agent_payload)."
    exit 81
fi

# Note: The jurisdiction logic (blocking writes to authority domains)
# has been entirely delegated to Hook 09 (Zero-Middleman) to resolve deadlocks.

tesla_log INFO "Hook 08 Anti-Spoofing passed"
exit "$TESLA_EXIT_OK"
