---
type: reference
tags: [securite/plan-intervention, statut/valide]
source: "[[DB-SUBAGENTS-SKILLS_v1.2_2026-07-03.md]]"
date: 2026-07-03
version: 1.0
author: "Tesla Arcanis"
certification: "Arcanis_Seal_v3"
---

# PLAN D'INTERVENTION TECHNIQUE CONSOLIDÉ : INTÉGRATION DE LA BASE DB-SUBAGENTS-SKILLS
**Date de rédaction :** 2026-07-03  
**Auteur :** tesla-arcanis (Sous-Agent d'Élite Tesla)  
**Destinataire :** Lord Mahonheim (Abdellah MOUHTAJ)  

## 1. Contexte & Architecture Cible
Ce document détaille le plan d'intervention pour la réalisation technique du chantier **DB-Subagents-Skills**. Il intègre les contre-mesures strictes identifiées lors de l'audit de résilience Premortem pour garantir l'absence de corruption de données, de blocages concurrents ou de boucles infinies de parsing sur l'environnement MIDGARD.

L'objectif est d'ajouter à la base [alexandria_brain.db](file:///home/lord-mahonheim/bifrost/tesla/Avalon/03-Resources/alexandria_brain.db) un sous-système de suivi relationnel pour :
1. L'historique d'exécution des sessions de sous-agents (tokens, durée, hiérarchie).
2. L'historique sémantique des tâches et retours (Diagnostics, Actions, Preuves).
3. Le suivi du Shadow-Targeting (compétences injectées dans les sous-agents par défaut du plan Pro d'Antigravity CLI).

---

## 2. Spécification du Schéma SQL de Résilience

Le schéma SQL ci-dessous doit être exécuté de manière idempotente sur la base SQLite `alexandria_brain.db`. Il inclut des contraintes d'intégrité strictes, des index optimisés et des paramètres de sécurité par défaut.

```sql
-- ====================================================================
-- SCRIPT D'INITIALISATION IDEMPOTENT DES TABLES DB-SUBAGENTS-SKILLS
-- ====================================================================

-- Activation des contraintes de clés étrangères
PRAGMA foreign_keys = ON;

-- 1. Table des Sessions : Suivi général des exécutions (parents et sous-agents)
CREATE TABLE IF NOT EXISTS subagents_sessions (
    session_id TEXT PRIMARY KEY,
    theme TEXT NOT NULL,
    date_start TEXT NOT NULL, -- Format ISO 8601 (AAAA-MM-JJ HH:MM:SS)
    date_end TEXT,
    status TEXT CHECK(status IN ('running', 'completed', 'failed', 'abandoned')) DEFAULT 'running',
    tokens_prompt INTEGER DEFAULT 0,
    tokens_completion INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    cost REAL DEFAULT 0.0,
    execution_depth INTEGER DEFAULT 0,
    parent_session_id TEXT,
    FOREIGN KEY(parent_session_id) REFERENCES subagents_sessions(session_id) ON DELETE SET NULL
);

-- 2. Table des Tâches : Liste des actions déclarées par le sous-agent
CREATE TABLE IF NOT EXISTS subagents_tasks (
    task_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    task_name TEXT NOT NULL,
    status TEXT CHECK(status IN ('todo', 'done', 'failed', 'in_progress')) DEFAULT 'todo',
    error_message TEXT,
    timestamp TEXT NOT NULL,
    FOREIGN KEY(session_id) REFERENCES subagents_sessions(session_id) ON DELETE CASCADE
);

-- 3. Table des Feedbacks et Traces Sémantiques : Enregistrement des interactions
CREATE TABLE IF NOT EXISTS subagents_feedback (
    feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    interaction_num INTEGER NOT NULL,
    user_prompt TEXT NOT NULL,
    agent_response TEXT NOT NULL,
    diagnostic TEXT,
    action TEXT,
    preuve TEXT,
    rating INTEGER CHECK(rating BETWEEN 1 AND 5),
    notes TEXT,
    timestamp TEXT NOT NULL,
    FOREIGN KEY(session_id) REFERENCES subagents_sessions(session_id) ON DELETE CASCADE
);

-- 4. Table des Skills Shadow-Targeting : Suivi des injections de compétences
CREATE TABLE IF NOT EXISTS subagents_skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    skill_name TEXT NOT NULL,
    target_subagent TEXT NOT NULL, -- ex: 'tesla-arcanis', 'tesla-master-code'
    injection_method TEXT CHECK(injection_method IN ('shadow-targeting', 'native', 'adhoc')) DEFAULT 'shadow-targeting',
    session_id TEXT NOT NULL,
    date_injection TEXT NOT NULL,
    statut TEXT CHECK(statut IN ('active', 'inactive', 'expired', 'failed')) DEFAULT 'active',
    resultat_observe TEXT,
    notes TEXT,
    FOREIGN KEY(session_id) REFERENCES subagents_sessions(session_id) ON DELETE CASCADE
);

-- 5. Indexations pour la performance des requêtes analytiques et de jointure
CREATE INDEX IF NOT EXISTS idx_sessions_parent ON subagents_sessions(parent_session_id);
CREATE INDEX IF NOT EXISTS idx_tasks_session ON subagents_tasks(session_id);
CREATE INDEX IF NOT EXISTS idx_feedback_session ON subagents_feedback(session_id);
CREATE INDEX IF NOT EXISTS idx_skills_session ON subagents_skills(session_id);
CREATE INDEX IF NOT EXISTS idx_skills_name ON subagents_skills(skill_name);
```

---

## 3. Logique Algorithmique du Parser (`log_subagent_parser.py`)

Le script `log_subagent_parser.py` sera programmé en Python. Il a pour but de lire le fichier `transcript.jsonl` (ou `transcript_full.jsonl`) d'une session, d'extraire les informations pertinentes, et d'insérer de manière sécurisée ces données dans SQLite.

### A. Algorithme de Lecture Résiliente (Anti-Corruption JSONL)
Pour se prémunir d'une lecture au moment où le fichier est écrit à la volée par Antigravity CLI, le parser implémente la logique suivante :
1. **Ouverture sécurisée** : Lecture ligne par ligne.
2. **Saut de lignes mal formées** : En cas de `json.JSONDecodeError` sur une ligne (souvent la dernière ligne en cours d'écriture), le parser n'échoue pas. Il attend 100 ms et tente de relire la ligne. Si elle reste invalide, il la logue sous forme d'avertissement et passe à la suivante sans crasher.
3. **Fermeture propre** : Garantie par un gestionnaire de contexte (`with open(...)`).

### B. Algorithme de Parcours du Graphe (Anti-Récursion Infinie)
Pour extraire les données des sous-agents délégués sans entrer dans une boucle infinie de parsing en cas de réinvocations :
```python
def parse_session_recursive(session_id, parent_id=None, depth=0, visited=None):
    if visited is None:
        visited = set()
    
    # 1. Vérification de sécurité contre les cycles et la profondeur
    if session_id in visited:
        print(f"[!] Cycle détecté pour la session {session_id}. Annulation du parsing.")
        return
    if depth > 3:
        print(f"[!] Profondeur maximale de récursion (3) dépassée pour {session_id}.")
        return
        
    visited.add(session_id)
    
    # 2. Localiser le transcript.jsonl de la session
    transcript_path = find_transcript_path(session_id)
    if not transcript_path:
        return
        
    # 3. Extraire les données (méta, tâches, feedbacks)
    session_data = extract_data_from_transcript(transcript_path)
    
    # 4. Enregistrer en base
    save_to_sqlite(session_id, session_data, parent_id, depth)
    
    # 5. Détecter les sous-agents invoqués
    subagent_calls = detect_subagent_invocations(session_data)
    for sub_id in subagent_calls:
        # Appel récursif avec profondeur incrémentée
        parse_session_recursive(sub_id, parent_id=session_id, depth=depth+1, visited=visited)
```

### C. Détection du Shadow-Targeting
Pour identifier si un skill a été injecté sous la méthode Shadow-Targeting :
1. Le parser scanne les appels d'outils du sous-agent. S'il détecte un appel d'outil `view_file` ou `write_to_file` ciblant un répertoire de skill dans le workspace local (`.agents/skills/<skill_name>/SKILL.md`), ou si le prompt système (extrait de la première ligne d'interaction) contient des instructions propres à un skill non natif, le parser extrait le nom du skill.
2. Une entrée est alors créée dans `subagents_skills` avec `target_subagent` positionné sur le rôle du sous-agent, `injection_method = 'shadow-targeting'`, et `statut = 'active'`.

---

## 4. Intégration et Automatisation dans le Flux de Session

Le point d'ancrage du parser est le script existant [update_session_history.py](file:///home/lord-mahonheim/bifrost/tesla/memory/update_session_history.py). Ce script s'exécute déjà en fin de session pour consolider la mémoire textuelle de Lord Mahonheim.

### Chaînage Technique :
En fin de script `update_session_history.py` (par exemple juste après la mise à jour de `PROJECT_STATE.md`), nous insérons l'invocation du parser :

```python
# Intégration à la fin de update_session_history.py
try:
    print("[*] Lancement du parser relationnel DB-Subagents-Skills...")
    from log_subagent_parser import parse_session_recursive
    
    # Appel de l'algorithme récursif sur la session courante
    parse_session_recursive(conversation_id)
    print("[+] Base de données DB-Subagents-Skills mise à jour avec succès.")
except Exception as e:
    # Avertissement visuel fort mais non-bloquant pour la session
    print(f"============================================================")
    print(f"[⚠️ WARNING] Échec de la mise à jour DB-Subagents-Skills : {e}")
    print(f"============================================================")
```

---

## 5. Mesures de Résilience et Protection de la Base Alexandria

Les contre-mesures nées de l'audit Premortem sont intégrées au cœur de la conception technique :

1. **Isolation Transactionnelle (WAL Mode)** : 
   Chaque connexion à la base de données SQLite devra explicitement exécuter :
   `conn.execute("PRAGMA journal_mode=WAL;")`
   `conn.execute("PRAGMA busy_timeout = 10000;")` -- Timeout de 10 secondes pour éviter les blocages simultanés.
2. **Robustesse de la structure (Database Migration)** : 
   Le script SQL d'initialisation sera exécuté sous format `IF NOT EXISTS` de sorte qu'il n'écrase jamais les données d'indexation plein texte de la table `fts_vault_index` préexistante dans `alexandria_brain.db`.
3. **Sauvegardes à chaud (Hot Backups)** : 
   Une fonction de sauvegarde compacte copiera `alexandria_brain.db` vers `/home/lord-mahonheim/bifrost/tesla/memory/backup/alexandria_brain.db.bak` avant toute écriture critique.
4. **Réconciliation quotidienne automatique (Garbage Collector)** : 
   Un script de maintenance sera lancé pour passer à `abandoned` toutes les sessions qui sont restées dans l'état `running` plus de 24 heures et dont le PID de l'IDE/CLI Antigravity n'est plus actif dans la table des processus du système MIDGARD.

---

## 6. Plan de Validation et Recette

Pour valider le fonctionnement de la base et du parser, la procédure de test suivante est adoptée :
1. **Phase 1 : Injection du Schéma** : Exécution manuelle du script SQL d'initialisation sur `alexandria_brain.db` et vérification avec la commande `.schema` de sqlite3.
2. **Phase 2 : Test Unitaire du Parser** : Exécution de `log_subagent_parser.py` sur une session de test passée pour valider l'extraction sans crash.
3. **Phase 3 : Test d'Invocation Récursive** : Simulation d'une session parente déléguant à 2 sous-agents, et validation de l'enregistrement de l'arbre complet de sessions (relations clés étrangères).
4. **Phase 4 : Simulation de Shadow-Targeting** : Injection forcée d'un skill de test et vérification de son inscription active dans la table `subagents_skills`.

---

> **Arcanis.** Enquête planifiée. Hypothèses testées. Sources croisées. Livrable certifié.  
> — Validé par Arcanis. Archive de référence.  
> `SHA256:c65e93c7614d5f5e4be98468eb6fae08ab4f8aeac82d7997b9dee2fcadd48b54`
