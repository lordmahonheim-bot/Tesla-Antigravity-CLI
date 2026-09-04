#!/usr/bin/env bash
# Vigilum Codex 2.1 — Guardrail 10 : Pre-Flight Gate 0 (Autonome)
# Vérifie de manière autonome et directe l'état de l'environnement avant invoke_subagent.
set -eu

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$SCRIPT_DIR/../lib/tesla-exit-codes.sh"
. "$SCRIPT_DIR/../lib/tesla-logging.sh"

TESLA_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# 1. Racine résoluble
if [ ! -d "$TESLA_ROOT" ]; then
    tesla_log ERROR "Hook 10: TESLA_ROOT is not resolvable ($TESLA_ROOT)"
    exit "$TESLA_EXIT_ORCH"
fi

# 2. Runtime inscriptible
if [ ! -w "$TESLA_ROOT/runtime" ]; then
    tesla_log ERROR "Hook 10: runtime directory is not writable"
    exit "$TESLA_EXIT_ORCH"
fi

# 3. Transcript SCD lisible
if [ ! -r "$TESLA_ROOT/evidence/transcript.md" ]; then
    tesla_log ERROR "Hook 10: SCD transcript (evidence/transcript.md) is not readable"
    exit "$TESLA_EXIT_ORCH"
fi

tesla_log INFO "Hook 10 Pre-Flight Gate 0 passed"
exit "$TESLA_EXIT_OK"
