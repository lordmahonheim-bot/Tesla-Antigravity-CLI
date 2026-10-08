#!/usr/bin/env bash
# Recupere et convertit les 7 graisses de la police Inter en .ttf
# pour le generateur de carrousel (reportlab ne lit pas le woff2).
#
# Usage : bash src/fetch_fonts.sh [dossier_de_sortie]
# Defaut : /tmp/fonts   (surchargeable via la variable TESLA_FONTS)
set -euo pipefail

DEST="${1:-${TESLA_FONTS:-/tmp/fonts}}"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

echo "==> Cible des polices : $DEST"

if ! command -v npm >/dev/null 2>&1; then
  echo "ERREUR : npm est requis (le paquet inter-ui fournit les fichiers)." >&2
  exit 1
fi
if ! python3 -c "import fontTools" 2>/dev/null; then
  echo "ERREUR : fontTools est requis. Installe-le :" >&2
  echo "        pip install fontTools brotli" >&2
  exit 1
fi

echo "==> Telechargement du paquet inter-ui (registre npm)…"
( cd "$WORK" && npm pack inter-ui --silent >/dev/null )
tar xzf "$WORK"/inter-ui-*.tgz -C "$WORK"

mkdir -p "$DEST"
for w in Light Regular Medium SemiBold Bold ExtraBold Black; do
  src="$(find "$WORK" -path "*/web/Inter-$w.woff2" | head -1)"
  if [ -z "$src" ]; then
    echo "ERREUR : Inter-$w.woff2 introuvable dans le paquet." >&2
    exit 1
  fi
  cp "$src" "$WORK/"
done

echo "==> Conversion woff2 -> ttf…"
python3 - "$WORK" "$DEST" <<'PY'
import glob, os, sys
from fontTools.ttLib import TTFont

work, dest = sys.argv[1], sys.argv[2]
for f in sorted(glob.glob(os.path.join(work, 'Inter-*.woff2'))):
    out = os.path.join(dest, os.path.basename(f).replace('.woff2', '.ttf'))
    ft = TTFont(f)
    ft.flavor = None          # retire la compression woff2
    ft.save(out)
    print(f"   {os.path.basename(out):24} {os.path.getsize(out)//1024:4d} KB")
PY

echo "==> Polices pretes dans $DEST"
echo "    Relance : python3 src/build_carousel.py"
