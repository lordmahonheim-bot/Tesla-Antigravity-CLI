#!/usr/bin/env python3
"""
Generateur du carrousel LinkedIn — Tesla-Antigravity-CLI
PDF 6 pages, format 4:5 (1080 x 1350 px), compatible "document" LinkedIn.

Emplacement : OUTPUTS/LinkedIn-Tesla-Antigravity-CLI/src/build_carousel.py
Sortie     : OUTPUTS/LinkedIn-Tesla-Antigravity-CLI/Carrousel-Tesla-Antigravity-CLI.pdf

Prerequis :
    pip install reportlab
    # + les 7 graisses Inter en .ttf dans le dossier de polices (voir fetch_fonts.sh)

Utilisation :
    python3 build_carousel.py                 # genere le PDF
    TESLA_FONTS=/autre/dossier python3 build_carousel.py

Historique des correctifs (v2) :
  - le tracking (Tc) des textobjects est isole par saveState/restoreState :
    il fuyait dans les Paragraph suivants et provoquait des debordements ;
  - les halos sont obtenus par melange de couleurs opaque vers le fond,
    l'alpha n'etant pas respecte par le rendu ;
  - la slide 6 est empilee par curseur calcule (zero collision).
"""
import os
import sys

from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, Color
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import Paragraph
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ------------------------------------------------------------------ CHEMINS
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.dirname(SRC_DIR)
DEFAULT_PDF = os.path.join(OUT_DIR, 'Carrousel-Tesla-Antigravity-CLI.pdf')
FONT_DIR = os.environ.get('TESLA_FONTS', '/tmp/fonts')

# ------------------------------------------------------------------ CONSTANTES
W, H = 1080, 1350
M = 88
CW = W - 2 * M                      # 904

BG_TOP   = HexColor('#0C1220')
BG_BOT   = HexColor('#070A11')
CARD     = HexColor('#121A29')
CARD_ALT = HexColor('#0F1622')
BORDER   = HexColor('#22304A')
ACCENT   = HexColor('#35D6C4')
ACCENT_D = HexColor('#1E8C82')
BLUE     = HexColor('#5B8CFF')
RISK     = HexColor('#FF6B6B')
WHITE    = HexColor('#FFFFFF')
MUTED    = HexColor('#98A6BC')
MUTED_D  = HexColor('#6B7A93')


# ------------------------------------------------------------------ POLICES
def register_fonts():
    files = [
        ('Inter-Light', 'Inter-Light.ttf'),
        ('Inter', 'Inter-Regular.ttf'),
        ('Inter-Medium', 'Inter-Medium.ttf'),
        ('Inter-SemiBold', 'Inter-SemiBold.ttf'),
        ('Inter-Bold', 'Inter-Bold.ttf'),
        ('Inter-ExtraBold', 'Inter-ExtraBold.ttf'),
        ('Inter-Black', 'Inter-Black.ttf'),
    ]
    missing = [f for _, f in files
               if not os.path.isfile(os.path.join(FONT_DIR, f))]
    if missing:
        sys.exit(
            f"Polices manquantes dans {FONT_DIR} : {', '.join(missing)}\n"
            "Lance d'abord : bash src/fetch_fonts.sh\n"
            "ou indique un autre dossier : TESLA_FONTS=/chemin python3 build_carousel.py"
        )
    for name, f in files:
        pdfmetrics.registerFont(TTFont(name, os.path.join(FONT_DIR, f)))
    pdfmetrics.registerFontFamily('Inter', normal='Inter', bold='Inter-Bold',
                                  italic='Inter', boldItalic='Inter-Bold')


# ------------------------------------------------------------------ OUTILS
def bg_rgb_at(y):
    """Couleur du degrade de fond a la hauteur y (0 = bas de page)."""
    t = (H - y) / H
    return tuple(
        getattr(BG_TOP, ch) + (getattr(BG_BOT, ch) - getattr(BG_TOP, ch)) * t
        for ch in ('red', 'green', 'blue')
    )


