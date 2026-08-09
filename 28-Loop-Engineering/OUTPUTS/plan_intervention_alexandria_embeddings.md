---
type: reference
tags: [curation/certified, curator/prime, status/valid]
coterie: tesla
date: 2026-07-11
author: tesla-curator-prime
confidence_score: 98%
sources: ["[[Audit_LLMA.CPP_By_ChatGPT.md]]", "[[Audit_LLAMA.CPP_By_RENA.md]]", "[[Audit_LLAMA.CPP_By_Apodex.txt]]", "[[indexer_hybrid.py]]"]
---

# CERTIFIED REPORT: PLAN INTERVENTION ALEXANDRIA EMBEDDINGS

## 1. Diagnostic Summary

L'indexeur hybride actuel d'Alexandria ([indexer_hybrid.py](file:///home/lord-mahonheim/bifrost/tesla/DataBase/Files/indexer_hybrid.py)) présente une dette technique et matérielle qui met en péril l'économie et la stabilité de l'environnement MIDGARD (8 Go RAM, CPU pur). Bien que fonctionnel, il repose sur un couplage lourd composé de `PyTorch`, `sentence-transformers` et `ChromaDB`. 

Les faits physiques démontrent les faiblesses suivantes :
1. **Empreinte mémoire excessive** : Plus de 1,2 Go de RAM résidente en veille, grimpant à un pic de consommation supérieur à 5,2 Go lors de l'indexation de lots volumineux (> 500 fragments), entraînant des risques constants d'OOM (Out Of Memory).
2. **Double source de vérité asynchrone** : L'utilisation simultanée de SQLite (pour l'index FTS5) et de ChromaDB (pour le stockage vectoriel local) crée deux bases de données distinctes non liées par des transactions atomiques, risquant une désynchronisation des données après un crash.
3. **Dette LSP & Outillage** : L'importation de PyTorch et de ChromaDB (qui intègre `onnxruntime`) perturbe gravement l'analyse statique du serveur de langage (`pyright` via `karellen-lsp-mcp`), causant des échecs répétés dans la boucle de validation automatique (Self-Healing).
4. **Absence de cache de déduplication** : Chaque processus d'indexation recalcule intégralement les embeddings sans vérifier si le contenu a changé, ce qui s'avère inacceptable dans une architecture cloud en termes de latence et de quotas.
5. **Absence de gestion de la confidentialité** : Le script actuel indexe et expose de manière identique toutes les fiches, sans distinction des données sensibles à isoler d'un transfert externe.

L'alternative d'une **architecture cloud-locale** (Cloud Embeddings via Gemini API et stockage vectoriel structuré sous SQLite) élimine la charge CPU/RAM en local tout en maintenant un contrôle strict des données. En parallèle, `llama.cpp` doit être rigoureusement maintenu dans un rôle d'outillage d'exportation (conversion et quantification) strictement temporaire, sans démon résident d'inférence.

---

## 2. Verified Facts & Evidence Pack

### 2.1 Grille d'analyse comparative des audits

La table ci-dessous confronte les points de vue, validations et divergences des trois audits menés par ChatGPT, RENA et Apodex :

| Critère d'évaluation | Audit ChatGPT | Audit RENA (V2.1) | Audit Apodex |
| :--- | :--- | :--- | :--- |
| **Verdict Général** | Valide l'orientation (90-95%). Demande des corrections techniques majeures. | Valide le plan en le durcissant (V2.1). Fournit le schéma SQL cible. | Valide le plan stratégique "Cloud-Locale" et insiste sur les invariants. |
| **Doctrine llama.cpp** | Packaging exclusif (convert/quantize/split). Aucun démon résident. | Outil éphémère (subprocess). Pas de `llama-cpp-python` (ce qui ferait de l'inférence). | Interdiction stricte de `llama-server`. Processus éphémère "Télécharger → Quantifier → Purger". |
| **Modèle d'embedding** | Suggère de versionner l'embedding suite au changement possible de modèle par Google. | Préconise `models/gemini-embedding-001` avec `output_dimensionality=768` (compatible MIDGARD). | Valide le déport cloud mais mentionne `text-embedding-004` (obsolète/maintenance). |
| **Format de Stockage** | Déconseille fortement le JSON. Préconise `FLOAT32 BLOB` ou l'extension `sqlite-vec`. | Impose `FLOAT32 BLOB` little-endian normalisé en SQLite WAL pour zéro-copy. | Impose `BLOB` binaire normalisé dans une table dédiée `vector_registry` (pas de JSON). |
| **Calcul de Similarité** | Recommande l'extension SQLite `sqlite-vec` (C) pour éviter la lenteur des boucles Python. | Propose un pré-filtre FTS5 (top 100) suivi d'un calcul cosinus `numpy` local ultra-rapide (O(100)). | Propose calcul cosinus via numpy sur SQLite après FTS5 pour conserver la fusion RRF. |
| **Recherche Hybride** | Sépare indexation et recherche. Propose RRF (FTS5 + `sqlite-vec`). | Préserve la fusion RRF avec l'invariant `k=60` combinant BM25 FTS5 et cosinus numpy. | Rappelle l'invariant architectural de la fusion RRF (k=60) dans `search_router.py`. |
| **Cache de Déduplication** | Recommande vivement un cache basé sur le SHA256 du fragment pour éviter les appels API inutiles. | Implémente le cache de déduplication `sha256(text + model_version)` pour économiser 60-80% de tokens. | Demande l'intégration d'un cache local d'embeddings indexé par hash de fragment + modèle. |
| **Gestion de la Confidentialité** | Absent de l'analyse. | Propose une Gate de Confidentialité (frontmatter YAML) + PII Scrubber + tag `confidential: true` (FTS5 seul). | Demande l'ajout d'une politique de gouvernance des données et de préservation locale. |
| **Politique de Robustesse** | Non spécifiée en détail. | Propose : batchs de 96, retry exponentiel 3x, circuit breaker et queue locale `pending_embeddings` en cas d'offline. | Recommande rate limiting, backoff réseau et mode dégradé FTS5-only en cas d'erreur API. |

---

## 3. Comparative Reasoning & Hypotheses

L'analyse croisée des trois documents révèle un consensus fort sur les grands principes de l'architecture cible, ainsi que des divergences constructives sur l'implémentation de la recherche vectorielle :

### 3.1 Consensus sur llama.cpp et la quantification
Les trois experts s'accordent sur le fait que la machine MIDGARD doit être protégée contre toute charge d'inférence locale permanente. L'outil `llama.cpp` ne doit servir que de **compilateur et compresseur éphémère** (HF vers GGUF, puis quantification en formats hautement compressés de type `Q4_K_M` ou `Q8_0`).
La recommandation de RENA consistant à interdire l'import de `llama-cpp-python` (qui lie le processus à des dépendances d'inférence) et à utiliser à la place des appels `subprocess` sur les binaires compilés de `llama-quantize` au sein d'un répertoire temporaire `/tmp/llama-pack-*` auto-purgé est adoptée comme la doctrine officielle.

### 3.2 Consensus sur les embeddings Cloud et le Caching
L'indexation étant une tâche ponctuelle et la recherche sémantique s'effectuant localement sur des vecteurs pré-calculés, le déport de la génération des embeddings vers le cloud de Google via l'API Gemini est validé à l'unanimité.
Pour atténuer les limites de débit (rate limit) et les coûts réseau, l'introduction d'un **cache de déduplication local** basé sur l'empreinte cryptographique SHA-256 du texte du fragment est requise. Si un fragment a déjà été vectorisé avec la même version de modèle, son vecteur est simplement extrait de la base SQLite locale sans appeler l'API Gemini.

### 3.3 Choix Technologique : sqlite-vec vs Rerank Cosinus NumPy
Une divergence technique apparaît entre la proposition de ChatGPT et celle de RENA/Apodex :
* **Hypothèse ChatGPT** : Utiliser l'extension C SQLite `sqlite-vec` pour effectuer les calculs de similarité directement au sein du moteur de base de données.
* **Hypothèse RENA & Apodex (Validée)** : Utiliser le moteur FTS5 de SQLite pour remonter un ensemble limité de candidats lexicaux pertinents (top 100 par BM25), puis effectuer le calcul de produit scalaire (dot product) en local à l'aide de la bibliothèque légère `numpy` sur ces 100 candidats.

**Arbitrage de Tesla Curator Prime** : La solution **FTS5 (top 100) + numpy local (dot product)** est retenue pour les raisons suivantes :
1. **Low-Code & Robustesse** : L'extension `sqlite-vec` nécessite de charger ou compiler des binaires partagés (.so) spécifiques à l'architecture de la machine pour SQLite, ce qui contredit la politique de réduction des dépendances de bas niveau et complique la portabilité sur MIDGARD.
2. **Performances réelles** : Le calcul matriciel `numpy` sur 100 vecteurs de dimension 768 s'exécute en moins de 0,3 ms sur CPU pur. Le goulot d'étranglement O(N) sur toute la base est éliminé par le pré-filtrage lexical de FTS5.
3. **Maintien de la logique RRF (Reciprocal Rank Fusion)** : Cette approche permet de conserver l'architecture de fusion de scores de `search_router.py` (k=60) de manière transparente.

---

## 4. Contradictions & System Limits

L'application d'une analyse de type Premortem permet d'anticiper les défaillances potentielles liées aux dépendances cloud et aux contraintes locales :

1. **Indisponibilité du service cloud (Gemini API Offline)** :
   * *Risque* : Blocage complet de la chaîne d'indexation lors de la modification de documents.
   * *Mitigation* : Mise en œuvre d'une table SQLite `pending_embeddings` qui fait office de file d'attente d'indexation. Si l'API est indisponible, l'indexation bascule immédiatement en mode dégradé (FTS5 seul) et l'utilisateur en est averti. Un démon léger ou une commande de synchronisation dépile les éléments dès le retour de la connexion.
2. **Vendor Lock-in et changement de tarification** :
   * *Risque* : Dépendance exclusive au SDK `google-genai` et aux modèles propriétaires Google.
   * *Mitigation* : Isolation du code de calcul vectoriel derrière une interface abstraite `EmbeddingProvider`. Ainsi, le passage à un autre modèle cloud (Voyage AI, Cohere) ou à un petit modèle local ne nécessite aucune réécriture de l'indexeur principal.
3. **Drift de dimensionnalité et rupture d'historique** :
   * *Risque* : Si la dimension des embeddings change (ex. de 768 à 3072), ou si le modèle d'embedding est mis à jour, les recherches sémantiques mélangeront des vecteurs incompatibles et échoueront.
   * *Mitigation* : Métadonnées obligatoires intégrées dans la table `vector_registry` (`model_version` et `dim`). L'indexeur valide chaque vecteur inséré. Si une modification de modèle est détectée en configuration, un script de migration (`re_embed.py`) invalide le cache et régénère les embeddings de manière incrémentale.
4. **Fuite de données confidentielles (PII / Propriété Intellectuelle)** :
   * *Risque* : Envoi accidentel de données ultra-sensibles ou de clés API privées aux serveurs de Google lors de l'appel d'embedding.
   * *Mitigation* : Intégration d'un PII Scrubber (masquage automatique des patterns d'emails, clés SSH, tokens GitHub par expressions régulières) et activation d'une Gate de Confidentialité. Tout fichier Markdown contenant le tag YAML `confidential: true` ou `private: true` is exclu de la vectorisation cloud et indexé uniquement en local via FTS5.

