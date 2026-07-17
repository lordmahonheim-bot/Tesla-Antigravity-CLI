#!/usr/bin/env bash
# =============================================================================
# voice-tesla-install.sh — Installateur du Pipeline Vocal VOICE-TESLA
# Version  : 1.0.0
# Chantier : VOICE-TESLA / Mission N4
# Objectif : Vérifier les dépendances, créer la structure, guider la config
# =============================================================================

set -euo pipefail

# Injection dynamique du chemin de whisper-cli
export PATH="$PATH:/home/lord-mahonheim/bifrost/tesla/tools/whisper.cpp/build/bin"

readonly SCRIPT_VERSION="1.0.0"
readonly INSTALL_DIR="${HOME}/.local/share/voice-tesla"
readonly BIN_DIR="${HOME}/.local/bin"
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Couleurs
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly CYAN='\033[0;36m'
readonly BOLD='\033[1m'
readonly RESET='\033[0m'

DEPS_OK=true

log_info()  { echo -e "${CYAN}[INFO]${RESET}  $*"; }
log_ok()    { echo -e "${GREEN}[ OK ]${RESET}  $*"; }
log_warn()  { echo -e "${YELLOW}[WARN]${RESET}  $*"; }
log_error() { echo -e "${RED}[FAIL]${RESET}  $*" >&2; DEPS_OK=false; }
section()   { echo -e "\n${BOLD}${CYAN}── $* ──${RESET}"; }

# ---------------------------------------------------------------------------
# PHASE 1 : VÉRIFICATION DES DÉPENDANCES
# ---------------------------------------------------------------------------
check_dependencies() {
    section "PHASE 1 : Vérification des Dépendances"

    # whisper-cli
    if command -v whisper-cli &>/dev/null; then
        log_ok "whisper-cli : $(whisper-cli --version 2>&1 | head -1 || echo 'présent')"
    else
        log_error "whisper-cli MANQUANT"
        echo ""
        echo -e "  ${BOLD}Installation whisper.cpp :${RESET}"
        echo "    git clone https://github.com/ggerganov/whisper.cpp"
        echo "    cd whisper.cpp && make -j\$(nproc)"
        echo "    cp build/bin/whisper-cli ${HOME}/.local/bin/"
        echo "    mkdir -p ${HOME}/.local/share/whisper"
        echo "    # Télécharger modèle base (~142 Mo) :"
        echo "    ./models/download-ggml-model.sh base"
        echo "    cp models/ggml-base.bin ${HOME}/.local/share/whisper/"
        echo ""
    fi

    # tmux
    if command -v tmux &>/dev/null; then
        log_ok "tmux : $(tmux -V)"
    else
        log_error "tmux MANQUANT"
        echo "    → sudo apt install tmux"
    fi

    # Backend audio (au moins un requis)
    local audio_ok=false
    if command -v pw-record &>/dev/null; then
        log_ok "pw-record : disponible (PipeWire)"
        audio_ok=true
    fi
    if command -v arecord &>/dev/null; then
        log_ok "arecord : disponible (ALSA)"
        audio_ok=true
    fi
    if command -v rec &>/dev/null; then
        log_ok "sox/rec : disponible"
        audio_ok=true
    fi
    if [[ "$audio_ok" == false ]]; then
        log_error "AUCUN backend audio"
        echo "    → sudo apt install pipewire-audio  (recommandé)"
        echo "    → sudo apt install alsa-utils       (alternatif)"
        echo "    → sudo apt install sox              (fallback)"
    fi

    # sox (pour conversion RAW→WAV)
    if command -v sox &>/dev/null; then
        log_ok "sox : disponible (conversion audio)"
    else
        log_warn "sox absent — conversion WAV en mode dégradé (fallback interne)"
        echo "    → sudo apt install sox  (recommandé)"
    fi

    # bc (pour affichage latence)
    if command -v bc &>/dev/null; then
        log_ok "bc : disponible (calcul latence)"
    else
        log_warn "bc absent — latence affichée en millisecondes brutes"
        echo "    → sudo apt install bc"
    fi

    # pactl (pour lister périphériques)
    if command -v pactl &>/dev/null; then
        log_ok "pactl : disponible (info périphériques)"
    else
        log_warn "pactl absent — détection périphériques limitée"
    fi
}

