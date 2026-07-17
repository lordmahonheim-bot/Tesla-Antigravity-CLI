#!/usr/bin/env bash
# =============================================================================
# voice-health-check.sh — Smoke Test du Pipeline Vocal VOICE-TESLA
# Version  : 1.0.0
# Chantier : VOICE-TESLA / Mission N4
# Objectif : Vérifier en < 10s que l'environnement est opérationnel
# =============================================================================

set -euo pipefail

# Injection dynamique du chemin de whisper-cli
export PATH="$PATH:/home/lord-mahonheim/bifrost/tesla/tools/whisper.cpp/build/bin"
readonly SCRIPT_NAME="voice-health-check"
readonly SCRIPT_VERSION="1.0.0"

# Couleurs
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly CYAN='\033[0;36m'
readonly BOLD='\033[1m'
readonly RESET='\033[0m'

# Compteurs
PASS=0
WARN=0
FAIL=0

# ---------------------------------------------------------------------------
# FONCTIONS D'ASSERTION
# ---------------------------------------------------------------------------
check_pass() { echo -e "  ${GREEN}✅ PASS${RESET}  $*"; ((PASS++)) || true; }
check_warn() { echo -e "  ${YELLOW}⚠️  WARN${RESET}  $*"; ((WARN++)) || true; }
check_fail() { echo -e "  ${RED}❌ FAIL${RESET}  $*"; ((FAIL++)) || true; }
section()    { echo -e "\n${BOLD}${CYAN}── $* ──${RESET}"; }

# ---------------------------------------------------------------------------
# SECTION 1 : WHISPER-CLI
# ---------------------------------------------------------------------------
check_whisper_cli() {
    section "1. whisper-cli"

    if command -v whisper-cli &>/dev/null; then
        local version
        version=$(whisper-cli --version 2>&1 | grep -i "version" | head -1 || echo "version inconnue") || true
        check_pass "whisper-cli accessible : ${version}"
    else
        check_fail "whisper-cli introuvable dans PATH"
        echo "    → Compilez whisper.cpp ou vérifiez votre PATH"
        return 1
    fi
}

# ---------------------------------------------------------------------------
# SECTION 2 : MODÈLES WHISPER
# ---------------------------------------------------------------------------
check_whisper_models() {
    section "2. Modèles Whisper"

    local found_any=false
    local model_paths=(
        "${HOME}/bifrost/tesla/tools/whisper.cpp/models"
        "${HOME}/.local/share/whisper"
        "${HOME}/.local/share/whisper.cpp/models"
        "${HOME}/whisper.cpp/models"
        "/usr/share/whisper"
        "/usr/local/share/whisper"
        "/opt/whisper/models"
    )

    for base_path in "${model_paths[@]}"; do
        if [[ -d "$base_path" ]]; then
            while IFS= read -r -d '' model_file; do
                local model_name
                model_name=$(basename "$model_file")
                local size
                size=$(du -sh "$model_file" 2>/dev/null | cut -f1)
                check_pass "Modèle trouvé : ${model_name} (${size}) @ ${model_file}"
                found_any=true
            done < <(find "$base_path" -name "ggml-*.bin" -print0 2>/dev/null)
        fi
    done

    if [[ "$found_any" == false ]]; then
        check_fail "Aucun modèle ggml-*.bin trouvé"
        echo "    → Téléchargez depuis : https://huggingface.co/ggerganov/whisper.cpp"
        echo "    → Chemin recommandé : ${HOME}/.local/share/whisper/ggml-base.bin"
    fi
}

