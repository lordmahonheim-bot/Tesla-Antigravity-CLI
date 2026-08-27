#!/usr/bin/env bash
# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                    TESLA LOGGING LIBRARY                                    ║
# ║              Bibliothèque de logging standardisé                            ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Variables globales
TESLA_LOG_FILE="${TESLA_LOG_FILE:-/tmp/tesla-hooks.log}"
TESLA_LOG_LEVEL="${TESLA_LOG_LEVEL:-INFO}"

# Niveaux de log
declare -A LOG_LEVELS=(
    ["DEBUG"]=0
    ["INFO"]=1
    ["WARN"]=2
    ["ERROR"]=3
    ["CRITICAL"]=4
)

# Fonction d'initialisation
tesla_log_init() {
    local log_file="$1"
    local min_level="$2"
    local component="$3"
    local trace_id="$4"
    
    export TESLA_LOG_FILE="$log_file"
    export TESLA_LOG_COMPONENT="$component"
    export TESLA_LOG_TRACE="$trace_id"
    export TESLA_LOG_MIN_LEVEL="${LOG_LEVELS[$min_level]:-1}"
    
    mkdir -p "$(dirname "$log_file")"
    echo "" >> "$log_file"
    echo "══════════════════════════════════════════════════════════════════" >> "$log_file"
    echo "Component: $component | Trace: $trace_id | Started: $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$log_file"
    echo "══════════════════════════════════════════════════════════════════" >> "$log_file"
}

# Fonction de logging principale
tesla_log() {
    local level="$1"
    local message="$2"
    local component="${TESLA_LOG_COMPONENT:-SYSTEM}"
    local trace_id="${TESLA_LOG_TRACE:-N/A}"
    
    local current_level="${LOG_LEVELS[$level]:-1}"
    
    # Filtrer selon le niveau minimum
    if [ "$current_level" -lt "${TESLA_LOG_MIN_LEVEL:-1}" ]; then
        return 0
    fi
    
    local timestamp
    timestamp=$(date +%H:%M:%S)
    
    local log_line="[$timestamp] [$level] [$component] [$trace_id] $message"
    
    # Écrire dans le fichier de log
    echo "$log_line" >> "$TESLA_LOG_FILE"
    
    # Écrire sur stderr avec couleur
    local color=""
    case "$level" in
        DEBUG)   color="$CYAN" ;;
        INFO)    color="$BLUE" ;;
        WARN)    color="$YELLOW" ;;
        ERROR)   color="$RED" ;;
        CRITICAL) color="$MAGENTA" ;;
    esac
    
    echo -e "${color}${log_line}${NC}" >&2
}

# Alias pratiques
tesla_debug() { tesla_log "DEBUG" "$1"; }
tesla_info()  { tesla_log "INFO" "$1"; }
tesla_warn()  { tesla_log "WARN" "$1"; }
tesla_error() { tesla_log "ERROR" "$1"; }
tesla_critical() { tesla_log "CRITICAL" "$1"; }

# Export
export -f tesla_log_init tesla_log
export -f tesla_debug tesla_info tesla_warn tesla_error tesla_critical
export RED GREEN YELLOW BLUE CYAN MAGENTA NC
