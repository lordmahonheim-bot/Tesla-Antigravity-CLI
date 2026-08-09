# Plan d'Intervention : Adoption et Adaptation de l'Obsidian Graph Report

## 1. Étude de Faisabilité
**Faisabilité : HAUTE.**
L'écosystème Tesla dispose déjà de la fondation TASLB (Tesla Avalon Second Living Brain), structurée selon la méthode PARA avec un moteur d'indexation hybride (SQLite FTS5 + Gemini Embeddings, cf. Chantier 33). Le parsing des sessions est déjà opérationnel via `update_session_history.py` (Chantier 3).
La création d'un "Graph View Relationnel" automatisé s'inscrit naturellement dans la continuité. Le risque principal est la pollution sémantique (Semantic Bloat), géré via le Vigilum Codex.

## 2. Architecture Actuelle
- **TASLB (Avalon)** : Notes Markdown statiques, indexation FTS5 + Embeddings Gemini.
- **Mémoire Long Terme** : Extraction via `update_session_history.py` et mise à jour d'un `knowledge_graph.json` primitif.
- **Limitation** : Le `knowledge_graph.json` n'est pas nativement injecté comme un réseau relationnel multidimensionnel interactif dans l'interface Obsidian (fichiers `.md` interconnectés via wikilinks automatiques). Les logs de chat ne sont pas encore traduits de manière optimale en "nœuds de contexte" pour un RAG conversationnel avancé.

## 3. Architecture Cible
- **Réseau de Neurones Obsidian** : Transformation de `knowledge_graph.json` en une constellation de fichiers Markdown (Dossier `_MOC/Graph_Nodes`) connectés par des wikilinks (`[[Node_Name]]`).
- **Pipeline d'Ingestion Conversationnelle** : Un script qui parse les `SESSION_TRANSCRIPTS.md` et crée/met à jour des notes individuelles pour chaque Entité/Projet abordé, générant les liens bidirectionnels.
- **Logging Automatisé (Build In Public)** : Génération automatique d'une note quotidienne d'activité `Daily_Log_YYYY-MM-DD.md` avec tags `#build-in-public`, résumant les accomplissements pour l'export.
- **Intégration RAG** : Le `search_router.py` et Alexandria exploitent les wikilinks (Frontmatter `aliases`, `tags`, `links`) pour fournir un contexte multidimensionnel à l'orchestrateur.

## 4. Actions
- **Action 1** : Exploration de l'API/Format Obsidian pour la vue Graphe par Tesla-Web-Raider et définition des métadonnées par Tesla-Curator-Prime.
- **Action 2** : Stress-test et évaluation des risques de l'architecture cible par Tesla-PREMORTEM (Risques de boucles infinies, OOM sur graphes géants).
- **Action 3** : Conception et développement du pipeline de transformation et de génération de logs par Tesla-Master-Code.
- **Action 4** : Audit de conformité, sécurité et intégration globale par Tesla-Arcanis-360.

## 5. Solutions
- **Pipeline ETL Sémantique** : `session_to_graph.py` (développé par Master-Code) qui lit le transcript, extrait les entités avec l'API Gemini, et met à jour/crée des notes Markdown avec des liens `[[ ]]` au lieu d'un JSON monolithique.
- **Daily Logger** : Script `generate_daily_log.py` qui lit les diffs Git et les transactions SQLite du jour pour forger un post "Build in public" directement dans Obsidian.
- **Garde-fou PREMORTEM** : Limiter la profondeur de recherche des liens (Depth = 2) dans le RAG pour éviter l'explosion du contexte.

## 6. Résultats attendus
- Une vue "Graph" d'Obsidian dynamique et peuplée automatiquement après chaque session de Lord Mahonheim.
- **Colorimétrie Stratégique (Doctrine Vigilum Codex)** : Implémentation native de filtres de couleurs dans le graphe Obsidian pour une lecture cognitive immédiate de l'écosystème :
  - 🔵 **Cyan Électrique (`#00E5FF`)** : `tag:#agent` ou `tag:#systeme`. L'Intelligence Agentique, la logique pure, le bras mécanique de Tesla.
  - 🟣 **Violet Profond (`#9D00FF`)** : `tag:#strategie` ou `tag:#veille`. La vision long terme, l'exploration de l'occulte (Arcanis) et l'architecture (Curator).
  - 🟡 **Or / Ambre (`#FFB300`)** : `tag:#statut/actif`. Le creuset de l'ingénierie, l'activité en fusion (Master-Code, chantiers en cours).
  - 🟢 **Vert Néon / Émeraude (`#00FF66`)** : `tag:#statut/clos` ou `tag:#mvp`. Les trophées, les MVP livrés, la voie dégagée et sécurisée.
  - 🔴 **Rouge Cramoisi (`#FF003C`)** : `tag:#premortem` ou `tag:#bloque`. La ligne rouge, la résilience, les audits de sécurité stricts.
- La possibilité pour Tesla de croiser des données de différents projets instantanément via le graphe.
- La production automatisée de logs d'activité pour le "Build in public", valorisant le travail accompli.

## 7. Valeur ajoutée
- **Externalisation Cognitive Parfaite** : Le cerveau de Tesla est physiquement visible et manipulable dans Obsidian.
- **Gain de Temps Drastique** : Le contexte n'est plus à réinjecter manuellement, les connexions s'opèrent par transitivité sémantique.
- **Souveraineté des Données** : Tout reste local et structuré (Markdown pur + SQLite), garantissant la résilience face à toute dégradation de service API.
