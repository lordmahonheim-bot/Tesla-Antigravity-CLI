#!/bin/bash
# ==============================================================================
# 👁️ Surveillance Automatisée (entr) - Projet Veille Stratégique
# ==============================================================================
# Ce script utilise 'entr' pour surveiller toute modification des fichiers Markdown
# dans le projet. Dès qu'un rapport ou highlight est ajouté ou modifié,
# l'action définie ci-dessous est automatiquement déclenchée.

# Vérification des dépendances
if ! command -v entr &> /dev/null; then
    echo "❌ L'utilitaire 'entr' est introuvable. Veuillez l'installer (ex: sudo apt install entr)."
    exit 1
fi

echo "🟢 [VIGILUM] Surveillance activée sur le dossier Veille Stratégique."
echo "En attente de modifications... (Ctrl+C pour quitter)"

# Commande 'entr' :
# -d : Réagit si un nouveau fichier est ajouté au répertoire
# -p : Ne pas effacer l'écran (postpone)
# Action par défaut : Afficher un log. 
# -> Remplacez la commande "echo ..." par votre trigger Alexandria, rsync ou git commit.

while sleep 1; do
    find . -name "*.md" | entr -d -p sh -c 'echo "⚡ [$(date +%H:%M:%S)] Modification détectée. Déclenchement du protocole de synchro/indexation."'
done
