#!/usr/bin/env bash
# =============================================================================
# voice-tesla.sh — Pipeline Vocal Local pour Antigravity CLI (MIDGARD)
# Version  : 1.0.0
# Chantier : VOICE-TESLA / Mission N4
# Chaîne   : PTT → enregistrement → transcription → confirmation → injection zellij
# Sécurité : Gate de confirmation OBLIGATOIRE + trap EXIT + zéro cloud
# =============================================================================

set -euo pipefail

# Injection dynamique du chemin de whisper-cli
export PATH="$PATH:/home/lord-mahonheim/bifrost/tesla/tools/whisper.cpp/build/bin:/home/lord-mahonheim/.local/bin"

# ---------------------------------------------------------------------------
# CONSTANTES & CONFIGURATION
# ---------------------------------------------------------------------------
readonly SCRIPT_NAME="voice-tesla"
readonly SCRIPT_VERSION="1.0.0"
readonly LOG_DIR="${HOME}/.local/share/voice-tesla"
readonly LOG_FILE="${LOG_DIR}/voice_log.jsonl"
readonly WHISPER_BIN="${WHISPER_BIN:-whisper-cli}"
readonly DEFAULT_MODEL_BASE="${HOME}/bifrost/tesla/tools/whisper.cpp/models"
readonly LATENCY_ALERT_SEC=7
readonly MIN_AUDIO_BYTES=1024       # Seuil silence : < 1 Ko = silence
RECORD_DURATION="${RECORD_DURATION:-15}"  # secondes par défaut

# Paramètres Whisper anti-hallucination
readonly WHISPER_LANG="auto"
readonly WHISPER_ENTROPY_THOLD="2.6"

# Couleurs terminal
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly CYAN='\033[0;36m'
readonly BOLD='\033[1m'
readonly RESET='\033[0m'

# ---------------------------------------------------------------------------
# VARIABLES GLOBALES (modifiables par flags)
# ---------------------------------------------------------------------------
DRY_RUN=false
SELECTED_MODEL=""
FORCE_SESSION=""
AUDIO_TMP=""

# ---------------------------------------------------------------------------
# TRAP : NETTOYAGE GARANTI (condition Premortem #2)
# ---------------------------------------------------------------------------
cleanup() {
    if [[ -n "${AUDIO_TMP}" && -f "${AUDIO_TMP}" ]]; then
        rm -f "${AUDIO_TMP}"
    fi
}
trap cleanup EXIT INT TERM

# ---------------------------------------------------------------------------
# FONCTIONS UTILITAIRES
# ---------------------------------------------------------------------------

log_info()    { echo -e "${CYAN}[INFO]${RESET}  $*" >&2; }
log_ok()      { echo -e "${GREEN}[OK]${RESET}    $*" >&2; }
log_warn()    { echo -e "${YELLOW}[WARN]${RESET}  $*" >&2; }
log_error()   { echo -e "${RED}[ERROR]${RESET} $*" >&2; }
log_header()  { echo -e "\n${BOLD}${CYAN}══ $* ══${RESET}" >&2; }

die() {
    log_error "$*"
    exit 1
}

usage() {
    cat <<EOF
${BOLD}voice-tesla v${SCRIPT_VERSION}${RESET} — Pipeline Vocal Local pour Antigravity CLI

Usage: $(basename "$0") [OPTIONS]

Options:
  -d, --duration  SEC    Durée d'enregistrement en secondes (défaut: ${RECORD_DURATION})
  -m, --model     NAME   Modèle whisper : tiny | base | small (défaut: auto-détection)
  -s, --session   NAME   Forcer le nom de session zellij cible
  --dry-run              Transcription sans injection dans zellij
  -v, --version          Afficher la version
  -h, --help             Afficher cette aide

Exemples:
  $(basename "$0")                    # Lancement standard 5s d'écoute
  $(basename "$0") -d 10              # Écoute de 10 secondes
  $(basename "$0") --dry-run          # Test sans injection
  $(basename "$0") -m small -d 8      # Modèle small, 8 secondes
EOF
}

# ---------------------------------------------------------------------------
# PARSING DES ARGUMENTS
# ---------------------------------------------------------------------------
parse_args() {
    local duration_override=""
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -d|--duration)
                duration_override="$2"
                shift 2
                ;;
            -m|--model)
                SELECTED_MODEL="$2"
                shift 2
                ;;
            -s|--session)
                FORCE_SESSION="$2"
                shift 2
                ;;
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            -v|--version)
                echo "voice-tesla v${SCRIPT_VERSION}"
                exit 0
                ;;
            -h|--help)
                usage
                exit 0
                ;;
            *)
                die "Option inconnue : $1. Utilisez --help."
                ;;
        esac
    done
    [[ -n "$duration_override" ]] && RECORD_DURATION="$duration_override" || true
}

