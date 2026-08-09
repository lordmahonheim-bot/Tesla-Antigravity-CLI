# Capability Scoring & Routing : Cluedo-Grands_Détectives-2023

## Matrice de Sélection des Modèles

- **N1: Acquisition & Extraction**
  - Profil : I/O volumétrique, recherche web, conversion d'assets.
  - Modèle Recommandé : **Gemini Flash** (Cost=100, Latency=100)
  - Agents: `tesla-web-raider`, `tesla-arcanis-360`

- **N2: Curation & UX Writing**
  - Profil : Rédaction, taxonomie, structuration sémantique.
  - Modèle Recommandé : **Gemini Pro / Claude Sonnet** (Reasoning=78-82, Memory=75-80)
  - Agents: `tesla-curator-prime`, `tesla-writing-skills`

- **N3: Engineering & HTML Construction**
  - Profil : Code complexe, SPA, intégration Base64 lourde, SVG, JS.
  - Modèle Recommandé : **Claude Sonnet** (Code=94)
  - Agents: `tesla-master-code`

- **N4: QA, Stress-Test & Resilience**
  - Profil : Audit critique, détection d'edge-cases, analyse de taille.
  - Modèle Recommandé : **Claude Opus** (Audit=96)
  - Agents: `premortem`

## Politique Retry & Fallback
- N1 : Si échec -> Gemini Pro.
- N3 : Si échec -> Claude Opus (Escalade budgétaire si accordée).
- N4 : Si échec -> Claude Sonnet (Optimisation de tokens).
