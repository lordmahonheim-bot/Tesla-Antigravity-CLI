#!/usr/bin/env bash
set -eu
. "$(dirname "$0")/../lib/tesla-exit-codes.sh"
. "$(dirname "$0")/../lib/tesla-logging.sh"

py_files=$(git diff --cached --name-only --diff-filter=AM | grep -E '\.py$' || true)
[ -n "$py_files" ] || exit "$TESLA_EXIT_OK"

for f in $py_files; do
  [ -f "$f" ] || continue
  if ! python3 -m py_compile "$f" >/dev/null 2>&1; then
    tesla_log ERROR "python syntax error in $f"
    exit "$TESLA_EXIT_LINT"
  fi
done

tesla_log INFO "lint check passed"
exit "$TESLA_EXIT_OK"
