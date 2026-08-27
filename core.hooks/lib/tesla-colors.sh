#!/usr/bin/env bash
# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                    TESLA COLORS LIBRARY                                    ║
# ║              Palette de couleurs pour affichage terminal                    ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

# ═══════════════════════════════════════════════════════════════════════════════
# CODES ANSI DE COULEURS
# ═══════════════════════════════════════════════════════════════════════════════

# Styles
BOLD='\033[1m'
DIM='\033[2m'
UNDERLINE='\033[4m'
BLINK='\033[5m'
REVERSE='\033[7m'
HIDDEN='\033[8m'
RESET='\033[0m'

# Couleurs de base
BLACK='\033[0;30m'
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[0;37m'

# Couleurs vives
BRIGHT_BLACK='\033[0;90m'
BRIGHT_RED='\033[0;91m'
BRIGHT_GREEN='\033[0;92m'
BRIGHT_YELLOW='\033[0;93m'
BRIGHT_BLUE='\033[0;94m'
BRIGHT_MAGENTA='\033[0;95m'
BRIGHT_CYAN='\033[0;96m'
BRIGHT_WHITE='\033[0;97m'

# Arrière-plans
BG_BLACK='\033[40m'
BG_RED='\033[41m'
BG_GREEN='\033[42m'
BG_YELLOW='\033[43m'
BG_BLUE='\033[44m'
BG_MAGENTA='\033[45m'
BG_CYAN='\033[46m'
BG_WHITE='\033[47m'

# Couleurs sémantiques Tesla
NC="$RESET"  # No Color - reset par défaut

# Statuts
STATUS_PASS="${GREEN}✔${NC}"
STATUS_FAIL="${RED}✘${NC}"
STATUS_WARN="${YELLOW}⚠${NC}"
STATUS_INFO="${CYAN}ℹ${NC}"
STATUS_BLOCK="${MAGENTA}🚫${NC}"

# Box drawing
BOX_TOP_LEFT='┌'
BOX_TOP_RIGHT='┐'
BOX_BOTTOM_LEFT='└'
BOX_BOTTOM_RIGHT='┘'
BOX_HORIZONTAL='─'
BOX_VERTICAL='│'
BOX_CROSS='┼'

# ═══════════════════════════════════════════════════════════════════════════════
# FONCTIONS UTILITAIRES
# ═══════════════════════════════════════════════════════════════════════════════

# Afficher un message avec couleur de statut
status_msg() {
    local status="$1"
    local message="$2"
    
    case "$status" in
        PASS|OK|SUCCESS)
            echo -e "${GREEN}[${STATUS_PASS}]${NC} $message"
            ;;
        FAIL|ERROR|NOK|FAILED)
            echo -e "${RED}[${STATUS_FAIL}]${NC} $message"
            ;;
        WARN|WARNING)
            echo -e "${YELLOW}[${STATUS_WARN}]${NC} $message"
            ;;
        INFO|NOTE)
            echo -e "${CYAN}[${STATUS_INFO}]${NC} $message"
            ;;
        BLOCK|BLOCKED)
            echo -e "${MAGENTA}[${STATUS_BLOCK}]${NC} $message"
            ;;
        *)
            echo -e "$message"
            ;;
    esac
}

# Afficher une boîte de dialogue
box_msg() {
    local title="$1"
    local content="$2"
    local width="${3:-60}"
    local color="${4:-$NC}"
    
    local line=""
    for ((i=0; i<width; i++)); do
        line+="$BOX_HORIZONTAL"
    done
    
    echo -e "${color}$BOX_TOP_LEFT${line}$BOX_TOP_RIGHT${NC}"
    echo -e "${color}$BOX_VERTICAL${NC} $(printf '%-*s' "$width" "$title") $(printf '%*s' 0 '') ${color}$BOX_VERTICAL${NC}"
    echo -e "${color}$BOX_VERTICAL${NC} $(printf '%-*s' "$width" "") ${color}$BOX_VERTICAL${NC}"
    
    # Word wrap le contenu
    while IFS= read -r word; do
        echo -e "${color}$BOX_VERTICAL${NC} $(printf '%-*s' "$width" "$word") ${color}$BOX_VERTICAL${NC}"
    done <<< "$content"
    
    echo -e "${color}$BOX_BOTTOM_LEFT${line}$BOX_BOTTOM_RIGHT${NC}"
}

# Export
export -f status_msg box_msg
export RED GREEN YELLOW BLUE MAGENTA CYAN WHITE NC
export STATUS_PASS STATUS_FAIL STATUS_WARN STATUS_INFO STATUS_BLOCK
export BOX_TOP_LEFT BOX_TOP_RIGHT BOX_BOTTOM_LEFT BOX_BOTTOM_RIGHT
export BOX_HORIZONTAL BOX_VERTICAL BOX_CROSS
