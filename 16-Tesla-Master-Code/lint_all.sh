#!/usr/bin/env bash
# lint_all.sh — Pre-flight codebase verification check
set -u

echo "=== [⚙️] Starting Master Code Verification Check ==="

# Check Python Syntax & Lints
if command -v ruff &> /dev/null; then
    echo "[*] Checking Python with Ruff..."
    ruff check .
    RUFF_STATUS=$?
else
    echo "[!] Warning: Ruff is not installed. Skipping Python linter."
    RUFF_STATUS=0
fi

# Check Web Syntax & Lints
if command -v biome &> /dev/null; then
    echo "[*] Checking Web assets with Biome..."
    biome check .
    BIOME_STATUS=$?
else
    echo "[!] Warning: Biome is not installed. Skipping JS/TS/JSON linter."
    BIOME_STATUS=0
fi

# Check Pyright typing
if command -v pyright &> /dev/null; then
    echo "[*] Verifying static types with Pyright..."
    pyright
    PYRIGHT_STATUS=$?
else
    echo "[!] Warning: Pyright is not installed. Skipping type validation."
    PYRIGHT_STATUS=0
fi

echo "=== [📋] Verification Diagnostics Summary ==="
echo "Python Ruff Status: $RUFF_STATUS"
echo "Web Biome Status: $BIOME_STATUS"
echo "Pyright Status: $PYRIGHT_STATUS"

if [ $RUFF_STATUS -eq 0 ] && [ $BIOME_STATUS -eq 0 ] && [ $PYRIGHT_STATUS -eq 0 ]; then
    echo "[✓] SUCCESS: All code verification checks passed."
    exit 0
else
    echo "[-] ERROR: Code verification failed. Fix lint or typing errors before committing."
    exit 1
fi
