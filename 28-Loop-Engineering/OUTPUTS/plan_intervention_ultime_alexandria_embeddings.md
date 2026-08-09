---
type: reference
tags: [curation/certified, curator/prime, status/valid]
coterie: tesla
date: 2026-07-11
author: tesla-curator-prime
confidence_score: 99%
sources: ["[[plan_intervention_alexandria_embeddings.md]]", "[[Plan_d_Intervention_By_RENA.md]]", "[[Plan_d_Intervention_By_Apodex.md]]", "[[Plan_d_Intervention_By_ChatGPT.txt]]"]
---

# CERTIFIED REPORT: PLAN INTERVENTION ULTIME ALEXANDRIA EMBEDDINGS

## 1. Diagnostic Summary

L'architecture sémantique actuelle d'Alexandria ([indexer_hybrid.py](file:///home/lord-mahonheim/bifrost/tesla/DataBase/Files/indexer_hybrid.py)) pose des risques matériels et financiers critiques sur MIDGARD (8 Go RAM, CPU pur). Son couplage avec `PyTorch`, `sentence-transformers` et `ChromaDB` (comprenant `onnxruntime`) consomme plus de 1,2 Go de RAM en veille et culmine à plus de 5,2 Go lors de l'indexation de lots volumineux. Cette dette technique fragilise le serveur de langage (`pyright` via `karellen-lsp-mcp`), provoquant des crashs répétés et bloquant la boucle d'auto-correction (Self-Healing). De plus, l'absence de cache local de déduplication et de politique stricte de confidentialité (PII/données confidentielles) expose le système à des fuites de données sensibles et à un gaspillage de quotas réseau lors des réindexations.

La transition vers une **architecture cloud-locale** s'appuyant sur l'API Gemini pour la génération d'embeddings et sur une unique base de données SQLite configurée en mode WAL (`alexandria_brain.db`) élimine totalement l'empreinte mémoire locale en veille tout en préservant la souveraineté et la rapidité des recherches locales.

Ce document constitue le **Plan d'Intervention Ultime** validé sous les principes du Vigilum Codex. Il fusionne les forces des plans d'intervention de **RENA (V2.1)**, **Apodex**, **ChatGPT** et de **Tesla (initial)** pour offrir le compromis le plus robuste, sécurisé et économe pour MIDGARD.

---

## 2. Verified Facts & Evidence Pack

### 2.1 Grille de Confrontation Objective des Plans

| Critère d'évaluation | Plan Initial Tesla | Plan RENA (V2.1) | Plan Apodex | Plan ChatGPT | **Plan Ultime Consolidé (Fusion)** |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Vision d'Infrarouge** | Validée. | Validée et durcie. | Validée. | Validée (90-95%). | **Consensus absolu sur la migration Cloud-Locale.** |
| **Doctrine llama.cpp** | Packaging temporaire. | Éphémère, subprocess, trap EXIT, ban de `llama-cpp-python`. | Idem RENA + doc `LLAMA_CPP_DOCTRINE.md`. | Packaging seul, pas de démon d'inférence. | **RENA + Apodex** : CLI subprocess éphémère sous `/tmp`, trap EXIT, doc de doctrine dédiée. |
| **Modèle d'embedding** | `text-embedding-004` (obsolète/maintenance). | `models/gemini-embedding-001` (dimension 768). | `models/gemini-embedding-001:768`. | Abstrait / Modulable (versionnable). | **Gemini-embedding-001 (768d)** configuré via abstraction `EmbeddingProvider` avec fallback possible. |
| **Format & Stockage** | BLOB SQLite. | BLOB Float32 normalisé L2 Little-Endian en SQLite WAL. | BLOB normalisé. | FLOAT32 BLOB ou sqlite-vec. | **RENA** : BLOB Float32 normalisé (L2) stocké en SQLite WAL (pas de JSON, évite les doublons). |
| **Recherche & Similarité** | Python pur / NumPy local. | FTS5 top 100 candidats BM25 + NumPy dot product (cosinus). | FTS5 top 100 + NumPy. | sqlite-vec (extension C). | **Double Vitesse** : NumPy local par défaut (Low-Code), sqlite-vec en option via abstraction. |
| **RRF Hybride k=60** | Conservé comme invariant. | Conservé (BM25 FTS5 + NumPy Cosine). | Conservé comme invariant. | Conservé. | **Invariant conservé** : fusion RRF (k=60) entre BM25 et score sémantique NumPy. |
| **Cache de Déduplication** | Cache SHA-256 demandé. | SHA256(text + model_version) implémenté (60-80% d'économie). | Cache validé. | SHA-256 recommandé. | **RENA** : Cache obligatoire basé sur `sha256(text + model_version)` pour éliminer les appels redondants. |
| **Confidentialité & RGPD** | Vague. | Gate `confidential:true` + PII Scrubber regex + FTS5-only. | Gate validée. | Absent. | **RENA** : Gate de Confidentialité (frontmatter YAML) + PII Scrubber (regex) pour exclure les données sensibles du cloud. |
| **Robustesse offline** | Rate limiting vague. | Batchs 96, retry exponentiel 3x, circuit breaker, queue SQLite. | Queue + FTS5-only en dégradé. | Absent. | **RENA + ChatGPT** : File d'attente SQLite `pending_embeddings`, circuit breaker réseau, recherche dégradée FTS5. |
| **Structure Base de Données** | Dénormalisée (duplication de texte). | Normalisée (4 tables : docs, chunks, registry, pending). | Idem RENA. | Sur-ingéniée (6 tables, metadata, sync_queue). | **RENA** : 4 tables minimales normalisées sous SQLite WAL. |
| **Gouvernance & SGC** | Mentionnée. | Intégration SGC + délégation `tesla-master-code`. | SGC, FORCE_TOOLING, double-copie MVP-GITHUB. | Benchmarks formels avant/après. | **Synthèse** : SGC 6 phases, benchmark Phase 0, double-copie MVP, validation LSP par `code-auditor`. |

### 2.2 Analyse Critique des Failles et Angles Morts

1. **Le Plan Initial de Tesla** :
   - *Forces* : Énonce correctement l'orientation stratégique globale et préserve l'invariant RRF k=60.
   - *Failles* : Présente un schéma relationnel dénormalisé où le texte brut est dupliqué entre les tables de chunks et le registre de vecteurs, gaspillant l'espace disque sur MIDGARD. Manque de rigueur sur la gestion du mode hors-ligne et l'organisation des tâches.
2. **Le Plan de RENA** :
   - *Forces* : C'est le plan le plus solide sur le plan de l'implémentation logicielle (batching, exponential backoff, circuit-breaker, structure SQL normalisée). La Gate de Confidentialité et le PII Scrubber en font le seul plan conforme aux exigences de sécurité du Vigilum Codex.
   - *Failles* : Rejette catégoriquement l'extension `sqlite-vec` sans prévoir de structure d'extension (abstraction) pour le cas où le corpus dépasserait un seuil de volumétrie critique (ex. >100k fragments), forçant un scan linéaire NumPy.
3. **Le Plan d'Apodex** :
   - *Forces* : Excellente structuration documentaire et focalisation sur la gouvernance (SGC, validation LSP, double-commit sur MVP-GITHUB). Propose la création formelle de la doctrine `LLAMA_CPP_DOCTRINE.md`.
   - *Failles* : Manque de profondeur technique propre ; il s'agit d'une reprise textuelle des choix de RENA sans valeur ajoutée algorithmique.
4. **Le Plan de ChatGPT** :
   - *Forces* : Apporte une excellente contribution architecturale en proposant l'interface `EmbeddingProvider` pour isoler SQLite de l'API de Google, ainsi qu'une séparation nette des pipelines d'indexation et de recherche pour simplifier les tests unitaires.
   - *Failles* : Propose initialement l'extension binaire `sqlite-vec` qui nécessite une compilation C sur l'hôte, violant la doctrine de simplicité de MIDGARD. Présente également un schéma SQL sur-ingénié à 6 tables difficile à maintenir.

---

## 3. Comparative Reasoning & Hypotheses

### 3.1 Arbitrage Technologique : sqlite-vec vs NumPy Local
L'utilisation de `sqlite-vec` (proposée par ChatGPT) permet des requêtes de similarité HNSW en C en moins de 2 ms, mais impose une compilation C spécifique et le chargement d'un binaire partagé (`.so`) au sein de SQLite, ce qui fragilise la portabilité et contredit la doctrine Low-Code.
À l'inverse, l'approche de RENA/Apodex réalise un pré-filtrage lexical via FTS5 pour remonter les 100 candidats les plus pertinents (BM25), puis effectue un calcul matriciel NumPy sur ces 100 vecteurs normalisés en moins de 0,3 ms. Le coût algorithmique O(N) sur toute la base est éliminé par la sélection lexicale préliminaire.

**Décision Validée (Double-Vitesse)** :
- **V3.0 (Actuelle)** : Utilisation de **FTS5 + NumPy local** (Low-Code, 0 dépendance binaire, stable et rapide).
- **V3.1 (Future/Optionnelle)** : Isolation du calcul vectoriel dans une classe `VectorSearchProvider`. Si le corpus dépasse 100k fragments et qu'une recherche purement vectorielle est requise, une implémentation `SqliteVecProvider` pourra être activée via la variable d'environnement `ENABLE_SQLITE_VEC=1` sans altérer l'indexeur sémantique.

### 3.2 Modularité de l'EmbeddingProvider
Pour éviter le verrouillage propriétaire (Vendor Lock-in) lié à l'API Gemini, le code d'appel réseau doit être encapsulé derrière une interface abstraite `EmbeddingProvider` :
- `GeminiEmbeddingProvider` (Actif par défaut, utilise le SDK officiel `google-genai`).
- `MockEmbeddingProvider` (Utilisé pour les tests unitaires et le mode offline).
- `VoyageEmbeddingProvider` (Extension future possible).

---

## 4. Contradictions & System Limits (AMDEC Shield)

| Défaillance Potentielle | Gravité (G) | Probabilité (P) | Détection (D) | RPN | Actions de Prévention & Mitigations |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **API Gemini Indisponible / Hors-ligne** | 4 | 3 | 1 | **12** | Stockage dans `pending_embeddings`. Bascule automatique en mode dégradé (FTS5 BM25 local uniquement). Reprise automatique via script cron/just. |
| **Dépassement de Quota API (Rate Limits)** | 3 | 3 | 2 | **18** | Traitement des requêtes d'indexation par batchs de 96, exponential backoff (retry exponentiel 3x) et circuit-breaker. |
| **Fuite de Clés API / Identifiants / PII** | 5 | 2 | 2 | **20** | PII Scrubber obligatoire analysant le texte par regex avant envoi. Exclusion des fiches marquées `confidential: true` de tout traitement Cloud. |
| **Incompatibilité de Dimension (Drift)** | 4 | 2 | 1 | **8** | Métadonnées stockées dans `vector_registry` (`model_version` et `dim`). Validation automatique de la dimension avant insertion. |
| **Consommation excessive RAM NumPy** | 2 | 2 | 2 | **8** | Limitation stricte du calcul cosinus au top 100 des candidats issus du pré-filtre FTS5 (limitation de la charge matricielle). |

---

## 5. Architectural Recommendations & Detailed Action Plan

### 5.1 Schéma SQLite Final Unifié (SQLite WAL)

Le schéma relationnel ci-dessous (normalisé, 4 tables) est configuré en mode WAL pour garantir des écritures concurrentes sécurisées et des transactions atomiques.

```sql
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

-- Table des documents importés
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY,
    path TEXT UNIQUE NOT NULL,
    mtime REAL NOT NULL,
    hash_doc TEXT NOT NULL,
    confidential INTEGER DEFAULT 0 -- 1 = Données sensibles isolées localement
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
    embedding BLOB NOT NULL, -- FLOAT32 BLOB normalisé L2 (Little-Endian, dimension 768)
    dim INTEGER NOT NULL DEFAULT 768,
    model_version TEXT NOT NULL DEFAULT 'gemini-embedding-001:768',
    hash_chunk TEXT NOT NULL,
    created_at REAL NOT NULL
);

-- File d'attente pour la gestion asynchrone des échecs d'appels API
CREATE TABLE IF NOT EXISTS pending_embeddings (
    chunk_id INTEGER PRIMARY KEY REFERENCES chunks(id) ON DELETE CASCADE,
    attempts INTEGER DEFAULT 0,
    last_error TEXT,
    next_retry_at REAL NOT NULL
);

-- Index pour accélérer la recherche et le nettoyage
CREATE INDEX IF NOT EXISTS idx_chunks_hash ON chunks(hash_chunk);
CREATE INDEX IF NOT EXISTS idx_vector_model ON vector_registry(model_version);
CREATE INDEX IF NOT EXISTS idx_docs_conf ON documents(confidential);
```

---

### 5.2 Spécification des Composants Logiciels

#### A. Le PII Scrubber (Gatekeeper)
Avant chaque envoi d'un fragment de texte à l'API Gemini, le module `PIIScrubber` doit exécuter un filtrage à base d'expressions régulières (regex) pour occulter les informations sensibles :
```python
import re

class PIIScrubber:
    PATTERNS = {
        "google_api_key": r"AIzaSy[a-zA-Z0-9\-_]{33}",
        "openai_api_key": r"sk-[a-zA-Z0-9]{48}",
        "github_token": r"gh[oprs]_[a-zA-Z0-9]{36,255}",
        "generic_secret": r"(?i)(password|secret|passwd|private_key)\s*[:=]\s*['\"][a-zA-Z0-9_\-\.\!\@\#\$]{8,}['\"]",
        "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        "jwt_token": r"eyJ[a-zA-Z0-9-_]+\.eyJ[a-zA-Z0-9-_]+\.[a-zA-Z0-9-_]+"
    }

    @classmethod
    def scrub(cls, text: str) -> str:
        scrubbed = text
        for name, pattern in cls.PATTERNS.items():
            scrubbed = re.sub(pattern, f"[REDACTED_{name.upper()}]", scrubbed)
        return scrubbed
```

#### B. La Gate de Confidentialité
Lors du parcours d'un fichier Markdown :
1. Analyser le frontmatter YAML du document.
2. Si le document contient le tag `confidential: true` ou `private: true`, ou si son chemin de fichier appartient au dossier protégé `/02-Areas/Confidentiel/` :
   - Assigner la valeur `1` à la colonne `confidential` de la table `documents`.
   - Indexer le texte du fragment uniquement dans l'index FTS5 local.
   - **Interdire strictement** tout appel à l'API Gemini pour ce fichier (pas d'insertion dans `vector_registry` ni dans `pending_embeddings`).

#### C. Cache de Déduplication Local
Pour optimiser les performances et la "Token Economy" :
1. Calculer `hash_chunk = sha256(text + model_version)`.
2. Interroger la base locale : `SELECT embedding FROM vector_registry WHERE hash_chunk = ? AND model_version = ?`.
3. Si le vecteur existe, l'insérer directement dans la table de destination liée au nouveau document, sans appeler le service Cloud.

#### D. Abstraction de l'EmbeddingProvider
```python
from abc import ABC, abstractmethod
import numpy as np

class EmbeddingProvider(ABC):
    @abstractmethod
    def generate_embeddings(self, texts: list[str]) -> list[np.ndarray]:
        """Génère une liste de vecteurs d'embeddings normalisés L2 pour une liste de textes."""
        pass
```

---

### 5.3 Pipelines d'Exécution

```
========================================================================================
                                PIPELINE D'INDEXATION
========================================================================================
 Fiche Markdown (*.md)
        │
        ▼
   Chunker Léger ──► [Si frontmatter confidential: true] ──► Indexation FTS5 Uniquement
        │ (1000 caract. / 200 overlap)                            (Marqué confidential=1)
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

---

### 5.4 La Doctrine llama.cpp (Usage Éphémère)

Pour prémunir MIDGARD de toute surcharge mémoire liée à l'exécution de démons résidentiels d'inférence, la toolchain `llama.cpp` doit obéir à la doctrine matérielle stricte formalisée dans le fichier [LLAMA_CPP_DOCTRINE.md](file:///home/lord-mahonheim/bifrost/tesla/DataBase/Files/LLAMA.CPP/LLAMA_CPP_DOCTRINE.md) :

1. **Interdiction d'Inférence Résidente** : Interdiction absolue de lancer `llama-server`, `llama-cli` en mode interactif, ou d'importer `llama-cpp-python` dans les scripts de production.
2. **Usage Unique / Outillage** : llama.cpp n'est autorisé que pour la conversion (HF en GGUF) et la quantification (Q4_K_M, Q8_0) de modèles.
3. **Workspace Éphémère Isolé** :
   - Chaque opération de quantification doit créer un dossier temporaire unique sous `/tmp/llama-pack-XXXX`.
   - Utilisation systématique de la commande `subprocess.run` pour appeler le binaire natif compilé localement `llama-quantize`.
   - Mise en œuvre d'un gestionnaire d'exception ou d'un `trap EXIT` en bash pour purger intégralement le dossier temporaire `/tmp/llama-pack-*` après exécution, même en cas d'erreur ou d'interruption.
   - Validation de l'intégrité de l'artefact quantifié en vérifiant la présence du header magique GGUF (`0x46554747` ou `GGUF` en ASCII).

---

### 5.5 Feuille de Route Opérationnelle (6 Phases - 7 jours)

#### Phase 0 : Benchmark & Diagnostic de Référence (Jour 1)
*   **Objectifs** : Capturer les performances physiques et la mémoire de l'ancien indexeur hybride (ChromaDB/Torch/sentence-transformers) pour documenter le gain de la migration.
*   **Actions** :
    1. Mesurer la RAM résidente de l'indexeur en état de veille (idle) et pendant l'indexation d'un lot témoin de 100 documents.
    2. Enregistrer la latence moyenne de recherche sémantique.
    3. Documenter ces métriques dans `/home/lord-mahonheim/bifrost/tesla/OUTPUTS/benchmark_midgard_before.md`.
*   **Recette de Validation (Phase 0)** : 
    - Le fichier de benchmark est créé et contient des données matérielles chiffrées réelles (RAM, CPU, temps).

#### Phase I : Refactorisation de l'Indexeur (Jours 2 - 3)
*   **Objectifs** : Éliminer les dépendances lourdes et développer la logique d'appel de l'indexeur cloud.
*   **Actions** :
    1. Supprimer `torch`, `sentence-transformers`, `chromadb` et `onnxruntime` du fichier `requirements.txt` et désinstaller les dépendances du `.venv`.
    2. Implémenter l'interface `EmbeddingProvider` et son implémentation `GeminiEmbeddingProvider` via le SDK `google-genai`.
    3. Intégrer le `PIIScrubber` et le cache de déduplication cryptographique (SHA-256).
*   **Recette de Validation (Phase I)** :
    - Exécution réussie de `pyright` via `karellen-lsp-mcp` démontrant 0 erreur d'importation.
    - Test unitaire validant le hachage SHA-256 et le masquage correct des secrets par le `PIIScrubber`.

#### Phase II : Migration SQLite & Recherche Hybride RRF (Jours 4 - 5)
*   **Objectifs** : Configurer la base de données relationnelle et mettre en place la fusion RRF.
*   **Actions** :
    1. Écrire et exécuter le script de migration `migrate_to_v2.py` pour créer les tables normalisées (`documents`, `chunks`, `vector_registry`, `pending_embeddings`).
    2. Mettre à jour `search_router.py` pour pré-filtrer via FTS5 (top 100), charger les BLOB de vecteurs correspondants, calculer la similarité cosinus avec NumPy et fusionner avec RRF (k=60).
*   **Recette de Validation (Phase II)** :
    - Exécution d'une recherche hybride test en moins de 50 ms pour un corpus d'au moins 1 000 fiches de test.
    - Vérification de la cohérence des dimensions (768) insérées dans SQLite.

#### Phase III : Formalisation llama.cpp & Outillage Éphémère (Jour 6 Matin)
*   **Objectifs** : Déployer le wrapper de quantification sécurisé et acter la doctrine.
*   **Actions** :
    1. Écrire le script `tools/quantize_model.py` utilisant `subprocess` sur le binaire `llama-quantize` local.
    2. Implémenter la création du dossier temporaire sous `/tmp/` et le nettoyage automatique via `trap EXIT` ou bloc Python `try...finally`.
    3. Rédiger le fichier de doctrine `/home/lord-mahonheim/bifrost/tesla/DataBase/Files/LLAMA.CPP/LLAMA_CPP_DOCTRINE.md`.
*   **Recette de Validation (Phase III)** :
    - Test de quantification d'un modèle minimal (ex: TinyLLaMA 110M) avec succès.
    - Vérification après exécution que le dossier temporaire `/tmp/llama-pack-*` a été entièrement détruit.

#### Phase IV : Tests de Résilience, Sécurité & Mode Dégradé (Jour 6 Après-midi)
*   **Objectifs** : Valider les verrous de sécurité et le fonctionnement en mode dégradé hors-ligne.
*   **Actions** :
    1. Injecter un document test contenant le tag `confidential: true` et vérifier qu'aucun appel réseau n'est émis.
    2. Simuler une coupure réseau (ou désactivation de la clé API) et vérifier la redirection des chunks vers `pending_embeddings` avec bascule immédiate en recherche FTS5 pure (mode dégradé sans crash).
    3. Exécuter un audit de code complet avec `tesla-code-auditor` (Semgrep et diagnostics LSP).
*   **Recette de Validation (Phase IV)** :
    - Validation par le Curator des traces d'audit montrant que 0 paquet IP n'a fuité pour les documents confidentiels.
    - Exécution sans erreur du moteur de recherche en mode dégradé (sans connexion internet).

#### Phase V : Certification, Alignement de la Mémoire & Clôture (Jour 7)
*   **Objectifs** : Finaliser le chantier, documenter l'architecture et synchroniser les dépôts.
*   **Actions** :
    1. Rédiger la documentation technique finale `ALEXANDRIA_V2_ARCHITECTURE.md` dans `Avalon/03-Resources/`.
    2. Mettre à jour les fichiers de la Mémoire Universelle : `memory/PROJECT_STATE.md`, `memory/SESSION_LOG.md` et `memory/liste_projets_antigravity_BASE.md`.
    3. Copier les nouveaux fichiers de code et de documentation vers le dépôt Git public `MVP-GITHUB/32-ALEXANDRIA-CLOUD-EMBEDDINGS/`.
    4. Exécuter le double commit et double push (avec autorisation expresse de Lord Mahonheim).
*   **Recette de Validation (Phase V)** :
    - Harmonisation complète du dossier `/memory/` vérifiée.
    - Commits Git locaux propres et statut Git `clean` sur le dépôt principal et MVP-GITHUB.

---
*Certified and signed on MIDGARD by Tesla Curator Prime.*
---
