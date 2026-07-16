#!/usr/bin/env python3
"""
Alexandria Core: Hybrid Search Router (RRF + SQLite WAL + NumPy local)
Moteur de fusion optimisé sous la doctrine du Vigilum Codex.
"""

import os
import re
import numpy as np
from dotenv import load_dotenv
load_dotenv()
from typing import List, Dict, Any, Tuple
from core.database_manager import DatabaseManager
from core.embeddings import GeminiEmbeddingProvider

# Configuration de l'infrastructure via variables d'environnement
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
DB_PATH = os.getenv("ALEXANDRIA_DB_PATH", os.path.join(ROOT_DIR, "Avalon", "03-Resources", "alexandria_brain.db"))
MODEL_NAME = os.getenv("ALEXANDRIA_MODEL_NAME", "models/gemini-embedding-001")
DIMENSION = int(os.getenv("ALEXANDRIA_EMBEDDING_DIM", "768"))

# Constantes de l'algorithme RRF
RRF_K = 60
TOP_N_RESULTS = 5


def execute_lexical_search(db_manager: DatabaseManager, query: str, limit: int = 100) -> List[Tuple[str, str, str]]:
    """Interroge la table virtuelle FTS5 de SQLite et retourne les candidats triés par BM25."""
    conn = db_manager.get_connection()
    query_clean = query.replace("'", " ")
    results = []
    try:
        cursor = conn.execute("""
            SELECT chunk_id, filepath, content 
            FROM fts_vault_index 
            WHERE fts_vault_index MATCH ? 
            ORDER BY rank 
            LIMIT ?
        """, (query_clean, limit))
        results = [(row["chunk_id"], row["filepath"], row["content"]) for row in cursor.fetchall()]
    except Exception:
        # Fallback automatique en cas d'erreur de syntaxe FTS5 (caractères spéciaux)
        query_fallback = " ".join(re.findall(r"\w+", query_clean))
        if query_fallback.strip():
            try:
                cursor = conn.execute("""
                    SELECT chunk_id, filepath, content 
                    FROM fts_vault_index 
                    WHERE fts_vault_index MATCH ? 
                    ORDER BY rank 
                    LIMIT ?
                """, (query_fallback, limit))
                results = [(row["chunk_id"], row["filepath"], row["content"]) for row in cursor.fetchall()]
            except Exception:
                results = []
    finally:
        conn.close()
    return results


def execute_hybrid_search(db_manager: DatabaseManager, provider: GeminiEmbeddingProvider, query_text: str) -> List[Dict[str, Any]]:
    """Exécute la recherche hybride avec RRF combinant FTS5 et similarité cosinus NumPy locale."""
    # 1. Génération de l'embedding de la requête
    query_vector = None
    try:
        # Tenter d'obtenir l'embedding via le provider cloud
        embeddings = provider.generate_embeddings([query_text])
        if embeddings:
            query_vector = embeddings[0]
    except Exception as e:
        print(f"[-] Mode offline degrade active : Impossible de generer l'embedding de la requete ({e})")
        print("[*] Bascule sur la recherche lexicale pure...")

    # 2. Pré-filtrage FTS5 (Top 100 candidats lexicaux)
    lexical_hits = execute_lexical_search(db_manager, query_text, limit=100)
    if not lexical_hits:
        return []

    # 3. Récupération des embeddings pour ces candidats
    semantic_scores = {}
    if query_vector is not None:
        chunk_hashes = [hit[0] for hit in lexical_hits]
        conn = db_manager.get_connection()
        try:
            # Charger les embeddings existants pour le modèle actif
            placeholders = ",".join("?" for _ in chunk_hashes)
            query_sql = f"""
                SELECT hash_chunk, embedding FROM vector_registry 
                WHERE hash_chunk IN ({placeholders}) AND model_version = ?
            """
            rows = conn.execute(query_sql, chunk_hashes + [provider.model_version]).fetchall()
            
            # Calculer les similarités cosinus (dot product sur vecteurs normalisés)
            for row in rows:
                chunk_hash = row["hash_chunk"]
                embedding_blob = row["embedding"]
                doc_vector = np.frombuffer(embedding_blob, dtype=np.float32)
                if len(doc_vector) == len(query_vector):
                    # Dot product
                    similarity = float(np.dot(query_vector, doc_vector))
                    semantic_scores[chunk_hash] = similarity
        except Exception as e:
            print(f"[-] Erreur lors du calcul de similarite sémantique NumPy : {e}")
        finally:
            conn.close()

    # 4. Ordonnancer les classements pour RRF
    # Classement Lexical (trié par ordre de retour FTS5)
    lexical_rank = {hit[0]: rank for rank, hit in enumerate(lexical_hits, start=1)}
    
    # Classement Sémantique (trié par score de similarité décroissant)
    sorted_semantic = sorted(semantic_scores.items(), key=lambda x: x[1], reverse=True)
    semantic_rank = {chunk_hash: rank for rank, (chunk_hash, _) in enumerate(sorted_semantic, start=1)}

    # 5. Fusion RRF k=60
    rrf_scores = {}
    for hit in lexical_hits:
        chunk_hash, filepath, content = hit
        score = 0.0
        
        # Contribution lexicale
        if chunk_hash in lexical_rank:
            score += 1.0 / (RRF_K + lexical_rank[chunk_hash])
            
        # Contribution sémantique
        if chunk_hash in semantic_rank:
            score += 1.0 / (RRF_K + semantic_rank[chunk_hash])
            
        rrf_scores[chunk_hash] = {
            "chunk_id": chunk_hash,
            "filepath": filepath,
            "content": content,
            "score": score,
            "semantic_score": semantic_scores.get(chunk_hash, 0.0)
        }

    # Tri final des candidats fusionnés par score RRF décroissant
    sorted_results = sorted(rrf_scores.values(), key=lambda x: x["score"], reverse=True)
    return sorted_results[:TOP_N_RESULTS]


def hybrid_query(query_text: str) -> None:
    """Point d'entrée CLI pour interroger le routeur de recherche."""
    db_manager = DatabaseManager(DB_PATH)
    provider = GeminiEmbeddingProvider(model_name=MODEL_NAME, dimension=DIMENSION)

    print(f"[*] Analyse hybride (V2 - RRF + NumPy) pour : '{query_text}'")
    results = execute_hybrid_search(db_manager, provider, query_text)

    print(" ────── ")
    print(f"[✓] Synthese RRF achevee. Top {len(results)} fragments retenus :")
    for idx, chunk in enumerate(results, start=1):
        print(f"\n[{idx}] SOURCE : {chunk['filepath']} (Score RRF: {chunk['score']:.5f}, Sem: {chunk['semantic_score']:.3f})")
        print(f"--- CONTENU ---\n{chunk['content'].strip()}\n---------------")
    print(" ────── ")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        hybrid_query(" ".join(sys.argv[1:]))
    else:
        print("[!] Erreur : Veuillez formuler une requete textuelle.")
