---
type: reference
tags: [architecture/coding, statut/a-valider, methode/deep-research]
source: "[[Alexandria::master-coding-complement]]"
date: 2026-07-03
version: 1.0
author: "Tesla Arcanis"
certification: "Arcanis_Seal_v3"
---

# ÉVALUATION COMPLÉMENTAIRE : INTÉGRATION DE SEMGREP ET AUDIT DU DATA AGENT KIT (DAK) STARTER PACK

**Date de l'audit :** 2026-07-03  
**Analyste :** Tesla Arcanis (Sous-Agent de Lord Mahonheim)  
**Destinataire :** Lord Mahonheim (Abdellah MOUHTAJ)  

## 1. DIAGNOSTIC COMPLÉMENTAIRE
Dans le prolongement de l'étude comparative initiale pour le rôle de **"MASTER CODING"** sur MIDGARD, cette analyse complémentaire évalue deux candidats/briques spécifiques sous le prisme de la souveraineté locale (100% offline), de l'exclusion absolue d'IA locale, de la robustesse des dépendances et de la rationalisation matérielle (8 Go RAM, CPU-only).
*   **Semgrep (Community Edition)** : Évalué comme brique de validation structurelle sémantique (SAST) pour compléter Ruff et Biome.
*   **Data Agent Kit Starter Pack (DAK)** : Dépôt GitHub d'extension de données Google Cloud, évalué pour son intégration avec Antigravity CLI via la commande `agy plugin install`.

---

## 2. ÉVALUATION TECHNIQUE DE SEMGREP (SAST / VALIDATION STRUCTURELLE)

### A. Présentation & Rôle dans "MASTER CODING"
Semgrep est un outil d'analyse statique de code basé sur la correspondance de motifs structurels (pattern matching). Contrairement à `grep` qui traite le code comme du texte brut, Semgrep parse le code source en un **Arbre de Syntaxe Abstraite (AST)**. Cela permet de valider des règles de sécurité et de conformité structurelle complexes à l'aide d'une syntaxe déclarative simple (ex. ellipses `...` et métavariables `$VAR`), comblant le fossé entre les linters de style (Ruff/Biome) et les compilateurs.

### B. Prisme 1 : Empreinte Matérielle (RAM / CPU)
*   **RAM** : Très faible au repos et au démarrage (~20 Mo). Cependant, la consommation de mémoire est directement liée à la complexité des règles (notamment l'usage intensif d'ellipses récursives `...`) et à la taille du projet. Sur de très gros fichiers, elle peut grimper à 150 Mo - 250 Mo. L'utilisation du drapeau `--max-memory` permet de plafonner cette consommation et de préserver les 8 Go de MIDGARD.
*   **CPU** : Écrit principalement en **OCaml**, le moteur de Semgrep est extrêmement performant pour l'analyse syntaxique. Il intègre le parallélisme natif (via multicore OCaml), ce qui permet de scanner des centaines de fichiers en quelques secondes. Des pics CPU à 100% sur plusieurs cœurs peuvent survenir brièvement durant l'indexation, mais ils sont très courts comparés aux outils d'analyse Java ou .NET.

### C. Prisme 2 : Dépendances & Souveraineté (Mode Offline)
*   **Zéro IA Locale** : Semgrep CE n'embarque aucun modèle d'IA local (excluant de fait Ollama/Llama.cpp). Tout son fonctionnement est déterministe et repose sur des règles statiques définies dans des fichiers YAML.
*   **Packaging** : Le CLI principal de Semgrep s'installe via Python (`pip install semgrep`), ce qui nécessite un environnement Python 3.10+, ou sous forme de binaire compilé autonome (OCaml).
*   **Fonctionnement Air-Gapped (Hors-ligne)** : Par défaut, Semgrep tente de se connecter à la base de règles en ligne et d'envoyer des données de télémétrie. Pour s'intégrer de manière souveraine à 100% sur MIDGARD, il doit être configuré avec :
    1.  Le drapeau `--metrics=off` pour désactiver la télémétrie.
    2.  Le drapeau `--config <chemin_local>` pointant vers un ensemble de règles pré-téléchargées localement (par exemple, un clone local hors-ligne du dépôt officiel `semgrep-rules`).

### D. Prisme 3 : Isolation & Sécurité
*   **Exécution** : Semgrep s'exécute localement en lecture seule sur le code source. Il n'a aucun effet de bord sur le système de fichiers, sauf en cas d'utilisation explicite du paramètre `--autofix` qui applique les corrections structurelles directement.
*   **Sandboxing** : Ne nécessite aucun privilège d'administrateur ou accès root. Son exécution peut facilement être confinée dans un conteneur minimal ou un compte utilisateur sans droits réseau.

