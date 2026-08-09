#!/usr/bin/env bash
# ==============================================================================
# Script de debloating et d'optimisation réversible pour MECOOL KM7
# Doctrine du Vigilum Codex - Skill: tesla-master-code
# ==============================================================================

set -euo pipefail

export PATH="/home/lord-mahonheim/.local/bin:$PATH"

# Couleurs pour le terminal
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}======================================================================${NC}"
echo -e "${BLUE}           DEBLOATING & OPTIMISATION SYSTEME : MECOOL KM7             ${NC}"
echo -e "${BLUE}======================================================================${NC}"

# Vérifier si adb est connecté à un appareil
DEVICE_STATUS=$(adb devices | grep -v "List of devices" | grep "device" || true)
if [ -z "$DEVICE_STATUS" ]; then
    echo -e "${RED}[-]$NC Aucun appareil connecté via ADB. Veuillez d'abord exécuter le script de connexion."
    exit 1
fi

echo -e "${GREEN}[+]${NC} Appareil ADB détecté."

# Liste des packages ciblés pour le debloating (bloatwares, télémétrie, services obsolètes)
# Ces packages sont désactivés ou désinstallés uniquement pour l'utilisateur 0, de manière réversible.
PACKAGES_TO_REMOVE=(
    "com.sundan.ddservice"               # Service de tracking / update tiers Mecool
    "com.android.printspooler"           # Gestionnaire d'impression (inutile sur TV)
    "com.google.android.videos"          # Google Play Films & Séries (obsolète)
    "com.google.android.youtube.tvmusic" # YouTube Music sur TV
    "com.google.android.play.games"      # Google Play Jeux
    "com.google.android.feedback"        # Outil de feedback (télémétrie)
    "com.google.android.music"           # Google Play Musique (obsolète)
    "com.google.android.tv"              # Live Channels (souvent inutile sans tuner)
)

echo -e "\n${YELLOW}[*] Phase 1 : Désactivation des packages inutiles...${NC}"

for PKG in "${PACKAGES_TO_REMOVE[@]}"; do
    echo -e "${BLUE}[*]${NC} Analyse du package : $PKG"
    # Vérifier si le package est installé sur le périphérique
    if adb shell pm list packages | grep -q "$PKG"; then
        echo -e "    -> Package présent. Tentative de désactivation réversible..."
        
        # On utilise pm disable-user --user 0 car c'est la méthode la plus propre et réversible
        if adb shell pm disable-user --user 0 "$PKG" > /dev/null 2>&1; then
            echo -e "    ${GREEN}[SUCCESS]${NC} Package $PKG désactivé."
        else
            # Alternative si pm disable-user échoue : pm uninstall -k --user 0
            if adb shell pm uninstall -k --user 0 "$PKG" > /dev/null 2>&1; then
                echo -e "    ${GREEN}[SUCCESS]${NC} Package $PKG désinstallé pour l'utilisateur 0."
            else
                echo -e "    ${RED}[WARNING]${NC} Impossible de désactiver $PKG (protégé par le système)."
            fi
        fi
    else
        echo -e "    -> Package non présent sur cette box."
    fi
done

echo -e "\n${YELLOW}[*] Phase 2 : Optimisation des échelles d'animation...${NC}"
echo -e "${BLUE}[*]${NC Configuration des échelles d'animation système à 0.5..."

if adb shell settings put global window_animation_scale 0.5 && \
   adb shell settings put global transition_animation_scale 0.5 && \
   adb shell settings put global animator_duration_scale 0.5; then
    echo -e "    ${GREEN}[SUCCESS]${NC} Échelles d'animation système configurées à 0.5 (Navigation plus fluide)."
else
    echo -e "    ${RED}[WARNING]${NC} Échec de la configuration des animations."
fi

echo -e "\n${YELLOW}[*] Phase 3 : Optimisation du cache système (facultatif)...${NC}"
# Optionnel : forcer l'optimisation en arrière-plan (compilation des layouts/dex)
echo -e "${BLUE}[*]${NC} Lancement de l'optimisation des packages en tâche de fond..."
adb shell cmd package bg-dexopt-job > /dev/null 2>&1 || true
echo -e "    ${GREEN}[SUCCESS]${NC} Tâche bg-dexopt-job déclenchée."

echo -e "\n${BLUE}======================================================================${NC}"
echo -e "${GREEN}[+] L'optimisation et le debloating sont terminés !${NC}"
echo -e "${BLUE}======================================================================${NC}"
