# OUTPUTS — Campagne LinkedIn : Tesla-Antigravity-CLI

![Status](https://img.shields.io/badge/Status-Prêt%20à%20publier-brightgreen) ![Format](https://img.shields.io/badge/Carrousel-4%3A5%201080x1350-blue) ![Slides](https://img.shields.io/badge/Slides-6-purple)

*Author:* Abdellah MOUHTAJ (Lord Mahonheim)
*Cible:* [linkedin.com/in/abdellah-mouhtaj-consultant-performance](https://www.linkedin.com/in/abdellah-mouhtaj-consultant-performance)
*Sujet:* mise en valeur du dépôt **Tesla-Antigravity-CLI**

---

## 📌 Executive Summary

Ce dossier contient l'intégralité d'une campagne de publication LinkedIn destinée à valoriser
le dépôt Tesla-Antigravity-CLI comme **réalisation personnelle**, en assumant le positionnement
de son auteur : non-développeur de formation, opérateur et architecte de systèmes par la pratique.

Le message central :

> « L'IA propose. Le code valide. »
> — et derrière cette doctrine, un effort humain réel : 60 modules, ~21 000 lignes de Python,
> ~29 000 lignes de documentation.

---

## 📂 Contenu du dossier

| Fichier | Rôle | Usage |
| :--- | :--- | :--- |
| `POST-LinkedIn-A-Copier-Coller.txt` | Texte du post + premier commentaire | **À copier tel quel dans LinkedIn** |
| `POST-LinkedIn-Tesla-Antigravity-CLI.md` | Dossier complet : 4 variantes du texte + conseils + stratégie | Référence éditoriale |
| `Carrousel-Tesla-Antigravity-CLI.pdf` | Carrousel 6 slides, 4:5 (1080×1350) | **À déposer dans le post** |
| `slides/slide-1.png` … `slide-6.png` | Les 6 slides en images 1080×1350 | Variante « publication en images » |
| `src/build_carousel.py` | Générateur du carrousel | Régénérer après modification du texte |
| `src/qa_check.py` | Contrôle qualité (marges + collisions) | Vérifier avant publication |
| `src/fetch_fonts.sh` | Récupère les polices Inter en `.ttf` | Prérequis du générateur |

---

## 🎞️ Les 6 slides du carrousel

| # | Titre interne | Message |
| :--- | :--- | :--- |
| 1 | Accroche | « Je ne suis pas développeur. » + les chiffres du dépôt |
| 2 | Le projet | Tesla-Antigravity-CLI et les 3 problèmes qu'il résout |
| 3 | La doctrine | « L'IA propose. Le code valide. » + les 3 principes (local, vérifié, approuvé) |
| 4 | Concrètement | 5 briques techniques réelles sur les 60 modules |
| 5 | Les chiffres | Les mesures du dépôt + le bloc « Ce dépôt, c'est mon travail. » |
| 6 | La leçon | « Le diplôme donne une autorisation. Le travail donne une légitimité. » |

---

## 🚀 Procédure de publication

### 1. Publier le post
1. Ouvrir `POST-LinkedIn-A-Copier-Coller.txt`.
2. Copier la section **CORPS DU POST** dans le rédacteur LinkedIn.
3. **Ne pas coller le lien GitHub dans le corps du post** (LinkedIn réduit sa portée).

### 2. Attacher le carrousel
1. Dans le rédacteur, cliquer sur **Ajouter un document** (*Add a document*).
2. Déposer `Carrousel-Tesla-Antigravity-CLI.pdf`.
3. **Renommer le document** : `Tesla-Antigravity-CLI — Gouvernance des agents IA`.
   → Ce titre devient le titre cliquable affiché sur le post. C'est ce qui déclenche le vrai format carrousel feuilletable.
4. Vérifier que la page de couverture est bien la slide 1.

### 3. Après publication (dans la minute)
1. Publier le **PREMIER COMMENTAIRE** (section dédiée du `.txt`) avec le lien GitHub.
2. Épingler ce commentaire si l'option est disponible.
3. Épingler le post en haut du profil.

---

## 🔄 Régénérer le carrousel

```bash
cd OUTPUTS/LinkedIn-Tesla-Antigravity-CLI

# 1) Dépendances
python3 -m venv .venv
.venv/bin/pip install reportlab pymupdf fontTools brotli

# 2) Polices Inter (une seule fois) -> /tmp/fonts par défaut
bash src/fetch_fonts.sh

# 3) Générer puis contrôler
.venv/bin/python src/build_carousel.py     # -> Carrousel-Tesla-Antigravity-CLI.pdf
.venv/bin/python src/qa_check.py           # -> "aucun probleme detecte"
```

Variantes :

```bash
# Polices dans un autre dossier
TESLA_FONTS=/chemin/vers/fonts .venv/bin/python src/build_carousel.py

# Export des 6 slides en PNG 1080x1350 (pour publier en images)
.venv/bin/python - <<'EOF'
import pymupdf
d = pymupdf.open('Carrousel-Tesla-Antigravity-CLI.pdf')
for i, p in enumerate(d):
    p.get_pixmap(matrix=pymupdf.Matrix(1, 1)).save(f'slides/slide-{i+1}.png')
EOF
```

`qa_check.py` sort en code 1 si un texte franchit les marges ou si deux blocs se
chevauchent : il est donc utilisable directement dans un pipeline.

---

## 🎨 Charte graphique

| Rôle | Couleur |
| :--- | :--- |
| Fond | `#0C1220` → `#070A11` (dégradé vertical) |
| Cartes | `#121A29` / `#0F1622` — bordure `#22304A` |
| Accent (validation) | `#35D6C4` |
| Accent secondaire | `#5B8CFF` |
| Alerte / risque | `#FF6B6B` |
| Texte | `#FFFFFF` · `#98A6BC` · `#6B7A93` |

**Police :** Inter (Light → Black). Le fichier PDF embarque les sous-ensembles de polices :
il s'affiche donc correctement sur tout appareil, y compris la prévisualisation LinkedIn.

---

## 📐 Choix techniques

| Décision | Raison |
| :--- | :--- |
| **PDF 1080×1350 (4:5)** | Format natif du carrousel LinkedIn : occupe le maximum d'écran mobile. |
| **PDF plutôt qu'images** | Un document LinkedIn reste feuilletable et génère plus d'impressions qu'une galerie d'images. |
| **Slides PNG fournies en plus** | Permet la variante « publication en images » sans régénérer quoi que ce soit. |
| **Génération par code** | Le carrousel reste modifiable (texte, chiffres, couleurs) et reproductible à l'identique. |
| **QA automatisée** | Les contrôles de marges et de collisions relèvent d'une vérification machine, pas de l'œil. |

### Défauts détectés et corrigés par la QA (v1 → v2)

1. **Interlettrage fuyant** — le paramètre de tracking d'un titre se propageait à tous les
   paragraphes suivants du même flux PDF, faisant sortir du texte des slides 2 et 6.
   Corrigé en isolant chaque état graphique (`saveState` / `restoreState`).
2. **Halos opaques** — la transparence n'étant pas respectée au rendu, les halos
   masquaient le contenu. Remplacés par un mélange de couleurs opaque vers le fond.
3. **Collision sur la slide 6** — l'origine du curseur d'empilement était inversée,
   superposant le titre et le bloc d'appel à l'action. Corrigé par un empilement calculé,
   puis validé par `qa_check.py` : *aucun problème détecté*.

---

## ✅ Contrôles avant publication

- [ ] `qa_check.py` retourne « aucun probleme detecte »
- [ ] Le PDF fait bien 6 pages en 1080×1350
- [ ] Le document LinkedIn est renommé avant publication
- [ ] Le lien GitHub est **uniquement** dans le premier commentaire
- [ ] Les chiffres du post correspondent au dépôt au moment de la publication
- [ ] Le post est épinglé sur le profil après publication

---

*« La précision dans le workflow, la gouvernance dans le processus, la stabilité dans le résultat. »*