# ---------------------------------------------------------------------------
# SECTION 3 : BACKEND AUDIO
# ---------------------------------------------------------------------------
check_audio_backend() {
    section "3. Backend Audio"

    local pipewire_ok=false
    local alsa_ok=false
    local sox_ok=false

    # PipeWire
    if command -v pw-record &>/dev/null; then
        if systemctl --user is-active --quiet pipewire 2>/dev/null || \
           pactl info 2>/dev/null | grep -qi "pipewire" 2>/dev/null; then
            check_pass "PipeWire actif et pw-record disponible (recommandé)"
            pipewire_ok=true
        else
            check_warn "pw-record disponible mais PipeWire non détecté comme actif"
        fi
    else
        check_warn "pw-record absent (PipeWire non installé)"
    fi

    # ALSA
    if command -v arecord &>/dev/null; then
        local devices
        devices=$(arecord -l 2>/dev/null | grep -c "card" || true)
        if (( devices > 0 )); then
            check_pass "ALSA disponible : ${devices} carte(s) audio détectée(s)"
            alsa_ok=true
        else
            check_warn "arecord disponible mais aucune carte audio ALSA détectée"
        fi
    else
        check_warn "arecord absent (alsa-utils non installé)"
    fi

    # SoX
    if command -v rec &>/dev/null; then
        check_pass "SoX (rec) disponible en fallback"
        sox_ok=true
    else
        check_warn "SoX (rec) absent"
    fi

    if [[ "$pipewire_ok" == false && "$alsa_ok" == false && "$sox_ok" == false ]]; then
        check_fail "Aucun backend audio fonctionnel ! Installez pw-record OU arecord OU sox"
    fi

    # Lister les périphériques d'entrée
    echo ""
    echo -e "  ${BOLD}Périphériques d'entrée détectés :${RESET}"
    if command -v pactl &>/dev/null; then
        pactl list sources short 2>/dev/null | grep -i "input\|mic" | \
            while read -r line; do echo "    - $line"; done || \
            echo "    (aucun périphérique pactl listé)"
    elif command -v arecord &>/dev/null; then
        arecord -l 2>/dev/null | grep "card" | \
            while read -r line; do echo "    - $line"; done || \
            echo "    (aucune carte ALSA)"
    else
        echo "    (impossible de lister — pactl/arecord absent)"
    fi
}

# ---------------------------------------------------------------------------
# SECTION 4 : TMUX & SESSION AGY
# ---------------------------------------------------------------------------
check_tmux_session() {
    section "4. tmux & Session AGY"

    if ! command -v tmux &>/dev/null; then
        check_fail "tmux introuvable"
        echo "    → Installez avec : sudo apt install tmux"
        return 1
    fi

    local tmux_version
    tmux_version=$(tmux -V 2>/dev/null || echo "version inconnue")
    check_pass "tmux installé : ${tmux_version}"

    # Lister toutes les sessions
    local sessions
    sessions=$(tmux ls 2>/dev/null | awk -F: '{print $1}') || true

    if [[ -z "$sessions" ]]; then
        check_warn "Aucune session tmux active"
        echo "    → Pour démarrer une session agy : tmux new-session -s agy 'agy'"
        return 0
    fi

    local agy_found=false
    for session in $sessions; do
        local procs
        procs=$(tmux list-panes -t "$session" -F "#{pane_current_command}" 2>/dev/null | tr '\n' ' ')
        if echo "${session} ${procs}" | grep -qi "agy\|antigravity"; then
            check_pass "Session AGY trouvée : '${session}' (processus: ${procs})"
            agy_found=true
        else
            echo -e "  ${CYAN}ℹ  INFO${RESET}  Session tmux disponible : '${session}' (${procs})"
        fi
    done

    if [[ "$agy_found" == false ]]; then
        check_warn "Aucune session tmux ne contient 'agy'. Utilisez --session NOM pour forcer."
    fi
}

