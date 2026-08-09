#!/usr/bin/env bash
set -euo pipefail

# Tesla-Eye Watcher Script
# Triggered by systemd path when a new screenshot is created.

LOCKFILE="/tmp/tesla_eye_watcher.lock"

# Strict anti-reentrancy lock using flock
exec 200>"$LOCKFILE"
if ! flock -n 200; then
    echo "Another instance is already running. Exiting."
    exit 0
fi

WATCH_DIR="$HOME/Images/Captures d’écran"
PROCESSING_DIR="/tmp/tesla_eye_processing"

mkdir -p "$PROCESSING_DIR"

# Find the most recently created file in the watch directory
# systemd path unit triggers on any modification in the directory.
NEWEST_FILE=$(find "$WATCH_DIR" -maxdepth 1 -type f \( -iname "*.png" -o -iname "*.jpg" -o -iname "*.jpeg" \) -printf "%T@ %p\n" 2>/dev/null | sort -n | tail -1 | cut -d' ' -f2-)

if [[ -n "$NEWEST_FILE" && -f "$NEWEST_FILE" ]]; then
    FILENAME=$(basename "$NEWEST_FILE")
    DEST_FILE="$PROCESSING_DIR/$FILENAME"
    
    # Check if we already processed it
    if [[ ! -f "$DEST_FILE" ]]; then
        echo "Processing new screenshot: $NEWEST_FILE"
        cp "$NEWEST_FILE" "$DEST_FILE"
        
        # Send a desktop notification
        if command -v notify-send >/dev/null 2>&1; then
            notify-send "Tesla-Eye" "Captured and processing new image: $FILENAME" || true
        fi
    fi
fi
