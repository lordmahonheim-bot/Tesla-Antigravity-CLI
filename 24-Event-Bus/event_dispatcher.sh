#!/usr/bin/env bash
# event_dispatcher.sh - Adaptateur de transition vers le Capability Bus (Phase 1)
# Ce script garantit la rétrocompatibilité des anciens appels.

FILE_MODIFIED="$1"
if [ -z "$FILE_MODIFIED" ]; then
    echo "[-] ERREUR: Usage: $0 <filename>"
    exit 1
fi

echo "[ℹ️ EVENT BUS] Adaptateur sollicité. Transfert vers le Capability Bus..."
"$(dirname "$0")/../capability_bus/capability_dispatcher.sh" "$FILE_MODIFIED"
