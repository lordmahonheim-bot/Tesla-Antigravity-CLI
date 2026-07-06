#!/usr/bin/env bash
# capability_dispatcher.sh - Dispatcher événementiel agnostique (V2)

FILE_MODIFIED="$1"
if [ -z "$FILE_MODIFIED" ]; then
    echo "[-] ERREUR: Usage: $0 <filename>"
    exit 1
fi

LOCKFILE="/tmp/tesla_capability_bus.lock"
PAYLOAD_FILE="/tmp/tesla_payload.json"

(
    flock -n 9 || exit 0
    sleep 2

    # Calculs du Payload
    EVENT_TYPE="FileChanged"
    if [ ! -f "$FILE_MODIFIED" ]; then
        EVENT_TYPE="FileDeleted"
    fi

    SHA256="null"
    if [ -f "$FILE_MODIFIED" ]; then
        SHA256=$(sha256sum "$FILE_MODIFIED" | awk '{print $1}')
    fi

    TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    EXTENSION="${FILE_MODIFIED##*.}"
    [ "$EXTENSION" == "$FILE_MODIFIED" ] && EXTENSION="none"

    # Classification
    LEVEL=3
    if [[ "$FILE_MODIFIED" == *"memory/"* ]] || \
       [[ "$FILE_MODIFIED" == *".agents/"* ]] || \
       [[ "$FILE_MODIFIED" == *"TESLA.json"* ]] || \
       [[ "$FILE_MODIFIED" == *"settings.json"* ]] || \
       [[ "$FILE_MODIFIED" == *"ABOUT_ME"* ]] || \
       [[ "$FILE_MODIFIED" == *"MY_BRANDING"* ]] || \
       [[ "$FILE_MODIFIED" == *"MY_COMPANY"* ]] || \
       [[ "$FILE_MODIFIED" == *"MY_STRATEGIC_STYLE"* ]]; then
        LEVEL=1
    elif [[ "$FILE_MODIFIED" == *"docs/"* ]] || [[ "$FILE_MODIFIED" == *"README"* ]]; then
        LEVEL=2
    fi

    # Forge du JSON Context & Payload
    cat <<EOF > "$PAYLOAD_FILE"
{
  "event": "$EVENT_TYPE",
  "source": "entr",
  "file": "$FILE_MODIFIED",
  "extension": "$EXTENSION",
  "level": $LEVEL,
  "profile": "default",
  "workspace": "Tesla",
  "manifest": "TESLA.json",
  "sha256": "$SHA256",
  "timestamp": "$TIMESTAMP"
}
EOF

    echo ""
    echo "[⚡ DISPATCHER] Événement intercepté : $EVENT_TYPE sur $FILE_MODIFIED (Niveau $LEVEL)"
    echo "[⚡ DISPATCHER] Délégation au Resolver..."
    
    RESOLVER_SCRIPT="$(dirname "$0")/capability_resolver.sh"
    if [ -x "$RESOLVER_SCRIPT" ]; then
        "$RESOLVER_SCRIPT" "$PAYLOAD_FILE"
    else
        echo "[-] ERREUR: Resolver introuvable ou non exécutable : $RESOLVER_SCRIPT"
    fi

) 9> "$LOCKFILE"
