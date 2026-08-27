#!/usr/bin/env bash
set -eu
dir=$(dirname "$0")
. "$dir/../lib/tesla-exit-codes.sh"
. "$dir/../lib/tesla-logging.sh"

"$dir/01-schema-validator.sh"
"$dir/02-secret-scanner.sh"
"$dir/03-scope-validator.sh"
"$dir/04-project-state-check.sh"
"$dir/05-marble-cert-check.sh"
"$dir/06-lint-check.sh"

tesla_log INFO "all pre-commit guardrails passed successfully"
exit "$TESLA_EXIT_OK"
