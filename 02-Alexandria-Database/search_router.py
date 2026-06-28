#!/usr/bin/env python3
"""
02-Alexandria-Database: Hybrid Search Router (RRF)
Fuses SQLite FTS5 lexical ranking and ChromaDB semantic search using RRF
"""
import os
import sqlite3
import re
import sys
from typing import List, Dict, Any, Tuple

try:
    import chromadb
    from sentence_transformers import SentenceTransformer
except ImportError:
    print("[-] Missing dependencies (chromadb / sentence-transformers).")
    sys.exit(1)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE = os.environ.get("TESLA_WORKSPACE", os.path.dirname(BASE_DIR))

DB_PATH = os.environ.get("ALEXANDRIA_DB_PATH", os.path.join(WORKSPACE, "database", "alexandria_brain.db"))
CHROMA_DIR = os.environ.get("ALEXANDRIA_CHROMA_DIR", os.path.join(WORKSPACE, "database", ".chroma_vectors"))
MODEL_NAME = os.environ.get("ALEXANDRIA_MODEL", "all-MiniLM-L6-v2")

RRF_K = 60
TOP_N_RESULTS = 5

def execute_lexical_search(query: str, limit: int = 20) -> List[Tuple[str, str, str]]:
    if not os.path.exists(DB_PATH):
        return []
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    query_clean = query.replace("'", " ")
    results = []
    try:
        cursor.execute("""
            SELECT chunk_id, filepath, content 
            FROM fts_vault_index 
            WHERE fts_vault_index MATCH ? 
            ORDER BY rank 
            LIMIT ?
        """, (query_clean, limit))
        results = cursor.fetchall()
    except sqlite3.OperationalError:
        query_fallback = " ".join(re.findall(r"\w+", query_clean))
        if query_fallback.strip():
            try:
                cursor.execute("""
                    SELECT chunk_id, filepath, content 
                    FROM fts_vault_index 
                    WHERE fts_vault_index MATCH ? 
                    ORDER BY rank 
                    LIMIT ?
                """, (query_fallback, limit))
                results = cursor.fetchall()
            except sqlite3.OperationalError:
                results = []
    conn.close()
    return results

def execute_semantic_search(query: str, chroma_collection: Any, encoder: SentenceTransformer, limit: int = 20) -> Dict[str, Any]:
    query_embedding = encoder.encode(query, show_progress_bar=False).tolist()
    return chroma_collection.query(query_embeddings=[query_embedding], n_results=limit)

def compute_rrf(lexical_results: List[Tuple[str, str, str]], semantic_results: Dict[str, Any]) -> List[Dict[str, Any]]:
    rrf_scores: Dict[str, Dict[str, Any]] = {}
    for rank, (chunk_id, filepath, content) in enumerate(lexical_results, start=1):
        if chunk_id not in rrf_scores:
            rrf_scores[chunk_id] = {"filepath": filepath, "content": content, "score": 0.0}
        rrf_scores[chunk_id]["score"] += 1.0 / (RRF_K + rank)

    if semantic_results and "ids" in semantic_results and semantic_results["ids"] and len(semantic_results["ids"]) > 0:
        ids = semantic_results["ids"][0]
        documents = semantic_results.get("documents", [[]])[0]
        metadatas = semantic_results.get("metadatas", [[]])[0]
        for rank, chunk_id in enumerate(ids, start=1):
            idx = rank - 1
            if chunk_id not in rrf_scores:
                filepath = metadatas[idx]["filepath"] if idx < len(metadatas) and metadatas[idx] else "unknown"
                content = documents[idx] if idx < len(documents) else ""
                rrf_scores[chunk_id] = {"filepath": filepath, "content": content, "score": 0.0}
            rrf_scores[chunk_id]["score"] += 1.0 / (RRF_K + rank)

    sorted_chunks = sorted(rrf_scores.values(), key=lambda x: x["score"], reverse=True)
    return sorted_chunks[:TOP_N_RESULTS]

def hybrid_query(query_text: str) -> None:
    if not os.path.exists(CHROMA_DIR):
        print(f"[-] Semantic index missing ({CHROMA_DIR}). Running lexical fallback...")
        lexical_hits = execute_lexical_search(query_text, limit=20)
        print(" ────── ")
        for idx, (_, filepath, content) in enumerate(lexical_hits, start=1):
            print(f"\n[{idx}] SOURCE: {filepath}\n{content.strip()}")
        print(" ────── ")
        return

    chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)
    try:
        chroma_collection = chroma_client.get_collection(name="alexandria_vault")
    except Exception as e:
        print(f"[-] ChromaDB Error: {e}. Running lexical fallback...")
        lexical_hits = execute_lexical_search(query_text, limit=20)
        return

    encoder = SentenceTransformer(MODEL_NAME, device="cpu")
    lexical_hits = execute_lexical_search(query_text, limit=20)
    semantic_hits = execute_semantic_search(query_text, chroma_collection, encoder, limit=20)
    final_context = compute_rrf(lexical_hits, semantic_hits)

    print(" ────── ")
    for idx, chunk in enumerate(final_context, start=1):
        print(f"\n[{idx}] SOURCE: {chunk['filepath']} (RRF Score: {chunk['score']:.5f})")
        print(f"--- CONTENT ---\n{chunk['content'].strip()}\n---------------")
    print(" ────── ")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        hybrid_query(" ".join(sys.argv[1:]))
    else:
        print("[!] Empty query. Usage: python search_router.py 'your query'")