# ---------------------------------------------------------------------------
# DÉTECTION AUDIO : PipeWire (pw-record) > ALSA (arecord)
# ---------------------------------------------------------------------------
detect_audio_backend() {
    if command -v pw-record &>/dev/null; then
        # Vérifier que PipeWire est bien actif
        if systemctl --user is-active --quiet pipewire 2>/dev/null || \
           pactl info 2>/dev/null | grep -qi "pipewire"; then
            echo "pipewire"
            return 0
        fi
    fi
    if command -v arecord &>/dev/null; then
        echo "alsa"
        return 0
    fi
    if command -v sox &>/dev/null && sox --help 2>&1 | grep -q "rec"; then
        echo "sox"
        return 0
    fi
    echo "none"
}

# ---------------------------------------------------------------------------
# ENREGISTREMENT AUDIO
# ---------------------------------------------------------------------------
record_audio() {
    local outfile="$1"
    local backend
    backend="$(detect_audio_backend)"

    log_header "ENREGISTREMENT"
    echo -e "${BOLD}${GREEN}🎙  Parlez maintenant... (Mode Open-free)${RESET}"
    echo -e "${YELLOW}    Appuyez sur [Entrée] pour terminer l'enregistrement${RESET}\n"

    local rec_pid

    case "$backend" in
        pipewire)
            log_info "Backend : PipeWire (pw-record)"
            pw-record \
                --rate=16000 \
                --channels=1 \
                --format=s16 \
                --target=auto \
                "${outfile%.wav}.raw" 2>/dev/null &
            rec_pid=$!
            ;;
        alsa)
            log_info "Backend : ALSA (arecord)"
            arecord \
                --quiet \
                --format=S16_LE \
                --rate=16000 \
                --channels=1 \
                "$outfile" 2>/dev/null &
            rec_pid=$!
            ;;
        sox)
            log_info "Backend : SoX (rec)"
            rec \
                --quiet \
                "$outfile" \
                rate 16000 channels 1 2>/dev/null &
            rec_pid=$!
            ;;
        none)
            die "Aucun backend audio trouvé. Installez pw-record, arecord ou sox."
            ;;
    esac

    # Attente que l'utilisateur appuie sur Entrée
    read -r
    kill "$rec_pid" 2>/dev/null || true
    wait "$rec_pid" 2>/dev/null || true

    # Convertir RAW → WAV 16kHz mono si pipewire
    if [[ "$backend" == "pipewire" ]]; then
        if command -v sox &>/dev/null; then
            sox -r 16000 -e signed -b 16 -c 1 "${outfile%.wav}.raw" "$outfile" 2>/dev/null
            rm -f "${outfile%.wav}.raw"
        else
            _raw_to_wav "${outfile%.wav}.raw" "$outfile" 16000
            rm -f "${outfile%.wav}.raw"
        fi
    fi

    echo -e "\n${BOLD}⏹  Enregistrement terminé.${RESET}"
}

# Conversion RAW PCM → WAV (fallback si sox absent)
_raw_to_wav() {
    local raw="$1"
    local wav="$2"
    local rate="$3"
    local size
    size=$(stat -c%s "$raw" 2>/dev/null || echo 0)
    local header_size=44
    local total_size=$(( size + header_size - 8 ))
    local data_size=$size
    local byte_rate=$(( rate * 2 ))
    # Écriture header WAV en Python-free (via printf + od trick avec dd)
    # On utilise une subshell avec printf pour écrire les bytes
    {
        printf "RIFF"
        printf "%b" "$(printf '\\x%02x\\x%02x\\x%02x\\x%02x' \
            $((total_size & 0xFF)) $(((total_size>>8) & 0xFF)) \
            $(((total_size>>16) & 0xFF)) $(((total_size>>24) & 0xFF)))"
        printf "WAVEfmt "
        printf "%b" "$(printf '\\x10\\x00\\x00\\x00')" # Chunk size 16
        printf "%b" "$(printf '\\x01\\x00')"            # PCM format
        printf "%b" "$(printf '\\x01\\x00')"            # 1 channel
        printf "%b" "$(printf '\\x%02x\\x%02x\\x%02x\\x%02x' \
            $((rate & 0xFF)) $(((rate>>8) & 0xFF)) \
            $(((rate>>16) & 0xFF)) $(((rate>>24) & 0xFF)))"
        printf "%b" "$(printf '\\x%02x\\x%02x\\x%02x\\x%02x' \
            $((byte_rate & 0xFF)) $(((byte_rate>>8) & 0xFF)) \
            $(((byte_rate>>16) & 0xFF)) $(((byte_rate>>24) & 0xFF)))"
        printf "%b" "$(printf '\\x02\\x00')"            # Block align
        printf "%b" "$(printf '\\x10\\x00')"            # Bits per sample
        printf "data"
        printf "%b" "$(printf '\\x%02x\\x%02x\\x%02x\\x%02x' \
            $((data_size & 0xFF)) $(((data_size>>8) & 0xFF)) \
            $(((data_size>>16) & 0xFF)) $(((data_size>>24) & 0xFF)))"
        [[ -f "$raw" ]] && cat "$raw" 2>/dev/null || true
    } > "$wav" || true
}

