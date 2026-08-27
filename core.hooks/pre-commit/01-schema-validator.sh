#!/usr/bin/env bash
# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                   TESLA SCHEMA VALIDATOR — PHASE 1                          ║
# ║              Validation des schémas YAML/JSON                               ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

set -euo pipefail

STAGED_FILES="$1"
TESLA_ROOT="$2"
TRACE_ID="$3"
LOG_FILE="${4:-/tmp/tesla-hooks.log}"

VIOLATIONS=0
SCHEMA_ERRORS=()

log_msg() {
    echo "[$(date +%H:%M:%S)] [SCHEMA_VALIDATOR] [$TRACE_ID] $1" >> "$LOG_FILE"
}

log_msg "Démarrage validation des schémas..."

validate_yaml() {
    local file="$1"
    
    if command -v python3 &>/dev/null; then
        if ! python3 -c "import yaml; yaml.safe_load(open('$file'))" 2>/dev/null; then
            return 1
        fi
    elif command -v python &>/dev/null; then
        if ! python -c "import yaml; yaml.safe_load(open('$file'))" 2>/dev/null; then
            return 1
        fi
    else
        # Fallback: simple check for basic syntax
        if grep -q "^\t" "$file" 2>/dev/null; then
            return 1  # Tabs not allowed in YAML
        fi
    fi
    return 0
}

validate_json() {
    local file="$1"
    
    if command -v jq &>/dev/null; then
        jq empty "$file" 2>/dev/null
        return $?
    elif command -v python3 &>/dev/null; then
        python3 -c "import json; json.load(open('$file'))" 2>/dev/null
        return $?
    fi
    return 0
}

# Vérifier les fichiers stagés
while IFS= read -r file; do
    [ -z "$file" ] && continue
    
    case "$file" in
        *.yaml|*.yml)
            if ! validate_yaml "$file"; then
                SCHEMA_ERRORS+=("YAML invalid: $file")
                ((VIOLATIONS++))
                log_msg "YAML invalid: $file"
            fi
            ;;
        *.json)
            if ! validate_json "$file"; then
                SCHEMA_ERRORS+=("JSON invalid: $file")
                ((VIOLATIONS++))
                log_msg "JSON invalid: $file"
            fi
            ;;
    esac
done <<< "$STAGED_FILES"

if [ "$VIOLATIONS" -gt 0 ]; then
    echo ""
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║              SCHÉMAS INVALIDES DÉTECTÉS                       ║"
    echo "╠═══════════════════════════════════════════════════════════════╣"
    for error in "${SCHEMA_ERRORS[@]}"; do
        printf "║ %-60s ║\n" "$error"
    done
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo ""
    log_msg "SCHEMA ERRORS FOUND: $VIOLATIONS — BLOCKING"
    exit 1
fi

echo "✓ Schémas YAML/JSON validés — aucun problème détecté"
log_msg "Schema validation completed — OK"
exit 0
