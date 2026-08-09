#!/usr/bin/env python3
# db_init.py — Initialize tables in alexandria_brain.db with schema versioning
import os
from datetime import datetime
from db_connector import get_db_connection, DB_PATH

def init_database():
    print(f"[*] Initializing database at {DB_PATH}...")
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = get_db_connection(create_if_missing=True)
    try:
        # Create schema_version table
        conn.execute("""
        CREATE TABLE IF NOT EXISTS schema_version (
            version TEXT PRIMARY KEY,
            applied_at TEXT NOT NULL
        );
        """)
        
        # Check applied versions
        cursor = conn.cursor()
        cursor.execute("SELECT version FROM schema_version;")
        applied_versions = {row[0] for row in cursor.fetchall()}
        
        print(f"[*] Applied schema versions: {sorted(list(applied_versions))}")
        
        updated = False
        
        if "1.0" not in applied_versions:
            # Run DDL scripts for 1.0
            print("[*] Applying schema version 1.0...")
            conn.executescript("""
            -- 1. Table des Sessions
            CREATE TABLE IF NOT EXISTS subagents_sessions (
                session_id TEXT PRIMARY KEY,
                theme TEXT NOT NULL,
                date_start TEXT NOT NULL,
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

            -- 2. Table des Tâches
            CREATE TABLE IF NOT EXISTS subagents_tasks (
                task_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                task_name TEXT NOT NULL,
                status TEXT CHECK(status IN ('todo', 'done', 'failed', 'in_progress')) DEFAULT 'todo',
                error_message TEXT,
                timestamp TEXT NOT NULL,
                FOREIGN KEY(session_id) REFERENCES subagents_sessions(session_id) ON DELETE CASCADE
            );

            -- 3. Table des Feedbacks
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

            -- 4. Table des Skills Shadow-Targeting
            CREATE TABLE IF NOT EXISTS subagents_skills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                skill_name TEXT NOT NULL,
                target_subagent TEXT NOT NULL,
                injection_method TEXT CHECK(injection_method IN ('shadow-targeting', 'native', 'adhoc')) DEFAULT 'shadow-targeting',
                session_id TEXT NOT NULL,
                date_injection TEXT NOT NULL,
                statut TEXT CHECK(statut IN ('active', 'inactive', 'expired', 'failed')) DEFAULT 'active',
                resultat_observe TEXT,
                notes TEXT,
                confidence_score REAL CHECK(confidence_score BETWEEN 0.0 AND 1.0),
                detection_method TEXT CHECK(detection_method IN ('file_access', 'system_prompt_heuristics', 'api_pattern', 'fallback')),
                FOREIGN KEY(session_id) REFERENCES subagents_sessions(session_id) ON DELETE CASCADE
            );

            -- 5. Indexations
            CREATE INDEX IF NOT EXISTS idx_sessions_parent ON subagents_sessions(parent_session_id);
            CREATE INDEX IF NOT EXISTS idx_tasks_session ON subagents_tasks(session_id);
            CREATE INDEX IF NOT EXISTS idx_feedback_session ON subagents_feedback(session_id);
            CREATE INDEX IF NOT EXISTS idx_skills_session ON subagents_skills(session_id);
            CREATE INDEX IF NOT EXISTS idx_skills_name ON subagents_skills(skill_name);
            CREATE INDEX IF NOT EXISTS idx_skills_target_status ON subagents_skills(target_subagent, statut);
            """)
            
            # Record version 1.0 application
            conn.execute(
                "INSERT INTO schema_version (version, applied_at) VALUES (?, ?);",
                ("1.0", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            )
            conn.commit()
            print("[+] Schema version 1.0 applied successfully.")
            applied_versions.add("1.0")
            updated = True
            
        if "2.0" not in applied_versions:
            # Run DDL scripts for 2.0
            print("[*] Applying schema version 2.0...")
            conn.executescript("""
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
            """)
            
            # Record version 2.0 application
            conn.execute(
                "INSERT INTO schema_version (version, applied_at) VALUES (?, ?);",
                ("2.0", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            )
            conn.commit()
            print("[+] Schema version 2.0 applied successfully.")
            applied_versions.add("2.0")
            updated = True

        if "3.0" not in applied_versions:
            # Run DDL scripts for 3.0
            print("[*] Applying schema version 3.0...")
            # Idempotent column check and alter table
            cursor.execute("PRAGMA table_info(subagents_skills);")
            columns = [col[1] for col in cursor.fetchall()]
            
            new_columns = {
                "model_used": "TEXT",
                "complexity": "TEXT",
                "tokens_estimate": "INTEGER",
                "node_id": "TEXT",
                "attempt_n": "INTEGER DEFAULT 1",
                "mission_state": "TEXT"
            }
            
            for col_name, col_type in new_columns.items():
                if col_name not in columns:
                    conn.execute(f"ALTER TABLE subagents_skills ADD COLUMN {col_name} {col_type};")
                    print(f"[+] Added column {col_name} to subagents_skills")
            
            # Record version 3.0 application
            conn.execute(
                "INSERT INTO schema_version (version, applied_at) VALUES (?, ?);",
                ("3.0", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            )
            conn.commit()
            print("[+] Schema version 3.0 applied successfully.")
            applied_versions.add("3.0")
            updated = True

        if "4.0" not in applied_versions:
            # Run DDL scripts for 4.0
            print("[*] Applying schema version 4.0...")
            conn.executescript("""
            -- 1. Table des documents
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT UNIQUE NOT NULL,
                mtime REAL NOT NULL,
                hash_doc TEXT NOT NULL,
                confidential INTEGER DEFAULT 0
            );

            -- 2. Table des chunks
            CREATE TABLE IF NOT EXISTS chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                doc_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
                chunk_index INTEGER NOT NULL,
                text TEXT NOT NULL,
                hash_chunk TEXT UNIQUE NOT NULL,
                token_count INTEGER,
                created_at REAL NOT NULL
            );

            -- 3. Table des vecteurs sémantiques
            CREATE TABLE IF NOT EXISTS vector_registry (
                chunk_id INTEGER PRIMARY KEY REFERENCES chunks(id) ON DELETE CASCADE,
                embedding BLOB NOT NULL,
                dim INTEGER NOT NULL DEFAULT 768,
                model_version TEXT NOT NULL DEFAULT 'gemini-embedding-001:768',
                hash_chunk TEXT NOT NULL,
                created_at REAL NOT NULL
            );

            -- 4. Table des embeddings en attente
            CREATE TABLE IF NOT EXISTS pending_embeddings (
                chunk_id INTEGER PRIMARY KEY REFERENCES chunks(id) ON DELETE CASCADE,
                attempts INTEGER DEFAULT 0,
                last_error TEXT,
                next_retry_at REAL NOT NULL
            );

            -- 5. Table virtuelle FTS5 pour l'indexation lexicale
            DROP TABLE IF EXISTS fts_vault_index;
            CREATE VIRTUAL TABLE fts_vault_index USING fts5(
                chunk_id,
                filepath,
                content
            );

            -- 6. Indexations
            CREATE INDEX IF NOT EXISTS idx_chunks_hash ON chunks(hash_chunk);
            CREATE INDEX IF NOT EXISTS idx_vector_model ON vector_registry(model_version);
            CREATE INDEX IF NOT EXISTS idx_docs_conf ON documents(confidential);
            """)
            
            # Record version 4.0 application
            conn.execute(
                "INSERT INTO schema_version (version, applied_at) VALUES (?, ?);",
                ("4.0", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            )
            conn.commit()
            print("[+] Schema version 4.0 applied successfully.")
            applied_versions.add("4.0")
            updated = True
            
        if not updated:
            print("[*] Schema version is already up to date.")
            
    except Exception as e:
        print(f"[-] Database initialization failed: {e}")
        conn.rollback()
        raise e
    finally:
        conn.close()

if __name__ == "__main__":
    init_database()
