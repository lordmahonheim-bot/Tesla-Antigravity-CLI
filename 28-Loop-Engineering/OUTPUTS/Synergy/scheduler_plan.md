# Scheduler Plan : Cluedo-Grands_Détectives-2023

## Mode d'exécution par Nœuds

- **N1: Acquisition & Extraction** (Parallèle / Fan-out)
  - `tesla-web-raider` : Scrape et rapatrie les assets (images/textes).
  - `tesla-arcanis-360` : Extrait et convertit en Base64 les assets critiques.
  - *Dépendances* : Aucune.

- **N2: Curation & UX Writing** (Parallèle)
  - `tesla-curator-prime` : Valide la taxonomie de l'encyclopédie et FAQ.
  - `tesla-writing-skills` : Formate les textes UX, règles et dialogues d'interface.
  - *Dépendances* : N1.

- **N3: Engineering & HTML Construction** (Série)
  - `tesla-master-code` : Assemble la SPA, le simulateur 3D et les moteurs logiques.
  - *Dépendances* : N2.

- **N4: QA, Stress-Test & Resilience** (Série)
  - `premortem` : Audite la taille du fichier, le chargement offline, l'accessibilité et la cohérence des règles du Cluedo.
  - *Dépendances* : N3.

## Chemin Critique
N1 -> N2 -> N3 -> N4
L'avancement de chaque nœud bloque strictement le suivant.