# ---------------------------------------------------------------------------
# VÉRIFICATION SILENCE
# ---------------------------------------------------------------------------
check_silence() {
    local audiofile="$1"
    local size
    size=$(stat -c%s "$audiofile" 2>/dev/null || echo 0)
    if (( size < MIN_AUDIO_BYTES )); then
        log_warn "Fichier audio trop petit (${size} octets < ${MIN_AUDIO_BYTES}). Silence détecté."
        return 1
    fi
    return 0
}

# ---------------------------------------------------------------------------
# RÉSOLUTION DU MODÈLE WHISPER
# ---------------------------------------------------------------------------
resolve_model_path() {
    local model_name="${1:-base}"
    local candidates=(
        "${DEFAULT_MODEL_BASE}/ggml-${model_name}.bin"
        "${HOME}/.local/share/whisper/ggml-${model_name}.bin"
        "${HOME}/.local/share/whisper.cpp/models/ggml-${model_name}.bin"
        "/usr/share/whisper/ggml-${model_name}.bin"
        "/usr/local/share/whisper/ggml-${model_name}.bin"
        "${HOME}/whisper.cpp/models/ggml-${model_name}.bin"
        "/opt/whisper/models/ggml-${model_name}.bin"
    )
    for path in "${candidates[@]}"; do
        if [[ -f "$path" ]]; then
            echo "$path"
            return 0
        fi
    done
    # Chercher avec find dans les paths courants
    local found
    found=$(find "${HOME}" /usr/share /usr/local/share -name "ggml-${model_name}.bin" 2>/dev/null | head -1 || true)
    if [[ -n "$found" ]]; then
        echo "$found"
        return 0
    fi
    return 1
}

auto_select_model() {
    # Priorité : base (déjà installé sur MIDGARD) → small → tiny
    for model in base small tiny; do
        if resolve_model_path "$model" &>/dev/null; then
            echo "$model"
            return 0
        fi
    done
    return 1
}

# ---------------------------------------------------------------------------
# TRANSCRIPTION WHISPER (avec benchmark latence)
# ---------------------------------------------------------------------------
transcribe_audio() {
    local audiofile="$1"
    local model_name="$2"
    local model_path
    model_path=$(resolve_model_path "$model_name") || \
        die "Modèle whisper '${model_name}' introuvable. Exécutez voice-health-check.sh."

    log_header "TRANSCRIPTION"
    log_info "Modèle : ${model_name} (${model_path})"
    log_info "Démarrage whisper-cli..."

    local ts_start ts_end latency_sec
    ts_start=$(date +%s%3N)  # millisecondes

    # Appel whisper-cli avec paramètres anti-hallucination
    local raw_output
    raw_output=$("${WHISPER_BIN}" \
        --model "$model_path" \
        --language "$WHISPER_LANG" \
        --entropy-thold "$WHISPER_ENTROPY_THOLD" \
        --no-timestamps \
        --output-txt \
        --file "$audiofile" \
        2>/dev/null) || true

    ts_end=$(date +%s%3N)
    local latency_ms=$(( ts_end - ts_start ))
    latency_sec=$(echo "scale=2; ${latency_ms}/1000" | bc 2>/dev/null || echo "${latency_ms}")

    # Benchmark alerte (condition Premortem #3)
    local latency_int=$(( latency_ms / 1000 ))
    if (( latency_int >= LATENCY_ALERT_SEC )); then
        log_warn "⚠️  Latence de transcription : ${latency_sec}s (seuil : ${LATENCY_ALERT_SEC}s)"
        log_warn "Considérez --model tiny pour réduire la latence."
    else
        log_ok "Latence transcription : ${latency_sec}s"
    fi

    # Extraire le texte transcrit (supprimer marqueurs temporels résiduels)
    local text
    text=$(echo "$raw_output" \
        | grep -v '^\[' \
        | sed 's/^[[:space:]]*//' \
        | sed '/^$/d' \
        | tr '\n' ' ' \
        | sed 's/[[:space:]]*$//')

    # Fallback : chercher fichier .txt généré par --output-txt
    if [[ -z "$text" ]]; then
        local txt_file="${audiofile%.wav}.txt"
        if [[ -f "$txt_file" ]]; then
            text=$(cat "$txt_file" | grep -v '^\[' | tr '\n' ' ' | sed 's/[[:space:]]*$//')
            rm -f "$txt_file"
        fi
    fi

    echo "${latency_ms}|${text}"
}

