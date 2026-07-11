#!/usr/bin/env python3
import sqlite3
import os
import time

class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        # Activer les clés étrangères et le mode WAL
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA journal_mode = WAL;")
        return conn

    def _init_db(self) -> None:
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = self.get_connection()
        try:
            with conn:
                # Table des documents
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS documents (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        path TEXT UNIQUE NOT NULL,
                        mtime REAL NOT NULL,
                        hash_doc TEXT NOT NULL,
                        confidential INTEGER DEFAULT 0
                    );
                """)
                # Table des chunks
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS chunks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        doc_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
                        chunk_index INTEGER NOT NULL,
                        text TEXT NOT NULL,
                        hash_chunk TEXT UNIQUE NOT NULL,
                        token_count INTEGER,
                        created_at REAL NOT NULL
                    );
                """)
                # Table des vecteurs sémantiques
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS vector_registry (
                        chunk_id INTEGER PRIMARY KEY REFERENCES chunks(id) ON DELETE CASCADE,
                        embedding BLOB NOT NULL,
                        dim INTEGER NOT NULL DEFAULT 768,
                        model_version TEXT NOT NULL DEFAULT 'gemini-embedding-001:768',
                        hash_chunk TEXT NOT NULL,
                        created_at REAL NOT NULL
                    );
                """)
                # Table des embeddings en attente
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS pending_embeddings (
                        chunk_id INTEGER PRIMARY KEY REFERENCES chunks(id) ON DELETE CASCADE,
                        attempts INTEGER DEFAULT 0,
                        last_error TEXT,
                        next_retry_at REAL NOT NULL
                    );
                """)
                # Table virtuelle FTS5 pour l'indexation lexicale
                try:
                    conn.execute("""
                        CREATE VIRTUAL TABLE fts_vault_index USING fts5(
                            chunk_id,
                            filepath,
                            content
                        );
                    """)
                except sqlite3.OperationalError:
                    # La table virtuelle existe déjà
                    pass

                # Index
                conn.execute("CREATE INDEX IF NOT EXISTS idx_chunks_hash ON chunks(hash_chunk);")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_vector_model ON vector_registry(model_version);")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_docs_conf ON documents(confidential);")
        finally:
            conn.close()

    def get_document_by_path(self, path: str) -> dict | None:
        conn = self.get_connection()
        try:
            row = conn.execute("SELECT * FROM documents WHERE path = ?", (path,)).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def register_document(self, path: str, mtime: float, hash_doc: str, confidential: bool) -> int:
        conn = self.get_connection()
        try:
            with conn:
                cursor = conn.execute("""
                    INSERT OR REPLACE INTO documents (path, mtime, hash_doc, confidential)
                    VALUES (?, ?, ?, ?)
                """, (path, mtime, hash_doc, 1 if confidential else 0))
                if cursor.lastrowid is not None:
                    return cursor.lastrowid
                raise RuntimeError("Impossible d'obtenir l'ID du document insere")
        finally:
            conn.close()

    def delete_document_by_path(self, path: str) -> None:
        conn = self.get_connection()
        try:
            with conn:
                # Récupérer l'ID du document pour nettoyer FTS5
                doc_row = conn.execute("SELECT id FROM documents WHERE path = ?", (path,)).fetchone()
                if doc_row:
                    doc_id = doc_row["id"]
                    # Supprimer de FTS5
                    chunk_rows = conn.execute("SELECT hash_chunk FROM chunks WHERE doc_id = ?", (doc_id,)).fetchall()
                    for chunk in chunk_rows:
                        conn.execute("DELETE FROM fts_vault_index WHERE chunk_id = ?", (chunk["hash_chunk"],))
                    
                    # Supprimer le document (cascade supprimera chunks, vector_registry, pending_embeddings)
                    conn.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
        finally:
            conn.close()

    def insert_chunk(self, doc_id: int, chunk_index: int, text: str, hash_chunk: str, token_count: int | None = None) -> int:
        conn = self.get_connection()
        try:
            with conn:
                # Essayer d'insérer le chunk
                cursor = conn.execute("""
                    INSERT OR IGNORE INTO chunks (doc_id, chunk_index, text, hash_chunk, token_count, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (doc_id, chunk_index, text, hash_chunk, token_count, time.time()))
                
                # Si déjà existant, récupérer l'ID existant
                if cursor.rowcount == 0:
                    row = conn.execute("SELECT id FROM chunks WHERE hash_chunk = ?", (hash_chunk,)).fetchone()
                    if row:
                        return row["id"]
                if cursor.lastrowid is not None:
                    return cursor.lastrowid
                raise RuntimeError("Impossible d'obtenir l'ID du chunk insere")
        finally:
            conn.close()

    def insert_fts_entry(self, chunk_hash: str, filepath: str, text: str) -> None:
        conn = self.get_connection()
        try:
            with conn:
                # S'assurer de ne pas insérer de doublons dans FTS5
                conn.execute("DELETE FROM fts_vault_index WHERE chunk_id = ?", (chunk_hash,))
                conn.execute("""
                    INSERT INTO fts_vault_index (chunk_id, filepath, content)
                    VALUES (?, ?, ?)
                """, (chunk_hash, filepath, text))
        finally:
            conn.close()

    def get_cached_embedding(self, hash_chunk: str, model_version: str) -> bytes | None:
        conn = self.get_connection()
        try:
            row = conn.execute("""
                SELECT embedding FROM vector_registry 
                WHERE hash_chunk = ? AND model_version = ?
            """, (hash_chunk, model_version)).fetchone()
            return row["embedding"] if row else None
        finally:
            conn.close()

    def insert_embedding(self, chunk_id: int, hash_chunk: str, embedding: bytes, dim: int, model_version: str) -> None:
        conn = self.get_connection()
        try:
            with conn:
                conn.execute("""
                    INSERT OR REPLACE INTO vector_registry (chunk_id, embedding, dim, model_version, hash_chunk, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (chunk_id, embedding, dim, model_version, hash_chunk, time.time()))
                # Retirer de la file d'attente pending
                conn.execute("DELETE FROM pending_embeddings WHERE chunk_id = ?", (chunk_id,))
        finally:
            conn.close()

    def add_to_pending(self, chunk_id: int, last_error: str) -> None:
        conn = self.get_connection()
        try:
            with conn:
                # Retry après 30s initialement, avec backoff géré lors du retraitement
                next_retry = time.time() + 30
                conn.execute("""
                    INSERT OR REPLACE INTO pending_embeddings (chunk_id, attempts, last_error, next_retry_at)
                    VALUES (?, COALESCE((SELECT attempts FROM pending_embeddings WHERE chunk_id = ?) + 1, 1), ?, ?)
                """, (chunk_id, chunk_id, last_error, next_retry))
        finally:
            conn.close()

    def get_pending_embeddings(self) -> list[dict]:
        conn = self.get_connection()
        try:
            rows = conn.execute("""
                SELECT p.chunk_id, c.text, c.hash_chunk, p.attempts 
                FROM pending_embeddings p
                JOIN chunks c ON p.chunk_id = c.id
                WHERE p.next_retry_at <= ?
                LIMIT 50
            """, (time.time(),)).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def get_all_registered_files(self) -> dict[str, float]:
        conn = self.get_connection()
        try:
            rows = conn.execute("SELECT path, mtime FROM documents").fetchall()
            return {r["path"]: r["mtime"] for r in rows}
        finally:
            conn.close()
