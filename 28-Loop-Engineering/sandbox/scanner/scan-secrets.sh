#!/usr/bin/env bash
set -euo pipefail

TARGET="${1:-}"

if [ -z "$TARGET" ] || [ ! -d "$TARGET" ]; then
  printf "SCAN_TARGET_INVALID=1\n" >&2
  printf "MAIN_RENDUE_A_MAHONHEIM=1\n"
  false
fi

if find "$TARGET" -type f \( -name ".env" -o -name ".env.*" -o -name "*.pem" -o -name "*.key" \) -print | grep -q .; then
  printf "SECRET_FILE_RISK=1\n"
  printf "MAIN_RENDUE_A_MAHONHEIM=1\n"
  false
fi

if grep -RIlE "(api[_-]?key|token|password|passwd|credential|client_secret|private[_ -]?key)[[:space:]]*[:=][[:space:]]*[A-Za-z0-9_./+=-]{12,}|BEGIN RSA|BEGIN OPENSSH|BEGIN PRIVATE" "$TARGET" >/dev/null 2>&1; then
  printf "SECRET_PATTERN_RISK=1\n"
  printf "MAIN_RENDUE_A_MAHONHEIM=1\n"
  false
fi

printf "SECRET_SCAN_OK=1\n"
printf "SCAN_TARGET=%s\n" "$TARGET"
printf "MAIN_RENDUE_A_MAHONHEIM=1\n"
