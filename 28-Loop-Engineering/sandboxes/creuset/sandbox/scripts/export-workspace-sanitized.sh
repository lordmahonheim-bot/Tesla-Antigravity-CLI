#!/usr/bin/env bash
set -euo pipefail

ROOT="${TESLA_ROOT:-$HOME/bifrost/tesla}"
OUT="${1:-$ROOT/sandboxes/workspace-sanitized}"

mkdir -p "$OUT"

rsync -a --delete --delete-excluded   --exclude ".git/"   --exclude ".env"   --exclude ".env.*"   --exclude ".ssh/"   --exclude ".gnupg/"   --exclude ".gemini/"   --exclude ".codex/"   --exclude ".config/"   --exclude ".local/"   --exclude ".antigravity/"   --exclude ".antigravitycli/"   --exclude "DataBase/"   --exclude "node_modules/"   --exclude "__pycache__/"   --exclude ".pytest_cache/"   --exclude "sandboxes/"   --exclude "artifacts/sandbox/"   --exclude "logs/sandbox/"   --exclude "sandbox/scanner/"   "$ROOT/" "$OUT/"

printf "TESLA_SANDBOX_WORKSPACE_EXPORT_SCRIPT_READY=1\n"
printf "SANITIZED_WORKSPACE_TARGET=%s\n" "$OUT"
printf "MAIN_RENDUE_A_MAHONHEIM=1\n"
