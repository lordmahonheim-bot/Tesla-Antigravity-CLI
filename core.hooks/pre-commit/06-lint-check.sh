#!/usr/bin/env bash
# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                   TESLA LINT CHECK — PHASE 6                               ║
# ║              Vérification format et lint                                    ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

set -euo pipefail

STAGED_FILES="$1"
TESLA_ROOT="$2"
TRACE_ID="$3"
LOG_FILE="${4:-/tmp/tesla-hooks.log}"

VIOLATIONS=0
LINT_ERRORS=()

log_msg() {
    echo "[$(date +%H:%M:%S)] [LINT_CHECK] [$TRACE_ID] $1" >> "$LOG_FILE"
}

log_msg "Démarrage vérification lint..."

# Vérifier YAML/JSON
while IFS= read -r file; do
    [ -z "$file" ] && continue
    
    case "$file" in
        *.yaml|*.yml)
            if command -v python3 &>/dev/null; then
                if ! python3 -c "import yaml; yaml.safe_load(open('$file'))" 2>/dev/null; then
                    LINT_ERRORS+=("YAML syntax error: $file")
                    ((VIOLATIONS++))
                fi
            fi
            ;;
        *.json)
            if command -v jq &>/dev/null; then
                if ! jq empty "$file" 2>/dev/null; then
                    LINT_ERRORS+=("JSON syntax error: $file")
                    ((VIOLATIONS++))
                fi
            fi
            ;;
        *.sh)
            if command -v shellcheck &>/dev/null; then
                if ! shellcheck "$file" 2>/dev/null | grep -q "No issues"; then
                    errors=$(shellcheck "$file" 2>/dev/null | head -3)
                    if [ -n "$errors" ]; then
                        LINT_ERRORS+=("ShellCheck: $file")
                        ((VIOLATIONS++))
                    fi
                fi
            fi
            ;;
    esac
done <<< "$STAGED_FILES"

if [ "$VIOLATIONS" -gt 0 ]; then
    echo ""
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║              ERREURS DE LINT DÉTECTÉES                        ║"
    echo "╠═══════════════════════════════════════════════════════════════╣"
    for error in "${LINT_ERRORS[@]}"; do
        printf "║ %-60s ║\n" "$error"
    done
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo ""
    log_msg "LINT ERRORS FOUND: $VIOLATIONS — BLOCKING"
    exit 1
fi

echo "✓ Vérification lint passed — aucune erreur détectée"
log_msg "Lint check completed — OK"
exit 0
