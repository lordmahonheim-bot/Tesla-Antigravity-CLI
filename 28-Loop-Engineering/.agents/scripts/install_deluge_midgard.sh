#!/usr/bin/env bash
#
# Zéro-Touch Installation Script for Deluge on MIDGARD
# Based on Output N3 Blueprint
#

set -euo pipefail

# Ensure script is run as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root"
  exit 1
fi

echo "Starting Deluge Zero-Touch Installation..."

# 1. Install dependencies
echo "Installing dependencies..."
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y deluged deluge-web deluge-console

# 2. Create user/group 'deluge' if it doesn't exist
echo "Setting up 'deluge' user and group..."
if ! getent group deluge > /dev/null; then
    groupadd -r deluge
fi

if ! getent passwd deluge > /dev/null; then
    useradd -r -g deluge -d /var/lib/deluge -s /usr/sbin/nologin -c "Deluge Daemon" deluge
fi

# Create Home and config directory
mkdir -p /var/lib/deluge/.config/deluge
mkdir -p /var/log/deluge

# Apply permissions for /var/lib/deluge and /var/log/deluge
chown -R deluge:deluge /var/lib/deluge /var/log/deluge
chmod 750 /var/lib/deluge
chmod 700 /var/lib/deluge/.config/deluge
chmod 750 /var/log/deluge

# 3. Create the tree /home/lord-mahonheim/midgard_data/{torrents,media}
echo "Setting up data directories..."
DATA_DIR="/home/lord-mahonheim/midgard_data"
mkdir -p "${DATA_DIR}/torrents"
mkdir -p "${DATA_DIR}/media"

# Set ownership and permissions as per blueprint (chmod 2770 + chown deluge:deluge)
chown -R deluge:deluge "${DATA_DIR}"
# Apply SGID and rwX to all dirs, since chmod 2770 sets it on the parent
# Find directories and set 2770, files 0660 (if any exist)
find "${DATA_DIR}" -type d -exec chmod 2770 {} +
find "${DATA_DIR}" -type f -exec chmod 0660 {} +

# 4. Generate systemd unit files
echo "Writing systemd unit files..."

cat << 'EOF' > /etc/systemd/system/deluged.service
[Unit]
Description=Deluge BitTorrent Client Daemon (deluged)
Documentation=man:deluged
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=deluge
Group=deluge
UMask=0002

# Environnement et exécution
Environment="HOME=/var/lib/deluge"
ExecStart=/usr/bin/deluged -d -c /var/lib/deluge/.config/deluge -l /var/log/deluge/daemon.log -L info

# Politique de redémarrage
Restart=on-failure
TimeoutStopSec=300

# ----------------------------------------------------
# ISOLATION DE SÉCURITÉ & RESSOURCES (Mitigation N2)
# ----------------------------------------------------
# MITIGATION CRITIQUE (OOM mmap libtorrent 2.x) :
MemoryHigh=1G
MemoryMax=2G

ProtectSystem=full
ProtectHome=read-only
ReadWritePaths=/home/lord-mahonheim/midgard_data /var/lib/deluge /var/log/deluge
PrivateTmp=true
NoNewPrivileges=true
ProtectKernelTunables=true
ProtectKernelModules=true
ProtectControlGroups=true
RestrictNamespaces=true
RestrictRealtime=true

[Install]
WantedBy=multi-user.target
EOF

cat << 'EOF' > /etc/systemd/system/deluge-web.service
[Unit]
Description=Deluge Web UI (deluge-web)
Documentation=man:deluge-web
After=network-online.target deluged.service
Wants=deluged.service

[Service]
Type=simple
User=deluge
Group=deluge
UMask=0002

Environment="HOME=/var/lib/deluge"
ExecStart=/usr/bin/deluge-web -d -c /var/lib/deluge/.config/deluge -l /var/log/deluge/web.log -L info

Restart=on-failure

# ----------------------------------------------------
# ISOLATION DE SÉCURITÉ
# ----------------------------------------------------
ProtectSystem=full
ProtectHome=read-only
ReadWritePaths=/var/lib/deluge /var/log/deluge
PrivateTmp=true
NoNewPrivileges=true
ProtectKernelTunables=true
ProtectKernelModules=true
ProtectControlGroups=true
RestrictNamespaces=true
RestrictRealtime=true

[Install]
WantedBy=multi-user.target
EOF

# Recommended Logrotate Config
echo "Writing logrotate configuration..."
cat << 'EOF' > /etc/logrotate.d/deluge
/var/log/deluge/*.log {
    weekly
    missingok
    rotate 4
    compress
    notifempty
    create 640 deluge deluge
}
EOF

# 5. systemctl daemon-reload, enable, restart
echo "Reloading and enabling systemd units..."
systemctl daemon-reload
systemctl enable deluged.service deluge-web.service
systemctl restart deluged.service deluge-web.service

echo "Deluge Zero-Touch Installation completed successfully."