def gradient_bg(c):
    steps = 270
    band = H / steps
    for i in range(steps):
        t = i / (steps - 1)
        c.setFillColor(Color(
            BG_TOP.red + (BG_BOT.red - BG_TOP.red) * t,
            BG_TOP.green + (BG_BOT.green - BG_TOP.green) * t,
            BG_TOP.blue + (BG_BOT.blue - BG_TOP.blue) * t,
        ))
        c.rect(0, H - (i + 1) * band, W, band + 1, stroke=0, fill=1)


def glow(c, x, y, r, col=ACCENT, intensity=0.13, layers=32):
    """Halo doux : cercles opaques melanges vers la couleur de fond."""
    br, bg_, bb = bg_rgb_at(y)
    for i in range(layers, 0, -1):
        a = intensity * (1.0 - i / layers) ** 2.2
        c.setFillColor(Color(br + (col.red - br) * a,
                             bg_ + (col.green - bg_) * a,
                             bb + (col.blue - bb) * a))
        c.circle(x, y, r * i / layers, stroke=0, fill=1)


def tracked(c, x, y, text, font='Inter-SemiBold', size=21,
            col=ACCENT, track=3.4):
    """Texte interlettre. Isole dans q/Q : Tc ne fuit pas dans le reste."""
    c.saveState()
    t = c.beginText(x, y)
    t.setFont(font, size)
    t.setFillColor(col)
    t.setCharSpace(track)
    t.textOut(text)
    c.drawText(t)
    c.restoreState()


def kicker(c, text, y=1226, col=ACCENT, size=21, track=3.4):
    tracked(c, M, y, text.upper(), 'Inter-SemiBold', size, col, track)


def rule(c, y, length=140, thickness=6, col=ACCENT, x=M):
    c.setFillColor(col)
    c.rect(x, y, length, thickness, stroke=0, fill=1)


def card(c, x, y, w, h, fill=CARD, stroke=BORDER, r=20, lw=1.6, accent_bar=None):
    c.setFillColor(fill)
    c.setStrokeColor(stroke)
    c.setLineWidth(lw)
    c.roundRect(x, y, w, h, r, stroke=1, fill=1)
    if accent_bar:
        c.setFillColor(accent_bar)
        c.rect(x, y, 7, h, stroke=0, fill=1)


def para(c, text, style, x, y_top, width):
    """Dessine un Paragraph dont le HAUT est a y_top. Renvoie sa hauteur."""
    p = Paragraph(text, style)
    p.wrapOn(c, width, 10000)
    p.drawOn(c, x, y_top - p.height)
    return p.height


def S(name, size, leading, color, font='Inter'):
    return ParagraphStyle(name, fontName=font, fontSize=size, leading=leading,
                          textColor=color, alignment=TA_LEFT)


def footer(c, idx, total=6):
    c.saveState()
    c.setFont('Inter-Medium', 19)
    c.setFillColor(MUTED_D)
    c.drawRightString(W - M, 66, f"{idx:02d} / {total:02d}")
    n, sw, gap = total, 54, 10
    x0 = (W - (n * sw + (n - 1) * gap)) / 2
    for i in range(n):
        c.setFillColor(ACCENT if i == idx - 1 else HexColor('#243250'))
        c.roundRect(x0 + i * (sw + gap), 72, sw, 7, 3.5, stroke=0, fill=1)
    c.restoreState()


