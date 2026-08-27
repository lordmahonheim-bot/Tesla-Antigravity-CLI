#!/usr/bin/env bash
# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                         TESLA PRE-COMMIT HOOK                              ║
# ║                     VIGILUM CODEX 2.0 — FAIL-CLOSED                      ║
# ╚══════════════════════════════════════════════════════════════════════════════╝
#
# SYNOPSIS    : Hook de sécurité pré-commit pour Tesla Antigravity CLI
# AUTEUR      : Tesla — Agent Principal & Orchestrateur
# VERSION     : 1.0.0
# DATE        : 2026-08-26
# DOCTRINE    : Vigilum Codex — Fail-Closed
#
# ─────────────────────────────────────────────────────────────────────────────
# RÈGLES ABSOLUES :
#   • TOUT ÉCHEC = COMMIT BLOQUÉ
#   • Aucune exception, aucun bypass, aucune excuse
#   • "Looks correct" ≠ "PASS"
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

TESLA_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
HOOKS_DIR="$(dirname "$(readlink -f "$0")")"
HOOKS_LIB="$TESLA_ROOT/core.hooks/lib"
HOOK_NAME="pre-commit"
TRACE_ID="precommit-$(date +%s)-$(head -c 4 /dev/urandom | xxd -p)"

# Répertoires de sortie
LOG_DIR="/tmp/tesla-hooks/logs"
REPORT_DIR="/tmp/tesla-hooks/reports"
mkdir -p "$LOG_DIR" "$REPORT_DIR"

LOG_FILE="$LOG_DIR/${TRACE_ID}.log"
REPORT_FILE="$REPORT_DIR/${TRACE_ID}.report"

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# ═══════════════════════════════════════════════════════════════════════════════
# LIBRAIRIES
# ═══════════════════════════════════════════════════════════════════════════════

# shellcheck source=lib/tesla-logging.sh
if [ -f "$HOOKS_LIB/tesla-logging.sh" ]; then
    source "$HOOKS_LIB/tesla-logging.sh"
    tesla_log_init "$LOG_FILE" "INFO" "$HOOK_NAME" "$TRACE_ID"
else
    mkdir -p "$LOG_FILE"
    echo "[$(date +%H:%M:%S)] [INFO] [pre-commit] [$TRACE_ID] Librairie logging absente — mode dégradé" >> "$LOG_FILE"
fi

# shellcheck source=lib/tesla-exit-codes.sh
if [ -f "$HOOKS_LIB/tesla-exit-codes.sh" ]; then
    source "$HOOKS_LIB/tesla-exit-codes.sh"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# FONCTIONS UTILITAIRES
# ═══════════════════════════════════════════════════════════════════════════════

log_msg() {
    local level="$1"
    local msg="$2"
    echo "[$(date +%H:%M:%S)] [$level] $msg" >> "$LOG_FILE"
    
    case "$level" in
        ERROR)   echo -e "${RED}[$level] $msg${NC}" ;;
        WARN)    echo -e "${YELLOW}[$level] $msg${NC}" ;;
        INFO)    echo -e "${BLUE}[$level] $msg${NC}" ;;
        *)       echo "[$level] $msg" ;;
    esac
}

report_phase() {
    local phase_name="$1"
    local phase_status="$2"
    local phase_duration="$3"
    local phase_details="${4:-}"
    echo "| $phase_name | $phase_status | ${phase_duration}ms | $phase_details |" >> "$REPORT_FILE"
}

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN EXECUTION
# ═══════════════════════════════════════════════════════════════════════════════