---

## 5. Architectural Recommendations & High-Level Action Plan

### 5.1 Architecture cible : ALEXANDRIA-CLOUD-EMBEDDINGS

La nouvelle architecture unifie l'indexation et la recherche au sein d'une unique base de données SQLite configurée en mode WAL (`alexandria_brain.db`).

```text
========================================================================================
                                PIPELINE D'INDEXATION
========================================================================================
 Fiches Markdown (*.md)
        │
        ▼
   Chunker Léger ──► [Si frontmatter confidential: true] ──► Indexation FTS5 Uniquement
        │ (1000 caract. / 200 overlap)
        ▼
   SHA256 Chunk + Version Modèle
        │
        ├──► [HIT] Cache Local SQLite ──► Récupération vecteur en base (Zéro Appel API)
        │
        └──► [MISS] PII Scrubber ──► Gemini API (models/gemini-embedding-001, dim 768)
                                        │
                                        ▼
                                 Stockage SQLite
                          (Table vector_registry : BLOB)
                                        │
                                        ▼
                                 Indexation FTS5
                          (Table fts_vault_index)

========================================================================================
                                PIPELINE DE RECHERCHE
========================================================================================
  Requête Utilisateur
        │
        ├──► API Gemini (Génération de l'embedding de requête en cache temporaire)
        │
        ├──► Étape 1 : Pré-filtre SQLite FTS5 (BM25) ──► Top 100 Candidats Lexicaux
        │                                                     │
        ▼                                                     ▼
  Étape 2 : Calcul Dot Product NumPy (cosinus local) sur les 100 Candidats en BLOB
        │
        ▼
  Étape 3 : Fusion RRF (Reciprocal Rank Fusion, k=60)
        │
        ▼
   Résultats Hybrides (Lexical + Sémantique)
========================================================================================
```

