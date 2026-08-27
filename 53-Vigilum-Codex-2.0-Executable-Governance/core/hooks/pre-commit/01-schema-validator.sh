#!/usr/bin/env bash
set -eu
. "$(dirname "$0")/../lib/tesla-exit-codes.sh"
. "$(dirname "$0")/../lib/tesla-logging.sh"

files=$(git diff --cached --name-only --diff-filter=AM | grep -E '\.(json|yaml|yml)$' || true)
[ -n "$files" ] || exit "$TESLA_EXIT_OK"

for f in $files; do
  [ -f "$f" ] || continue
  if [[ "$f" =~ \.json$ ]]; then
    if ! python3 -m json.tool "$f" >/dev/null 2>&1; then
      tesla_log ERROR "invalid JSON syntax: $f"
      exit "$TESLA_EXIT_SCHEMA"
    fi
  else
    if ! python3 -c 'import sys, yaml; yaml.safe_load(open(sys.argv[1]))' "$f" >/dev/null 2>&1; then
      tesla_log ERROR "invalid YAML syntax: $f"
      exit "$TESLA_EXIT_SCHEMA"
    fi
  fi
done
tesla_log INFO "schema validation passed"
exit "$TESLA_EXIT_OK"
