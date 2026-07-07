#!/usr/bin/env bash
# Tesla Governance Gateway (TGG) - Policy Engine v1

set -e

# Dossier d'exécution
TGG_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TESLA_ROOT="$(cd "$TGG_DIR/../.." && pwd)"
HEALTH_DIR="$TESLA_ROOT/.runtime/capability-health"

mkdir -p "$HEALTH_DIR"

# Génération d'un trace_id unique pour cette validation
TRACE_ID="req-$(head -c 4 /dev/urandom | xxd -p)"
export TRACE_ID

echo "═══════════════════════════════════════════"
echo " Tesla Governance Gateway (TGG v1.0)"
echo " Trace ID : $TRACE_ID"
echo "═══════════════════════════════════════════"

REGISTRY_FILE="$TGG_DIR/capability_registry.json"

if [ ! -f "$REGISTRY_FILE" ]; then
    echo "[CRITICAL] Capability Registry introuvable."
    exit 1
fi

# Parsing des capacités avec jq
CAPABILITIES=$(jq -c '.capabilities[]' "$REGISTRY_FILE")

declare -a SYNC_PIDS
declare -a SYNC_CAPS

while read -r CAP; do
    CAP_ID=$(echo "$CAP" | jq -r '.id')
    AGENT=$(echo "$CAP" | jq -r '.agent')
    SCRIPT=$(echo "$CAP" | jq -r '.script')
    PRIORITY=$(echo "$CAP" | jq -r '.priority')
    ASYNC=$(echo "$CAP" | jq -r '.async')

    SCRIPT_PATH="$TGG_DIR/$SCRIPT"

    if [ ! -x "$SCRIPT_PATH" ]; then
        echo "  [?] Agent $AGENT non exécutable ou absent ($SCRIPT_PATH)"
        continue
    fi

    # Exécution
    if [ "$ASYNC" = "true" ]; then
        echo "  [>] $PRIORITY : Dispatch async -> $CAP_ID ($AGENT)"
        nohup "$SCRIPT_PATH" > /dev/null 2>&1 &
    else
        echo "  [>] $PRIORITY : Exécution parallèle -> $CAP_ID ($AGENT)"
        "$SCRIPT_PATH" &
        PID=$!
        SYNC_PIDS+=($PID)
        SYNC_CAPS+=("$CAP_ID")
    fi
done <<< "$CAPABILITIES"

# Attente des tâches synchrones
for pid in "${SYNC_PIDS[@]}"; do
    wait $pid || true
done

echo ""
echo "═══════════════════════════════════════════"
echo " Commit Validation Report"
echo "═══════════════════════════════════════════"

HAS_ERROR=0

# Analyse des Health Reports
for CAP_ID in "${SYNC_CAPS[@]}"; do
    REPORT_FILE="$HEALTH_DIR/${TRACE_ID}_${CAP_ID}.json"

    if [ ! -f "$REPORT_FILE" ]; then
        echo -e "\033[31m[CRITICAL]\033[0m $CAP_ID : AUCUN REPORT (Contournement détecté)"
        HAS_ERROR=1
        continue
    fi

    STATUS=$(jq -r '.status' "$REPORT_FILE")
    REASON=$(jq -r '.reason' "$REPORT_FILE")

    if [ "$STATUS" = "CRITICAL" ] || [ "$STATUS" = "ERROR" ]; then
        echo -e "\033[31m[$STATUS]\033[0m $CAP_ID : $REASON"
        HAS_ERROR=1
    elif [ "$STATUS" = "WARNING" ]; then
        echo -e "\033[33m[$STATUS]\033[0m $CAP_ID : $REASON"
    else
        echo -e "\033[32m[$STATUS]\033[0m $CAP_ID"
    fi
done

echo "═══════════════════════════════════════════"

if [ $HAS_ERROR -eq 1 ]; then
    echo -e "\033[31mFINAL RESULT: ✘ COMMIT REJETÉ\033[0m"
    exit 1
else
    echo -e "\033[32mFINAL RESULT: ✔ COMMIT AUTORISÉ\033[0m"
    exit 0
fi