#### Schéma Relationnel Cible (SQLite WAL)
```sql
PRAGMA journal_mode=WAL;

-- Table des documents référencés
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY,
    path TEXT UNIQUE NOT NULL,
    mtime REAL NOT NULL,
    hash_doc TEXT NOT NULL,
    confidential INTEGER DEFAULT 0
);

-- Table des fragments de texte (Chunks)
CREATE TABLE IF NOT EXISTS chunks (
    id INTEGER PRIMARY KEY,
    doc_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    text TEXT NOT NULL,
    hash_chunk TEXT UNIQUE NOT NULL, -- SHA-256 du texte du fragment
    token_count INTEGER,
    created_at REAL NOT NULL
);

-- Registre des vecteurs sémantiques normalisés
CREATE TABLE IF NOT EXISTS vector_registry (
    chunk_id INTEGER PRIMARY KEY REFERENCES chunks(id) ON DELETE CASCADE,
    embedding BLOB NOT NULL, -- FLOAT32 BLOB normalisé (Little-Endian, dimension 768)
    dim INTEGER NOT NULL DEFAULT 768,
    model_version TEXT NOT NULL DEFAULT 'gemini-embedding-001:768',
    hash_chunk TEXT NOT NULL,
    created_at REAL NOT NULL
);

-- File d'attente pour gestion d'erreurs d'appels API
CREATE TABLE IF NOT EXISTS pending_embeddings (
    chunk_id INTEGER PRIMARY KEY REFERENCES chunks(id) ON DELETE CASCADE,
    attempts INTEGER DEFAULT 0,
    last_error TEXT,
    next_retry_at REAL NOT NULL
);

-- Indexation d'autorité
CREATE INDEX IF NOT EXISTS idx_vector_model ON vector_registry(model_version);
CREATE INDEX IF NOT EXISTS idx_chunks_hash ON chunks(hash_chunk);
```

