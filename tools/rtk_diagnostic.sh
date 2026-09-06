#!/bin/bash
# rtk_diagnostic.sh - A executer au demarrage de session

# 1. Verifier que RTK est installe
if ! command -v rtk >/dev/null 2>&1; then
    echo "[CRITICAL] RTK non installe. Installation requise."
    exit 1
fi

# 2. Verifier que les hooks sont actifs
GAIN=$(rtk gain --format json 2>/dev/null)
if [ -z "$GAIN" ]; then
    echo "[CRITICAL] RTK gain ne retourne aucune donnee. Les hooks sont inactifs."
    echo "[ACTION] Reinitialisez les hooks manuellement : rtk init -g --gemini"
    exit 1
fi

# 3. Test de compression reel : comparer sortie brute vs sortie RTK
# Necessite d'etre dans un depot Git
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    RAW_LINES=$(git status 2>/dev/null | wc -l)
    RTK_LINES=$(rtk git status 2>/dev/null | wc -l)
    if [ "$RAW_LINES" -gt 0 ] && [ "$RTK_LINES" -ge "$RAW_LINES" ]; then
        echo "[CRITICAL] RTK ne compresse pas. Sorties identiques ($RAW_LINES lignes)."
        exit 1
    else
        RATIO=$(( (RAW_LINES - RTK_LINES) * 100 / RAW_LINES ))
        echo "[OK] RTK compression active : $RAW_LINES vers $RTK_LINES lignes ($RATIO% reduit)."
    fi
else
    echo "[INFO] Pas dans un depot Git. Test de compression ignore."
fi
