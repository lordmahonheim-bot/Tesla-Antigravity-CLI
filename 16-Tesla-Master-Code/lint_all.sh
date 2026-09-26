#!/usr/bin/env bash
# lint_all.sh — Pre-flight codebase verification check
set -u

echo "=== [⚙️] Starting Master Code Verification Check ==="

UNAVAILABLE_STATUS=66
MISSING_TOOLS=0

# Check Python Syntax & Lints
if command -v ruff &> /dev/null; then
    echo "[*] Checking Python with Ruff..."
    ruff check .
    RUFF_STATUS=$?
else
    echo "[!] ERROR: Ruff is not installed. Code verification cannot proceed (Fail-open forbidden)."
    RUFF_STATUS=$UNAVAILABLE_STATUS
    MISSING_TOOLS=1
fi

echo "=== [📋] Verification Diagnostics Summary ==="
echo "Python Ruff Status: $RUFF_STATUS"
echo "Pyright Status: Skipped"

if [ $MISSING_TOOLS -ne 0 ]; then
    echo "[-] ERROR: Code verification failed due to missing tools. Return code $UNAVAILABLE_STATUS."
    exit $UNAVAILABLE_STATUS
elif [ $RUFF_STATUS -eq 0 ]; then
    echo "[✓] SUCCESS: All code verification checks passed."
    exit 0
else
    echo "[-] ERROR: Code verification failed. Fix lint or typing errors before committing."
    exit 1
fi
