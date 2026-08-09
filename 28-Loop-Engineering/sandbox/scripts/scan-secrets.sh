#!/usr/bin/env bash
# scan-secrets.sh — Scan anti-secrets bloquant
set -euo pipefail

TARGET="${1:-}"
CONFIG_DIR="$(dirname "$(dirname "$(readlink -f "$0")")")/config"
PATTERNS_FILE="$CONFIG_DIR/secret-patterns.txt"

if [ -z "$TARGET" ] || [ ! -d "$TARGET" ]; then
  echo "[-] Target directory invalid or not provided." >&2
  exit 1
fi

echo "[*] Scanning target: $TARGET"

# 1. Check for sensitive filenames (excluding dependency/cache directories)
if find "$TARGET" \( -name node_modules -o -name .venv -o -name .git -o -name .cache -o -name .agents \) -prune -o -type f \( -name ".env" -o -name ".env.*" -o -name "*.pem" -o -name "*.key" -o -name "id_rsa*" \) -print | grep -q .; then
  echo "[!] SECRET_FILE_RISK: Sensitive file names detected in target!" >&2
  find "$TARGET" \( -name node_modules -o -name .venv -o -name .git -o -name .cache -o -name .agents \) -prune -o -type f \( -name ".env" -o -name ".env.*" -o -name "*.pem" -o -name "*.key" -o -name "id_rsa*" \) -print
  exit 2
fi

# 2. Check for patterns in file content
if [ -f "$PATTERNS_FILE" ]; then
  # Read patterns and construct grep search
  while IFS= read -r pattern || [ -n "$pattern" ]; do
    # Skip empty lines or comments
    [[ -z "$pattern" || "$pattern" =~ ^# ]] && continue
    if grep -RIlE --exclude-dir=node_modules --exclude-dir=.venv --exclude-dir=.git --exclude-dir=.cache --exclude-dir=.agents "$pattern" "$TARGET" >/dev/null 2>&1; then
      echo "[!] SECRET_PATTERN_RISK: Secret pattern matching '$pattern' found!" >&2
      grep -RInE --exclude-dir=node_modules --exclude-dir=.venv --exclude-dir=.git --exclude-dir=.cache --exclude-dir=.agents "$pattern" "$TARGET"
      exit 3
    fi
  done < "$PATTERNS_FILE"
else
  # Fallback patterns if config file is missing
  echo "[*] Warning: secret-patterns.txt not found. Using fallback regex."
  FALLBACK="(api[_-]?key|token|password|passwd|credential|client_secret|private[_ -]?key)[[:space:]]*[:=][[:space:]]*[A-Za-z0-9_./+=-]{12,}|BEGIN RSA|BEGIN OPENSSH|BEGIN PRIVATE"
  if grep -RIlE --exclude-dir=node_modules --exclude-dir=.venv --exclude-dir=.git --exclude-dir=.cache --exclude-dir=.agents "$FALLBACK" "$TARGET" >/dev/null 2>&1; then
    echo "[!] SECRET_PATTERN_RISK: Secret patterns found (fallback regex)!" >&2
    grep -RInE --exclude-dir=node_modules --exclude-dir=.venv --exclude-dir=.git --exclude-dir=.cache --exclude-dir=.agents "$FALLBACK" "$TARGET"
    exit 3
  fi
fi

echo "[+] Secret scan passed successfully. No secrets found."
exit 0
