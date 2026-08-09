#!/usr/bin/env python3
"""
Alexandria Core: Hybrid Search Router (RRF)
Moteur de fusion des classements lexicaux (FTS5) et sémantiques (ChromaDB)
Calibré pour MIDGARD (Ubuntu 24.04, 8 Go RAM, Exécution CPU unifiée)
"""

import os
import sqlite3
import re
from typing import List, Dict, Any, Tuple
import chromadb
from sentence_transformers import SentenceTransformer

# Verrous de configuration de l'infrastructure
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
DB_PATH = os.path.join(ROOT_DIR, "database", "alexandria_brain.db")
CHROMA_DIR = os.path.join(ROOT_DIR, "database", ".chroma_vectors")
MODEL_NAME = "all-MiniLM-L6-v2"

# Constantes de l'algorithme RRF
RRF_K = 60
TOP_N_RESULTS = 5


def execute_lexical_search(query: str, limit: int = 20) -> List[Tuple[str, str, str]]:
    """Interroge la table virtuelle FTS5 de SQLite et retourne les candidats triés par BM25."""
    if not os.path.exists(DB_PATH):
        return []
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Nettoyage initial simple des guillemets
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
        # Fallback automatique en cas d'erreur de syntaxe FTS5 (caractères spéciaux)
        # On ne garde que les mots alphanumériques pour une recherche textuelle simple
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
    """Calcule l'embedding de la requête en CPU local et extrait le top K de ChromaDB."""
    query_embedding = encoder.encode(query, show_progress_bar=False).tolist()
    
    results = chroma_collection.query(
        query_embeddings=[query_embedding],
        n_results=limit
    )
    return results


def compute_rrf(lexical_results: List[Tuple[str, str, str]], semantic_results: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Applique l'algorithme Reciprocal Rank Fusion sur l'intersection des deux index."""
    rrf_scores: Dict[str, Dict[str, Any]] = {}

    # 1. Traitement des rangs du moteur Lexical (SQLite FTS5)
    for rank, (chunk_id, filepath, content) in enumerate(lexical_results, start=1):
        if chunk_id not in rrf_scores:
            rrf_scores[chunk_id] = {"filepath": filepath, "content": content, "score": 0.0}
        rrf_scores[chunk_id]["score"] += 1.0 / (RRF_K + rank)

    # 2. Traitement des rangs du moteur Sémantique (ChromaDB)
    if semantic_results and "ids" in semantic_results and semantic_results["ids"] and len(semantic_results["ids"]) > 0:
        ids = semantic_results["ids"][0]
        documents = semantic_results.get("documents", [[]])[0]
        metadatas = semantic_results.get("metadatas", [[]])[0]
        
        for rank, chunk_id in enumerate(ids, start=1):
            idx = rank - 1
            if chunk_id not in rrf_scores:
                # Vérification de sécurité des indices de ChromaDB
                filepath = metadatas[idx]["filepath"] if idx < len(metadatas) and metadatas[idx] and "filepath" in metadatas[idx] else "unknown_file"
                content = documents[idx] if idx < len(documents) else ""
                rrf_scores[chunk_id] = {"filepath": filepath, "content": content, "score": 0.0}
            rrf_scores[chunk_id]["score"] += 1.0 / (RRF_K + rank)

    # Tri de masse selon le score RRF décroissant
    sorted_chunks = sorted(rrf_scores.values(), key=lambda x: x["score"], reverse=True)
    return sorted_chunks[:TOP_N_RESULTS]


def hybrid_query(query_text: str) -> None:
    """Point d'entrée unique orchestrant la recherche hybride."""
    # Connexion au stockage vectoriel local avec gestion d'erreurs d'initialisation
    if not os.path.exists(CHROMA_DIR):
        print(f"[-] Erreur : Index sémantique inexistant sous {CHROMA_DIR}.")
        print("[*] Fallback temporaire sur la recherche lexicale pure...")
        lexical_hits = execute_lexical_search(query_text, limit=20)
        print(" ────── ")
        print(f"[✓] Synthèse Lexicale Pure (ChromaDB manquant). Top {len(lexical_hits)} fragments :")
        for idx, (chunk_id, filepath, content) in enumerate(lexical_hits, start=1):
            print(f"\n[{idx}] SOURCE : {filepath} (ID: {chunk_id[:8]}...)")
            print(f"--- CONTENU ---\n{content.strip()}\n---------------")
        print(" ────── ")
        return

    chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)
    try:
        chroma_collection = chroma_client.get_collection(name="alexandria_vault")
    except Exception as e:
        print(f"[-] Erreur de chargement de la collection ChromaDB : {e}")
        print("[*] Fallback temporaire sur la recherche lexicale pure...")
        lexical_hits = execute_lexical_search(query_text, limit=20)
        print(" ────── ")
        print(f"[✓] Synthèse Lexicale Pure (ChromaDB inaccessible). Top {len(lexical_hits)} fragments :")
        for idx, (chunk_id, filepath, content) in enumerate(lexical_hits, start=1):
            print(f"\n[{idx}] SOURCE : {filepath} (ID: {chunk_id[:8]}...)")
            print(f"--- CONTENU ---\n{content.strip()}\n---------------")
        print(" ────── ")
        return
    
    # Chargement du transformer léger
    encoder = SentenceTransformer(MODEL_NAME, device="cpu")

    print(f"[*] Analyse hybride de la requête : '{query_text}'")
    
    # Exécution des scans parallèles
    lexical_hits = execute_lexical_search(query_text, limit=20)
    semantic_hits = execute_semantic_search(query_text, chroma_collection, encoder, limit=20)

    # Calcul mathématique RRF
    final_context = compute_rrf(lexical_hits, semantic_hits)

    print(" ────── ")
    print(f"[✓] Synthèse RRF achevée. Top {len(final_context)} fragments retenus :")
    for idx, chunk in enumerate(final_context, start=1):
        print(f"\n[{idx}] SOURCE : {chunk['filepath']} (Score RRF: {chunk['score']:.5f})")
        print(f"--- CONTENU ---\n{chunk['content'].strip()}\n---------------")
    print(" ────── ")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        hybrid_query(" ".join(sys.argv[1:]))
    else:
        print("[!] Erreur : Veuillez formuler une requête textuelle.")
