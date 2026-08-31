#!/usr/bin/env bash
# Vigilum Codex 2.1 — Guardrail 07 : Orchestration Gate (Gate 2 + Anti-Usurpation)
# Deterministic enforcement of RETEX E7: any Team-Synergy synthesis artifact or
# Mission Graph / contract change staged for commit is BLOCKED unless an
# approved (sealed) DAG and the physical subagent receipt quorum are present.
set -eu

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODULE_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
. "$SCRIPT_DIR/../lib/tesla-exit-codes.sh"
. "$SCRIPT_DIR/../lib/tesla-logging.sh"

staged=$(git diff --cached --name-only --diff-filter=ACM || true)
[ -n "$staged" ] || exit "$TESLA_EXIT_OK"

repo_root=$(git rev-parse --show-toplevel 2>/dev/null || echo "$PWD")

# Fast path: detect trigger files (explicit markers only — no heuristics).
trigger=0
for f in $staged; do
  case "$f" in
    *mission_graph* | */contracts/* | *.team-synergy* | *.synergy*)
      trigger=1
      ;;
    *.json | *.yaml | *.yml)
      if [ -f "$f" ]; then
        # Marker detection: YAML (team_synergy: true) and JSON ("team_synergy": true)
        if grep -qE "[\"']?(team_synergy|x-vigilum-team-synergy)[\"']?[[:space:]]*:[[:space:]]*true" "$f" 2>/dev/null; then
          trigger=1
        fi
      fi
      ;;
  esac
  [ "$trigger" = 1 ] && break
done

[ "$trigger" = 1 ] || exit "$TESLA_EXIT_OK"

GATE="$MODULE_ROOT/core/orchestration/orchestration_gate.py"
if [ ! -f "$GATE" ]; then
  tesla_log ERROR "orchestration gate tool missing: $GATE"
  exit "$TESLA_EXIT_ORCH"
fi

targets=""
for f in $staged; do
  targets="$targets --target $f"
done

if ! python3 "$GATE" intent-guard --root "$repo_root" $targets; then
  tesla_log ERROR "orchestration gate BLOCKED (Gate 2 / Anti-Usurpation): Team-Synergy synthesis without approved DAG + receipt quorum"
  exit "$TESLA_EXIT_ORCH"
fi

tesla_log INFO "orchestration gate passed (Gate 2 approved, receipt quorum satisfied)"
exit "$TESLA_EXIT_OK"
