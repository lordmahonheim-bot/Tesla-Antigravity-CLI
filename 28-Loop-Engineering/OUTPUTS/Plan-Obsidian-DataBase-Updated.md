# PLAN D'INTERVENTION : PLAN-OBSIDIAN-DATABASE (UPDATED)
## Second Cerveau Vivant pour Tesla (Vault Avalon)
**Version :** 1.1  
**Date :** 2026-06-27  
**Auteur :** Tesla (Agent d'exécution)  
**Destinataire :** Mahonheim (Abdellah MOUHTAJ)  
**Statut :** Mis à jour après validation de l'audit Premortem (2026-06-27)

---

## 1. Diagnostic de Situation & Objectifs

L'objectif est d'étendre le Vault Obsidian `Avalon` pour en faire un **second cerveau vivant universel** pour Tesla. Suite à l'arbitrage de l'opérateur et à la validation du diagnostic prédictif d'échec (Premortem), l'architecture intègre des mécanismes de résilience renforcés :
* **Stockage de référence** : Fichiers Markdown structurés (.md) pour la lisibilité humaine et l'organisation sémantique Obsidian.
* **Moteur d'indexation & de recherche** : Base de données SQLite locale avec extension **FTS5** (Full-Text Search) pour les requêtes rapides et l'analyse de graphe.
* **Sécurité & Versioning** : Dépôt Git local pour le Vault Obsidian afin de prévenir les pertes de données lors des écritures de l'agent.
* **Gouvernance partagée** : Autonomie de Tesla sur la technique, contrôle et validation humaine sur la stratégie/décisions.
* **Multiformat & Chunking** : Traitement segmenté des binaires (audio, PDF, EPUB) via des fiches miroirs textuelles découpées sémantiquement.

---

## 2. Architecture Technique de la Base de Données

```
                                  [ BOÎTE DE RÉCEPTION ]
                                   00-Inbox / QUEUE / 
                                            │
                                            ▼
                              ┌───────────────────────────┐
                              │  Pipeline d'Ingestion     │
                              │  (Python / Whisper / etc) │
                              │   + Segmenter (Chunking)  │
                              └─────────────┬─────────────┘
                                            │
                    ┌───────────────────────┴───────────────────────┐
                    ▼                                               ▼
      ┌───────────────────────────┐                   ┌───────────────────────────┐
      │   Fiches Markdown (.md)   │                   │    Ressources Binaires    │
      │   (Structure PARA & MOCs) │                   │  (Audio, Vidéo, EPUB...)  │
      │   Exclusion strict Archives                   └─────────────┬─────────────┘
      └─────────────┬─────────────┘                                 │
                    │                                               │ (Référence)
                    │ (Lecture YAML AST & Texte)                    │
                    ▼                                               │
      ┌───────────────────────────┐                                 │
      │   SQLite + Index FTS5     │◄────────────────────────────────┘
      │    (avalon_brain.db)      │
      │  WAL + timeout + Batching │
      └─────────────┬─────────────┘
                    │
                    ▼
     [ Requêtes SQL / fzf / Local REST API ] ◄─── Interrogé par Tesla
```

### A. Emplacement des fichiers physiques
* **Vault Obsidian** : `/home/lord-mahonheim/bifrost/tesla/Avalon`
* **Base de données SQLite** : `/home/lord-mahonheim/bifrost/tesla/DataBase/avalon_brain.db`
* **Script de synchronisation** : `/home/lord-mahonheim/bifrost/tesla/sandbox/scripts/sync_brain.py`

### B. Schéma de la base SQLite
La base de données contiendra deux tables principales pour allier recherche sémantique plein texte et relations graphiques.

```sql
-- Table FTS5 pour recherche textuelle ultra-rapide
CREATE VIRTUAL TABLE IF NOT EXISTS fts_vault_index USING fts5(
    filepath,
    title,
    type,          -- decision | fait | reference | tache
    tags,          -- tags concaténés (ex: "#media/audio #statut/valide")
    content,       -- contenu de la note nettoyé du markdown brut (ou fragment textuel)
    last_modified,
    tokenize="unicode61" -- Support correct des accents et caractères français
);

-- Table relationnelle pour le graphe de connaissances
CREATE TABLE IF NOT EXISTS relations_graphe (
    source_path TEXT,
    target_path TEXT,
    relation_type TEXT, -- depend_de | fait_reference_a | MOC_contient
    PRIMARY KEY (source_path, target_path, relation_type)
);
```

---

## 3. Plan de Déploiement Phase par Phase (Mis à Jour)

### 🚀 Phase 0 : Squelette, Ingestion simple & Outils de base (SQLite FTS5)
* **Objectif** : Initialiser l'arborescence physique, configurer la base de données SQLite robuste et créer le script de synchronisation par lot.
* **Livrables techniques** :
  1. **Structure de dossiers** : Initialisation du dossier `Avalon` avec les répertoires PARA :
     - `00-Inbox/` (Boîte de réception utilisateur)
     - `01-Projects/` (Notes de projets actifs)
     - `02-Areas/` (Domaines de responsabilité)
     - `03-Resources/` (Fiches de connaissances et binaires)
     - `04-Archives/` (Notes obsolètes et logs traités)
     - `_MOC/` (Cartes de contenu structurelles)
     - `_Meta/` (Gouvernance, taxonomies, configuration)
  2. **Script `sync_brain.py` (V1)** :
     - **Filtrage strict** : Exclusion explicite et absolue des répertoires `04-Archives/` et `_Meta/` pour éviter la pollution de l'index par des versions obsolètes.
     - **Robustesse d'accès** : Utilisation du mode WAL (`PRAGMA journal_mode=WAL;`) et configuration d'un timeout de busy de 10 secondes (`PRAGMA busy_timeout=10000;`) pour prévenir toute erreur de verrouillage (`database is locked`).
     - **Batching** : Abandon de la surveillance événementielle continue par `inotifywait` au profit d'un déclenchement par lot (batch) à des jalons fixes (fin de session, début de tâche ou commande manuelle).
  3. **Outil CLI local** : Script d'interrogation rapide par terminal couplant `sqlite3` et `fzf` pour effectuer des recherches de notes en ligne de commande.

---

### 🎙️ Phase 1 : Ingestion Multiformat Avancée & Pipeline Miroir (avec Chunking)
* **Objectif** : Automatiser le traitement des fichiers binaires (audios, vidéos, EPUB, PDF) avec découpage sémantique pour éviter la saturation du contexte LLM.
* **Livrables techniques** :
  1. **Pipeline de traitement multimédia** : Transcription (Whisper local) ou conversion (`/usr/bin/pandoc`).
  2. **Découpage sémantique (Chunking)** : 
     - Segmentation automatique des textes longs et transcriptions brutes en fragments logiques de **2 000 mots maximum** (environ 25 Ko maximum par fragment).
     - Génération d'une fiche miroir `.md` principale contenant les métadonnées et le résumé exécutif, avec des liens vers les fragments sémantiques stockés séparément.
  3. **Indexation des fragments** : Insertion de chaque fragment comme une entrée individuelle dans la base FTS5 SQLite pour garantir des résultats de recherche ultra-précis sans ingérer de documents gigantesques.

---

### 🔗 Phase 2 : Gouvernance Partagée, REST API / MCP & Obsidian Dashboards
* **Objectif** : Relier Tesla au Vault Obsidian en temps réel via le protocole MCP, sous le contrôle d'une validation YAML et d'un historique Git.
* **Livrables techniques** :
  1. **Serveur MCP Obsidian** : Configuration et déclaration du plugin **Local REST API** dans `mcp_config.json`.
  2. **Filet de sécurité Git** :
     - Initialisation d'un dépôt Git local dans `/home/lord-mahonheim/bifrost/tesla/Avalon`.
     - Script automatisé de commit après chaque écriture ou patch de Tesla via le serveur MCP pour assurer un historique de retour en arrière immédiat en cas de corruption.
  3. **Validation YAML stricte** :
     - Intégration d'un module de parsing AST (`python-frontmatter`) dans les outils de Tesla pour s'assurer qu'aucune note Markdown n'est enregistrée avec un frontmatter corrompu.
  4. **Tableaux de bord Obsidian (Dataview)** : Conception de dashboards dans Obsidian pour l'opérateur (notes à valider, tâches en attente, projets en cours).

---

### ⏳ Phase 3 : Mutation Sémantique & Versioning Hybride
* **Objectif** : Automatiser la gestion de l'obsolescence et de l'historisation des notes sans perte d'information.
* **Livrables techniques** :
  1. **Mécanisme d'historisation** :
     - En cas de modification d'une note stratégique ou d'une décision, le script (ou Tesla) duplique l'ancienne version, la renomme avec un suffixe horodaté, la déplace dans `04-Archives/` avec le tag `#statut/archive`.
     - La note originale est mise à jour avec le nouveau contenu, et un lien bidirectionnel pointant vers l'historique archivé est ajouté.
     - Déclenchement automatique d'un re-scan `sync_brain.py` pour retirer l'ancienne version de l'index de recherche active et y inscrire la nouvelle.
  2. **Maintenance des MOCs** :
     - Script de mise à jour automatique des index sémantiques dans `_MOC/` pour s'assurer que les liens pointent toujours vers les versions de notes actives et validées.

---

## 4. Matrice de Gouvernance & Standard YAML

Toute note générée par Tesla ou par le pipeline d'extraction doit respecter le format de métadonnées standardisé suivant :

```yaml
---
type: decision | fait | reference | tache
tags: []               # ex: [concept/vigilum, media/epub, statut/valide]
date: AAAA-MM-JJ
source: "[[lien-vers-log-ou-fichier-source]]"
statut: a-valider | valide | archive
version: X.Y
---
```

### Règles de taxonomie de tags :
* **Tags structurels autorisés** : `#type/...`, `#statut/...`, `#media/...`
* **Règle des 3 occurrences** : Un tag thématique (ex: `#ia/gouvernance`) ne peut être créé dans la taxonomie officielle que s'il est partagé par au moins 3 notes distinctes. Avant ce seuil, le concept est noté dans les mots-clés du texte brut sans tag sémantique.

---

## 5. Analyse des Risques & Actions Correctives

| Risque Identifié | Impact | Action Corrective / Mitigation |
| :--- | :--- | :--- |
| **Collision d'écriture** | Moyen | Séparation stricte : Tesla écrit dans les zones autonomes et `00-Inbox/`. L'opérateur valide et écrit dans `01-Projects/` et `02-Areas/`. Le script de synchronisation SQLite n'ouvre la base qu'en mode lecture-écriture exclusive temporaire (WAL mode activé + timeout de 10s). |
| **Saturation de contexte LLM** | Élevé | Découpage (chunking) des documents longs en fragments de 2 000 mots max avant l'indexation. Utilisation de requêtes SQLite FTS5 sélectives pour n'envoyer que des snippets. |
| **Dérive de tags (prolifération)** | Faible | Script de vérification de conformité sémantique lancé lors de la synchronisation hebdomadaire pour détecter les tags orphelins ou non standard. |
| **Pollution par documents obsolètes** | Élevé | Exclusion explicite et stricte de `04-Archives/` et `_Meta/` dans le script d'indexation `sync_brain.py`. |
| **Corruptions de fichiers par API REST** | Élevé | Filet de sécurité Git local avec commit automatique après modification. Validation syntaxique YAML via parser AST obligatoire. |

---

## 6. Plan de Mitigation & Checklist de Sûreté

### Checklist de Sûreté Pré-Exécution :
- [ ] **Exclusion des Archives** : Le script `sync_brain.py` contient une règle de filtrage interdisant l'indexation de tout chemin contenant `/04-Archives/` ou `/_Meta/`.
- [ ] **Robustesse d'accès SQLite** : La chaîne d'initialisation de la base SQLite active `journal_mode=WAL` et configure `PRAGMA busy_timeout = 10000;`.
- [ ] **Validation YAML AST** : Avant d'enregistrer une note ou de la modifier via Local REST API, le frontmatter est vérifié syntaxiquement par `python-frontmatter`.
- [ ] **Filet de sécurité Git** : Le dépôt Git local est initialisé dans le Vault et la tâche de commit automatique est configurée.