# ---------------------------------------------------------------------------
# DÉTECTION SESSION ZELLIJ AGY
# ---------------------------------------------------------------------------
detect_zellij_session() {
    if [[ -n "${FORCE_SESSION}" ]]; then
        # Vérifier que la session forcée existe
        if zellij list-sessions 2>/dev/null | grep -q "^${FORCE_SESSION}\b"; then
            echo "${FORCE_SESSION}"
            return 0
        else
            log_warn "Session zellij forcée '${FORCE_SESSION}' introuvable."
            return 1
        fi
    fi

    # Chercher une session contenant "agy" dans son nom
    local sessions
    sessions=$(zellij list-sessions -n 2>/dev/null | sed 's/ (.*//' || true)

    for session in $sessions; do
        if echo "$session" | grep -qi "agy"; then
            echo "$session"
            return 0
        fi
    done

    # Fallback : proposer la première session disponible
    local first_session
    first_session=$(zellij list-sessions -n 2>/dev/null | head -1 | sed 's/ (.*//' || true)
    if [[ -n "$first_session" ]]; then
        log_warn "Aucune session 'agy' trouvée. Utilisation de '${first_session}'."
        echo "$first_session"
        return 0
    fi

    return 1
}

# ---------------------------------------------------------------------------
# GATE DE CONFIRMATION (condition Premortem #1 — RPN 378)
# ---------------------------------------------------------------------------
confirmation_gate() {
    local text="$1"
    local action=""

    log_header "GATE DE CONFIRMATION"
    echo -e "${BOLD}Texte transcrit :${RESET}" >&2
    echo -e "\n  ${CYAN}「${text}」${RESET}\n" >&2

    while true; do
        echo -e "${BOLD}Action :${RESET}" >&2
        echo -e "  ${GREEN}[O]${RESET} OK — Injecter dans agy" >&2
        echo -e "  ${YELLOW}[R]${RESET} Rééditier — Modifier manuellement" >&2
        echo -e "  ${RED}[A]${RESET} Annuler — Abandonner" >&2
        echo -n -e "\n  Votre choix [O/R/A] : " >&2

        read -r -t 30 choice || { echo >&2; log_warn "Timeout (30s). Annulation."; action="A"; break; }
        choice="${choice^^}"  # Majuscule

        case "$choice" in
            O|OK|OUI|Y|YES)
                action="OK"
                break
                ;;
            R|REEDIT|EDIT)
                echo -n -e "\n  Nouveau texte : "
                read -r edited_text
                if [[ -n "$edited_text" ]]; then
                    text="$edited_text"
                    echo -e "\n${CYAN}Texte modifié : 「${text}」${RESET}"
                    # Re-confirmer après édition
                    continue
                else
                    log_warn "Texte vide. Annulation."
                    action="A"
                fi
                break
                ;;
            A|ANNULER|CANCEL|N|NO|NON)
                action="A"
                break
                ;;
            *)
                echo -e "  ${RED}Choix invalide. Entrez O, R ou A.${RESET}"
                ;;
        esac
    done

    echo "${action}|${text}"
}

# ---------------------------------------------------------------------------
# INJECTION ZELLIJ
# ---------------------------------------------------------------------------
inject_zellij() {
    local session="$1"
    local text="$2"

    log_header "INJECTION ZELLIJ"
    log_info "Session cible : ${session}"
    log_info "Commande : ${text}"

    if $DRY_RUN; then
        log_warn "[DRY-RUN] Injection simulée — aucune commande envoyée à zellij."
        return 0
    fi

    # Injection sécurisée
    zellij action --session "${session}" write-chars "${text}"
    sleep 0.1
    zellij action --session "${session}" write 13

    log_ok "✅ Commande injectée dans zellij:${session}"
}