# ---------------------------------------------------------------------------
# SECTION 5 : BENCHMARK DE TRANSCRIPTION
# ---------------------------------------------------------------------------
check_latency_benchmark() {
    section "5. Benchmark Latence Transcription"

    # Trouver le premier modèle disponible
    local model_path=""
    local model_name=""
    for m in base small tiny; do
        for base_dir in \
            "${HOME}/bifrost/tesla/tools/whisper.cpp/models" \
            "${HOME}/.local/share/whisper" \
            "${HOME}/.local/share/whisper.cpp/models" \
            "${HOME}/whisper.cpp/models" \
            "/usr/share/whisper" \
            "/usr/local/share/whisper"; do
            local candidate="${base_dir}/ggml-${m}.bin"
            if [[ -f "$candidate" ]]; then
                model_path="$candidate"
                model_name="$m"
                break 2
            fi
        done
    done

    if [[ -z "$model_path" ]]; then
        check_warn "Aucun modèle trouvé — benchmark de latence ignoré"
        return 0
    fi

    # Créer un fichier WAV de test minimal (0.5s de silence à 16kHz)
    local test_wav
    test_wav=$(mktemp --suffix=".wav" /tmp/vt-healthcheck-XXXXXX)

    # Générer 0.5s de silence WAV 16kHz mono
    if command -v sox &>/dev/null; then
        sox -n -r 16000 -c 1 "$test_wav" trim 0 0.5 2>/dev/null || \
            sox -n -r 16000 -c 1 -b 16 "$test_wav" trim 0.0 0.5 2>/dev/null || true
    elif command -v arecord &>/dev/null; then
        # Générer via /dev/zero
        arecord --quiet --format=S16_LE --rate=16000 --channels=1 \
            --duration=1 "$test_wav" < /dev/zero 2>/dev/null || true
    fi

    if [[ ! -f "$test_wav" || ! -s "$test_wav" ]]; then
        check_warn "Impossible de générer un fichier WAV de test"
        rm -f "$test_wav"
        return 0
    fi

    # Mesurer la latence
    local ts_start ts_end latency_ms
    ts_start=$(date +%s%3N)
    whisper-cli \
        --model "$model_path" \
        --language fr \
        --no-timestamps \
        --file "$test_wav" \
        &>/dev/null || true
    ts_end=$(date +%s%3N)
    latency_ms=$(( ts_end - ts_start ))
    local latency_sec
    latency_sec=$(echo "scale=2; ${latency_ms}/1000" | bc 2>/dev/null || echo "${latency_ms}ms")

    rm -f "$test_wav"

    if (( latency_ms < 7000 )); then
        check_pass "Latence benchmark (modèle ${model_name}, fichier silence) : ${latency_sec}s ✅"
    elif (( latency_ms < 12000 )); then
        check_warn "Latence élevée : ${latency_sec}s — Considérez --model tiny"
    else
        check_fail "Latence trop élevée : ${latency_sec}s — Pipeline probablement inutilisable"
        echo "    → Passez au modèle tiny : voice-tesla.sh --model tiny"
    fi

    # RAM consommée par le processus
    local mem_mb
    mem_mb=$(ps aux 2>/dev/null | awk '/whisper/ && !/awk/ {sum+=$6} END {printf "%.0f", sum/1024}') || true
    [[ -n "$mem_mb" ]] && echo -e "  ${CYAN}ℹ  INFO${RESET}  RAM estimée whisper-cli : ${mem_mb} Mo"
}

# ---------------------------------------------------------------------------
# SECTION 6 : RÉPERTOIRE DE LOG
# ---------------------------------------------------------------------------
check_log_dir() {
    section "6. Répertoire de Log"

    local log_dir="${HOME}/.local/share/voice-tesla"
    local log_file="${log_dir}/voice_log.jsonl"

    if [[ -d "$log_dir" ]]; then
        check_pass "Répertoire log existant : ${log_dir}"
        if [[ -f "$log_file" ]]; then
            local lines
            lines=$(wc -l < "$log_file" 2>/dev/null || echo "0")
            check_pass "Journal JSONL : ${lines} entrées"
        else
            check_warn "Journal JSONL absent (sera créé au premier run)"
        fi
    else
        check_warn "Répertoire ${log_dir} absent — il sera créé au premier run"
    fi
}

# ---------------------------------------------------------------------------
# RAPPORT FINAL
# ---------------------------------------------------------------------------
print_report() {
    local total=$(( PASS + WARN + FAIL ))
    echo ""
    echo -e "${BOLD}═════════════════════════════════════════${RESET}"
    echo -e "${BOLD}  RAPPORT SANTÉ VOICE-TESLA v${SCRIPT_VERSION}${RESET}"
    echo -e "${BOLD}═════════════════════════════════════════${RESET}"
    echo -e "  Horodatage : $(date '+%Y-%m-%d %H:%M:%S')"
    echo -e "  Hôte       : $(hostname)"
    echo ""
    echo -e "  ${GREEN}✅ PASS${RESET} : ${PASS}/${total}"
    echo -e "  ${YELLOW}⚠️  WARN${RESET} : ${WARN}/${total}"
    echo -e "  ${RED}❌ FAIL${RESET} : ${FAIL}/${total}"
    echo ""

    if (( FAIL == 0 && WARN == 0 )); then
        echo -e "  ${GREEN}${BOLD}🎉 Environnement OPTIMAL — voice-tesla.sh prêt !${RESET}"
    elif (( FAIL == 0 )); then
        echo -e "  ${YELLOW}${BOLD}⚠️  Environnement PARTIEL — vérifiez les warnings${RESET}"
    else
        echo -e "  ${RED}${BOLD}❌ Environnement DÉGRADÉ — corrigez les échecs avant usage${RESET}"
    fi

    echo -e "${BOLD}═════════════════════════════════════════${RESET}"
    echo ""

    # Code de retour
    (( FAIL == 0 )) && return 0 || return 1
}

# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
echo -e "\n${BOLD}${CYAN}voice-health-check v${SCRIPT_VERSION}${RESET} — Démarrage..."

check_whisper_cli
check_whisper_models
check_audio_backend
check_tmux_session
check_latency_benchmark
check_log_dir
print_report