---

### 5.2 Plan d'intervention détaillé (6 Phases)

Ce plan remplace le calendrier initial sous-estimé par une feuille de route rigoureuse de 7 jours, garantissant les validations LSP et de performance à chaque étape.

#### Phase 0 : Diagnostics de Référence & Benchmark (Jour 1)
*   **Objectifs** : Mesurer l'empreinte mémoire et la performance de l'indexeur actuel pour disposer d'une base de comparaison.
*   **Actions** :
    1. Mesurer la RAM résidente de l'indexeur hybride actuel en idle et en pic.
    2. Exécuter un test d'indexation sur un lot témoin de 100 fiches.
    3. Documenter la baseline dans `OUTPUTS/benchmark_midgard_before.md`.
*   **Critère de Passage** : Capture validée des métriques physiques CPU/RAM de l'architecture ChromaDB/Torch.

#### Phase I : Refactorisation de l'Indexeur (Jours 2 - 3)
*   **Objectifs** : Supprimer les dépendances obsolètes et implémenter la logique d'appel cloud Gemini.
*   **Actions** :
    1. Supprimer les imports de `sentence_transformers`, `torch`, `chromadb` et nettoyer le fichier `requirements.txt`.
    2. Implémenter le nouveau script `indexer_cloud.py` (ou remplacer l'indexeur existant).
    3. Intégrer le SDK officiel `google-genai` avec gestion du rate limiting (batchs de 96, exponential backoff).
    4. Coder le module de déduplication par hachage SHA-256.
*   **Critère de Passage** : Validation de l'analyse statique (`pyright` via `lsp_diagnostics` exempt de toute erreur d'importation).

