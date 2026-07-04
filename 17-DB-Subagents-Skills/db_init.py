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
        
        # Check current version
        cursor = conn.cursor()
        cursor.execute("SELECT version FROM schema_version ORDER BY applied_at DESC LIMIT 1;")
        row = cursor.fetchone()
        current_version = row[0] if row else "0.0"
        
        print(f"[*] Current schema version: {current_version}")
        
        if current_version == "0.0":
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
        else:
            print("[*] Schema version is already up to date.")
            
    except Exception as e:
        print(f"[-] Database initialization failed: {e}")
        conn.rollback()
        raise e
    finally:
        conn.close()

if __name__ == "__main__":
    init_database()
