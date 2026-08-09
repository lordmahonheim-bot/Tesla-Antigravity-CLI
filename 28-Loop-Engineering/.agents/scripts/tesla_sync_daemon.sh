#!/bin/bash
# TESLA SYNC DAEMON - Vigilum Codex Rule 8
# Watches for changes in canonical /memory files and syncs them to their respective locations.

MEMORY_DIR="/home/lord-mahonheim/bifrost/tesla/memory"
AGENTS_DIR="/home/lord-mahonheim/bifrost/tesla/.agents"
GEMINI_DIR="/home/lord-mahonheim/.gemini"
AVALON_CANONICAL="/home/lord-mahonheim/bifrost/tesla/Avalon/99-System/CANONICAL"

FILES="$MEMORY_DIR/AGENTS.md $MEMORY_DIR/ENGINE.md $MEMORY_DIR/FORCE_TOOLING.md $MEMORY_DIR/GEMINI.md $MEMORY_DIR/TESLA.json $MEMORY_DIR/settings.json"

echo "Tesla Sync Daemon Starting..."
echo "$FILES" | tr ' ' '\n' | /home/lord-mahonheim/.local/bin/entr -n -p /bin/bash -c "
    echo \"[$(date)] Change detected. Syncing canonical files...\"
    
    # Sync to .agents
    cp -f $MEMORY_DIR/AGENTS.md $AGENTS_DIR/AGENTS.md 2>/dev/null
    cp -f $MEMORY_DIR/ENGINE.md $AGENTS_DIR/ENGINE.md 2>/dev/null
    cp -f $MEMORY_DIR/FORCE_TOOLING.md $AGENTS_DIR/FORCE_TOOLING.md 2>/dev/null
    cp -f $MEMORY_DIR/GEMINI.md $AGENTS_DIR/GEMINI.md 2>/dev/null
    
    # Sync to .gemini
    cp -f $MEMORY_DIR/AGENTS.md $GEMINI_DIR/AGENTS.md 2>/dev/null
    cp -f $MEMORY_DIR/ENGINE.md $GEMINI_DIR/ENGINE.md 2>/dev/null
    cp -f $MEMORY_DIR/FORCE_TOOLING.md $GEMINI_DIR/FORCE_TOOLING.md 2>/dev/null
    cp -f $MEMORY_DIR/GEMINI.md $GEMINI_DIR/GEMINI.md 2>/dev/null
    
    # Sync to Avalon Vault
    cp -f $MEMORY_DIR/AGENTS.md $AVALON_CANONICAL/AGENTS.md 2>/dev/null
    cp -f $MEMORY_DIR/ENGINE.md $AVALON_CANONICAL/ENGINE.md 2>/dev/null
    cp -f $MEMORY_DIR/FORCE_TOOLING.md $AVALON_CANONICAL/FORCE_TOOLING.md 2>/dev/null
    cp -f $MEMORY_DIR/GEMINI.md $AVALON_CANONICAL/GEMINI.md 2>/dev/null
    cp -f $MEMORY_DIR/TESLA.json $AVALON_CANONICAL/TESLA.json 2>/dev/null
    cp -f $MEMORY_DIR/settings.json $AVALON_CANONICAL/settings.json 2>/dev/null
    
    echo \"[$(date)] Sync complete.\"
"
