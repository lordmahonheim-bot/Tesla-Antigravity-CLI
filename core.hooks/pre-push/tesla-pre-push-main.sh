#!/usr/bin/env bash
# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                         TESLA PRE-PUSH HOOK                                ║
# ║                     VIGILUM CODEX 2.0 — FAIL-CLOSED                        ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

set -euo pipefail

TESLA_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
HOOKS_DIR="$(dirname "$(readlink -f "$0")")"
HOOKS_LIB="$TESLA_ROOT/core.hooks/lib"
HOOK_NAME="pre-push"
TRACE_ID="prepush-$(date +%s)-$(head -c 4 /dev/urandom | xxd -p)"

LOG_DIR="/tmp/tesla-hooks/logs"
REPORT_DIR="/tmp/tesla-hooks/reports"
mkdir -p "$LOG_DIR" "$REPORT_DIR"

LOG_FILE="$LOG_DIR/${TRACE_ID}.log"
REPORT_FILE="$REPORT_DIR/${TRACE_ID}.report"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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
    echo "| $1 | $2 | $3 |" >> "$REPORT_FILE"
}

# Paramètres git
REMOTE_URL="$1"
REMOTE_NAME="$2"
LOCAL_REF="$3"
LOCAL_SHA="$4"
REMOTE_REF="$5"
REMOTE_SHA="$6"

{
    echo "# TESLA PRE-PUSH REPORT"
    echo "Trace ID: $TRACE_ID"
    echo "Timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "Remote: $REMOTE_NAME"
    echo "Remote URL: $REMOTE_URL"
    echo ""
    echo "| Phase | Status | Details |"
    echo "|-------|--------|---------|"
} > "$REPORT_FILE"

log_msg "INFO" "═══════════════════════════════════════════════════════"
log_msg "INFO" "TESLA PRE-PUSH HOOK v1.0.0"
log_msg "INFO" "Trace ID: $TRACE_ID"
log_msg "INFO" "Remote: $REMOTE_NAME ($REMOTE_URL)"
log_msg "INFO" "Local:  $LOCAL_REF ($LOCAL_SHA)"
log_msg "INFO" "Remote: $REMOTE_REF ($REMOTE_SHA)"
log_msg "INFO" "═══════════════════════════════════════════════════════"

PUSH_BLOCKED=0
FIRST_PUSH=0

# Vérifier premier push
if [ "$REMOTE_SHA" = "0000000000000000000000000000000000000000" ]; then
    log_msg "INFO" "Premier push — règles renforcées"
    FIRST_PUSH=1
fi

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 1: BIOLOGICAL GATE (AUTHORIZATION CHECK)
# ═══════════════════════════════════════════════════════════════════════════════

log_msg "INFO" "PHASE 1: Vérification Biological Gate..."

AUTH_REQUIRED=0
case "$REMOTE_URL" in
    *github.com*|*gitlab.com*|*bitbucket.org*)
        AUTH_REQUIRED=1
        ;;
esac

AUTH_FILE="$TESLA_ROOT/OUTPUTS/authorized_pushes.txt"

if [ "$AUTH_REQUIRED" -eq 1 ]; then
    if [ -f "$AUTH_FILE" ]; then
        AUTH_LINE=$(grep -E "^${REMOTE_NAME}@${REMOTE_REF}@${LOCAL_SHA}@" "$AUTH_FILE" 2>/dev/null || true)
        
        if [ -n "$AUTH_LINE" ]; then
            AUTH_EXPIRY=$(echo "$AUTH_LINE" | cut -d@ -f4)
            AUTH_BY=$(echo "$AUTH_LINE" | cut -d@ -f5)
            
            EXPIRY_EPOCH=$(date -d "$AUTH_EXPIRY" +%s 2>/dev/null || echo 0)
            CURRENT_EPOCH=$(date +%s)
            
            if [ "$EXPIRY_EPOCH" -gt "$CURRENT_EPOCH" ]; then
                log_msg "INFO" "Push autorisé par $AUTH_BY"
                report_phase "BIOLOGICAL_GATE" "PASS" "Authorized by $AUTH_BY"
            else
                log_msg "ERROR" "Autorisation expirée"
                report_phase "BIOLOGICAL_GATE" "FAIL" "Authorization expired"
                PUSH_BLOCKED=1
            fi
        else
            log_msg "ERROR" "Aucune autorisation trouvée"
            report_phase "BIOLOGICAL_GATE" "FAIL" "No authorization"
            PUSH_BLOCKED=1
        fi
    else
        log_msg "ERROR" "Fichier d'autorisations introuvable"
        report_phase "BIOLOGICAL_GATE" "FAIL" "Auth file missing"
        PUSH_BLOCKED=1
    fi
