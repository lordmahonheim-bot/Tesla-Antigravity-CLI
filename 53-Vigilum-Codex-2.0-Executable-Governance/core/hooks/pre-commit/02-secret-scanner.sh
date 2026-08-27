#!/usr/bin/env bash
set -eu
. "$(dirname "$0")/../lib/tesla-exit-codes.sh"
. "$(dirname "$0")/../lib/tesla-logging.sh"

files=$(git diff --cached --name-only --diff-filter=AM || true)
[ -n "$files" ] || exit "$TESLA_EXIT_OK"

# Multi-engine scanner: Regex patterns + Shannon entropy detector
SECRET_REGEX='(AIza[0-9A-Za-z_-]{35}|sk-[A-Za-z0-9_-]{20,}|ghp_[0-9A-Za-z]{36}|gho_[0-9A-Za-z]{36}|xox[baprs]-[0-9A-Za-z_-]{10,}|-----BEGIN (RSA|EC|OPENSSH|PRIVATE) KEY-----)'

for f in $files; do
  [ -f "$f" ] || continue
  case "$f" in
    *.png|*.jpg|*.jpeg|*.gif|*.ico|*.pdf|*.bin|*.lock|*.pyc) continue ;;
  esac

  # Engine 1: Regex scan
  if grep -E -n "$SECRET_REGEX" "$f" >/dev/null 2>&1; then
    tesla_log ERROR "potential high-confidence secret detected in $f"
    exit "$TESLA_EXIT_SECRET"
  fi

  # Engine 2: Shannon entropy detection on long alphanumeric strings
  if python3 - "$f" <<'PY'
import sys, math, re
from pathlib import Path
content = Path(sys.argv[1]).read_text(encoding='utf-8', errors='ignore')
tokens = re.findall(r'[A-Za-z0-9_-]{32,}', content)
for t in tokens:
    if t.startswith("sha256") or t.startswith("sha512") or len(set(t)) < 8:
        continue
    probs = [t.count(c)/len(t) for c in set(t)]
    entropy = -sum(p * math.log2(p) for p in probs)
    if entropy > 4.5 and len(t) >= 40:
        sys.exit(1)
sys.exit(0)
PY
  then
    :
  else
    tesla_log ERROR "high Shannon-entropy token (probable secret/key) detected in $f"
    exit "$TESLA_EXIT_SECRET"
  fi
done

tesla_log INFO "secret scan passed"
exit "$TESLA_EXIT_OK"