# ------------------------------------------------------------------ SLIDES
def slide1(c):
    gradient_bg(c)
    glow(c, 1005, 1275, 420, ACCENT, 0.16)
    glow(c, 60, 150, 340, BLUE, 0.10)

    kicker(c, "Retour d'expérience · Gouvernance IA")

    para(c, 'Je ne suis pas<br/><font name="Inter-Black" color="#35D6C4">'
            'développeur.</font>',
         S('s1', 102, 112, WHITE, 'Inter-Bold'), M, 1128, CW)

    rule(c, 840)

    para(c, "Pas de diplôme d'informatique. Pas de poste en ESN.<br/>"
            "Pas de « 10 ans d'expérience en dev ».",
         S('s1b', 31, 47, MUTED), M, 772, CW)

    card(c, M, 372, CW, 232, CARD, BORDER, accent_bar=ACCENT)
    para(c, "ET POURTANT, JE VIENS DE PUBLIER :",
         S('s1c', 27, 38, MUTED_D, 'Inter-SemiBold'), M + 44, 556, CW - 88)
    para(c, "<font color='#35D6C4'>60 modules</font> &nbsp;·&nbsp; "
            "<font color='#35D6C4'>~21 000</font> lignes de Python<br/>"
            "<font color='#35D6C4'>~29 000</font> lignes de documentation",
         S('s1d', 40, 54, WHITE, 'Inter-Bold'), M + 44, 508, CW - 88)

    c.setFillColor(ACCENT)
    c.setFont('Inter-SemiBold', 26)
    c.drawString(M, 200, "Faites défiler  →")
    c.setFillColor(MUTED_D)
    c.setFont('Inter', 22)
    c.drawString(M + 240, 200, "6 slides")

    footer(c, 1)


def slide2(c):
    gradient_bg(c)
    glow(c, 960, 250, 400, BLUE, 0.11)

    kicker(c, "Le projet")

    para(c, 'Tesla-Antigravity-CLI',
         S('s2a', 68, 78, WHITE, 'Inter-ExtraBold'), M, 1136, CW)

    para(c, "L'infrastructure qui gouverne les agents IA autonomes.",
         S('s2b', 34, 48, ACCENT, 'Inter-SemiBold'), M, 1026, CW)

    rule(c, 878)

    para(c, "Autrement dit : le cadre qui empêche une IA de faire "
            "n'importe quoi sur votre machine.",
         S('s2c', 30, 45, MUTED), M, 826, CW)

    items = [
        ("01", "L'IA touche à vos fichiers",
         "Écritures non médiatisées, chemins cassés, scripts non portables."),
        ("02", "Le contexte explose",
         "Les balayages linéaires saturent le cache du modèle : lenteur, échecs."),
        ("03", "Les commandes se bloquent",
         "Prompts TTY absents, clés SSH non liées, push non maîtrisé."),
    ]
    ch, gap = 136, 18
    y = 560
    for num, title, desc in items:
        card(c, M, y, CW, ch, CARD_ALT, BORDER, 18)
        c.setFillColor(RISK)
        c.setFont('Inter-Bold', 24)
        c.drawString(M + 32, y + ch - 48, num)
        c.setFillColor(WHITE)
        c.setFont('Inter-SemiBold', 28)
        c.drawString(M + 100, y + ch - 48, title)
        para(c, desc, S('s2d', 22, 31, MUTED_D), M + 100, y + ch - 68, CW - 152)
        y -= (ch + gap)

    para(c, "Mon dépôt, c'est <font color='#35D6C4'>60 réponses</font> "
            "concrètes à ces 60 problèmes.",
         S('s2e', 30, 42, WHITE, 'Inter-SemiBold'), M, 212, CW)

    footer(c, 2)


def slide3(c):
    gradient_bg(c)
    glow(c, 540, 1000, 470, ACCENT, 0.09)

    kicker(c, "La doctrine")

    para(c, "« L'IA propose.<br/>"
            "<font name='Inter-Black' color='#35D6C4'>Le code valide.</font> »",
         S('s3a', 74, 92, WHITE, 'Inter-Bold'), M, 1130, CW)

    rule(c, 892)

    para(c, "Parce qu'un agent non gouverné n'est pas un assistant.<br/>"
            "<font color='#FF6B6B' name='Inter-SemiBold'>C'est un risque.</font>",
         S('s3b', 34, 48, MUTED), M, 840, CW)

    pillars = [
        ("LOCAL", "Tout s'exécute sur la machine.",
         "Aucune télémétrie vers l'extérieur. Souveraineté des données."),
        ("VÉRIFIÉ", "Analyse statique avant commit.",
         "Un code non validé ne franchit jamais la porte."),
        ("APPROUVÉ", "Aucune action sensible sans accord.",
         "L'autorité humaine reste au centre du système."),
    ]
    ph, gap = 132, 16
    y = 528
    for name, title, desc in pillars:
        card(c, M, y, CW, ph, CARD, BORDER, 18)
        tracked(c, M + 36, y + ph - 46, name, 'Inter-Bold', 22, ACCENT, 2.6)
        c.setFillColor(WHITE)
        c.setFont('Inter-SemiBold', 27)
        c.drawString(M + 36, y + ph - 84, title)
        para(c, desc, S('s3d', 22, 31, MUTED_D), M + 36, y + ph - 100, CW - 72)
        y -= (ph + gap)

    para(c, "La sécurité ne vit pas dans un prompt.<br/>"
            "<font color='#FFFFFF' name='Inter-SemiBold'>"
            "Elle vit dans l'architecture.</font>",
         S('s3e', 29, 42, MUTED), M, 196, CW)

    footer(c, 3)