# ---------------------------------------------------------------------------
# PHASE 2 : CRÉATION DE LA STRUCTURE
# ---------------------------------------------------------------------------
setup_directories() {
    section "PHASE 2 : Création de la Structure"

    mkdir -p "${INSTALL_DIR}"
    log_ok "Répertoire data : ${INSTALL_DIR}"

    mkdir -p "${BIN_DIR}"
    log_ok "Répertoire bin  : ${BIN_DIR}"

    # Vérifier que ~/.local/bin est dans le PATH
    if echo "$PATH" | grep -q "${BIN_DIR}"; then
        log_ok "PATH inclut ${BIN_DIR}"
    else
        log_warn "${BIN_DIR} absent du PATH"
        echo ""
        echo "  Ajoutez cette ligne à votre ~/.bashrc ou ~/.zshrc :"
        echo -e "  ${CYAN}export PATH=\"\$HOME/.local/bin:\$PATH\"${RESET}"
        echo ""
    fi

    # Créer le fichier JSONL de log vide si absent
    local log_file="${INSTALL_DIR}/voice_log.jsonl"
    if [[ ! -f "$log_file" ]]; then
        touch "$log_file"
        log_ok "Journal JSONL créé : ${log_file}"
    else
        log_ok "Journal JSONL existant : $(wc -l < "$log_file") entrées"
    fi
}

# ---------------------------------------------------------------------------
# PHASE 3 : INSTALLATION DES SCRIPTS
# ---------------------------------------------------------------------------
install_scripts() {
    section "PHASE 3 : Installation des Scripts"

    local scripts=("voice-tesla.sh" "voice-health-check.sh" "voice-tesla-install.sh")

    for script in "${scripts[@]}"; do
        local src="${SCRIPT_DIR}/${script}"
        local dst_name="${script%.sh}"  # Retirer .sh pour le binaire
        local dst="${BIN_DIR}/${dst_name}"

        if [[ -f "$src" ]]; then
            chmod +x "$src"
            # Créer un lien symbolique dans ~/.local/bin
            ln -sf "$src" "$dst"
            log_ok "Lien symlink : ${dst} → ${src}"
        else
            log_warn "${script} non trouvé dans ${SCRIPT_DIR}"
        fi
    done

    # Alias court pratique
    local alias_file="${BIN_DIR}/vt"
    local main_script="${SCRIPT_DIR}/voice-tesla.sh"
    if [[ -f "$main_script" ]]; then
        cat > "$alias_file" <<EOF
#!/usr/bin/env bash
exec "${main_script}" "\$@"
EOF
        chmod +x "$alias_file"
        log_ok "Raccourci 'vt' créé : ${alias_file}"
    fi
}

