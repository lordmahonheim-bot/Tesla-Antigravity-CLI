#!/usr/bin/env bash
# tesla-sandbox.sh — Sandbox orchestration script
set -euo pipefail
IFS=$'\n\t'

# Configuration
REAL_WORKSPACE="/home/lord-mahonheim/bifrost/tesla"
SANDBOX_WORKSPACE="$REAL_WORKSPACE/sandboxes/workspace-sanitized"
EXCLUDE_FILE="$REAL_WORKSPACE/sandbox/config/rsync-exclude.txt"
LOG_FILE="$REAL_WORKSPACE/sandbox/logs/audit.log"
SCANNER_SCRIPT="$REAL_WORKSPACE/sandbox/scripts/scan-secrets.sh"

# Ensure directories exist
mkdir -p "$(dirname "$LOG_FILE")"
mkdir -p "$SANDBOX_WORKSPACE"

log() {
  local msg="[$(date +'%Y-%m-%d %H:%M:%S')] $1"
  echo "$msg"
  echo "$msg" >> "$LOG_FILE"
}

check_prerequisites() {
  local missing=()
  for cmd in rsync git bwrap; do
    if ! command -v "$cmd" &>/dev/null; then
      missing+=("$cmd")
    fi
  done
  if [ ${#missing[@]} -ne 0 ]; then
    echo "[-] Error: Missing prerequisites: ${missing[*]}" >&2
    exit 1
  fi
}

cmd_init() {
  log "Initializing sandbox..."
  
  if [ ! -f "$EXCLUDE_FILE" ]; then
    echo "[-] Exclusions file missing: $EXCLUDE_FILE" >&2
    exit 1
  fi

  # Sync host files to sandbox, deleting excluded/residual files in sandbox
  rsync -a --delete --delete-excluded --exclude-from="$EXCLUDE_FILE" "$REAL_WORKSPACE/" "$SANDBOX_WORKSPACE/"
  
  # Create the local .agents/AGENTS.md inside the sandbox
  mkdir -p "$SANDBOX_WORKSPACE/.agents"
  cat << 'EOF' > "$SANDBOX_WORKSPACE/.agents/AGENTS.md"
# Règles de la Sandbox Jetable

## Périmètre
- Ces règles ne s'appliquent QUE dans /sandboxes/workspace-sanitized.

## Auto-validation
- Auto-validation (always-proceed) activée pour les commandes shell internes, l'installation de dépendances et le refactoring.

## Interdits stricts
- Interdiction de lire/écrire hors de la sandbox.
- Interdiction de toute tentative d'accès réseau (l'isolation reste le garde-fou).
- Aucune écriture de secret en clair dans les fichiers du projet.

## Sortie
- Tout rapatriement vers l'hôte passe obligatoirement par `tesla-sandbox sync` (scan + diff + signature humaine). L'agent ne contourne jamais ce passage.
EOF

  log "Sandbox initialized at $SANDBOX_WORKSPACE"
}

cmd_run() {
  if [ $# -eq 0 ]; then
    log "Opening interactive shell in sandbox..."
    local run_cmd=("/bin/bash")
  else
    log "Running command in sandbox: $*"
    local run_cmd=("$@")
  fi

  # Build bwrap arguments
  # We bind / read-only, mount proc/sys/dev, bind-mount sandbox workspace writable, and map caches read-only
  # Network is completely disabled (--unshare-net)
  bwrap \
    --ro-bind / / \
    --dev-bind /dev /dev \
    --proc /proc \
    --tmpfs /tmp \
    --bind "$SANDBOX_WORKSPACE" "$SANDBOX_WORKSPACE" \
    --ro-bind-try "$HOME/.npm" "$HOME/.npm" \
    --ro-bind-try "$HOME/.cache" "$HOME/.cache" \
    --unshare-net \
    --chdir "$SANDBOX_WORKSPACE" \
    --setenv PIP_NO_INDEX 1 \
    --setenv PIP_FIND_LINKS "$HOME/.cache/pip" \
    --setenv PATH "$SANDBOX_WORKSPACE/.venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin" \
    "${run_cmd[@]}"
}

cmd_sync() {
  log "Starting synchronization audit..."
  
  # 1. Run Secrets Scan (Blocking)
  if [ ! -x "$SCANNER_SCRIPT" ]; then
    echo "[-] Secrets scanner script not found or not executable: $SCANNER_SCRIPT" >&2
    exit 1
  fi
  
  if ! "$SCANNER_SCRIPT" "$SANDBOX_WORKSPACE"; then
    log "[-] ALERT: Sync blocked due to secret risk detection!"
    exit 3
  fi

  # 2. Show virtual diff
  log "Generating diff..."
  # Use git diff --no-index to check changes, ignoring standard dependency, environment, and cache folders
  git diff --no-index \
    --exclude=".git" \
    --exclude=".env*" \
    --exclude="*.pem" \
    --exclude="*.key" \
    --exclude="id_rsa*" \
    --exclude="node_modules" \
    --exclude="__pycache__" \
    --exclude=".venv" \
    --exclude="dist" \
    --exclude="build" \
    --exclude=".cache" \
    --exclude="sandboxes" \
    --exclude="artifacts" \
    --exclude="logs" \
    --exclude=".agents" \
    "$REAL_WORKSPACE" "$SANDBOX_WORKSPACE" || true

  # 3. Interactive confirmation (if run from terminal/user context, fallback if non-interactive)
  local auto_approve=false
  if [[ "${1:-}" == "--yes" || "${1:-}" == "-y" ]]; then
    auto_approve=true
  fi

  if [ "$auto_approve" = false ]; then
    read -p "[?] Do you approve these changes and want to sync to host? (y/N): " choice
    case "$choice" in 
      y|Y|yes|Yes ) ;;
      * ) log "Sync aborted by user."; exit 0 ;;
    esac
  fi

  # 4. Sync files back, creating horodated backups on host
  log "Rapatriement des fichiers vers l'hôte avec sauvegardes..."
  
  # Backup existing changed files on host before overwrite
  # Find files that differ using a safe output format (one path per line, without headers/footers)
  local files_to_backup
  files_to_backup=$(rsync -a --delete --delete-excluded --dry-run --out-format="%n" --exclude-from="$EXCLUDE_FILE" "$SANDBOX_WORKSPACE/" "$REAL_WORKSPACE/" || true)
  
  local timestamp
  timestamp=$(date +%Y%m%d_%H%M%S)
  
  if [ -n "$files_to_backup" ]; then
    log "Backing up files to be overwritten..."
    for file in $files_to_backup; do
      if [ -f "$REAL_WORKSPACE/$file" ]; then
        mkdir -p "$(dirname "$REAL_WORKSPACE/$file.bak_$timestamp")"
        cp "$REAL_WORKSPACE/$file" "$REAL_WORKSPACE/$file.bak_$timestamp"
        log "Backup created: $file.bak_$timestamp"
      fi
    done
  fi

  # Apply files to real workspace
  rsync -a --delete --delete-excluded --exclude-from="$EXCLUDE_FILE" "$SANDBOX_WORKSPACE/" "$REAL_WORKSPACE/"
  
  log "Sync completed successfully."
}

cmd_clean() {
  log "Cleaning sandbox workspace..."
  rm -rf "$SANDBOX_WORKSPACE"
  mkdir -p "$SANDBOX_WORKSPACE"
  log "Sandbox cleaned."
}

cmd_warm() {
  if [ $# -eq 0 ]; then
    echo "Usage: $0 warm <pip-packages...>" >&2
    exit 1
  fi
  log "Warming up pip cache on host for: $*"
  pip download "$@" -d "$HOME/.cache/pip"
  log "Cache warmed up."
}

usage() {
  echo "Usage: $0 {init|run [cmd]|sync [--yes]|clean|warm [packages...]}" >&2
  exit 1
}

# Main Entry Point
check_prerequisites

case "${1:-}" in
  init)
    cmd_init
    ;;
  run)
    shift
    cmd_run "$@"
    ;;
  sync)
    shift
    cmd_sync "$@"
    ;;
  clean)
    cmd_clean
    ;;
  warm)
    shift
    cmd_warm "$@"
    ;;
  *)
    usage
    ;;
esac
