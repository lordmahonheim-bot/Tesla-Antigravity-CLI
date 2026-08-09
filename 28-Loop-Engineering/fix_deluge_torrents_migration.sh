#!/bin/bash
set -e

# Dossier d'état de Deluge
DELUGE_STATE_DIR="/var/lib/deluge/.config/deluge/state"
# Dossier de sauvegarde temporaire
TEMP_RECOVERY_DIR="/tmp/deluge_recovery"

echo "=== Début de la Nécromancie Zéro Friction : Migration des torrents Deluge ==="

# Vérification des privilèges
if [ "$EUID" -ne 0 ]; then
  echo "Erreur : Ce script doit être exécuté en tant que root (sudo)."
  exit 1
fi

# 1. Sauvegarder temporairement tous les fichiers *.torrent
echo "[1/7] Création du répertoire temporaire et sauvegarde des fichiers .torrent..."
mkdir -p "$TEMP_RECOVERY_DIR"

# Utilisation de shopt pour gérer le cas où il n'y a pas de fichiers .torrent (évite les erreurs de globbing)
shopt -s nullglob
fichiers_torrent=("$DELUGE_STATE_DIR"/*.torrent)

if [ ${#fichiers_torrent[@]} -gt 0 ]; then
    cp "${fichiers_torrent[@]}" "$TEMP_RECOVERY_DIR/"
    echo "${#fichiers_torrent[@]} fichier(s) .torrent sauvegardé(s) dans $TEMP_RECOVERY_DIR."
    
    # Suppression des .torrent du dossier state pour éviter le rechargement automatique
    rm -f "$DELUGE_STATE_DIR"/*.torrent
else
    echo "Aucun fichier .torrent trouvé dans $DELUGE_STATE_DIR. La suite risque de ne rien ré-injecter."
fi

# 2. Purger la session actuelle de deluged
echo "[2/7] Purge de la session actuelle dans deluged..."
sudo -u deluge deluge-console "rm -c '*'" || echo "Purge de la session terminee"

# 3. Arrêter deluged
echo "[3/7] Arrêt du service deluged..."
systemctl stop deluged

# 4. Supprimer torrents.state et torrents.fastresume
echo "[4/7] Purge des fichiers d'état pour nettoyer l'interface de Deluge..."
rm -f "$DELUGE_STATE_DIR/torrents.state"
rm -f "$DELUGE_STATE_DIR/torrents.fastresume"

# 5. Redémarrer deluged
echo "[5/7] Redémarrage du service deluged..."
systemctl start deluged

# Attendre quelques secondes
echo "Attente de 3 secondes pour l'initialisation du service..."
sleep 3

# 5. Boucler sur les fichiers .torrent sauvegardés et les ré-injecter
echo "[6/7] Ré-injection des fichiers .torrent via deluge-console..."
fichiers_sauvegardes=("$TEMP_RECOVERY_DIR"/*.torrent)

if [ ${#fichiers_sauvegardes[@]} -gt 0 ]; then
    for fichier_torrent in "${fichiers_sauvegardes[@]}"; do
        echo "Ajout du torrent : $fichier_torrent"
        # Injection du torrent dans la file via la commande demandée
        sudo -u deluge deluge-console "add -p /srv/midgard_data/torrents \"$fichier_torrent\""
    done
else
    echo "Aucun fichier à ré-injecter."
fi

# 6. Nettoyer le dossier temporaire
echo "[7/7] Nettoyage du dossier temporaire de récupération..."
rm -rf "$TEMP_RECOVERY_DIR"

echo "=== Opération terminée avec succès ! ==="