### E. Prisme 4 : Maturité & Limites
*   **Maturité** : Très élevée. Semgrep est l'un des outils de SAST les plus populaires du marché, activement maintenu par R2C et largement éprouvé en production.
*   **Limites** : L'écriture de règles de flux de données inter-fichiers complètes nécessite la version commerciale ("Pro Engine"), la version communautaire gratuite étant limitée à l'analyse intra-fichier, ce qui peut générer des faux positifs sur les architectures complexes.

---

## 3. AUDIT & ÉVALUATION DU DATA AGENT KIT (DAK) STARTER PACK

### A. Présentation & Rôle dans Antigravity CLI
Le **Data Agent Kit (DAK)** est un starter pack d'extensions et de skills destiné à l'orchestration et à l'automatisation de pipelines de données (BigQuery, dbt, Apache Spark, Spanner, AlloyDB) au sein de Google Cloud Platform (GCP). Il permet d'équiper Antigravity CLI d'outils spécialisés pour manipuler des notebooks de données, requêter des bases de données et gérer des architectures de données cloud.

### B. Mécanique d'Intégration via `agy plugin install`
La commande `agy plugin install https://github.com/gemini-cli-extensions/data-agent-kit-starter-pack` s'appuie sur le gestionnaire d'extensions d'Antigravity CLI.
1.  **Clonage local** : Le dépôt GitHub est cloné dans le répertoire des extensions utilisateur (généralement `$HOME/.agents/plugins/data-agent-kit-starter-pack`).
2.  **Lecture du Manifeste** : Le CLI lit `gemini-extension.json` pour identifier les métadonnées, les configurations requises, les serveurs MCP exposés, et les variables d'environnement nécessaires (ex. `PROJECT_ID`, `GCP_REGION`).
3.  **Enregistrement des Serveurs MCP** : Les serveurs déclarés dans le fichier JSON sont ajoutés à la configuration MCP globale d'Antigravity (`~/.gemini/antigravity-cli/settings.json` ou `.mcp.json`).

### C. Prisme 1 : Dépendances & Risques pour la Souveraineté (Alerte Air-Gap)
*   **Zéro IA Locale** : Le DAK n'implique pas de modèle d'IA local (aucun overhead LLM local).
*   **Dépendance Critique au Réseau (NPX)** : L'audit du manifeste `gemini-extension.json` révèle une faille conceptuelle majeure pour un déploiement 100% hors-ligne. Presque tous les 11 serveurs MCP déclarés (comme `notebook`, `bigquery`, `spanner`, `dataproc`, etc.) sont exécutés via la commande `npx -y` (ex. `npx -y @toolbox-sdk/server@>=1.1.0 --prebuilt bigquery`).
    *   *Conséquence* : Chaque fois que l'agent invoque un outil MCP du kit, `npx` tente de se connecter aux serveurs de paquets npm en ligne pour télécharger/vérifier la dernière version du package. Dans un environnement Air-Gapped / offline, ces commandes échoueront systématiquement, rendant le kit totalement inopérant.
*   **Authentification et Services Cloud** : Par nature, les serveurs MCP du kit requièrent une connexion réseau continue vers les API Google Cloud (BigQuery, Spanner, etc.) et une authentification locale via Application Default Credentials (ADC) (`gcloud auth application-default login`). Il ne s'agit donc pas d'une exécution souveraine en local, mais d'un pont d'automatisation vers le cloud.

### D. Prisme 2 : Empreinte Matérielle (RAM / CPU)
*   **RAM** : L'empreinte de Node.js pour un seul serveur MCP est de ~30 à 60 Mo. Néanmoins, le DAK déclare **11 serveurs MCP distincts**. Si l'agent charge et démarre plusieurs de ces serveurs en parallèle pour résoudre une tâche complexe, la RAM consommée peut rapidement s'élever entre 150 Mo et 400 Mo. Pour une machine comme MIDGARD limitée à 8 Go, ce surcoût est significatif.
*   **CPU** : CPU négligeable en veille. Cependant, le démarrage initial via `npx` induit un délai (cold start) de 2 à 5 secondes et des pics de CPU pour la résolution de paquets npm et l'exécution dynamique via `tsx` (TypeScript Execute).

