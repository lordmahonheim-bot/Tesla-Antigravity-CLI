#!/usr/bin/env bash
set -eu
. "$(dirname "$0")/../lib/tesla-exit-codes.sh"
. "$(dirname "$0")/../lib/tesla-logging.sh"

allowed_prefixes=${TESLA_ALLOWED_PATH_PREFIXES:-}
[ -n "$allowed_prefixes" ] || exit "$TESLA_EXIT_OK"

for f in $(git diff --cached --name-only --diff-filter=AM || true); do
  allowed=false
  for p in $allowed_prefixes; do
    if [[ "$f" == "$p"* ]]; then
      allowed=true
      break
    fi
  done
  if [ "$allowed" = false ]; then
    tesla_log ERROR "file outside allowed scope prefixes: $f"
    exit "$TESLA_EXIT_SCOPE"
  fi
done

tesla_log INFO "scope validation passed"
exit "$TESLA_EXIT_OK"