def slide4(c):
    gradient_bg(c)
    glow(c, 1020, 1200, 380, ACCENT, 0.12)

    kicker(c, "Concrètement")

    para(c, "Ce que le dépôt contient",
         S('s4a', 58, 68, WHITE, 'Inter-ExtraBold'), M, 1136, CW)

    para(c, "5 briques parmi les 60 modules publiés.",
         S('s4b', 27, 38, MUTED_D), M, 1030, CW)

    rows = [
        ("01", "Gouvernance exécutable",
         "8 847 lignes de Python : confinement anti-TOCTOU, jetons cryptographiques "
         "anti-rejeu, médiation transactionnelle des écritures."),
        ("02", "Auto-guérison du code",
         "Diagnostic LSP / Pyright automatique avant chaque commit. "
         "Le code se répare, ou il ne passe pas."),
        ("03", "Bouclier anti-secrets",
         "AWS, GitHub, Slack, JWT et clés SSH filtrés par regex sur tous les "
         "journaux de session."),
        ("04", "Garde-fous Git",
         "Tout push non autorisé est refusé par des hooks POSIX et des "
         "jetons à usage unique."),
        ("05", "Mémoire locale",
         "Base de connaissances SQLite FTS5, RAG local et rotation "
         "automatique du contexte."),
    ]
    rh, gap = 146, 14
    y = 818
    for num, title, desc in rows:
        card(c, M, y, CW, rh, CARD_ALT, BORDER, 18)
        c.setFillColor(HexColor('#0B1622'))
        c.setStrokeColor(ACCENT_D)
        c.setLineWidth(1.5)
        c.roundRect(M + 28, y + rh - 60, 48, 40, 10, stroke=1, fill=1)
        c.setFillColor(ACCENT)
        c.setFont('Inter-Bold', 21)
        c.drawCentredString(M + 52, y + rh - 49, num)

        c.setFillColor(WHITE)
        c.setFont('Inter-SemiBold', 28)
        c.drawString(M + 96, y + rh - 48, title)

        para(c, desc, S('s4d', 22, 31, MUTED), M + 96, y + rh - 68, CW - 132)
        y -= (rh + gap)

    footer(c, 4)


