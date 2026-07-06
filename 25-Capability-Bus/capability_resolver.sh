#!/usr/bin/env bash
# capability_resolver.sh - Résolution déterministe des dépendances et exécution (V2)

PAYLOAD_FILE="$1"
if [ ! -f "$PAYLOAD_FILE" ]; then
    echo "[-] ERREUR RESOLVER: Payload introuvable ($PAYLOAD_FILE)"
    exit 1
fi

REGISTRY="$(dirname "$0")/registry.json"
PLUGINS_DIR="$(dirname "$0")/plugins"
HEALTH_DIR="/tmp/tesla_health"

mkdir -p "$HEALTH_DIR"

EVENT_TYPE=$(jq -r '.event' "$PAYLOAD_FILE")
LEVEL=$(jq -r '.level' "$PAYLOAD_FILE")

echo " ↳ [Resolver] Chargement du registre et calcul de l'arbre d'exécution..."

if [ ! -f "$REGISTRY" ]; then
    echo "[-] ERREUR RESOLVER: Registre introuvable ($REGISTRY)"
    exit 1
fi

# Le Resolver ne fait QUE la résolution.
# Il filtre les plugins (enabled=true, events, levels) et les trie par priority.
# (La résolution complète en DAG est préparée via les champs depends_on, mais le tri par priorité 
# assure la séquence correcte de manière déterministe pour cette itération).

PLUGINS_TO_RUN=$(jq -r --arg event "$EVENT_TYPE" --argjson level "$LEVEL" \
    '.plugins | map(select(.enabled == true and (.events | index($event)) and (.levels | index($level)))) | sort_by(.priority) | .[] | @base64' "$REGISTRY")

for row in $PLUGINS_TO_RUN; do
    _jq() {
        echo "${row}" | base64 --decode | jq -r "${1}"
    }
    
    PLUGIN_ID=$(_jq '.id')
    SCRIPT_NAME=$(_jq '.script')
    TIMEOUT=$(_jq '.policy.timeout')
    
    # Vérification des prérequis
    REQUIRES=$(_jq '.requires | join(" ")')
    MISSING_REQ=false
    for req in $REQUIRES; do
        if ! command -v "$req" >/dev/null 2>&1; then
            MISSING_REQ=true
            echo " ↳ [Resolver] Échec: Prérequis manquant ($req) pour la Capability $PLUGIN_ID"
            break
        fi
    done
    
    if [ "$MISSING_REQ" = true ]; then
        continue
    fi
    
    plugin_path="$PLUGINS_DIR/$SCRIPT_NAME"
    if [ -x "$plugin_path" ]; then
        echo " ↳ [Resolver] Ordonnancement -> $PLUGIN_ID"
        
        # Exécution avec timeout
        timeout "$TIMEOUT" "$plugin_path" "$PAYLOAD_FILE"
        EXIT_CODE=$?
        
        # Vérification si le Health Status a été généré
        HEALTH_FILE="$HEALTH_DIR/${PLUGIN_ID}.json"
        if [ ! -f "$HEALTH_FILE" ]; then
            echo " ↳ [Resolver] AVERTISSEMENT : La capability n'a pas produit de Status File."
        fi
        
        if [ $EXIT_CODE -ne 0 ]; then
            IS_CRITICAL=$(_jq '.policy.critical')
            if [ "$IS_CRITICAL" == "true" ]; then
                echo "[-] ERREUR RESOLVER: Capability critique ($PLUGIN_ID) a échoué. Arrêt de la chaîne."
                exit 1
            fi
        fi
    else
        echo " ↳ [Resolver] AVERTISSEMENT: Script manquant ou non exécutable : $SCRIPT_NAME"
    fi
done

echo "[✓ CAPABILITY BUS] Résolution et exécution terminées avec succès."
