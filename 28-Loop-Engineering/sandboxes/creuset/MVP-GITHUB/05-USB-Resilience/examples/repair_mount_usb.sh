#!/bin/bash
# 05-USB-Resilience: Repair and Mount NTFS Partition
# Safely clears dirty NTFS bits and mounts partition using local ntfs3
set -euo pipefail

DEVICE=${1:-"/dev/sdb1"}
MOUNT_POINT=${2:-"/media/$USER/DISK"}

echo "=== [⚙️] Starting NTFS Resilience mount script for $DEVICE ==="

# 1. Checks device existence
if [ ! -b "$DEVICE" ]; then
    echo "[-] Error: Device $DEVICE is not available or is not a block device."
    exit 1
fi

# 2. Clears NTFS dirty bit
echo "[*] Fixing filesystem inconsistencies using ntfsfix..."
if ! sudo ntfsfix "$DEVICE"; then
    echo "[!] Warning: ntfsfix exited with warnings, proceeding anyway."
fi

# 3. Creates mount directory
echo "[*] Creating mount point: $MOUNT_POINT"
sudo mkdir -p "$MOUNT_POINT"

# 4. Mounts partition using ntfs3 with forced write option
echo "[*] Mounting device using ntfs3 driver (forced rw)..."
if sudo mount -t ntfs3 -o force "$DEVICE" "$MOUNT_POINT"; then
    echo "[✓] Mount successful! Write access granted under $MOUNT_POINT"
else
    echo "[-] Forced rw mount failed. Retrying read-only (ro)..."
    if sudo mount -t ntfs3 -o ro "$DEVICE" "$MOUNT_POINT"; then
        echo "[✓] Read-only mount successful under $MOUNT_POINT"
    else
        echo "[-] Critical Error: Unable to mount partition $DEVICE."
        exit 1
    fi
fi
