#!/usr/bin/env bash
# Main pre-commit hook aggregator for Tesla Vigilum Codex
set -eu

dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$dir/../lib/tesla-exit-codes.sh"
. "$dir/../lib/tesla-logging.sh"

tesla_log INFO "running pre-commit guardrails..."

"$dir/01-schema-validator.sh"
"$dir/02-secret-scanner.sh"
"$dir/03-scope-validator.sh"
"$dir/04-project-state-check.sh"
"$dir/05-marble-cert-check.sh"
"$dir/06-lint-check.sh"
"$dir/07-orchestration-gate.sh"
"$dir/08-draft-artifact-guard.sh"

tesla_log INFO "all pre-commit guardrails passed successfully"
exit "$TESLA_EXIT_OK"
