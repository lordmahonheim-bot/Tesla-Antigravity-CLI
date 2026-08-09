# Rapport d'Exploration Technique : Intégration de la Base de Données (DDL v2.0)

**Jalon :** 3 (`tesla-loop-orchestrator`)  
**Rôle :** Explorer 3 (Analyse de la persistance & DDL)  
**Destinataire :** Lord Mahonheim  
**Date :** 10 Juillet 2026  
**Version :** v1.0  
**Statut :** Validé (Prêt pour l'implémentation)

---

## 1. Diagnostic de l'Existant (Observations)

Après exploration de la base de code locale sur la station **MIDGARD**, les faits suivants ont été établis :

1. **Trois fichiers d'initialisation de base de données distincts** coexistent dans le projet :
   * `memory/db_init.py` : Utilise le module centralisé `db_connector.py`.
   * `MVP-GITHUB/17-DB-Subagents-Skills/db_init.py` : Version destinée au dépôt public.
   * `Avalon/03-Resources/db_init.py` : Implémente sa propre fonction locale `get_db_connection()` et définit le chemin absolu en dur :
     `DB_PATH = "/home/lord-mahonheim/bifrost/tesla/Avalon/03-Resources/alexandria_brain.db"`

2. **Structure de `db_init.py` actuelle** :
   Ces scripts gèrent un système élémentaire de versioning via la table `schema_version`. Actuellement, la seule version gérée et appliquée est la **version 1.0** (introduisant les tables `subagents_sessions`, `subagents_tasks`, `subagents_feedback` et `subagents_skills`).

3. **État de la Base de Données locale** :
   La base `/home/lord-mahonheim/bifrost/tesla/Avalon/03-Resources/alexandria_brain.db` est actuellement en version `1.0` (appliquée le `2026-07-03 17:12:01`). Les tables `loop_executions` et `loop_iterations` n'existent pas encore.

---

## 2. Recommandations de Conception : Schéma DDL Version 2.0

Le schéma proposé dans le *Plan d'Intervention Consolidé* (`OUTPUTS/plan_intervention_loop_engineering_v1.0_2026-07-10.md`) présente des ambiguïtés sémantiques concernant les coûts et budgets.

### Analyse des faiblesses du schéma initial :
* **Confusion Jetons vs USD** : La colonne `total_token_cost` est de type `REAL` (suggérant un coût financier en USD), tandis que `token_budget` est également de type `REAL` (suggérant aussi un coût financier ou un nombre de jetons). 
* **Dualité des Limites** : Le contrat YAML distingue clairement `financial_budget_usd` (ex. `3.50`) et `token_budget` (ex. `80000`). Le schéma de base de données doit refléter fidèlement ces deux limites physiques distinctes pour permettre un contrôle exact de la machine d'état.

### Schéma DDL v2.0 Corrigé & Optimisé :
Nous préconisons le déploiement du schéma révisé suivant, garantissant la cohérence avec le modèle de données de la version 1.0 (qui stocke les tokens en `INTEGER` et les coûts en `REAL`) :

```sql
-- Extension DDL Alexandria - Loop Engineering (v2.0)

-- 1. Table de suivi des sessions de boucles autonomes
CREATE TABLE IF NOT EXISTS loop_executions (
    id TEXT PRIMARY KEY,
    project TEXT NOT NULL,
    contract_version TEXT NOT NULL,
    goal TEXT NOT NULL,
    start_time TEXT NOT NULL,          -- Format ISO 8601 UTC (ex. 'YYYY-MM-DDTHH:MM:SSZ')
    end_time TEXT,                     -- Format ISO 8601 UTC
    status TEXT NOT NULL CHECK(status IN ('PASS', 'DELAY', 'BLOCK', 'RUNNING')),
    total_iterations INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,    -- Comptabilisation exacte des jetons consommés
    total_cost_usd REAL DEFAULT 0.0,   -- Coût financier cumulé en USD
    max_iterations INTEGER NOT NULL,
    token_budget INTEGER NOT NULL,     -- Limite de jetons (ex. 80000)
    financial_budget_usd REAL NOT NULL -- Limite financière (ex. 5.00)
);

-- 2. Table de suivi détaillé des itérations
CREATE TABLE IF NOT EXISTS loop_iterations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    execution_id TEXT NOT NULL,
    iteration_number INTEGER NOT NULL,
    timestamp TEXT NOT NULL,           -- Format ISO 8601 UTC
    action_taken TEXT NOT NULL,
    verdict TEXT NOT NULL CHECK(verdict IN ('PASS', 'DELAY', 'BLOCK')),
    learning_deltas TEXT,              -- JSON sérialisé (advice, errors, etc.)
    tokens_used INTEGER DEFAULT 0,     -- Jetons consommés pour cette itération
    cost_usd REAL DEFAULT 0.0,         -- Coût financier de cette itération en USD
    report_path TEXT,                  -- Chemin vers le rapport d'audit détaillé
    FOREIGN KEY (execution_id) REFERENCES loop_executions(id) ON DELETE CASCADE
);

-- 3. Indexations d'optimisation
CREATE INDEX IF NOT EXISTS idx_loop_executions_status ON loop_executions(status);
CREATE INDEX IF NOT EXISTS idx_loop_iterations_exec ON loop_iterations(execution_id);
```

---

## 3. Stratégie d'Exécution et Migration de la DDL

Pour assurer la rétrocompatibilité et éviter tout écrasement de données ou corruption :

### 3.1 Modification Logique de `db_init.py`
Le code d'initialisation dans `db_init.py` doit être modifié de façon séquentielle :
1. Récupération de la version actuelle depuis `schema_version`.
2. Si `current_version == "0.0"` : Exécuter la DDL de la version `1.0`, enregistrer la version `1.0` en base, puis poursuivre.
3. Si `current_version == "1.0"` : Exécuter uniquement la DDL de la version `2.0`, puis enregistrer la version `2.0` en base.
4. Cette approche garantit la transition transparente des bases existantes (actuellement en 1.0) vers la 2.0, tout en permettant une installation propre (0.0 -> 1.0 -> 2.0).

### 3.2 Synchronisation des Fichiers (Règle MVP-GITHUB)
Selon la règle **12 de AGENTS.md**, toute modification de `memory/db_init.py` doit faire l'objet d'une double copie manuelle vers les répertoires cibles avant la clôture :
* Copier `memory/db_init.py` vers `MVP-GITHUB/17-DB-Subagents-Skills/db_init.py`.
* Mettre à jour en parallèle la version simplifiée de `Avalon/03-Resources/db_init.py` pour y inclure la migration v2.0 avec son driver de connexion en dur.

---

## 4. Recommandations d'Interaction pour l'Orchestrateur Python

Le script `scripts/tesla_loop_orchestrator.py` doit interagir avec la base de données selon des patterns stricts pour prévenir la corruption de fichiers et les verrous concurrents :

1. **Isolation des Transactions & Context Managers** :
   Le script doit encapsuler chaque écriture dans un bloc `with connection:` pour valider automatiquement les modifications (`commit`) ou les annuler (`rollback`) en cas d'exception.
   ```python
   with get_db_connection() as conn:
       conn.execute("INSERT INTO loop_iterations ...", params)
   ```

2. **Gestion des Verrous (Write Lock Backoff)** :
   Bien que `db_connector.py` active le mode WAL et un timeout de 10 secondes, l'orchestrateur doit implémenter un wrapper de retry robuste avec attente exponentielle et perturbation aléatoire (jitter) pour intercepter `sqlite3.OperationalError` (cas de base verrouillée) :
   $$\text{Délai} = 2^{\text{retry\_count}} \times 0.1 + \text{random\_jitter}(0, 0.05)$$

3. **Requêtes Paramétrées Strictes** :
   Interdiction formelle de concaténer des chaînes SQL pour y injecter des variables. Toujours utiliser les arguments positionnels SQLite (`?`) :
   ```python
   # CORRECT
   conn.execute("UPDATE loop_executions SET status = ? WHERE id = ?", (status, exec_id))
   ```

4. **Sérialisation JSON Robuste** :
   Les deltas d'apprentissage (`learning_deltas`) devant être persistés sous forme de texte, l'orchestrateur doit utiliser `json.dumps()` et intercepter les erreurs de sérialisation pour éviter tout blocage de boucle.

---

## 5. Protocole de Vérification (Preuve)

Pour valider le succès des modifications apportées par l'implémenteur :

1. **Exécution du script de migration** :
   ```bash
   python3 memory/db_init.py
   ```
   La console doit afficher :
   ```
   [*] Initializing database at /home/lord-mahonheim/bifrost/tesla/Avalon/03-Resources/alexandria_brain.db...
   [*] Current schema version: 1.0
   [*] Applying schema version 2.0...
   [+] Schema version 2.0 applied successfully.
   ```

2. **Vérification de la structure SQL via le CLI SQLite3** :
   ```bash
   sqlite3 Avalon/03-Resources/alexandria_brain.db "SELECT version FROM schema_version ORDER BY applied_at DESC LIMIT 1;"
   ```
   *Attendu :* `2.0`

   ```bash
   sqlite3 Avalon/03-Resources/alexandria_brain.db "PRAGMA table_info(loop_executions);"
   ```
   *Attendu :* Liste complète des colonnes révisées avec types exacts (notamment `total_cost_usd` et `financial_budget_usd`).