# ---------------------------------------------------------------------------
# LOGGING JSON (condition #10)
# ---------------------------------------------------------------------------
append_log() {
    local timestamp="$1"
    local text="$2"
    local latency_ms="$3"
    local action="$4"
    local model="$5"

    mkdir -p "${LOG_DIR}"
    local entry
    # Échapper les guillemets dans le texte
    local safe_text="${text//\"/\\\"}"
    entry=$(printf '{"ts":"%s","text":"%s","latency_ms":%s,"action":"%s","model":"%s","dry_run":%s}\n' \
        "$timestamp" "$safe_text" "$latency_ms" "$action" "$model" \
        "$(${DRY_RUN} && echo true || echo false)")
    echo "$entry" >> "${LOG_FILE}"
}

# ---------------------------------------------------------------------------
# FONCTION PRINCIPALE
# ---------------------------------------------------------------------------
main() {
    parse_args "$@"

    log_header "voice-tesla v${SCRIPT_VERSION}"
    [[ "$DRY_RUN" == true ]] && log_warn "MODE DRY-RUN ACTIF — aucune injection réelle"

    # --- Pré-vérification des outils ---
    command -v whisper-cli &>/dev/null || \
        die "whisper-cli introuvable. Exécutez voice-tesla-install.sh."
    command -v zellij &>/dev/null || \
        die "zellij introuvable. Veuillez l'installer."
    command -v bc &>/dev/null || log_warn "bc absent — affichage latence en ms uniquement"

    # --- Sélection du modèle ---
    if [[ -z "$SELECTED_MODEL" ]]; then
        SELECTED_MODEL=$(auto_select_model) || \
            die "Aucun modèle whisper trouvé. Téléchargez ggml-base.bin."
        log_info "Modèle auto-sélectionné : ${SELECTED_MODEL}"
    fi

    # --- Détection session zellij ---
    local zellij_session=""
    if ! $DRY_RUN; then
        zellij_session=$(detect_zellij_session) || {
            log_warn "Aucune session zellij trouvée."
            log_warn "Démarrez une session avec : zellij -s agy"
            if ! $DRY_RUN; then
                die "Session zellij requise pour l'injection."
            fi
        }
    fi

    # --- Fichier audio temporaire ---
    AUDIO_TMP=$(mktemp --suffix=".wav" /tmp/voice-tesla-XXXXXX)

    # --- Enregistrement ---
    record_audio "${AUDIO_TMP}" "${RECORD_DURATION}"

    # --- Vérification silence ---
    check_silence "${AUDIO_TMP}" || {
        log_info "[silence détecté] — Aucune transcription effectuée."
        append_log "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "[silence]" "0" "SILENCE" "${SELECTED_MODEL}"
        exit 0
    }

    # --- Transcription ---
    local transcription_result
    transcription_result=$(transcribe_audio "${AUDIO_TMP}" "${SELECTED_MODEL}")
    local latency_ms text
    latency_ms="${transcription_result%%|*}"
    text="${transcription_result#*|}"

    if [[ -z "$text" ]]; then
        log_warn "Transcription vide (possible silence ou audio trop court)."
        append_log "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "[vide]" "${latency_ms}" "EMPTY" "${SELECTED_MODEL}"
        exit 0
    fi

    # --- Gate de confirmation ---
    local gate_result action final_text
    gate_result=$(confirmation_gate "$text")
    action="${gate_result%%|*}"
    final_text="${gate_result#*|}"

    local log_action
    case "$action" in
        OK)
            inject_zellij "${zellij_session}" "${final_text}"
            log_action="INJECTED"
            ;;
        A)
            log_info "Annulé par l'utilisateur."
            log_action="CANCELLED"
            ;;
        *)
            log_warn "Action inattendue : ${action}"
            log_action="UNKNOWN"
            ;;
    esac

    # --- Logging ---
    append_log "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "${final_text}" "${latency_ms}" \
        "${log_action}" "${SELECTED_MODEL}"

    log_header "FIN"
    log_info "Log : ${LOG_FILE}"

    echo -n -e "\n${BOLD}Appuyez sur Entrée pour fermer la fenêtre...${RESET} " >&2
    read -r
}

# ---------------------------------------------------------------------------
# POINT D'ENTRÉE
# ---------------------------------------------------------------------------
main "$@"