# ---------------------------------------------------------------------------
# PHASE 4 : RECHERCHE DU MODÈLE WHISPER
# ---------------------------------------------------------------------------
check_whisper_model() {
    section "PHASE 4 : Modèle Whisper"

    local model_dir="${HOME}/.local/share/whisper"
    mkdir -p "$model_dir"

    local found=false
    for model_path in "${HOME}/bifrost/tesla/tools/whisper.cpp/models" "${model_dir}"; do
        for model in base small tiny; do
            local model_file="${model_path}/ggml-${model}.bin"
            if [[ -f "$model_file" ]]; then
                local size
                size=$(du -sh "$model_file" | cut -f1)
                log_ok "Modèle ggml-${model}.bin trouvé (${size}) dans ${model_path}"
                found=true
            fi
        done
    done

    # Chercher ailleurs
    if [[ "$found" == false ]]; then
        local located
        located=$(find "${HOME}" /usr/share /usr/local -name "ggml-*.bin" 2>/dev/null | head -3 || true)
        if [[ -n "$located" ]]; then
            echo "$located" | while read -r f; do
                log_ok "Modèle trouvé : $f"
                found=true
            done
        fi
    fi

    if [[ "$found" == false ]]; then
        log_warn "Aucun modèle whisper trouvé"
        echo ""
        echo -e "  ${BOLD}Téléchargement du modèle base (recommandé, ~142 Mo) :${RESET}"
        echo ""
        echo "    # Option 1 — Script officiel whisper.cpp :"
        echo "    cd ~/whisper.cpp && bash models/download-ggml-model.sh base"
        echo "    cp ~/whisper.cpp/models/ggml-base.bin ${model_dir}/"
        echo ""
        echo "    # Option 2 — Téléchargement direct :"
        echo "    mkdir -p ${model_dir}"
        echo "    wget -O ${model_dir}/ggml-base.bin \\"
        echo "      https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin"
        echo ""
        echo "    # Option tiny (rapide, ~75 Mo) :"
        echo "    wget -O ${model_dir}/ggml-tiny.bin \\"
        echo "      https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-tiny.bin"
        echo ""
    fi
}

# ---------------------------------------------------------------------------
# PHASE 5 : CONFIGURATION DU RACCOURCI CLAVIER
# ---------------------------------------------------------------------------
configure_keybinding() {
    section "PHASE 5 : Raccourci Clavier (PTT)"

    local main_script="${SCRIPT_DIR}/voice-tesla.sh"
    local voice_cmd="bash ${main_script}"

    echo -e "  Script à lier : ${CYAN}${main_script}${RESET}"
    echo -e "  Raccourcis recommandés : ${BOLD}Caps_Lock${RESET} ou ${BOLD}Super+V${RESET}"
    echo ""

    # --- i3 / i3wm ---
    echo -e "  ${BOLD}► i3 / Sway (${HOME}/.config/i3/config ou ~/.config/sway/config) :${RESET}"
    echo '    bindsym Caps_Lock exec --no-startup-id bash '"${main_script}"
    echo '    # OU appui maintenu (PTT-style) :'
    echo '    bindsym --release Caps_Lock exec --no-startup-id bash '"${main_script}"
    echo '    bindsym $mod+v exec --no-startup-id bash '"${main_script}"
    echo ""

    # --- Sway ---
    echo -e "  ${BOLD}► Sway spécifique :${RESET}"
    echo "    Même syntaxe que i3 ci-dessus."
    echo ""

    # --- GNOME (via dconf/Settings) ---
    echo -e "  ${BOLD}► GNOME (Settings → Keyboard → Custom Shortcuts) :${RESET}"
    echo "    Nom     : Voice Tesla"
    echo "    Commande: bash ${main_script}"
    echo "    Raccourci: Super+V (ou Caps_Lock)"
    echo ""
    echo "    # Via CLI :"
    echo "    gsettings set org.gnome.settings-daemon.plugins.media-keys custom-keybindings \\"
    echo "      \"['/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/voice-tesla/']\""
    echo "    gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/voice-tesla/ name 'Voice Tesla'"
    echo "    gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/voice-tesla/ command 'bash ${main_script}'"
    echo "    gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/voice-tesla/ binding '<Super>v'"
    echo ""

    # --- KDE Plasma ---
    echo -e "  ${BOLD}► KDE Plasma (System Settings → Shortcuts → Custom Shortcuts) :${RESET}"
    echo "    Créez un raccourci 'Commande/URL' :"
    echo "    Trigger  : Super+V (ou Caps_Lock)"
    echo "    Action   : bash ${main_script}"
    echo ""

    # --- Script xbindkeys (universel X11) ---
    echo -e "  ${BOLD}► xbindkeys (universel X11, sans WM spécifique) :${RESET}"
    echo "    Ajoutez dans ~/.xbindkeysrc :"
    echo "    \"bash ${main_script}\""
    echo "    Caps_Lock"
    echo ""
    echo "    Démarrez xbindkeys : xbindkeys"
    echo "    Ajoutez 'xbindkeys' dans vos autostart."
    echo ""

    # --- Wrapper terminal ---
    echo -e "  ${BOLD}⚠️  Note Importante (Wayland) :${RESET}"
    echo "    Le script tourne dans un terminal. Si votre WM ne l'ouvre pas automatiquement,"
    echo "    wrappez la commande avec un émulateur terminal :"
    echo "    bindsym \$mod+v exec --no-startup-id kitty bash ${main_script}"
    echo "    bindsym \$mod+v exec --no-startup-id alacritty -e bash ${main_script}"
    echo "    bindsym \$mod+v exec --no-startup-id xterm -e bash ${main_script}"
    echo ""
}

