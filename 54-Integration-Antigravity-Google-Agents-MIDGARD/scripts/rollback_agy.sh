#!/bin/bash
# rollback_agy.sh - Revenir a la version precedente stable d'agy

CURRENT_AGY=$(which agy)
BACKUP_AGY="/usr/local/bin/agy.stable.bak"

if [ -f "$BACKUP_AGY" ]; then
    echo "[INFO] Restauration du binaire stable..."
    sudo cp "$BACKUP_AGY" "$CURRENT_AGY"
    chmod +x "$CURRENT_AGY"
    agy --version
    echo "[OK] Rollback effectue."
else
    echo "[CRITICAL] Aucun backup stable trouve a $BACKUP_AGY."
    echo "[ACTION] Telechargement manuel obligatoire depuis :"
    echo "  https://github.com/google-antigravity/antigravity-cli/releases"
    exit 1
fi
