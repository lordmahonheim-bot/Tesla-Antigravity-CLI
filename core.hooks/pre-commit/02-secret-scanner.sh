#!/usr/bin/env bash
# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                   TESLA SECRET SCANNER — PHASE 2                           ║
# ║              Détection de secrets, tokens et PII                            ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

set -euo pipefail

STAGED_FILES="$1"
TESLA_ROOT="$2"
TRACE_ID="$3"
LOG_FILE="${4:-/tmp/tesla-hooks.log}"

# Patterns de secrets à détecter
SECRET_PATTERNS=(
    # Clés API / Tokens
    "api[_-]?key['\":\s=]+[a-zA-Z0-9_-]{20,}"
    "api[_-]?secret['\":\s=]+[a-zA-Z0-9_-]{20,}"
    "access[_-]?token['\":\s=]+['\"]?[a-zA-Z0-9_-]{20,}['\"]?"
    "bearer['\":\s]+[a-zA-Z0-9_-]{20,}"
    "ghp_[a-zA-Z0-9]{36,}"
    "gho_[a-zA-Z0-9]{36,}"
    "xox[baprs]-[a-zA-Z0-9]{10,}"
    "sk-[a-zA-Z0-9]{48,}"
    "sk-proj-[a-zA-Z0-9_-]{48,}"
    # Mots de passe
    "password['\":\s=]+['\"]?[^\s'\"]{8,}['\"]?"
    "passwd['\":\s=]+['\"]?[^\s'\"]{8,}['\"]?"
    "pwd['\":\s=]+['\"]?[^\s'\"]{8,}['\"]?"
    # Connexions DB
    "mongodb://[^\s'\"]{10,}"
    "postgres://[^\s'\"]{10,}"
    "mysql://[^\s'\"]{10,}"
    "redis://[^\s'\"]{10,}"
    # Clés SSH / Certificats
    "-----BEGIN[ A-Z]+PRIVATE KEY-----"
    "ssh-rsa AAAA[0-9A-Za-z+/]{100,}"
    # AWS
    "AKIA[0-9A-Z]{16}"
    "aws[_-]?secret[_-]?access[_-]?key['\":\s=]+"
    # URLs avec credentials
    "https?://[a-zA-Z0-9_-]+:[a-zA-Z0-9_-]+@[^\s'\"<>]+"
)

# Fichiers à exclure du scan
EXCLUDE_PATTERNS=(
    "*.png" "*.jpg" "*.jpeg" "*.gif" "*.ico" "*.woff" "*.woff2" "*.ttf" "*.svg"
    ".git/*" "node_modules/*" "__pycache__/*" "*.pyc" "*.min.js" "*.min.css"
    "*.lock" "package-lock.json" "yarn.lock" "Cargo.lock"
    "*.pdf" "*.zip" "*.tar" "*.gz"
)

SECRETS_FOUND=0
SECRET_DETAILS=()

log_msg() {
    echo "[$(date +%H:%M:%S)] [SECRET_SCANNER] [$TRACE_ID] $1" >> "$LOG_FILE"
}

scan_file_for_secrets() {
    local file="$1"
    local found=0
    
    # Vérifier si le fichier doit être exclu
    for pattern in "${EXCLUDE_PATTERNS[@]}"; do
        if [[ "$file" == $pattern ]]; then
            return 0
        fi
    done
    
    # Scanner le fichier avec grep
    for pattern in "${SECRET_PATTERNS[@]}"; do
        if grep -E -n -i -- "$pattern" "$file" 2>/dev/null | head -3 >> "$LOG_FILE"; then
            local matches
            matches=$(grep -E -n -i -- "$pattern" "$file" 2>/dev/null | head -3)
            while IFS= read -r match; do
                [ -z "$match" ] && continue
                SECRET_DETAILS+=("  $file: $match")
                ((SECRETS_FOUND++))
                found=1
            done <<< "$matches"
        fi
    done
    
    return $found
}

log_msg "Démarrage du scan de secrets..."

# Scanner chaque fichier stagé
while IFS= read -r file; do
    [ -z "$file" ] && continue
    if [ -f "$file" ]; then
        scan_file_for_secrets "$file" || true
    fi
done <<< "$STAGED_FILES"

# Résultat
if [ "$SECRETS_FOUND" -gt 0 ]; then
    echo ""
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║              ATTENTION: SECRETS DÉTECTÉS                      ║"
    echo "╠═══════════════════════════════════════════════════════════════╣"
    printf "║ %-60s ║\n" "Secrets détectés: $SECRETS_FOUND"
    echo "╠═══════════════════════════════════════════════════════════════╣"
    for detail in "${SECRET_DETAILS[@]}"; do
        printf "║ %-60s ║\n" "$detail"
    done
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo ""
    echo "ACTION REQUISE:"
    echo "  1. Retirez les secrets du code"
    echo "  2. Utilisez des variables d'environnement ou un vault"
    echo "  3. Re-stagez les fichiers corrigés"
    echo ""
    log_msg "SECRETS FOUND: $SECRETS_FOUND — BLOCKING"
    exit 1
fi

echo "✓ Aucun secret détecté dans les fichiers stagés"
log_msg "Scan terminé — Aucun secret détecté"
exit 0
