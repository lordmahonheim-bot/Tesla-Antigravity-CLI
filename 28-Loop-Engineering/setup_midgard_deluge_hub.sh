#!/bin/bash
# setup_midgard_deluge_hub.sh
# Script d'ingénierie : Relocalisation du dossier de téléchargement de Deluge vers /srv/midgard_data
# Doit être exécuté avec des privilèges sudo (root)

# Mode strict d'exécution (arrête le script à la première erreur)
set -e

echo "Démarrage de la séquence d'ingénierie : Configuration du hub Deluge sur Midgard..."

# 1. Création de l'arborescence
echo "[1/5] Création du dossier /srv/midgard_data/torrents..."
mkdir -p /srv/midgard_data/torrents

# 2. Création du groupe système "media" s'il n'existe pas
echo "[2/5] Création du groupe media..."
groupadd -f media

# 3. Ajout des utilisateurs au groupe media
echo "[3/5] Ajout des utilisateurs deluge et lord-mahonheim au groupe media..."
# On utilise usermod. On ignore les erreurs si l'utilisateur n'existe pas (bien que ce soit mieux de vérifier, set -e arrêtera si usermod échoue).
# Pour un script robuste, on suppose que les utilisateurs existent.
usermod -aG media deluge
usermod -aG media lord-mahonheim

# 4. Application des droits et du bit SGID (Set Group ID)
echo "[4/5] Configuration des permissions et du bit SGID..."
chown -R deluge:media /srv/midgard_data
chmod -R 2770 /srv/midgard_data

# 5. Configuration de Deluge via deluge-console
echo "[5/5] Configuration du dossier par défaut dans Deluge..."
# Exécution de la commande en tant qu'utilisateur deluge
sudo -u deluge deluge-console "config -s download_location /srv/midgard_data/torrents"

# 6. Redémarrage du service
echo "[6/5] Redémarrage du service deluged..."
systemctl restart deluged

echo "Succès : La relocalisation du dossier de téléchargement de Deluge a été effectuée avec succès !"
