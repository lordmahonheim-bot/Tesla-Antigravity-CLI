#!/usr/bin/env bash
# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                   TESLA SCOPE VALIDATOR — PHASE 3                           ║
# ║          Validation des fichiers autorisés/interdits                         ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

set -euo pipefail

STAGED_FILES="$1"
TESLA_ROOT="$2"
TRACE_ID="$3"
LOG_FILE="${4:-/tmp/tesla-hooks.log}"

# Fichiers/répertoires STRICTEMENT INTERDITS
FORBIDDEN_PATTERNS=(
    ".git/config"
    ".git/credentials"
    "*.key"
    "*.pem"
    "secrets.yaml"
    "secrets.yml"
    "secrets.json"
    "credentials.json"
)

# Extensions de fichiers à risque
FORBIDDEN_EXTENSIONS=(
    ".exe" ".dll" ".so" ".dylib"
    ".db" ".sqlite" ".sqlite3"
)

VIOLATIONS=0
VIOLATION_DETAILS=()

log_msg() {
    echo "[$(date +%H:%M:%S)] [SCOPE_VALIDATOR] [$TRACE_ID] $1" >> "$LOG_FILE"
}

# Vérifier les fichiers stagés
while IFS= read -r file; do
    [ -z "$file" ] && continue
    
    # Vérification: Chemins interdits
    for forbidden in "${FORBIDDEN_PATTERNS[@]}"; do
        if [[ "$file" == *"$forbidden"* ]]; then
            VIOLATION_DETAILS+=("PATH: Accès interdit à $file")
            ((VIOLATIONS++))
            continue 2
        fi
    done
    
    # Vérification: Extensions interdites
    for ext in "${FORBIDDEN_EXTENSIONS[@]}"; do
        if [[ "$file" == *"$ext" ]]; then
            VIOLATION_DETAILS+=("EXT: Extension interdite $ext dans $file")
            ((VIOLATIONS++))
            continue 2
        fi
    done
    
    # Vérification spéciale: memory/ ou .agents/ avec Marble Certificate
    if [[ "$file" == memory/* ]] || [[ "$file" == .agents/* ]]; then
        marble_dir="$TESLA_ROOT/OUTPUTS/MARBLE_CERTIFICATES/"
        if [ -d "$marble_dir" ]; then
            recent_cert=$(find "$marble_dir" -name "*.yaml" -mtime -1 2>/dev/null | head -1)
            if [ -z "$recent_cert" ]; then
                VIOLATION_DETAILS+=("MEMORY/AGENTS: Modification sans Marble Certificate récent")
                ((VIOLATIONS++))
            fi
        else
            VIOLATION_DETAILS+=("MEMORY/AGENTS: Modification sans répertoire Marble")
            ((VIOLATIONS++))
        fi
    fi
    
done <<< "$STAGED_FILES"

if [ "$VIOLATIONS" -gt 0 ]; then
    echo ""
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║              VIOLATION DE SCOPE DÉTECTÉE                     ║"
    echo "╠═══════════════════════════════════════════════════════════════╣"
    printf "║ %-60s ║\n" "Violations: $VIOLATIONS"
    echo "╠═══════════════════════════════════════════════════════════════╣"
    for detail in "${VIOLATION_DETAILS[@]}"; do
        printf "║ %-60s ║\n" "$detail"
    done
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo ""
    echo "ACTION: git checkout -- <fichier_interdit> puis re-stagez"
    echo ""
    log_msg "VIOLATIONS FOUND: $VIOLATIONS — BLOCKING"
    exit 1
fi

echo "✓ Périmètre des fichiers validé — aucune violation"
log_msg "Validation terminée — Scope OK"
exit 0
