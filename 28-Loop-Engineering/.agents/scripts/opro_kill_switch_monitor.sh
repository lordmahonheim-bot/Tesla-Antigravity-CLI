#!/usr/bin/env bash
# opro_kill_switch_monitor.sh
# Règle 15 : Kill-Switch Physique & Limites d'Auto-Évolution
# VERDICT PREMORTEM : Exécution synchrone (Bloquante Pré-Inférence) pour éliminer la latence de 10s.

KILL_SWITCH_FILE="/etc/tesla/HALT_OPRO"
STATE_FILE="/home/lord-mahonheim/bifrost/tesla/.agents/schemas/kill_switch_state.json"
MAX_DAILY_TOKENS=500000
MAX_HOURLY_TRIGGERS=5

# Niveau 1 : Kill-Switch Physique (Vérification micro-seconde)
if [ -f "$KILL_SWITCH_FILE" ]; then
    echo "[URGENCE] 🛑 Fichier HALT_OPRO détecté. Inférence immédiate VERROUILLÉE."
    exit 1
fi

# Initialisation du state si inexistant
if [ ! -f "$STATE_FILE" ]; then
    echo '{"hourly_triggers_count": 0, "daily_token_usage": 0}' > "$STATE_FILE"
fi

# Niveau 2 & 3 : Extraction des métriques
HOURLY_TRIGGERS=$(jq '.hourly_triggers_count' "$STATE_FILE")
DAILY_TOKENS=$(jq '.daily_token_usage' "$STATE_FILE")

if [ "$DAILY_TOKENS" -gt 400000 ]; then
    MAX_HOURLY_TRIGGERS=1
    echo "[BACKPRESSURE] ⚠️ Budget Token > 80% (400k). Réduction MAX_HOURLY_TRIGGERS à 1."
fi

if [ "$HOURLY_TRIGGERS" -ge "$MAX_HOURLY_TRIGGERS" ]; then
    echo "[BLOCAGE] ⛔ Rate limit atteint : $MAX_HOURLY_TRIGGERS déclenchements OPRO dans l'heure."
    exit 2
fi

if [ "$DAILY_TOKENS" -ge "$MAX_DAILY_TOKENS" ]; then
    echo "[BLOCAGE] ⛔ Budget Token Quotidien OPRO épuisé (500k)."
    exit 3
fi

exit 0