# ---------------------------------------------------------------------------
# PHASE 6 : TEST FINAL
# ---------------------------------------------------------------------------
run_final_test() {
    section "PHASE 6 : Validation Finale"

    local health_script="${SCRIPT_DIR}/voice-health-check.sh"
    if [[ -f "$health_script" ]]; then
        log_info "Exécution du smoke test..."
        bash "$health_script" || true
    else
        log_warn "voice-health-check.sh absent — test ignoré"
    fi
}

# ---------------------------------------------------------------------------
# RÉSUMÉ INSTALLATION
# ---------------------------------------------------------------------------
print_summary() {
    echo ""
    echo -e "${BOLD}═════════════════════════════════════════════${RESET}"
    echo -e "${BOLD}  RÉSUMÉ INSTALLATION voice-tesla v${SCRIPT_VERSION}${RESET}"
    echo -e "${BOLD}═════════════════════════════════════════════${RESET}"

    if [[ "$DEPS_OK" == true ]]; then
        echo -e "  ${GREEN}${BOLD}✅ Installation RÉUSSIE${RESET}"
        echo ""
        echo -e "  ${BOLD}Commandes disponibles :${RESET}"
        echo -e "  ${CYAN}voice-tesla${RESET}          — Pipeline vocal (5s écoute)"
        echo -e "  ${CYAN}voice-tesla -d 10${RESET}    — Pipeline vocal (10s écoute)"
        echo -e "  ${CYAN}voice-tesla --dry-run${RESET} — Test sans injection"
        echo -e "  ${CYAN}voice-health${RESET}          — Smoke test santé"
        echo -e "  ${CYAN}vt${RESET}                   — Raccourci court"
        echo ""
        echo -e "  ${BOLD}Première utilisation :${RESET}"
        echo "    1. Lancez une session tmux : tmux new-session -s agy 'agy'"
        echo "    2. Testez : voice-tesla --dry-run"
        echo "    3. Liez Caps_Lock au script (voir instructions Phase 5 ci-dessus)"
    else
        echo -e "  ${RED}${BOLD}❌ Installation INCOMPLÈTE — Corrigez les dépendances manquantes${RESET}"
    fi

    echo -e "${BOLD}═════════════════════════════════════════════${RESET}"
    echo ""
}

# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
echo -e "\n${BOLD}${CYAN}voice-tesla-install v${SCRIPT_VERSION}${RESET}"
echo -e "Installateur du Pipeline Vocal pour Antigravity CLI"
echo -e "Machine : $(hostname) | $(date '+%Y-%m-%d %H:%M:%S')\n"

check_dependencies
setup_directories
install_scripts
check_whisper_model
configure_keybinding

# Demander si lancer le test final
echo ""
echo -n -e "${BOLD}Lancer le smoke test maintenant ? [O/n] :${RESET} "
read -r -t 10 answer || answer="O"
answer="${answer^^}"
if [[ "$answer" != "N" && "$answer" != "NON" ]]; then
    run_final_test
fi

print_summary
