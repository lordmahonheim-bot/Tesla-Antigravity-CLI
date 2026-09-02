#!/usr/bin/env bash
# Vigilum Codex 2.1.1 — Guardrail 04 : Project State & Memory Parity (Invariant M-014)
# 1) Project-state-file coherence guard (legacy).
# 2) Memory parity: when TESLA_ENFORCE_MEMORY_PARITY=1, runs
#    bin/memory_parite.py (manifest-driven 13 pillars, SHA-256) and BLOCKS the
#    commit with exit 40 on any desynchronization (BLOCKED/STALE_STATE) or
#    unobservable memory/ (UNKNOWN — P3: UNKNOWN != PASS).
set -eu

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODULE_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
. "$SCRIPT_DIR/../lib/tesla-exit-codes.sh"
. "$SCRIPT_DIR/../lib/tesla-logging.sh"

# 1) Project state file guard
state_file=${TESLA_PROJECT_STATE_FILE:-}
if [ -n "$state_file" ]; then
  [ -f "$state_file" ] || { tesla_log ERROR "project state file missing: $state_file"; exit "$TESLA_EXIT_STATE"; }

  staged=$(git diff --cached --name-only || true)
  if [ -n "$staged" ] && ! echo "$staged" | grep -F -x "$state_file" >/dev/null 2>&1; then
    if [ "${TESLA_REQUIRE_STATE_UPDATE:-0}" = "1" ]; then
      tesla_log ERROR "commit contains modifications without updating $state_file"
      exit "$TESLA_EXIT_STATE"
    fi
  fi
fi

# 2) Memory parity (Invariant M-014) — strict mode only, opt-in via env
if [ "${TESLA_ENFORCE_MEMORY_PARITY:-0}" = "1" ]; then
  tesla_root=${TESLA_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || echo "$PWD")}
  parity_log=$(mktemp)
  set +e
  python3 "$MODULE_ROOT/bin/memory_parite.py" --root "$tesla_root" \
    --mission "${TESLA_MISSION_ID:-SGC-EXEC-GOV-03}" >"$parity_log" 2>&1
  parity_code=$?
  set -e
  if [ "$parity_code" -ne 0 ]; then
    tesla_log ERROR "memory parity BLOCKED (exit $parity_code) — Invariant M-014: 13/13 piliers requis (manifest-driven)"
    tail -n 14 "$parity_log" >&2 || true
    rm -f "$parity_log"
    exit "$TESLA_EXIT_STATE"   # 40 = ERR_MEMORY_DESYNC
  fi
  rm -f "$parity_log"
  tesla_log INFO "memory parity passed (13/13 SHA-256, manifest-driven)"
fi

tesla_log INFO "project state & memory parity check passed"
exit "$TESLA_EXIT_OK"
