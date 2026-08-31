#!/usr/bin/env bash
# Guardrail 04: project state & memory parity check
set -eu

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODULE_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
. "$SCRIPT_DIR/../lib/tesla-exit-codes.sh"
. "$SCRIPT_DIR/../lib/tesla-logging.sh"

staged=$(git diff --cached --name-only --diff-filter=ACM || true)
[ -n "$staged" ] || exit "$TESLA_EXIT_OK"

repo_root=$(git rev-parse --show-toplevel 2>/dev/null || echo "$PWD")
tesla_root="${TESLA_ROOT:-$repo_root}"

if [ "${TESLA_ENFORCE_MEMORY_PARITY:-0}" = "1" ] && [ -f "$MODULE_ROOT/bin/memory_parite.py" ]; then
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
