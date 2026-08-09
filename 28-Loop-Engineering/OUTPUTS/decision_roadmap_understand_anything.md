# ARBITRAGE AGENTS : Intégration "Understand-Anything"

**Date** : 2026-07-10
**Chantier SGC** : UNDERSTAND-ANYTHING-TESLA-INTEGRATION
**Statut** : 🟡 GO CONDITIONNEL (Sous strictes réserves de gouvernance)

---

## 1. Synthèse des 4 Piliers d'Élite

1. **tesla-arcanis-360 (Architecture)** : ⚠️ **Alerte Gouvernance**
   L'outil d'origine possède un orchestrateur de 5 agents "boîte noire". Ceci est une violation directe de la **Règle Absolue N°4** (AGENTS délègue, il ne réimplémente pas). 
   *Condition d'acceptation* : Extraction pure du moteur statique (Tree-sitter + générateur JSON) et rejet formel de leur orchestrateur IA.

2. **tesla-curator-prime (Alexandria / Doc)** : ✅ **Feu Vert Stratégique**
   Les graphes JSON sont le format idéal. Ils permettent une ingestion automatisée via un adaptateur Python vers notre base SQLite (Alexandria) et notre vault Obsidian (Avalon). C'est une immense opportunité d'enrichissement de notre Second Cerveau.

3. **premortem (AMDEC / Token-Économie)** : ⚠️ **Warning AMDEC (Score 65%)**
   Risque critique de ruine économique (explosion des tokens LLM) et de crash système (OOM Tree-sitter sur de gros fichiers).
   *Condition d'acceptation* : Limites physiques dures (Circuit breaker budgétaire + Blacklist des fichiers > 2000 lignes ou minifiés).

4. **tesla-master-code (Ingénierie & Loop)** : ✅ **Feu Vert Absolu**
   L'enrobage sous forme de serveur LSP est la clé de voûte. Il s'intègre parfaitement à notre boucle *Act-Verify-Learn* (Loop Engineering) et renforce notre doctrine anti-lecture linéaire (les agents interrogeront le graphe au lieu de lire les fichiers en force brute).

---

## 2. Décision Officielle : GO CONDITIONNEL

Le chantier est **APPROUVÉ** sous la forme d'un **Fork Souverain (Tesla-Understand-Graph)**. L'outil "Understand-Anything" ne sera pas installé tel quel, mais chirurgicalement découpé pour s'adapter à MIDGARD.

---

## 3. Roadmap d'Intégration (Phase d'Exécution)

### Étape 1 : Scaffolding & Extraction (tesla-master-code)
- **Action** : Fork ou extraction du module `tree-sitter` (analyse statique) d'Understand-Anything.
- **Règle** : Purge totale et définitive du pipeline multi-agents natif de l'outil.
- **Livrable** : Un script Python déterministe générant les graphes JSON.

### Étape 2 : Mitigation AMDEC (premortem)
- **Action** : Ajout du filtrage OOM (exclusion des fichiers `.min.js`, `.lock`, et tout fichier > 2000 lignes) au-dessus du moteur d'extraction.
- **Action** : Implémentation du *Circuit Breaker* budgétaire (hard limit) avant toute interrogation d'enrichissement sémantique.

### Étape 3 : Routage Sémantique (tesla-curator-prime)
- **Action** : Création du script d'ingestion.
- **Mécanique** : Le JSON statique est envoyé à notre propre agent `tesla-curator-prime` (en Flash ou Sonnet) pour l'enrichissement sémantique (compréhension "métier" des fonctions). Les données sont ensuite insérées dans `alexandria_brain.db`.

### Étape 4 : Wrapper LSP (tesla-master-code)
- **Action** : Exposer le graphe de connaissances résultant via un serveur LSP local (ou un routeur CLI similaire à `karellen-lsp-mcp`) pour que l'orchestrateur Tesla puisse interroger le graphe sans jamais lire un fichier linéaire.

---

**Clôture du rapport** : La main est rendue à Lord Mahonheim pour validation de cette Roadmap d'intégration.