def slide5(c):
    gradient_bg(c)
    glow(c, 90, 1270, 360, BLUE, 0.12)

    kicker(c, "Les chiffres")

    para(c, "Ce que représente ce dépôt",
         S('s5a', 58, 68, WHITE, 'Inter-ExtraBold'), M, 1136, CW)

    stats = [
        ("60", "modules documentés"),
        ("21 000", "lignes de Python"),
        ("29 000", "lignes de documentation"),
        ("4 000", "lignes de Bash"),
    ]
    gw = (CW - 24) / 2
    gh = 190
    for i, (val, lab) in enumerate(stats):
        x = M + (i % 2) * (gw + 24)
        y = 846 - (i // 2) * (gh + 24)
        card(c, x, y, gw, gh, CARD, BORDER, 20)
        c.setFillColor(ACCENT)
        c.setFont('Inter-Black', 58)
        c.drawString(x + 34, y + gh - 82, val)
        c.setFillColor(MUTED_D)
        c.setFont('Inter-Medium', 24)
        c.drawString(x + 34, y + gh - 128, lab)

    card(c, M, 300, CW, 290, HexColor('#101C24'), ACCENT_D, 20, 2, ACCENT)
    para(c, "Ce dépôt, c'est mon travail.",
         S('s5b', 40, 54, WHITE, 'Inter-Bold'), M + 44, 550, CW - 88)
    para(c, "Mon effort personnel. Mes nuits.<br/>"
            "Mes erreurs. Mes recommencements.",
         S('s5c', 29, 42, HexColor('#CFE9E5')), M + 44, 480, CW - 88)
    para(c, "Pas un tutoriel recopié. Pas un template acheté.<br/>"
            "Pas un projet rendu pour valider un diplôme.",
         S('s5d', 26, 37, MUTED_D, 'Inter-Medium'), M + 44, 380, CW - 88)

    footer(c, 5)


def slide6(c):
    """Empilement vertical calcule : chaque bloc est pose sous le precedent."""
    gradient_bg(c)
    glow(c, 540, 1180, 480, ACCENT, 0.10)
    glow(c, 540, 180, 340, BLUE, 0.08)

    kicker(c, "La leçon")

    h = para(c, "Le diplôme donne une "
                "<font color='#98A6BC'>autorisation</font>.<br/>"
                "Le travail donne une "
                "<font color='#35D6C4' name='Inter-Black'>légitimité</font>.",
             S('s6a', 50, 64, WHITE, 'Inter-Bold'), M, 1120, CW)
    cursor = 1120 - h - 62

    rule(c, cursor)
    cursor -= 60

    h = para(c, "J'ai 21 000 lignes de Python à vous montrer.<br/>"
                "Je n'ai aucun diplôme d'informatique à faire valoir.<br/>"
                "<font color='#FFFFFF' name='Inter-SemiBold'>"
                "Le second ne prouve rien. Le premier, si.</font>",
             S('s6b', 31, 45, MUTED), M, cursor, CW - 30)
    cursor -= h

    cy, ch = 316, 344
    card(c, M, cy, CW, ch, CARD, BORDER, 20, 1.6, ACCENT)

    cursor = cy + ch
    cursor -= 52
    h = para(c, "DÉPÔT PUBLIC ET DOCUMENTÉ",
             S('s6c', 27, 38, MUTED_D, 'Inter-SemiBold'), M + 44, cursor, CW - 88)
    cursor -= (h + 18)
    h = para(c, "Tesla-Antigravity-CLI",
             S('s6d', 40, 52, WHITE, 'Inter-Bold'), M + 44, cursor, CW - 88)
    cursor -= (h + 24)
    h = para(c, "Lien GitHub en premier commentaire.<br/>"
                "Critiques et retours bienvenus — c'est comme ça qu'on progresse.",
             S('s6e', 25, 36, MUTED), M + 44, cursor, CW - 88)
    cursor -= (h + 34)

    c.setFillColor(ACCENT)
    c.setFont('Inter-SemiBold', 26)
    c.drawString(M + 44, cursor, "Je n'ai pas demandé d'autorisation.")

    c.setFillColor(WHITE)
    c.setFont('Inter-Bold', 28)
    c.drawString(M, 248, "Abdellah MOUHTAJ")
    c.setFillColor(MUTED_D)
    c.setFont('Inter', 23)
    c.drawString(M, 214, "Performance Humaine & Opérations IA Gouvernées")

    footer(c, 6)


# ------------------------------------------------------------------ MAIN
def build(path=DEFAULT_PDF):
    register_fonts()
    c = canvas.Canvas(path, pagesize=(W, H))
    c.setTitle("Tesla-Antigravity-CLI — Carrousel LinkedIn")
    c.setAuthor("Abdellah MOUHTAJ")
    for fn in (slide1, slide2, slide3, slide4, slide5, slide6):
        fn(c)
        c.showPage()
    c.save()
    print("PDF genere :", path)
    return path


if __name__ == '__main__':
    build(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PDF)
