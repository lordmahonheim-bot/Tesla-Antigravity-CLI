#!/usr/bin/env bash
# watch_and_count.sh — Watch a file and print its token count using entr and tiktoken

if [ -z "$1" ]; then
    echo "Usage: $0 <file_to_watch>"
    exit 1
fi

TARGET_FILE="$1"

if [ ! -f "$TARGET_FILE" ]; then
    echo "Error: File '$TARGET_FILE' does not exist."
    exit 1
fi

# Resolve absolute path
ABS_FILE=$(realpath "$TARGET_FILE")

echo "Watching $ABS_FILE. Press Ctrl+C to stop."
TOKENS=$(tiktoken < "$ABS_FILE")
echo "[$(date '+%H:%M:%S')] Initial token count: $TOKENS"

# Watch file and run tiktoken on change
echo "$ABS_FILE" | entr -s "TOKENS=\$(tiktoken < '$ABS_FILE'); echo \"[\$(date '+%H:%M:%S')] File modified. Current token count: \$TOKENS\""
