#!/bin/bash
# git_backup.sh - Effectue un commit automatique de sauvegarde sur le dépôt local du Vault Avalon.

VAULT_DIR="/home/lord-mahonheim/bifrost/tesla/Avalon"

if [ ! -d "$VAULT_DIR/.git" ]; then
    echo "[!] Dépôt Git introuvable dans $VAULT_DIR."
    exit 1
fi

cd "$VAULT_DIR" || exit 1

# S'assurer que l'identité locale est préservée
git config user.name "Tesla" &>/dev/null
git config user.email "tesla@antigravity.local" &>/dev/null

# Vérifier s'il y a des changements (fichiers modifiés ou non suivis)
if [ -n "$(git status --porcelain)" ]; then
    git add .
    git commit -m "Auto-commit: Tesla update $(date '+%Y-%m-%d %H:%M:%S')"
    echo "[+] Sauvegarde Git complétée avec succès."
else
    echo "[*] Aucun changement détecté dans le Vault."
fi
