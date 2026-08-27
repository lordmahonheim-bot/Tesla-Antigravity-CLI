#!/usr/bin/env bash
# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║              TESLA MARBLE CERTIFICATE CHECK — PHASE 5                      ║
# ║     Vérification de l'existence du Marble Certificate pour mutations       ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

set -euo pipefail

STAGED_FILES="$1"
TESLA_ROOT="$2"
TRACE_ID="$3"
LOG_FILE="${4:-/tmp/tesla-hooks.log}"

MARBLE_DIR="$TESLA_ROOT/OUTPUTS/MARBLE_CERTIFICATES"
VIOLATIONS=0

log_msg() {
    echo "[$(date +%H:%M:%S)] [MARBLE_CHECK] [$TRACE_ID] $1" >> "$LOG_FILE"
}

mkdir -p "$MARBLE_DIR"

REQUIRES_MARBLE=0
REQUIRED_FOR=()

while IFS= read -r file; do
    [ -z "$file" ] && continue
    
    case "$file" in
        memory/*|.agents/*|PROTOCOLES/*)
            REQUIRES_MARBLE=1
            REQUIRED_FOR+=("$file")
            ;;
        *.md)
            if grep -q "^# PROTOCOLE CANONIQUE" "$file" 2>/dev/null; then
                REQUIRES_MARBLE=1
                REQUIRED_FOR+=("$file")
            fi
            ;;
    esac
done <<< "$STAGED_FILES"

if [ "$REQUIRES_MARBLE" -eq 1 ]; then
    echo "⚠ Marble Certificate requis pour cette modification"
    
    RECENT_MARBLE=$(find "$MARBLE_DIR" -name "*.yaml" -mtime -1 2>/dev/null | head -1)
    
    if [ -z "$RECENT_MARBLE" ]; then
        echo ""
        echo "╔═══════════════════════════════════════════════════════════════╗"
        echo "║           MARBLE CERTIFICATE REQUIS                          ║"
        echo "╠═══════════════════════════════════════════════════════════════╣"
        echo "║                                                               ║"
        echo "║  Les fichiers suivants requièrent un Marble Certificate:     ║"
        for f in "${REQUIRED_FOR[@]}"; do
            printf "║    • %-50s ║\n" "$f"
        done
        echo "║                                                               ║"
        echo "║  RÈGLE VIGILUM CODEX: 'No Proof, No Marble.'                ║"
        echo "╚═══════════════════════════════════════════════════════════════╝"
        echo ""
        echo "ACTION: Exécutez le protocole Gravure sur Marbre ou obtenez"
        echo "        l'autorisation de Lord Mahonheim"
        echo ""
        ((VIOLATIONS++))
    else
        echo "✓ Marble Certificate trouvé: $(basename "$RECENT_MARBLE")"
        log_msg "Marble cert present: $(basename "$RECENT_MARBLE")"
    fi
fi

if [ "$VIOLATIONS" -gt 0 ]; then
    log_msg "MARBLE CERT MISSING — BLOCKING"
    exit 1
fi

echo "✓ Vérification Marble Certificate passed"
log_msg "Marble check completed — OK"
exit 0
