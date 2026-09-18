#!/usr/bin/env bash
# install.sh - Installe le demon Ouroboros Auto-Capture (service utilisateur).
#
# Conforme GEMINI.md R8 (Zero-Touch Background Ops) : aucune execution manuelle
# persistante demandee a l'operateur, le demon est un service systemd --user.
#   ./install.sh [--interval 60] [--no-start]
#   ./install.sh --uninstall
set -euo pipefail

MVP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TESLA_ROOT="${TESLA_ROOT:-$(git -C "$MVP_DIR" rev-parse --show-toplevel 2>/dev/null || echo "$MVP_DIR")}"
BRAIN_ROOT="${TESLA_BRAIN_ROOT:-$HOME/.gemini/antigravity-cli/brain}"
INTERVAL=60
START=1
UNIT_NAME="ouroboros-capture.service"
UNIT_DIR="$HOME/.config/systemd/user"

usage() { echo "Usage: $0 [--interval N] [--no-start] [--uninstall]"; }

UNINSTALL=0
while [ $# -gt 0 ]; do
  case "$1" in
    --interval) INTERVAL="$2"; shift 2 ;;
    --no-start) START=0; shift ;;
    --uninstall) UNINSTALL=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Option inconnue: $1" >&2; usage; exit 2 ;;
  esac
done

if [ "$UNINSTALL" -eq 1 ]; then
  systemctl --user disable --now "$UNIT_NAME" 2>/dev/null || true
  rm -f "$UNIT_DIR/$UNIT_NAME"
  systemctl --user daemon-reload 2>/dev/null || true
  echo "[Install] Service $UNIT_NAME desinstalle."
  exit 0
fi

PYTHON="$(command -v python3)"
mkdir -p "$UNIT_DIR"
sed -e "s#__PYTHON__#$PYTHON#" \
    -e "s#__MVP_DIR__#$MVP_DIR#" \
    -e "s#__INTERVAL__#$INTERVAL#" \
    -e "s#__TESLA_ROOT__#$TESLA_ROOT#" \
    -e "s#__BRAIN_ROOT__#$BRAIN_ROOT#" \
    "$MVP_DIR/deploy/ouroboros-capture.service.template" > "$UNIT_DIR/$UNIT_NAME"

echo "[Install] Unite ecrite : $UNIT_DIR/$UNIT_NAME"
echo "[Install]   TESLA_ROOT=$TESLA_ROOT"
echo "[Install]   BRAIN_ROOT=$BRAIN_ROOT (cree si absent a l'execution)"
echo "[Install]   INTERVAL=${INTERVAL}s"

# Enregistrement best-effort du hook post-outil (voie immediate).
HOOK_SRC="$MVP_DIR/hooks/antigravity/hook_11_ouroboros_capture.sh"
HOOK_REGISTERED=0
for candidate in "$TESLA_ROOT/.antigravity/hooks" "$HOME/.config/antigravity/hooks"; do
  if [ -d "$candidate" ]; then
    ln -sf "$HOOK_SRC" "$candidate/hook_11_ouroboros_capture.sh" 2>/dev/null || true
    echo "[Install] Hook enregistre : $candidate/hook_11_ouroboros_capture.sh"
    HOOK_REGISTERED=1
  fi
done
if [ "$HOOK_REGISTERED" -eq 0 ]; then
  echo "[Install] Aucun repertoire de hooks Antigravity detecte :"
  echo "          copiez $HOOK_SRC vers le repertoire de hooks du runtime"
  echo "          (la voie demon/scan reste garantie sans le hook)."
fi

if ! command -v systemctl >/dev/null 2>&1; then
  echo "[Install] systemctl introuvable : demarrez manuellement :"
  echo "          TESLA_ROOT=$TESLA_ROOT python3 $MVP_DIR/scripts/ouroboros_daemon.py"
  exit 0
fi

systemctl --user daemon-reload
systemctl --user enable "$UNIT_NAME"
if [ "$START" -eq 1 ]; then
  systemctl --user restart "$UNIT_NAME"
  sleep 1
  systemctl --user status "$UNIT_NAME" --no-pager || true
  echo "[Install] Premier backfill : journalctl --user -u $UNIT_NAME -f"
else
  echo "[Install] Service active (non demarre) : systemctl --user start $UNIT_NAME"
fi