main() {
    local start_time end_time duration
    local overall_status="PASS"
    local failed_phases=()
    
    log_msg "INFO" "═══════════════════════════════════════════════════════"
    log_msg "INFO" "TESLA PRE-COMMIT HOOK v1.0.0"
    log_msg "INFO" "Trace ID: $TRACE_ID"
    log_msg "INFO" "Tesla Root: $TESLA_ROOT"
    log_msg "INFO" "═══════════════════════════════════════════════════════"
    
    # Initialisation du rapport
    {
        echo "# TESLA PRE-COMMIT REPORT"
        echo "Trace ID: $TRACE_ID"
        echo "Timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
        echo "Git Branch: $(git symbolic-ref --short HEAD 2>/dev/null || echo 'detached')"
        echo "Git SHA: $(git rev-parse HEAD 2>/dev/null || echo 'N/A')"
        echo ""
        echo "| Phase | Status | Duration | Details |"
        echo "|-------|--------|----------|---------|"
    } > "$REPORT_FILE"
    
    log_msg "INFO" "Détection des fichiers modifiés..."
    
    # Récupérer la liste des fichiers stagés
    local staged_files
    staged_files=$(git diff --cached --name-only --diff-filter=ACM 2>/dev/null || echo "")
    
    if [ -z "$staged_files" ]; then
        log_msg "WARN" "Aucun fichier stagé — nothing to commit"
        echo "| (none) | SKIP | 0 | No staged files |" >> "$REPORT_FILE"
        {
            echo ""
            echo "RESULT: PASS (no changes staged)"
        } >> "$REPORT_FILE"
        cat "$REPORT_FILE"
        exit 0
    fi
    
    local file_count
    file_count=$(echo "$staged_files" | wc -l)
    log_msg "INFO" "$file_count fichier(s) stagé(s)"
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PHASE 1: SCHEMA VALIDATOR
    # ═══════════════════════════════════════════════════════════════════════════
    
    if [ -f "$HOOKS_DIR/01-schema-validator.sh" ]; then
        start_time=$(date +%s%3N)
        log_msg "INFO" "PHASE 1: Validation des schémas YAML/JSON..."
        
        if bash "$HOOKS_DIR/01-schema-validator.sh" "$staged_files" "$TESLA_ROOT" "$TRACE_ID" "$LOG_FILE"; then
            end_time=$(date +%s%3N)
            duration=$((end_time - start_time))
            report_phase "SCHEMA_VALIDATOR" "PASS" "$duration"
            log_msg "INFO" "PHASE 1: PASS (${duration}ms)"
        else
            end_time=$(date +%s%3N)
            duration=$((end_time - start_time))
            report_phase "SCHEMA_VALIDATOR" "FAIL" "$duration" "Schema invalid"
            log_msg "ERROR" "PHASE 1: FAIL"
            overall_status="FAIL"
            failed_phases+=("SCHEMA_VALIDATOR")
        fi
    fi
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PHASE 2: SECRET SCANNER
    # ═══════════════════════════════════════════════════════════════════════════
    
    if [ -f "$HOOKS_DIR/02-secret-scanner.sh" ]; then
        start_time=$(date +%s%3N)
        log_msg "INFO" "PHASE 2: Scan de secrets et PII..."
        
        if bash "$HOOKS_DIR/02-secret-scanner.sh" "$staged_files" "$TESLA_ROOT" "$TRACE_ID" "$LOG_FILE"; then
            end_time=$(date +%s%3N)
            duration=$((end_time - start_time))
            report_phase "SECRET_SCANNER" "PASS" "$duration"
            log_msg "INFO" "PHASE 2: PASS (${duration}ms)"
        else
            end_time=$(date +%s%3N)
            duration=$((end_time - start_time))
            report_phase "SECRET_SCANNER" "FAIL" "$duration" "Secret/PII detected"
            log_msg "ERROR" "PHASE 2: FAIL — SECRET DÉTECTÉ"
            overall_status="FAIL"
            failed_phases+=("SECRET_SCANNER")
        fi
    fi
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PHASE 3: SCOPE VALIDATOR
    # ═══════════════════════════════════════════════════════════════════════════
    
    if [ -f "$HOOKS_DIR/03-scope-validator.sh" ]; then
        start_time=$(date +%s%3N)
        log_msg "INFO" "PHASE 3: Validation du périmètre (scope)..."
        
        if bash "$HOOKS_DIR/03-scope-validator.sh" "$staged_files" "$TESLA_ROOT" "$TRACE_ID" "$LOG_FILE"; then
            end_time=$(date +%s%3N)
            duration=$((end_time - start_time))
            report_phase "SCOPE_VALIDATOR" "PASS" "$duration"
            log_msg "INFO" "PHASE 3: PASS (${duration}ms)"
        else
            end_time=$(date +%s%3N)
            duration=$((end_time - start_time))
            report_phase "SCOPE_VALIDATOR" "FAIL" "$duration" "Scope violation"
            log_msg "ERROR" "PHASE 3: FAIL — SCOPE VIOLATION"
            overall_status="FAIL"
            failed_phases+=("SCOPE_VALIDATOR")
        fi
    fi
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PHASE 4: PROJECT_STATE SYNC CHECK
    # ═══════════════════════════════════════════════════════════════════════════
    
    if [ -f "$HOOKS_DIR/04-project-state-check.sh" ]; then
        start_time=$(date +%s%3N)
        log_msg "INFO" "PHASE 4: Vérification PROJECT_STATE..."
        
        if bash "$HOOKS_DIR/04-project-state-check.sh" "$staged_files" "$TESLA_ROOT" "$TRACE_ID" "$LOG_FILE"; then
            end_time=$(date +%s%3N)
            duration=$((end_time - start_time))
            report_phase "PROJECT_STATE_SYNC" "PASS" "$duration"
            log_msg "INFO" "PHASE 4: PASS (${duration}ms)"
        else
            end_time=$(date +%s%3N)
            duration=$((end_time - start_time))
            report_phase "PROJECT_STATE_SYNC" "FAIL" "$duration" "PROJECT_STATE not synced"
            log_msg "ERROR" "PHASE 4: FAIL — PROJECT_STATE DÉSYNCHRONISÉ"
            overall_status="FAIL"
            failed_phases+=("PROJECT_STATE_SYNC")
        fi
    fi
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PHASE 5: MARBLE CERTIFICATE CHECK
    # ═══════════════════════════════════════════════════════════════════════════
    
    if [ -f "$HOOKS_DIR/05-marble-cert-check.sh" ]; then
        start_time=$(date +%s%3N)
        log_msg "INFO" "PHASE 5: Vérification Marble Certificate..."
        
        if bash "$HOOKS_DIR/05-marble-cert-check.sh" "$staged_files" "$TESLA_ROOT" "$TRACE_ID" "$LOG_FILE"; then
            end_time=$(date +%s%3N)
            duration=$((end_time - start_time))
            report_phase "MARBLE_CERT_CHECK" "PASS" "$duration"
            log_msg "INFO" "PHASE 5: PASS (${duration}ms)"
        else
            end_time=$(date +%s%3N)
            duration=$((end_time - start_time))
            report_phase "MARBLE_CERT_CHECK" "FAIL" "$duration" "Marble cert missing"
            log_msg "ERROR" "PHASE 5: FAIL — MARBLE CERTIFICATE ABSENT"
            overall_status="FAIL"
            failed_phases+=("MARBLE_CERT_CHECK")
        fi
    fi
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PHASE 6: LINT CHECK
    # ═══════════════════════════════════════════════════════════════════════════
    
    if [ -f "$HOOKS_DIR/06-lint-check.sh" ]; then
        start_time=$(date +%s%3N)
        log_msg "INFO" "PHASE 6: Vérification format et lint..."
        
        if bash "$HOOKS_DIR/06-lint-check.sh" "$staged_files" "$TESLA_ROOT" "$TRACE_ID" "$LOG_FILE"; then
            end_time=$(date +%s%3N)
            duration=$((end_time - start_time))
            report_phase "LINT_CHECK" "PASS" "$duration"
            log_msg "INFO" "PHASE 6: PASS (${duration}ms)"
        else
            end_time=$(date +%s%3N)
            duration=$((end_time - start_time))
            report_phase "LINT_CHECK" "FAIL" "$duration" "Lint errors"
            log_msg "ERROR" "PHASE 6: FAIL — LINT ERRORS"
            overall_status="FAIL"
            failed_phases+=("LINT_CHECK")
        fi
    fi
    
    # ═══════════════════════════════════════════════════════════════════════════
    # RÉSULTAT FINAL
    # ═══════════════════════════════════════════════════════════════════════════
    
    {
        echo ""
        echo "═══════════════════════════════════════════════════════════════"
        echo "FINAL RESULT: $overall_status"
        echo "═══════════════════════════════════════════════════════════════"
        echo "Log: $LOG_FILE"
        echo "Report: $REPORT_FILE"
    } >> "$REPORT_FILE"
    
    log_msg "INFO" "═══════════════════════════════════════════════════════"
    log_msg "INFO" "RÉSULTAT FINAL: $overall_status"
    log_msg "INFO" "═══════════════════════════════════════════════════════"
    
    cat "$REPORT_FILE"
    
    if [ "$overall_status" = "FAIL" ]; then
        echo ""
        echo -e "${RED}╔═══════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${RED}║                    COMMIT BLOQUÉ                             ║${NC}"
        echo -e "${RED}║                                                               ║${NC}"
        echo -e "${RED}║  Échec(s): ${failed_phases[*]}${NC}"
        echo -e "${RED}║                                                               ║${NC}"
        echo -e "${RED}║  Consultez le rapport: $REPORT_FILE${NC}"
        echo -e "${RED}╚═══════════════════════════════════════════════════════════════╝${NC}"
        exit 1
    fi
    
    echo ""
    echo -e "${GREEN}╔═══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                    COMMIT AUTORISÉ                             ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════════════════╝${NC}"
    exit 0
}

# Exécution
main "$@"