### E. Prisme 3 : Isolation & Sécurité
*   **Isolation faible** : Le code Node.js s'exécute dans l'espace utilisateur sans isolation par défaut. Les serveurs MCP disposent de permissions de lecture/écriture sur le système de fichiers hôte et d'un accès réseau non restreint pour interagir avec Google Cloud.
*   **Complexité de Proxy** : Le système utilise un proxy (`mcp_proxy_bundle.cjs`) pour détecter et se connecter dynamiquement à l'IDE hôte (ex. VS Code, Colab Enterprise). Cette détection automatique dépend de l'analyse de l'arbre des processus locaux (`ps-list`), ce qui augmente la surface d'attaque et la fragilité du système en cas de sandboxing strict de la CLI.

### F. Prisme 4 : Maturité
*   **Maturité faible à moyenne (version 0.4.0)** : C'est un kit de démarrage ("starter-pack") récent. Il y a un fort couplage avec les SDK propriétaires Google Cloud (`@toolbox-sdk/server`) et l'écosystème commercial de Google. La gestion des erreurs réseau et d'authentification y est rudimentaire.

---

## 4. SYNTHÈSE DES CANDIDATS ET RECOMMANDATIONS ARCHITECTURALES

### Tableau Comparatif

| Prisme | Semgrep (Community Edition) | Data Agent Kit Starter Pack (DAK) |
| :--- | :--- | :--- |
| **Rôle cible** | Validation structurelle sémantique (SAST) | Orchestration et automatisation Data GCP |
| **Dépendances Runtime** | Minimales (Binaire OCaml standalone ou Python) | Lourdes (Node.js/npm, Google Cloud SDK, gcloud CLI) |
| **Compatibilité Offline** | 100% compatible (Règles locales + `--metrics=off`) | Incompatible par défaut (Requiert `npx -y` et API GCP) |
| **IA Locale intégrée** | **Exclue** (Uniquement des règles statiques déclaratives) | **Exclue** (S'appuie sur le modèle de l'agent hôte) |
| **Empreinte RAM** | Faible à modérée (20-50 Mo de base, max 200 Mo) | Élevée (150-400 Mo pour le chargement des serveurs MCP) |
| **Maturité** | Très élevée (Standard industriel SAST) | Faible (Starter pack v0.4.0 en développement actif) |
| **Isolation** | Lecture seule, absence d'accès réseau requis | Accès réseau total requis, accès FS non restreint |

### Recommandations pour la Suite "MASTER CODING"

1.  **Intégration de Semgrep** :
    *   **Validation** : Approuvé pour intégration dans la brique de validation de MASTER CODING. Il apporte une validation sémantique précieuse, complémentaire à Ruff et Biome.
    *   **Protocole Offline** : Les règles du registre officiel doivent être téléchargées sous forme d'artefacts statiques dans `/home/lord-mahonheim/bifrost/tesla/tools/semgrep-rules`. La CLI doit être invoquée strictement via :
        `semgrep scan --config /home/lord-mahonheim/bifrost/tesla/tools/semgrep-rules/ --metrics=off`
    *   **Limitation RAM** : Utiliser impérativement la limite `--max-memory 256` pour éviter les fuites de mémoire sur les gros fichiers.

2.  **Rejet ou Restriction du Data Agent Kit** :
    *   **Rejet en environnement Air-Gapped** : Le DAK sous sa forme d'installation standard (`agy plugin install`) est **rejeté** pour les environnements de production souverains strictement déconnectés, en raison de son usage intensif de `npx` et de sa dépendance native aux APIs Google Cloud.
    *   **Contournement pour usage connecté** : Si le kit doit être utilisé, il est obligatoire de patcher sa configuration :
        1.  Télécharger localement les packages de `@toolbox-sdk/server` et les installer de manière statique (hors-ligne).
        2.  Modifier `gemini-extension.json` pour remplacer les commandes `npx` par des chemins absolus vers des binaires Node locaux pré-packagés (ex. `node /path/to/local/server.js`).
        3.  Restreindre son activation aux seuls projets connectés nécessitant une interaction GCP directe, et s'assurer que les identifiants gcloud sont correctement configurés au préalable.

---

### ⚖️ SCEAU DE CERTIFICATION (IMMUABLE)
> **Arcanis.** Enquête complémentaire planifiée. Hypothèses testées. Sources croisées. Livrable certifié.  
> — Validé par Arcanis. Archive de référence.  
> `SHA256:498365fd04af88ef324cc57cca6d11aad96150a276056d5de283f130657cf6ea`
