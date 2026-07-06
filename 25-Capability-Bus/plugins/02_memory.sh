#!/usr/bin/env bash
# 02_memory.sh - Gestion des liens symboliques vers memory/
PAYLOAD="$1"
FILE=$(jq -r '.file' "$PAYLOAD")
EVENT=$(jq -r '.event' "$PAYLOAD")
START_TIME=$(date +%s%3N)
STATUS="OK"

if [ "$EVENT" == "FileChanged" ] || [ "$EVENT" == "FileCreated" ]; then
    FILENAME=$(basename "$FILE")
    MEMORY_DEST="memory/$FILENAME"
    ln -sf "$(realpath "$FILE")" "$MEMORY_DEST" || STATUS="ERROR"
    [ "$STATUS" == "OK" ] && echo "      [Capability: Memory] Lien virtuel mis à jour : $MEMORY_DEST"
fi

END_TIME=$(date +%s%3N)
DURATION=$((END_TIME - START_TIME))

cat <<EOF > "/tmp/tesla_health/memory_linker.json"
{
  "id": "memory_linker",
  "version": "1.0",
  "status": "$STATUS",
  "duration_ms": $DURATION,
  "warnings": [],
  "errors": [],
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
}
EOF
[ "$STATUS" == "OK" ] || exit 1