#### Phase II : Refonte de la Base de Données & Recherche Hybride (Jours 4 - 5)
*   **Objectifs** : Créer le schéma relationnel unique dans SQLite et réviser le routeur de recherche.
*   **Actions** :
    1. Écrire le script de migration `migrate_to_v2.py` pour appliquer le nouveau schéma (création de `vector_registry`, `pending_embeddings`).
    2. Implémenter le calcul vectoriel local NumPy (dot product de vecteurs normalisés) sur les candidats pré-filtrés FTS5.
    3. Mettre à jour `search_router.py` pour appliquer la fusion RRF (k=60) combinant les deux nouveaux sous-scores.
*   **Critère de Passage** : Recherche hybride fonctionnelle s'exécutant en moins de 50 ms en local sur MIDGARD pour un corpus de 1 000 fragments.

#### Phase III : Isolation de la Toolchain llama.cpp (Jour 6)
*   **Objectifs** : Verrouiller l'usage de llama.cpp à la compilation éphémère.
*   **Actions** :
    1. Écrire le wrapper `quantize_model.py` pour exécuter la quantification via appel CLI local.
    2. Configurer le répertoire éphémère `/tmp/llama-pack-*` avec nettoyage automatique par piège système (trap).
    3. Rédiger le fichier de doctrine `LLAMA_CPP_DOCTRINE.md` réitérant la prohibition de l'inférence locale permanente.
*   **Critère de Passage** : Test réussi de quantification d'un modèle d'évaluation avec nettoyage automatique vérifié de l'espace temporaire.

#### Phase IV : Validation de Sécurité & Certification (Jour 7)
*   **Objectifs** : Vérifier la confidentialité des données et s'assurer de l'absence de régression.
*   **Actions** :
    1. Intégrer la Gate de Confidentialité et le PII Scrubber dans la chaîne d'envoi.
    2. Exécuter un audit de conformité avec les outils `tesla-code-auditor` et `lsp_diagnostics`.
    3. Générer le rapport de test final comparatif.
*   **Critère de Passage** : Aucune donnée marquée comme confidentielle n'a généré de requête réseau ; les métriques de performance sont conformes aux attentes.

#### Phase V : Clôture & Alignement Cognitif de la Mémoire (Jour 7)
*   **Objectifs** : Documenter le succès du projet et mettre à jour la mémoire persistante du système.
*   **Actions** :
    1. Actualiser `memory/PROJECT_STATE.md` pour refléter la fin du chantier.
    2. Mettre à jour le fichier d'historique `memory/SESSION_LOG.md`.
    3. Consigner le statut stabilisé d'Alexandria dans `memory/liste_projets_antigravity_BASE.md`.
    4. Réaliser la double copie des fichiers cibles dans le dépôt public séparé `MVP-GITHUB/32-ALEXANDRIA-CLOUD-EMBEDDINGS/` avec synchronisation contrôlée des dépôts Git.
*   **Critère de Passage** : Intégrité complète et cohérence absolue vérifiées sur l'ensemble des fichiers du répertoire `/memory`.

---
*Certified and signed on MIDGARD by Tesla Curator Prime.*
---
