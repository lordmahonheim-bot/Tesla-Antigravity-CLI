#!/usr/bin/env bash
# 03_avalon.sh - Versionnage et archivage horodaté dans le Cerveau Historique
PAYLOAD="$1"
FILE=$(jq -r '.file' "$PAYLOAD")
HASH=$(jq -r '.sha256' "$PAYLOAD")
START_TIME=$(date +%s%3N)
STATUS="OK"

YEAR=$(date +"%Y")
MONTH=$(date +"%m")
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
FILENAME=$(basename "$FILE")

ARCHIVE_DIR="Avalon/Archives/$YEAR/$MONTH"
mkdir -p "$ARCHIVE_DIR"

DEST="$ARCHIVE_DIR/${TIMESTAMP}_${HASH:0:7}_${FILENAME}"
cp "$FILE" "$DEST" || STATUS="ERROR"

[ "$STATUS" == "OK" ] && echo "      [Capability: Avalon] Archive canonique générée : $DEST"

END_TIME=$(date +%s%3N)
DURATION=$((END_TIME - START_TIME))

cat <<EOF > "/tmp/tesla_health/avalon_archiver.json"
{
  "id": "avalon_archiver",
  "version": "1.0",
  "status": "$STATUS",
  "duration_ms": $DURATION,
  "warnings": [],
  "errors": [],
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
}
EOF
[ "$STATUS" == "OK" ] || exit 1
