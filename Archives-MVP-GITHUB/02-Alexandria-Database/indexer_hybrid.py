#!/usr/bin/env python3
"""
02-Alexandria-Database: Incremental Hybrid Indexer
Indexes documentation using lexical SQLite FTS5 and semantic ChromaDB
"""
import os
import sqlite3
import hashlib
from typing import List, Any
import sys

# Conditional load of heavy dependencies
try:
    import chromadb
    from sentence_transformers import SentenceTransformer
except ImportError:
    print("[-] Missing dependencies (chromadb / sentence-transformers).")
    print("[*] Please install them: pip install chromadb sentence-transformers")
    sys.exit(1)

# Dynamic directories configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE = os.environ.get("TESLA_WORKSPACE", os.path.dirname(BASE_DIR))

DB_PATH = os.environ.get("ALEXANDRIA_DB_PATH", os.path.join(WORKSPACE, "database", "alexandria_brain.db"))
CHROMA_DIR = os.environ.get("ALEXANDRIA_CHROMA_DIR", os.path.join(WORKSPACE, "database", ".chroma_vectors"))
VAULT_DIR = os.environ.get("ALEXANDRIA_VAULT_DIR", os.path.join(WORKSPACE, "vault"))
MODEL_NAME = os.environ.get("ALEXANDRIA_MODEL", "all-MiniLM-L6-v2")

CHUNK_SIZE = 500
CHUNK_OVERLAP = 100

def init_infrastructure() -> None:
    """Initializes sqlite database and vault folders."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    os.makedirs(CHROMA_DIR, exist_ok=True)
    os.makedirs(VAULT_DIR, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS file_registry (
            filepath TEXT PRIMARY KEY,
            last_modified REAL NOT NULL
        )
    """)
    try:
        cursor.execute("""
            CREATE VIRTUAL TABLE fts_vault_index USING fts5(
                chunk_id,
                filepath,
                content
            )
        """)
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.close()

def generate_deterministic_id(filepath: str, chunk_index: int) -> str:
    key = f"{filepath}#chunk_{chunk_index}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()

def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    chunks = []
    start = 0
    if len(text) <= size:
        return [text] if text.strip() else []
    while start < len(text):
        end = start + size
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk)
        start += size - overlap
    return chunks

def purge_file_index(filepath: str, chroma_collection: Any) -> None:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM fts_vault_index WHERE filepath = ?", (filepath,))
    conn.commit()
    conn.close()
    try:
        chroma_collection.delete(where={"filepath": filepath})
    except Exception:
        pass

def index_file(filepath: str, chroma_collection: Any, encoder: SentenceTransformer) -> None:
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    rel_path = os.path.relpath(filepath, WORKSPACE)
    chunks = chunk_text(content)
    if not chunks:
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    chroma_ids = []
    chroma_texts = []
    chroma_metadatas = []

    for idx, chunk in enumerate(chunks):
        chunk_id = generate_deterministic_id(rel_path, idx)
        cursor.execute(
            "INSERT INTO fts_vault_index (chunk_id, filepath, content) VALUES (?, ?, ?)",
            (chunk_id, rel_path, chunk)
        )
        chroma_ids.append(chunk_id)
        chroma_texts.append(chunk)
        chroma_metadatas.append({"filepath": rel_path, "chunk_index": idx})

    embeddings = encoder.encode(chroma_texts, show_progress_bar=False).tolist()
    chroma_collection.add(
        embeddings=embeddings,
        documents=chunks,
        metadatas=chroma_metadatas,
        ids=chroma_ids
    )

    mtime = os.path.getmtime(filepath)
    cursor.execute(
        "INSERT OR REPLACE INTO file_registry (filepath, last_modified) VALUES (?, ?)",
        (rel_path, mtime)
    )
    conn.commit()
    conn.close()

def run_hybrid_indexation() -> None:
    print("[*] Initializing Alexandria Database structures...")
    init_infrastructure()
    chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)
    chroma_collection = chroma_client.get_or_create_collection(name="alexandria_vault")

    print(f"[*] Loading local semantic model ({MODEL_NAME})...")
    encoder = SentenceTransformer(MODEL_NAME, device="cpu")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT filepath, last_modified FROM file_registry")
    registry = dict(cursor.fetchall())
    conn.close()

    indexed_count = 0
    purged_count = 0
    seen_files = set()

    print(f"[*] Scanning vault path: {VAULT_DIR}")
    for root, _, files in os.walk(VAULT_DIR):
        for file in files:
            if file.endswith(".md") or file.endswith(".txt"):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, WORKSPACE)
                current_mtime = os.path.getmtime(full_path)
                seen_files.add(rel_path)

                if rel_path not in registry or current_mtime != registry[rel_path]:
                    print(f"[+] Change detected on file: {rel_path}")
                    purge_file_index(rel_path, chroma_collection)
                    index_file(full_path, chroma_collection, encoder)
                    indexed_count += 1

    orphan_files = set(registry.keys()) - seen_files
    if orphan_files:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        for orphan_path in orphan_files:
            print(f"[-] Removing deleted file from index: {orphan_path}")
            purge_file_index(orphan_path, chroma_collection)
            cursor.execute("DELETE FROM file_registry WHERE filepath = ?", (orphan_path,))
            purged_count += 1
        conn.commit()
        conn.close()

    env_name = os.environ.get("ENVIRONMENT_NAME", "local production")
    print(" ────── ")
    print(f"[✓] Hybrid scan completed on environment: {env_name}")
    print(f"    - Updated / Added files  : {indexed_count}")
    print(f"    - Orphaned files purged   : {purged_count}")
    print(" ────── ")

if __name__ == "__main__":
    run_hybrid_indexation()
