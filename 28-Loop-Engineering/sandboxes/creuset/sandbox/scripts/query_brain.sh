#!/bin/bash
# query_brain.sh - Outil CLI local de recherche rapide combinant sqlite3 et fzf.

DB_PATH="/home/lord-mahonheim/bifrost/tesla/DataBase/avalon_brain.db"
VAULT_DIR="/home/lord-mahonheim/bifrost/tesla/Avalon"

if [ ! -f "$DB_PATH" ]; then
    echo "[!] Base de données introuvable à l'emplacement : $DB_PATH"
    echo "[*] Veuillez exécuter le script de synchronisation d'abord."
    exit 1
fi

# Recherche directe en argument si spécifié
if [ -n "$1" ]; then
    echo "=== Résultats pour la recherche FTS5 : '$1' ==="
    sqlite3 -header -column "$DB_PATH" "
    SELECT filepath, title, type, tags 
    FROM fts_vault_index 
    WHERE fts_vault_index MATCH '$1' 
    ORDER BY rank;
    "
    exit 0
fi

# Mode interactif avec fzf si disponible
if ! command -v fzf &> /dev/null; then
    echo "[!] fzf n'est pas disponible dans le PATH. Veuillez fournir un argument pour la recherche."
    echo "Usage: $0 <terme_de_recherche>"
    exit 1
fi

# Sélection de note dynamique via fzf
selected=$(sqlite3 "$DB_PATH" "SELECT filepath || ' | ' || title || ' [' || type || ']' FROM fts_vault_index;" | fzf --prompt="Recherche Avalon > " --header="Sélectionnez une note pour afficher son contenu")

if [ -n "$selected" ]; then
    # Extraire le filepath (première partie de la chaîne avant le premier pipe)
    filepath=$(echo "$selected" | cut -d'|' -f1 | xargs)
    
    echo ""
    echo "========================================================================"
    echo " FICHE : $filepath"
    echo "========================================================================"
    
    # Afficher le contenu depuis SQLite
    sqlite3 "$DB_PATH" "SELECT content FROM fts_vault_index WHERE filepath = '$filepath';"
    
    echo "========================================================================"
    echo " Chemin physique : $VAULT_DIR/$filepath"
fi
