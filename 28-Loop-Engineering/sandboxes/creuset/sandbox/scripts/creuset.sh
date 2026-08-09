#!/usr/bin/env bash
# creuset.sh — Orchestrateur du Creuset des Subagents de Tesla
set -euo pipefail
IFS=$'\n\t'

REAL_WORKSPACE="/home/lord-mahonheim/bifrost/tesla"
CREUSET_DIR="$REAL_WORKSPACE/sandboxes/creuset"
EXCLUDE_FILE="$REAL_WORKSPACE/sandbox/config/rsync-exclude.txt"
LOG_FILE="$REAL_WORKSPACE/sandbox/logs/creuset_audit.log"
SCANNER_SCRIPT="$REAL_WORKSPACE/sandbox/scripts/scan-secrets.sh"

mkdir -p "$(dirname "$LOG_FILE")"
mkdir -p "$CREUSET_DIR"

log() {
  local msg="[$(date +'%Y-%m-%d %H:%M:%S')] [Creuset] $1"
  echo "$msg"
  echo "$msg" >> "$LOG_FILE"
}

# 1. INITIALISATION DU CREUSET
cmd_init() {
  log "Initialisation du Creuset à l'état pur..."
  
  if [ ! -f "$EXCLUDE_FILE" ]; then
    echo "[-] Fichier d'exclusions manquant: $EXCLUDE_FILE" >&2
    exit 1
  fi

  # Synchronisation propre depuis le workspace hôte
  # On exclut le Vault Avalon, les secrets (.env) et les dépendances lourdes (.venv)
  rsync -a --delete --delete-excluded --exclude-from="$EXCLUDE_FILE" "$REAL_WORKSPACE/" "$CREUSET_DIR/"
  
  # Création d'une constitution locale pour les sous-agents au sein du Creuset
  mkdir -p "$CREUSET_DIR/.agents"
  cat << 'EOF' > "$CREUSET_DIR/.agents/AGENTS.md"
# Constitution du Creuset (Subagents)
- Tu es un sous-agent spécialisé, instancié par l'orchestrateur Tesla.
- Ton espace de travail est STRICTEMENT limité à /sandboxes/creuset.
- Tu n'as aucun accès réseau direct (isolation bwrap).
- Tu produis des résultats testables, propres et documentés.
- Tout commit ou modification doit être validé par Tesla.
EOF

  log "Creuset initialisé et prêt à l'adresse: $CREUSET_DIR"
}

# 2. EXÉCUTION ISOLÉE (High-Tech & Haute performance)
# On monte le .venv de l'hôte en LECTURE SEULE pour que le subagent ait accès instantanément
# à toutes les dépendances (Playwright, pytest, etc.) sans pouvoir altérer le venv de l'hôte.
cmd_run() {
  if [ $# -eq 0 ]; then
    log "Ouverture d'un shell interactif dans le Creuset..."
    local run_cmd=("/bin/bash")
  else
    log "Exécution dans le Creuset: $*"
    local run_cmd=("$@")
  fi

  # Montage sécurisé avec bubblewrap (bwrap)
  bwrap \
    --ro-bind / / \
    --dev-bind /dev /dev \
    --proc /proc \
    --tmpfs /tmp \
    --bind "$CREUSET_DIR" "$CREUSET_DIR" \
    --ro-bind-try "$REAL_WORKSPACE/.venv" "$CREUSET_DIR/.venv" \
    --ro-bind-try "$HOME/.cache" "$HOME/.cache" \
    --unshare-net \
    --chdir "$CREUSET_DIR" \
    --setenv PATH "$CREUSET_DIR/.venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin" \
    "${run_cmd[@]}"
}

# 3. SCAN DE SÉCURITÉ ET AUDIT (Pre-merge)
cmd_audit() {
  log "Démarrage de l'audit de sécurité du Creuset..."
  
  if [ ! -x "$SCANNER_SCRIPT" ]; then
    echo "[-] Script de scan de secrets non trouvé: $SCANNER_SCRIPT" >&2
    exit 1
  fi
  
  if ! "$SCANNER_SCRIPT" "$CREUSET_DIR"; then
    log "[-] ALERT: Audit Échoué ! Présence suspecte de patterns de secrets dans le Creuset !"
    exit 3
  fi
  
  log "Audit réussi. Aucun secret en clair détecté dans le Creuset."
}

# 4. NETTOYAGE COMPLET
cmd_clean() {
  log "Purification et nettoyage du Creuset..."
  rm -rf "$CREUSET_DIR"
  mkdir -p "$CREUSET_DIR"
  log "Creuset purifié."
}

usage() {
  echo "Usage: $0 {init|run [cmd]|audit|clean}" >&2
  exit 1
}

# Point d'entrée principal
case "${1:-}" in
  init) cmd_init ;;
  run) shift; cmd_run "$@" ;;
  audit) cmd_audit ;;
  clean) cmd_clean ;;
  *) usage ;;
esac
