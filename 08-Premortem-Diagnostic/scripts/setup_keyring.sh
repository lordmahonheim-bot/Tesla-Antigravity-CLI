#!/bin/bash
# setup_keyring.sh - Configuration de l'infrastructure keyring pour agy

# 1. Installer les dependances minimales
sudo apt-get install --no-install-recommends -y dbus gnome-keyring libsecret-1-0 xdg-utils

# 2. Creer le repertoire de stockage keyring
mkdir -p ~/.local/share/keyrings

# 3. Configurer le daemon au demarrage de session
# Ajouter les lignes suivantes au fichier ~/.bashrc manuellement :
#
# if [ -z "$DBUS_SESSION_BUS_ADDRESS" ]; then
#     export DBUS_SESSION_BUS_ADDRESS=$(dbus-daemon --session --print-address --fork)
# fi
# if [ -z "$GNOME_KEYRING_CONTROL" ]; then
#     export $(echo -n "" | gnome-keyring-daemon --unlock --start --components=secrets 2>/dev/null)
# fi

echo "[INFO] Ajouter le bloc keyring au fichier ~/.bashrc, puis redemarrer le shell."
echo "AVERTISSEMENT : Le keyring est deverrouille sans mot de passe."
echo "Acceptable UNIQUEMENT sur une machine mono-utilisateur isolee."
