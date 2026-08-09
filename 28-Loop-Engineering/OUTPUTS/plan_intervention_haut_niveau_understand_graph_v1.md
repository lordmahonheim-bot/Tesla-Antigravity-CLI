# Plan d'Intervention de Haut Niveau : Tesla-Understand-Graph

**Date** : 2026-07-10
**Statut** : 🟢 VALIDÉ & PRÊT POUR EXÉCUTION
**Cible** : Intégration souveraine et sécurisée d'Understand-Anything dans l'écosystème Antigravity CLI.

---

## 1. Objectif Souverain (Le Fork)

Création immédiate du dépôt `Tesla-Understand-Graph/` (sous `MVP-GITHUB/`).
**Interdiction absolue** d'importer l'orchestrateur natif (boîte noire 5-agents). L'outil est décapité de sa logique LLM d'origine pour ne conserver que son **moteur d'extraction déterministe** (Tree-sitter vers JSON). Toute la gouvernance s'effectue sur MIDGARD via nos agents d'élite.

## 2. Refonte Stratégique Budgétaire (Token-Economy v4.0)

Pour assurer la viabilité financière de l'analyse sémantique massive, le budget est rééquilibré selon le routage de capacités recommandé :
- **40% Gemini Flash** : Réservé à l'enrichissement sémantique "batch" de l'Agent `tesla-curator-prime` (Nœud N2). Le volume à bas coût.
- **40% Claude 3.5 Sonnet** : Réservé à l'architecture profonde, l'écriture du Wrapper LSP et l'intégration Loop Engineering (Nœuds N1 & N4).
- **20% GPT-4o** : Réservé à l'audit adversarial continu, le Premortem, et la réserve de sécurité d'exécution (Nœud N3).

## 3. Phasage d'Exécution

### PHASE I : Scaffolding & Extraction Statique (Moteur)
**Lead :** `tesla-master-code`
- Clonage partiel du code source original.
- Isolement chirurgical du module `tree-sitter` et du parseur syntaxique.
- **Livrable** : Script `graph_generator.py` produisant le `code_graph.json` brut, sans le moindre appel API externe.

### PHASE II : Blindage AMDEC (Bouclier)
**Lead :** `premortem` & `tesla-master-code`
- Implémentation d'un **Circuit Breaker** limitant le nombre de requêtes LLM/jour (Hard Limit).
- Mise en place du **Filtre Anti-OOM** : exclusion algorithmique des fichiers `> 2000 lignes`, fichiers `.min.*`, et verrous (locks).
- Approbation manuelle bloquante (`MAIN_RENDUE_A_MAHONHEIM=1`) pour tout refactoring dépassant 500 lignes.

### PHASE III : Routeur Sémantique & Alexandria (Second Cerveau)
**Lead :** `tesla-curator-prime`
- Création du script d'ingestion `understand_to_alexandria.py`.
- Injection du graphe JSON brut vers Gemini Flash pour vulgarisation et mapping des logiques métier.
- Écriture dans `alexandria_brain.db` (SQLite) et génération des notes interconnectées dans le vault Obsidian (Avalon).

### PHASE IV : Serveur LSP & Loop Engineering (L'Œil de Tesla)
**Lead :** `tesla-master-code`
- Enrobage de l'accès au Graphe via un serveur LSP local (ou extension de `karellen-lsp-mcp`).
- Intégration à la boucle de *Self-Healing* (Act-Verify-Learn-Repeat) : au lieu de relire le code de façon linéaire, les agents formuleront des requêtes `textDocument/references` pour interroger le graphe sémantique en O(1) cognitif.

---

## 4. Critères de Go-Live (Succès)

- Le pipeline s'exécute de bout en bout sur le dépôt cible sans violer le circuit breaker.
- La RAM du processus `tree-sitter` reste confinée `< 2 Go`.
- Le Graphe généré s'explore via LSP depuis un agent Antigravity CLI, prouvant la fin de la lecture linéaire forcée.
