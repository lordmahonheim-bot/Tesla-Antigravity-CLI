#!/usr/bin/env bash
# Vigilum Codex 2.1 — Guardrail 08 : Draft / Ephemeral Artifact Guard
# Deterministic enforcement of RETEX E5 (Encombrement du Creuset): drafts,
# temporary files and non-canonical versioned documents are refused at commit.
# Canonical finals (LOCKED / FINAL / CANON / SPEC / SEALED) remain allowed.
# Override for intentional canonicalization: TESLA_ALLOW_DRAFT_COMMIT=1
set -eu

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$SCRIPT_DIR/../lib/tesla-exit-codes.sh"
. "$SCRIPT_DIR/../lib/tesla-logging.sh"

staged=$(git diff --cached --name-only --diff-filter=ACM || true)
[ -n "$staged" ] || exit "$TESLA_EXIT_OK"

if [ "${TESLA_ALLOW_DRAFT_COMMIT:-0}" = "1" ]; then
  tesla_log INFO "draft guard overridden by TESLA_ALLOW_DRAFT_COMMIT=1"
  exit "$TESLA_EXIT_OK"
fi

blocked=""
for f in $staged; do
  base=$(basename "$f")
  reason=""

  case "$base" in
    *.tmp | *.bak | *.orig | *.swp | *.swo | *~ | .DS_Store)
      reason="EPHEMERAL_EXTENSION"
      ;;
  esac

  if [ -z "$reason" ] && [[ "$base" =~ ^.*[Vv][0-9]+(\.[0-9]+)+.*\.(md|markdown)$ ]]; then
    if ! [[ "$base" =~ (LOCKED|FINAL|CANON|SPEC|SEALED|DIAGNOSTIC) ]]; then
      reason="DRAFT_VERSION_DOC"
    fi
  fi

  if [ -z "$reason" ] && [[ "$f" == */.runtime/* ]]; then
    reason="RUNTIME_SCRATCH"
  fi

  if [ -n "$reason" ]; then
    blocked="$blocked\n  - $f [$reason]"
  fi
done

if [ -n "$blocked" ]; then
  tesla_log ERROR "draft/ephemeral artifacts blocked at commit:$blocked"
  tesla_log ERROR "override only if intentional: TESLA_ALLOW_DRAFT_COMMIT=1 (canonicalisation documentée)"
  exit "$TESLA_EXIT_DRAFT"
fi

tesla_log INFO "draft artifact guard passed"
exit "$TESLA_EXIT_OK"
