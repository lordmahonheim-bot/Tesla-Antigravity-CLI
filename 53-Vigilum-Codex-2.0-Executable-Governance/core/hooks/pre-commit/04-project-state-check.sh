#!/usr/bin/env bash
set -eu
. "$(dirname "$0")/../lib/tesla-exit-codes.sh"
. "$(dirname "$0")/../lib/tesla-logging.sh"

state_file=${TESLA_PROJECT_STATE_FILE:-}
[ -n "$state_file" ] || exit "$TESLA_EXIT_OK"
[ -f "$state_file" ] || { tesla_log ERROR "project state file missing: $state_file"; exit "$TESLA_EXIT_STATE"; }

staged=$(git diff --cached --name-only || true)
if [ -n "$staged" ] && ! echo "$staged" | grep -F -x "$state_file" >/dev/null 2>&1; then
  if [ "${TESLA_REQUIRE_STATE_UPDATE:-0}" = "1" ]; then
    tesla_log ERROR "commit contains modifications without updating $state_file"
    exit "$TESLA_EXIT_STATE"
  fi
fi

tesla_log INFO "project state check passed"
exit "$TESLA_EXIT_OK"
