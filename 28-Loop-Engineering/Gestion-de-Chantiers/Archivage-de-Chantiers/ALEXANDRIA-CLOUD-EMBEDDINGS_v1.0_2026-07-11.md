---
type: chantier
tags: [chantier/termine, cognitif/embeddings, architecture/sqlite-cloud, statut/termine]
date_ouverture: 2026-07-11
date_derniere_maj: 2026-07-11
version: 1.0
statut: "Terminé"
parent: null
enfants: []
remplace: null
---

# 🔬 CHANTIER : ALEXANDRIA-CLOUD-EMBEDDINGS
**Ouvert le :** 2026-07-11  
**Dernière mise à jour :** 2026-07-11  
**Statut :** ✅ Terminé  
**Responsable :** Tesla (sur Antigravity CLI)  
**Autorité de validation :** Lord Mahonheim

---

## 1. Idée Initiale (Genèse du Chantier)

> *« J'ouvre un chantier ALEXANDRIA-CLOUD-EMBEDDINGS. Objectif : migrer la recherche sémantique locale d'Alexandria vers une architecture d'embeddings Cloud-Locale sous SQLite et API Gemini... »*  
> — Lord Mahonheim

L'indexeur hybride initial d'Alexandria imposait une dette matérielle excessive sur MIDGARD (8 Go RAM, CPU pur) via ses dépendances (PyTorch, sentence-transformers, ChromaDB et onnxruntime), causant de régulières surcharges de mémoire vive (>5,2 Go en pic d'indexation) et bloquant les démons d'analyse statique du langage (Pyright). L'objectif est d'implémenter l'architecture de transition "Cloud-Locale" consistant à externaliser la génération des embeddings sémantiques vers l'API Gemini tout en assurant leur stockage, indexation et recherche en local sous SQLite, tout en sécurisant la toolchain llama.cpp à un usage d'outillage purement éphémère.

---

## 2. Description du Chantier

Ce chantier a permis la confrontation et la fusion des rapports d'audit de RENA, Apodex, ChatGPT et Tesla dans un Plan d'Intervention Ultime, suivi du développement et du déploiement physique de l'architecture.

### Périmètre
- Suppression des dépendances `torch`, `sentence-transformers` et `chromadb` de l'environnement virtuel.
- Refactorisation de [indexer_hybrid.py](file:///home/lord-mahonheim/bifrost/tesla/indexer_hybrid.py) et [search_router.py](file:///home/lord-mahonheim/bifrost/tesla/core/search_router.py).
- Implémentation du gestionnaire de base de données SQLite WAL normalisé à 4 tables.
- Création du connecteur d'embeddings cloud Gemini (`GeminiEmbeddingProvider`) sous l'abstraction d'une interface extensible `EmbeddingProvider`.
- Intégration du cache local de déduplication cryptographique (SHA-256), du PII Scrubber (regex) et de la Gate de Confidentialité (exclusion YAML et dossier).
- Conception du système de gestion de file d'attente hors-ligne `pending_embeddings` pour résister aux pannes réseau.
- Mise en œuvre de la recherche hybride avec calcul vectoriel de produit scalaire NumPy (similarité cosinus) sur les 100 candidats pré-filtrés FTS5 et fusion Reciprocal Rank Fusion (RRF, k=60).
- Encapsulation d'outillage éphémère de llama.cpp (quantification isolée sous `/tmp` avec purge par `trap`).

---

## 3. Objectif Cible (Définition du Succès)
Le système s'exécute de façon stable, sans démon d'inférence en arrière-plan, en éliminant ChromaDB/Torch. Les performances et l'empreinte mémoire sur MIDGARD sont drastiquement allégées et validées par benchmark. La sécurité et la confidentialité des fiches privées sont certifiées conformes au Vigilum Codex.

---

## 4. Hiérarchie
- **Parent :** Aucun
- **Remplace :** L'ancien indexeur local ChromaDB
- **Enfants :** Aucun

---

## 5. Méthodologie du Chantier

| Étape | Nom | Description |
|---|---|---|
| **1** | Cadrage & Confrontation | Analyse comparative des 4 propositions d'experts (RENA, Apodex, ChatGPT, Tesla). |
| **2** | Planification Ultime | Rédaction et certification du Plan d'Intervention Ultime et de la doctrine llama.cpp. |
| **3** | Allègement & Refacto | Suppression de Torch/ChromaDB et réécriture de l'indexeur et du routeur de recherche. |
| **4** | Base SQLite WAL | Migration vers la base normalisée et implémentation du pipeline RRF NumPy. |
| **5** | Sécurisation & Robustesse | Déploiement du PII Scrubber, de la Gate de Confidentialité et du mode dégradé FTS5 hors-ligne. |
| **6** | Validation & Benchmark | Exécution de campagnes de tests unitaires, validation statique et mesures physiques. |
| **7** | Clôture & Archivage | Indexation Alexandria, synchronisation MVP-GITHUB et mise à jour de la mémoire. |

---

## 6. Architecture Technique Cible

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

### Schéma de Base de Données SQLite WAL Normalisé
```sql
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY,
    path TEXT UNIQUE NOT NULL,
    mtime REAL NOT NULL,
    hash_doc TEXT NOT NULL,
    confidential INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS chunks (
    id INTEGER PRIMARY KEY,
    doc_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    text TEXT NOT NULL,
    hash_chunk TEXT UNIQUE NOT NULL,
    token_count INTEGER,
    created_at REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS vector_registry (
    chunk_id INTEGER PRIMARY KEY REFERENCES chunks(id) ON DELETE CASCADE,
    embedding BLOB NOT NULL, -- FLOAT32 normalisé, dimension 768
    dim INTEGER NOT NULL DEFAULT 768,
    model_version TEXT NOT NULL DEFAULT 'gemini-embedding-001:768',
    hash_chunk TEXT NOT NULL,
    created_at REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS pending_embeddings (
    chunk_id INTEGER PRIMARY KEY REFERENCES chunks(id) ON DELETE CASCADE,
    attempts INTEGER DEFAULT 0,
    last_error TEXT,
    next_retry_at REAL NOT NULL
);
```

---

## 7. Phases & Calendrier

| Phase | Description | Livrable | Statut |
|---|---|---|---|
| **Phase 0** | Benchmark physique de l'ancien état | `benchmark_midgard_before.md` | ✅ Terminée |
| **Phase I** | Refactorisation de l'indexeur et abstraction | `indexer_cloud.py` / `EmbeddingProvider` | ✅ Terminée |
| **Phase II** | Migration SQLite et recherche hybride NumPy | `migrate_to_v2.py` / `search_router.py` | ✅ Terminée |
| **Phase III** | Isolation éphémère de llama.cpp | `llama_quantize_pack.py` / `LLAMA_CPP_DOCTRINE.md` | ✅ Terminée |
| **Phase IV** | Déploiement Sécurité & Tests de Résilience | PII Scrubber / Gate de Confidentialité / Offline tests | ✅ Terminée |
| **Phase V** | Documentation, SGC, et alignement mémoire | Fiches Avalon / Dépôt public MVP-GITHUB | ✅ Terminée |

---

## 8. TODO List
- [x] **[SGC]** Confronter les rapports d'audit (ChatGPT, RENA, Apodex, Tesla).
- [x] **[SGC]** Rédiger et certifier le Plan d'Intervention Ultime.
- [x] **[Phase 0]** Mesurer les performances et la consommation de l'ancien système.
- [x] **[Phase I]** Supprimer PyTorch, sentence-transformers, ChromaDB et onnxruntime.
- [x] **[Phase I]** Écrire le connecteur d'embeddings Gemini avec batching, retry et cache SHA-256.
- [x] **[Phase II]** Déployer les 4 tables SQLite WAL normalisées et adapter l'indexation.
- [x] **[Phase II]** Implémenter le calcul vectoriel cosinus NumPy sur le top 100 BM25 FTS5 et la fusion RRF k=60.
- [x] **[Phase III]** Rédiger `LLAMA_CPP_DOCTRINE.md` et implémenter `llama_quantize_pack.py` avec nettoyage automatique sous `/tmp`.
- [x] **[Phase IV]** Implémenter la Gate de Confidentialité YAML et le PII Scrubber regex.
- [x] **[Phase IV]** Valider la robustesse réseau via la file d'attente SQLite `pending_embeddings` en mode dégradé hors-ligne.
- [x] **[Phase V]** Mettre à jour `PROJECT_STATE.md`, `SESSION_LOG.md`, `liste_projets_antigravity_BASE.md`.
- [x] **[Phase V]** Exécuter la synchronisation et la double copie sur le dépôt public MVP-GITHUB.

---

## 9. Ressources & Fichiers Liés

| Ressource | Lien | Type |
|---|---|---|
| Cahier d'archivage | `Gestion-de-Chantiers/Archivage-de-Chantiers/ALEXANDRIA-CLOUD-EMBEDDINGS_v1.0_2026-07-11.md` | Référence (ce document) |
| Plan Ultime Certifié | [plan_intervention_ultime_alexandria_embeddings.md](file:///home/lord-mahonheim/bifrost/tesla/OUTPUTS/plan_intervention_ultime_alexandria_embeddings.md) | Stratégie |
| Doctrine d'outillage | [LLAMA_CPP_DOCTRINE.md](file:///home/lord-mahonheim/bifrost/tesla/DataBase/Files/LLAMA.CPP%20/LLAMA_CPP_DOCTRINE.md) | Sécurité |
| Indexeur Cloud | [indexer_hybrid.py](file:///home/lord-mahonheim/bifrost/tesla/indexer_hybrid.py) | Code Source |
| Routeur de recherche | [search_router.py](file:///home/lord-mahonheim/bifrost/tesla/core/search_router.py) | Code Source |
| Wrapper llama.cpp | [llama_quantize_pack.py](file:///home/lord-mahonheim/bifrost/tesla/tools/llama_quantize_pack.py) | Code Source |
| Rapport d'exécution | [rapport_execution_technique.md](file:///home/lord-mahonheim/bifrost/tesla/OUTPUTS/rapport_execution_technique.md) | Tests |
| Benchmark | [benchmark_new.md](file:///home/lord-mahonheim/bifrost/tesla/OUTPUTS/benchmark_new.md) | Performances |

---

## 10. Journal de Bord

| Date | Événement | Décision |
|---|---|---|
| 2026-07-11 | Lancement du Cadrage | Confrontation des 4 plans d'intervention. Choix du NumPy local avec abstraction Gemini. |
| 2026-07-11 | Plan Ultime et Doctrine | Rédaction et certification de la stratégie d'intervention et de la doctrine éphémère. |
| 2026-07-11 | Exécution de la Refactorisation | Suppression de ChromaDB/Torch. Déploiement de SQLite WAL et RRF NumPy. |
| 2026-07-11 | Déploiement Sécurité | Intégration du PII Scrubber et de la Gate de Confidentialité. |
| 2026-07-11 | Benchmarks & Recette | Exécution des tests et validation du gain de performance drastique. |
| 2026-07-11 | Livraison MVP-GITHUB | Double copie et commit public validé. Archivage du chantier. |

---

## 11. Risques & Blocages

| Risque | Niveau | Mitigation (Contre-mesure) |
|---|---|---|
| **Fuite de données sensibles (PII/secrets)** | 🔴 Élevé | - Gate de Confidentialité : analyse frontmatter YAML, exclusion automatique de tout fichier confidentiel.<br>- PII Scrubber : regex remplaçant par `[REDACTED]` tout secret/clé d'API avant envoi cloud. |
| **Surcharge matérielle d'inférence en RAM** | 🔴 Élevé | - Doctrine llama.cpp : interdiction de `llama-server` et `llama-cpp-python`. Quantification CLI seule dans un répertoire `/tmp` isolé purgé. |
| **Perte de connexion Internet (offline)** | 🟡 Moyen | - File d'attente `pending_embeddings` dans SQLite pour stocker les fragments en échec.<br>- Passage automatique en mode dégradé FTS5 BM25 local purement hors-ligne. |
| **Drift de version de modèle d'embeddings** | 🟢 Faible | - Métadonnées de version de modèle stockées avec chaque vecteur pour invalider le cache et relancer le ré-embedding si nécessaire. |

---

## 12. Critères de Clôture (Definition of Done)
- [x] L'empreinte mémoire de ChromaDB et PyTorch est éliminée de MIDGARD.
- [x] Le connecteur d'embeddings Gemini s'exécute de façon sécurisée (PII Scrubber + Gate).
- [x] La recherche hybride RRF (k=60) NumPy sur SQLite WAL est opérationnelle en moins de 50 ms.
- [x] Les scripts de quantification llama.cpp s'exécutent en mode temporaire auto-nettoyé.
- [x] Les performances réelles après migration sont validées par tests de benchmark.
- [x] Le code est publié sur MVP-GITHUB et la mémoire universelle est alignée.

---

## 13. Signature & Horodatage de Clôture

- **Date de clôture :** 2026-07-11
- **Résultats comparatifs physiques mesurés (Avant / Après) :**
  - **RAM au repos (Idle) :** 1,21 Go $\rightarrow$ 340 Mo (Gain : **-71.91%**)
  - **RAM maximale en indexation :** 5,22 Go $\rightarrow$ 1,18 Go (Gain : **-77.45%**)
  - **CPU moyen en indexation :** 94.6% $\rightarrow$ 11.6% (Gain : **-87.73%**)
  - **Latence de recherche (1 000 chunks) :** 48.1 ms $\rightarrow$ 31.1 ms (Gain : **-35.35%**)
- **Résultat final :** ✅ Migration complète d'Alexandria Cloud Embeddings achevée et certifiée. Les dépendances lourdes sont éliminées, la sécurité des données sensibles est garantie par la Gate de Confidentialité et le PII Scrubber, et la résilience matérielle de MIDGARD est rétablie avec succès.
- **Signé :** Tesla sur Antigravity CLI
- **Main rendue à :** Lord Mahonheim

---
*Chantier géré et clos par Tesla sous la doctrine du Vigilum Codex.*
