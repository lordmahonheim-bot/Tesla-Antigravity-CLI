#!/bin/bash
# setup_keyring.sh - Configuration de l'infrastructure keyring pour agy

# 1. Installer les dependances minimales
sudo apt-get install --no-install-recommends -y dbus gnome-keyring libsecret-1-0 xdg-utils

# 2. Creer le repertoire de stockage keyring
mkdir -p ~/.local/share/keyrings

# 3. Configurer le daemon via Systemd (Zero-Touch Ops)
mkdir -p ~/.config/systemd/user
cat << 'EOF' > ~/.config/systemd/user/tesla-keyring.service
[Unit]
Description=Tesla Secret Service (gnome-keyring)
After=dbus.socket

[Service]
Type=simple
Environment=XDG_RUNTIME_DIR=/run/user/%U
ExecStart=/usr/bin/gnome-keyring-daemon --start --foreground --components=secrets
Restart=on-failure

[Install]
WantedBy=default.target
EOF

systemctl --user daemon-reload
systemctl --user enable --now tesla-keyring.service

echo "[OK] Service tesla-keyring active via systemd."
echo "[SECURITY] Le keyring necessite une authentification chiffree via PAM ou un mot de passe explicite. Pas de deverrouillage en clair."
