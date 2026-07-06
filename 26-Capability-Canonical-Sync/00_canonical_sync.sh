#!/usr/bin/env bash
# 00_canonical_sync.sh - Moteur de synchronisation de la Source de Vérité vers ses miroirs
PAYLOAD="$1"
FILE=$(jq -r '.file' "$PAYLOAD")
START_TIME=$(date +%s%3N)

STATUS="OK"
FILES_SYNCED=0
FILES_SKIPPED=0
ERRORS="[]"

BASENAME=$(basename "$FILE")
SOURCES_JSON="$(dirname "$0")/../sources.json"
LOG_FILE="Avalon/SYNC_LOG.md"
mkdir -p "Avalon"

echo "      [Capability: Canonical Sync] Évaluation de $BASENAME..."

if [ -f "$SOURCES_JSON" ]; then
    # Vérifier si le fichier est dans la carte des sources
    ENTRY=$(jq -r --arg bn "$BASENAME" '.[$bn]' "$SOURCES_JSON")
    
    if [ "$ENTRY" != "null" ]; then
        CANONICAL_PATH=$(jq -r --arg bn "$BASENAME" '.[$bn].canonical' "$SOURCES_JSON")
        REAL_FILE=$(realpath "$FILE")
        
        if [ "$REAL_FILE" == "$CANONICAL_PATH" ]; then
            TARGETS=$(jq -r --arg bn "$BASENAME" '.[$bn].targets[]' "$SOURCES_JSON")
            SOURCE_SHA=$(sha256sum "$CANONICAL_PATH" | awk '{print $1}')
            
            for target in $TARGETS; do
                DO_SYNC=true
                if [ -f "$target" ]; then
                    TARGET_SHA=$(sha256sum "$target" | awk '{print $1}')
                    if [ "$SOURCE_SHA" == "$TARGET_SHA" ]; then
                        DO_SYNC=false
                    fi
                fi
                
                if [ "$DO_SYNC" = true ]; then
                    mkdir -p "$(dirname "$target")"
                    cp -f "$CANONICAL_PATH" "$target"
                    if [ $? -eq 0 ]; then
                        FILES_SYNCED=$((FILES_SYNCED + 1))
                        echo "- $(date +"%Y-%m-%d %H:%M") | $BASENAME | memory -> $(dirname "$target") | OK" >> "$LOG_FILE"
                        echo "        -> Synced: $target"
                    else
                        STATUS="ERROR"
                        ERRORS="$(echo "$ERRORS" | jq '. + ["Erreur de copie vers '"$target"'"]')"
                        echo "- $(date +"%Y-%m-%d %H:%M") | $BASENAME | memory -> $(dirname "$target") | ERROR" >> "$LOG_FILE"
                    fi
                else
                    FILES_SKIPPED=$((FILES_SKIPPED + 1))
                    echo "        -> Skipped (SHA match): $target"
                fi
            done
        else
            echo "      [Capability: Canonical Sync] Ignoré : $FILE n'est pas le chemin canonique officiel."
        fi
    else
        echo "      [Capability: Canonical Sync] Ignoré : $BASENAME non cartographié."
    fi
else
    STATUS="ERROR"
    ERRORS="[\"Fichier sources.json introuvable\"]"
    echo "[-] ERREUR: sources.json introuvable."
fi

END_TIME=$(date +%s%3N)
DURATION=$((END_TIME - START_TIME))

cat <<EOF > "/tmp/tesla_health/canonical_sync.json"
{
  "id": "canonical_sync",
  "version": "1.0",
  "status": "$STATUS",
  "files_synced": $FILES_SYNCED,
  "files_skipped": $FILES_SKIPPED,
  "duration_ms": $DURATION,
  "warnings": [],
  "errors": $ERRORS,
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
}
EOF

[ "$STATUS" == "OK" ] || exit 1