else
    log_msg "INFO" "Autorisation non requise (local/dev remote)"
    report_phase "BIOLOGICAL_GATE" "SKIP" "Local remote"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 2: REMOTE SHA VERIFICATION
# ═══════════════════════════════════════════════════════════════════════════════

if [ "$FIRST_PUSH" -eq 0 ]; then
    log_msg "INFO" "PHASE 2: Vérification SHA distant..."
    
    ACTUAL_REMOTE_SHA=$(git ls-remote "$REMOTE_URL" "$REMOTE_REF" 2>/dev/null | cut -f1 || echo "ERROR")
    
    if [ "$ACTUAL_REMOTE_SHA" = "ERROR" ]; then
        log_msg "WARN" "Impossible de lire l'état distant"
        report_phase "REMOTE_STATE" "WARN" "Cannot verify"
    elif [ "$ACTUAL_REMOTE_SHA" != "$REMOTE_SHA" ]; then
        log_msg "ERROR" "SHA distant changé!"
        report_phase "REMOTE_STATE" "FAIL" "Remote SHA mismatch"
        PUSH_BLOCKED=1
    else
        log_msg "INFO" "SHA distant vérifié: OK"
        report_phase "REMOTE_STATE" "PASS" "SHA verified"
    fi
else
    report_phase "REMOTE_STATE" "SKIP" "First push"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 3: FORCE PUSH DETECTION
# ═══════════════════════════════════════════════════════════════════════════════

if [ "$FIRST_PUSH" -eq 0 ]; then
    log_msg "INFO" "PHASE 3: Détection force-push..."
    
    MERGE_BASE=$(git merge-base "$REMOTE_SHA" "$LOCAL_SHA" 2>/dev/null || echo "")
    
    if [ -n "$MERGE_BASE" ] && [ "$MERGE_BASE" != "$REMOTE_SHA" ]; then
        log_msg "WARN" "FORCE-PUSH détecté!"
        
        FORCE_AUTH=$(grep -E "FORCE@${REMOTE_NAME}@" "$AUTH_FILE" 2>/dev/null || true)
        
        if [ -z "$FORCE_AUTH" ]; then
            log_msg "ERROR" "Force-push non autorisé"
            report_phase "FORCE_PUSH" "FAIL" "Force-push blocked"
            PUSH_BLOCKED=1
        else
            report_phase "FORCE_PUSH" "PASS" "Force-push authorized"
        fi
    else
        report_phase "FORCE_PUSH" "PASS" "Standard push"
    fi
else
    report_phase "FORCE_PUSH" "SKIP" "First push"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# RÉSULTAT FINAL
# ═══════════════════════════════════════════════════════════════════════════════

{
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    if [ "$PUSH_BLOCKED" -eq 1 ]; then
        echo "FINAL RESULT: BLOCKED"
    else
        echo "FINAL RESULT: PASS"
    fi
    echo "═══════════════════════════════════════════════════════════════"
} >> "$REPORT_FILE"

log_msg "INFO" "═══════════════════════════════════════════════════════"
log_msg "INFO" "RÉSULTAT: $([ "$PUSH_BLOCKED" -eq 1 ] && echo 'BLOCKED' || echo 'PASS')"
log_msg "INFO" "═══════════════════════════════════════════════════════"

cat "$REPORT_FILE"

if [ "$PUSH_BLOCKED" -eq 1 ]; then
    echo ""
    echo -e "${RED}╔═══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║                    PUSH BLOQUÉ                              ║${NC}"
    echo -e "${RED}║                                                               ║${NC}"
    echo -e "${RED}║  Consultez: $REPORT_FILE${NC}"
    echo -e "${RED}║                                                               ║${NC}"
    echo -e "${RED}║  Pour autoriser: OUTPUTS/authorized_pushes.txt              ║${NC}"
    echo -e "${RED}╚═══════════════════════════════════════════════════════════════╝${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                    PUSH AUTORISÉ                              ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════════╝${NC}"
exit 0
