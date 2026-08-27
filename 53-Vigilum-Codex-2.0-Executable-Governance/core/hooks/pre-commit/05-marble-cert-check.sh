#!/usr/bin/env bash
set -eu
. "$(dirname "$0")/../lib/tesla-exit-codes.sh"
. "$(dirname "$0")/../lib/tesla-logging.sh"

cert_files=$(git diff --cached --name-only --diff-filter=AM | grep -E '^CERTIFICATES/.*\.json$' || true)
[ -n "$cert_files" ] || exit "$TESLA_EXIT_OK"

for f in $cert_files; do
  [ -f "$f" ] || continue
  if ! python3 -m json.tool "$f" >/dev/null 2>&1; then
    tesla_log ERROR "invalid marble certificate syntax: $f"
    exit "$TESLA_EXIT_MARBLE"
  fi
done

tesla_log INFO "marble certificate validation passed"
exit "$TESLA_EXIT_OK"
