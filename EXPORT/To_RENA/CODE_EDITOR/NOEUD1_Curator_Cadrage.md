> **ARCHIVE — remplacée pour le parcours sans Chrome (audit du 2026-09-19).**
> Les commandes, modèles, chiffres et certifications ci-dessous ne sont pas
> une procédure validée. Ne pas appliquer les changements système ni les
> exemples d’auto-exécution. Utiliser le [guide corrigé TERMINATOR](LIVRABLE_FINAL_AIStudio_Headless_Terminator.md).

### 1. CADRAGE DU PROJET
Le projet vise à combler les 30% des besoins non couverts par Antigravity CLI (édition visuelle, arborescence, debug, refactoring). L'objectif est de mettre en place un environnement hybride où l'éditeur, AGY (v1.2.7) et Google Chrome fonctionnent de manière simultanée.

### 2. CONTRAINTES DE MIDGARD
- **RAM Limite** : ~3 Go restants (7.6 Go total). Le budget alloué à l'éditeur est strictement plafonné à **500 Mo**.
- **Stockage Critique** : Disque mécanique (HDD). Toute mise en swap sur le disque entraîne un freeze du système (VS Code, JetBrains = proscrits).
- **Processeur / Graphique** : Intel i7 10e gen + NVIDIA MX130.

### 3. CONTEXTE GOOGLE AI STUDIO & FIREBASE
- **Sunset** : Firebase Studio s'arrête le **22 mars 2027**.
- **Stratégie** : Google réoriente vers Google AI Studio et des outils compatibles AGY.
- **Workflow** : Prototypage Cloud (Google AI Studio via Chrome) avec rapatriement local du code, puis orchestration locale avec AGY.
