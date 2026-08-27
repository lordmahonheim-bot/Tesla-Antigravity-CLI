#!/usr/bin/env bash
# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║              TESLA PROJECT_STATE SYNC CHECK — PHASE 4                       ║
# ║     Vérification que PROJECT_STATE.md est synchronisé avec les commits       ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

set -euo pipefail

STAGED_FILES="$1"
TESLA_ROOT="$2"
TRACE_ID="$3"
LOG_FILE="${4:-/tmp/tesla-hooks.log}"

PROJECT_STATE="$TESLA_ROOT/memory/PROJECT_STATE.md"
VIOLATIONS=0

log_msg() {
    echo "[$(date +%H:%M:%S)] [PROJECT_STATE] [$TRACE_ID] $1" >> "$LOG_FILE"
}

MODIFIES_PROJECT_STATE=0
MODIFIES_OUTPUTS=0

OUTPUT_PATTERNS=(
    "*/MVP-*/*"
    "*/OUTPUTS/*"
    "*/*-Skill/*"
    "*/*-skill/*"
)

# Vérifier les fichiers stagés
while IFS= read -r file; do
    [ -z "$file" ] && continue
    
    if [[ "$file" == "memory/PROJECT_STATE.md" ]]; then
        MODIFIES_PROJECT_STATE=1
        continue
    fi
    
    for pattern in "${OUTPUT_PATTERNS[@]}"; do
        if [[ "$file" == $pattern ]]; then
            MODIFIES_OUTPUTS=1
            break
        fi
    done
    
done <<< "$STAGED_FILES"

# Si OUTPUTS modifié mais PROJECT_STATE non modifié → VIOLATION
if [ "$MODIFIES_OUTPUTS" -eq 1 ] && [ "$MODIFIES_PROJECT_STATE" -eq 0 ]; then
    echo ""
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║           PROJECT_STATE DÉSYNCHRONISÉ                         ║"
    echo "╠═══════════════════════════════════════════════════════════════╣"
    echo "║                                                               ║"
    echo "║  OUTPUTS/MVP/Skills modifiés mais PROJECT_STATE non mis à jour ║"
    echo "║                                                               ║"
    echo "║  RÈGLE: PROJECT_STATE est TOUJOURS obligatoire               ║"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo ""
    echo "ACTION: Mettez à jour memory/PROJECT_STATE.md puis re-stagez"
    echo ""
    ((VIOLATIONS++))
fi

# Si PROJECT_STATE modifié, vérifier qu'il a un format valide
if [ "$MODIFIES_PROJECT_STATE" -eq 1 ] && [ -f "$PROJECT_STATE" ]; then
    if ! grep -q "^# PROJECT STATE" "$PROJECT_STATE" 2>/dev/null; then
        echo "⚠ PROJECT_STATE.md modifié mais format invalide"
        ((VIOLATIONS++))
    fi
fi

if [ "$VIOLATIONS" -gt 0 ]; then
    log_msg "PROJECT_STATE DESYNC — BLOCKING"
    exit 1
fi

echo "✓ PROJECT_STATE synchronisé"
log_msg "Synchronisation vérifiée — OK"
exit 0
