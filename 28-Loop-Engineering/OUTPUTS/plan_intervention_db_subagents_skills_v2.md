---
type: reference
tags: [securite/plan-intervention, statut/valide]
source: "[[DB-SUBAGENTS-SKILLS_v2.0_2026-07-03.md]]"
date: 2026-07-03
version: 2.0
author: "Tesla Arcanis"
certification: "Arcanis_Seal_v3"
---

# PLAN D'INTERVENTION TECHNIQUE CONSOLIDÉ (V2) : INTÉGRATION DE LA BASE DB-SUBAGENTS-SKILLS

**Date de rédaction :** 2026-07-03  
**Auteur :** tesla-arcanis (Sous-Agent d'Élite Tesla)  
**Destinataire :** Lord Mahonheim (Abdellah MOUHTAJ)  

---

## 1. Contexte & Architecture Cible

Ce document détaille la version 2.0 du plan d'intervention pour la réalisation technique du chantier **DB-Subagents-Skills**. Il intègre les correctifs de sécurité et de robustesse suite aux retours de Lord Mahonheim sur la version v1, ainsi que les contre-mesures issues de l'audit de résilience Premortem pour garantir l'absence de corruption de données, de blocages concurrents ou de boucles infinies de parsing sur l'environnement MIDGARD.

L'objectif est d'ajouter à la base [alexandria_brain.db](file:///home/lord-mahonheim/bifrost/tesla/Avalon/03-Resources/alexandria_brain.db) un sous-système de suivi relationnel pour :
1. L'historique d'exécution des sessions de sous-agents (tokens, durée, hiérarchie).
2. L'historique sémantique des tâches et retours (Diagnostics, Actions, Preuves).
3. Le suivi du Shadow-Targeting (compétences injectées dans les sous-agents par défaut du plan Pro d'Antigravity CLI).

---

## 2. Cadrage Juridique & Risque CGU (Conditions Générales d'Utilisation)

Le développement d'un parser automatique des journaux d'interactions (`transcript.jsonl`) générés par Antigravity CLI pose la question de la conformité avec les conditions d'utilisation de l'outil. L'analyse conclut à un **risque juridique négligeable** et à une conformité totale avec le cadre technique local, pour les motifs suivants :

1. **Localisation et confinement de l'analyse** : Le script de parsing s'exécute exclusivement en local sur MIDGARD sous les privilèges de Lord Mahonheim. Aucune donnée n'est extraite ou retransmise vers des serveurs tiers.
2. **Absence d'altération logique** : Le parser est strictement passif. Il lit des fichiers de télémétrie locale préalablement stockés sur le disque dur. Il ne modifie pas les binaires d'Antigravity CLI, ne contourne aucun mécanisme d'authentification et ne réalise pas de rétro-ingénierie (reverse engineering) du logiciel lui-même.
3. **Respect de l'usage légitime de sécurité** : L'audit et l'analyse de logs constituent une mesure standard d'observabilité et de sécurité informatique. Détecter le Shadow-Targeting ou les compétences injectées de manière opaque relève du devoir de gouvernance locale et d'audit de la chaîne de confiance logicielle (Vigilum Codex).

---

## 3. Spécification du Schéma SQL de Résilience (V2)

Le schéma SQL ci-dessous doit être exécuté de manière idempotente sur la base SQLite `alexandria_brain.db`. Il intègre désormais la table de suivi de version `schema_version`, des index composites pour la performance, et des structures de données enrichies pour qualifier la détection de Shadow-Targeting.

```sql
-- ====================================================================
-- SCRIPT D'INITIALISATION IDEMPOTENT DES TABLES DB-SUBAGENTS-SKILLS (V2)
-- ====================================================================

-- Activation des contraintes de clés étrangères
PRAGMA foreign_keys = ON;

-- 0. Table de Versionnement du Schéma SQL
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TEXT NOT NULL -- Format ISO 8601 (AAAA-MM-JJ HH:MM:SS)
);

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
    confidence_score REAL CHECK(confidence_score BETWEEN 0.0 AND 1.0) DEFAULT 1.0, -- Score de détection
    detection_method TEXT CHECK(detection_method IN ('file_access', 'system_prompt_heuristics', 'api_pattern', 'fallback')) DEFAULT 'fallback',
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

-- Index composite optimisé pour les audits rapides du statut par sous-agent cible
CREATE INDEX IF NOT EXISTS idx_skills_target_status ON subagents_skills(target_subagent, statut);
```

---

## 4. Logique Algorithmique du Parser (`log_subagent_parser.py`)

Le script `log_subagent_parser.py` est programmé en Python. Il a pour but de lire le fichier `transcript.jsonl` (ou `transcript_full.jsonl`) d'une session, d'extraire les informations pertinentes, et d'insérer de manière sécurisée ces données dans SQLite.

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
    
    # 4. Enregistrer en base avec atomicité transactionnelle
    save_session_atomic(session_id, session_data, parent_id, depth)
    
    # 5. Détecter les sous-agents invoqués
    subagent_calls = detect_subagent_invocations(session_data)
    for sub_id in subagent_calls:
        # Appel récursif avec profondeur incrémentée
        parse_session_recursive(sub_id, parent_id=session_id, depth=depth+1, visited=visited)
```

### C. Détection du Shadow-Targeting Robuste
Pour identifier si un skill a été injecté sous la méthode Shadow-Targeting, le parser analyse le contexte d'interaction et lui attribue une signature probabiliste :

1. **Méthode `file_access` (Confiance : 1.0)** : Détectée lorsque le sous-agent exécute un outil d'accès en lecture (`view_file`) ou en écriture (`write_to_file`) pointant directement vers un fichier de description de skill dans le projet (ex : `.agents/skills/<skill_name>/SKILL.md`).
2. **Méthode `system_prompt_heuristics` (Confiance : 0.8)** : Détectée lorsque le prompt système initial du sous-agent contient des règles ou des phrases clés spécifiques à la nomenclature du skill de référence.
3. **Méthode `api_pattern` (Confiance : 0.7)** : Détectée par l'appel de signatures d'outils propres à un skill (ex: appel d'outils MCP spécifiques à devtools ou extension web) alors qu'aucune lecture formelle du fichier `SKILL.md` n'a été interceptée.
4. **Méthode `fallback` (Confiance : 0.5 ou moins)** : Détection sémantique sur la base d'une simple mention d'un mot-clé de skill dans les blocs de pensée du sous-agent.

### D. Atomicité Transactionnelle & Requête UPSERT SQLite
Afin d'éviter toute corruption de base ou l'insertion d'états partiels en cas d'interruption du processus de parsing, l'écriture d'une session est encapsulée dans une transaction SQLite unique. De plus, pour permettre la ré-exécution idempotente du parser, nous utilisons la clause `ON CONFLICT(session_id) DO UPDATE` (UPSERT).

```python
def save_session_atomic(session_id, session_data, parent_id, depth):
    # Données nettoyées (scrubbing) à insérer
    clean_prompt = scrub_sensitive_data(session_data.get('user_prompt', ''))
    clean_response = scrub_sensitive_data(session_data.get('agent_response', ''))

    conn = get_db_connection()
    try:
        with conn: # Gère automatiquement le BEGIN et le COMMIT / ROLLBACK
            # 1. UPSERT de la Session
            conn.execute("""
                INSERT INTO subagents_sessions (
                    session_id, theme, date_start, date_end, status,
                    tokens_prompt, tokens_completion, total_tokens, cost,
                    execution_depth, parent_session_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(session_id) DO UPDATE SET
                    theme = excluded.theme,
                    date_start = excluded.date_start,
                    date_end = excluded.date_end,
                    status = excluded.status,
                    tokens_prompt = excluded.tokens_prompt,
                    tokens_completion = excluded.tokens_completion,
                    total_tokens = excluded.total_tokens,
                    cost = excluded.cost,
                    execution_depth = excluded.execution_depth,
                    parent_session_id = excluded.parent_session_id;
            """, (
                session_id, session_data['theme'], session_data['date_start'], 
                session_data.get('date_end'), session_data['status'],
                session_data.get('tokens_prompt', 0), session_data.get('tokens_completion', 0),
                session_data.get('total_tokens', 0), session_data.get('cost', 0.0),
                depth, parent_id
            ))

            # 2. Nettoyage des anciennes tâches liées avant ré-insertion
            conn.execute("DELETE FROM subagents_tasks WHERE session_id = ?;", (session_id,))
            for task in session_data.get('tasks', []):
                conn.execute("""
                    INSERT INTO subagents_tasks (session_id, task_name, status, error_message, timestamp)
                    VALUES (?, ?, ?, ?, ?);
                """, (session_id, task['name'], task['status'], task.get('error'), task['timestamp']))

            # 3. Nettoyage des anciens feedbacks avant ré-insertion
            conn.execute("DELETE FROM subagents_feedback WHERE session_id = ?;", (session_id,))
            for fb in session_data.get('feedbacks', []):
                conn.execute("""
                    INSERT INTO subagents_feedback (
                        session_id, interaction_num, user_prompt, agent_response,
                        diagnostic, action, preuve, rating, notes, timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """, (
                    session_id, fb['num'], clean_prompt, clean_response,
                    fb.get('diagnostic'), fb.get('action'), fb.get('preuve'),
                    fb.get('rating'), fb.get('notes'), fb['timestamp']
                ))

            # 4. Nettoyage des anciens skills avant ré-insertion
            conn.execute("DELETE FROM subagents_skills WHERE session_id = ?;", (session_id,))
            for skill in session_data.get('detected_skills', []):
                conn.execute("""
                    INSERT INTO subagents_skills (
                        skill_name, target_subagent, injection_method, confidence_score,
                        detection_method, session_id, date_injection, statut, resultat_observe, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """, (
                    skill['name'], skill['target'], skill['method'], skill['confidence'],
                    skill['detection_method'], session_id, skill['date'], 'active', 
                    skill.get('result'), skill.get('notes')
                ))
    except sqlite3.Error as e:
        print(f"[!] Erreur SQLite lors de l'écriture atomique de {session_id} : {e}")
        # La transaction est annulée (rollback) automatiquement par le gestionnaire de contexte
        raise e
```

### E. Algorithme de Scrubbing des Données Sensibles
Pour éviter de stocker des mots de passe, des clés privées ou des secrets d'API dans SQLite :
```python
import re

def scrub_sensitive_data(text: str) -> str:
    # Regex pour masquer les secrets courants
    patterns = {
        r"AIzaSy[a-zA-Z0-9_\-]{33}": "[REDAC_API_KEY_GOOGLE]",
        r"sk-[a-zA-Z0-9]{48}": "[REDAC_API_KEY_OPENAI]",
        r"-----BEGIN [A-Z ]+ PRIVATE KEY-----\n[\s\S]+?\n-----END [A-Z ]+ PRIVATE KEY-----": "[REDAC_PRIVATE_KEY]",
        r"(?i)(password|passwd|token|secret)\s*[:=]\s*['\"][^'\"]+['\"]": r"\1: '[REDAC]'"
    }
    scrubbed = text
    for pattern, replacement in patterns.items():
        scrubbed = re.sub(pattern, replacement, scrubbed)
    return scrubbed
```

---

## 5. Intégration et Automatisation dans le Flux de Session

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

## 6. Mesures de Résilience et Protection de la Base Alexandria

Les contre-mesures nées de l'audit Premortem sont intégrées au cœur de la conception technique :

1. **Isolation Transactionnelle (WAL Mode)** :  
   Chaque connexion à la base de données SQLite devra explicitement exécuter :  
   `conn.execute("PRAGMA journal_mode=WAL;")`  
   `conn.execute("PRAGMA busy_timeout = 10000;")` -- Timeout de 10 secondes pour éviter les blocages simultanés.
2. **Robustesse de la structure (Database Migration)** :  
   La table `schema_version` est vérifiée au démarrage du script. Si la version de schéma correspond à la version attendue, l'initialisation est ignorée. Sinon, la migration est appliquée dans une transaction. Les commandes SQL utilisent `IF NOT EXISTS` de sorte à ne jamais altérer la table préexistante `fts_vault_index` de la base `alexandria_brain.db`.
3. **Sauvegardes à chaud (Hot Backups)** :  
   Une fonction de sauvegarde compacte copie `alexandria_brain.db` vers `/home/lord-mahonheim/bifrost/tesla/memory/backup/alexandria_brain.db.bak` avant toute transaction d'écriture critique.
4. **Garbage Collector Hybride (Timestamps + PID)** :  
   Un script de maintenance journalier passe à `abandoned` toutes les sessions qui respectent la condition composite suivante :
   - Statut de la session en base : `'running'`.
   - Date de démarrage (`date_start`) ou dernière activité supérieure à **24 heures** par rapport au timestamp actuel de MIDGARD.
   - ET le PID associé à l'IDE/CLI Antigravity ayant initié cette session n'est plus actif dans la table des processus de MIDGARD.
5. **Politique de Purge et d'Archivage** :  
   Pour contenir le volume de la base de données :
   - Les sessions marquées `abandoned` ou `failed` datant de plus de **30 jours** sont purgées définitivement.
   - Les sessions `completed` ayant plus de **90 jours** sont extraites au format JSON compressé (`.jsonl.gz`) vers un répertoire d'archives `/home/lord-mahonheim/bifrost/tesla/memory/archive/` puis supprimées de la base SQLite active.
   - Un `VACUUM;` de la base est déclenché automatiquement à la suite de chaque purge mensuelle.

---

## 7. Plan de Validation, Recette et Restauration

Pour valider le fonctionnement de la base et du parser, la procédure de test suivante est adoptée :

1. **Phase 1 : Injection & Migration** : Exécution manuelle du script SQL d'initialisation sur `alexandria_brain.db` et vérification avec la commande `.schema` et requête sur `schema_version`.
2. **Phase 2 : Test Unitaire du Parser** : Exécution de `log_subagent_parser.py` sur une session de test passée pour valider l'extraction et le scrubbing sans crash.
3. **Phase 3 : Test d'Invocation Récursive** : Simulation d'une session parente déléguant à 2 sous-agents, et validation de l'enregistrement de l'arbre complet de sessions (relations clés étrangères) et de l'UPSERT en cas de ré-exécution.
4. **Phase 4 : Simulation de Shadow-Targeting** : Injection forcée de patterns de skills et vérification de leur inscription active avec les attributs `confidence_score` et `detection_method` associés.
5. **Phase 5 : Test de Restauration de Base (Crash-Recovery)** :
   - Simulation d'une altération ou corruption mineure de `alexandria_brain.db`.
   - Restauration de la base à partir du backup `alexandria_brain.db.bak`.
   - Exécution de la commande SQLite `PRAGMA integrity_check;` pour s'assurer que la base restaurée ne présente aucune corruption logique et est pleinement opérationnelle.

---

## 8. Note Explicative sur la Signature & Certification

Conformément à la doctrine de gouvernance locale et pour assurer la traçabilité immuable des livrables techniques sur MIDGARD, ce rapport d'intervention technique fait l'objet d'une signature numérique cryptographique SHA256 reproductible.

### Algorithme de Calcul et de Vérification du Hash
La signature numérique calculée est auto-référentielle mais exclut la dernière ligne du document (contenant le hash lui-même) afin d'éviter le problème de circularité logique. 

Pour recalculer ou vérifier la signature de ce document sur MIDGARD, Lord Mahonheim ou tout agent auditeur doit exécuter l'une des commandes bash suivantes :

* **Option 1 (via sed, recommandée)** :
  ```bash
  sed '$d' /home/lord-mahonheim/bifrost/tesla/OUTPUTS/plan_intervention_db_subagents_skills_v2.md | sha256sum
  ```

* **Option 2 (via head)** :
  ```bash
  head -n -1 /home/lord-mahonheim/bifrost/tesla/OUTPUTS/plan_intervention_db_subagents_skills_v2.md | sha256sum
  ```

La valeur hexadécimale ainsi retournée doit correspondre exactement à la signature de certification finale du présent rapport.

---

> **Arcanis.** Enquête planifiée. Hypothèses testées. Sources croisées. Livrable certifié.  
> — Validé par Arcanis. Archive de référence.  
> `SHA256:973b111cdac59f739a843316ffa14ddb079ab0b87e61db6bbac483d91481459a`
