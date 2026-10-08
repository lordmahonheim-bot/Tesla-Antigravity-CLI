#!/usr/bin/env python3
"""
Controle qualite du carrousel LinkedIn.

Verifie, page par page :
  1. qu'aucun texte ne franchit les marges de securite ;
  2. qu'aucun bloc de texte n'en chevauche un autre (collision).

Code de sortie : 0 si tout est propre, 1 sinon (utilisable en CI).

Usage :
    python3 qa_check.py [chemin_du_pdf]
"""
import os
import sys

import pymupdf

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_PDF = os.path.join(os.path.dirname(SRC_DIR),
                           'Carrousel-Tesla-Antigravity-CLI.pdf')

W, H = 1080, 1350
ML, MR, MT, MB = 88, 88, 88, 56      # marges de securite
COLLISION_THRESHOLD = 0.35           # recouvrement tolere du plus petit bloc


def main(path):
    if not os.path.isfile(path):
        sys.exit(f"PDF introuvable : {path}")
    if not (W == 1080 and H == 1350):
        sys.exit("Dimensions internes inattendues.")

    doc = pymupdf.open(path)
    problems = 0

    if doc.page_count != 6:
        problems += 1
        print(f"[GLOBAL] {doc.page_count} pages au lieu de 6 attendues")

    for pno in range(doc.page_count):
        page = doc[pno]
        rect = page.rect
        if abs(rect.width - W) > 0.5 or abs(rect.height - H) > 0.5:
            problems += 1
            print(f"[P{pno+1}] format {rect.width}x{rect.height} != {W}x{H}")

        spans = []
        for b in page.get_text("dict")["blocks"]:
            for line in b.get("lines", []):
                for s in line["spans"]:
                    if s["text"].strip():
                        spans.append((pymupdf.Rect(s["bbox"]), s["text"]))

        for r, t in spans:
            if (r.x1 > W - MR + 1 or r.x0 < ML - 1
                    or r.y0 < MT - 1 or r.y1 > H - MB + 1):
                problems += 1
                print(f"[P{pno+1}] HORS MARGE  x0={r.x0:7.1f} x1={r.x1:7.1f} "
                      f"y0={r.y0:7.1f} y1={r.y1:7.1f} :: {t[:46]!r}")

        for i in range(len(spans)):
            for j in range(i + 1, len(spans)):
                r1, t1 = spans[i]
                r2, t2 = spans[j]
                inter = r1 & r2
                if inter.is_empty:
                    continue
                small = min(r1.get_area(), r2.get_area())
                if small and inter.get_area() / small > COLLISION_THRESHOLD:
                    problems += 1
                    print(f"[P{pno+1}] COLLISION  {t1[:28]!r}  ><  {t2[:28]!r}")

    print("\nRESULTAT :", "aucun probleme detecte" if problems == 0
          else f"{problems} probleme(s)")
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PDF))
