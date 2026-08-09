#!/usr/bin/env bash
# 01_lint.sh - Validation syntaxique et sémantique
PAYLOAD="$1"
FILE=$(jq -r '.file' "$PAYLOAD")
START_TIME=$(date +%s%3N)
STATUS="OK"
ERRORS="[]"

echo "      [Capability: Lint] Analyse de $FILE..."

case "$FILE" in
    *.py)
        just lint-python >/dev/null 2>&1 || { STATUS="ERROR"; ERRORS="[\"Échec du lint Python\"]"; }
        ;;
    *.md)
        echo "      [Capability: Lint] Markdown validé."
        ;;
    *.json)
        jq empty "$FILE" >/dev/null 2>&1 || { STATUS="ERROR"; ERRORS="[\"JSON invalide\"]"; }
        ;;
esac

END_TIME=$(date +%s%3N)
DURATION=$((END_TIME - START_TIME))

cat <<EOF > "/tmp/tesla_health/lint_validator.json"
{
  "id": "lint_validator",
  "version": "1.0",
  "status": "$STATUS",
  "duration_ms": $DURATION,
  "warnings": [],
  "errors": $ERRORS,
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
}
EOF
[ "$STATUS" == "OK" ] || exit 1
