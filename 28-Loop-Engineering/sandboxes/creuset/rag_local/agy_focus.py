#!/usr/bin/env python3
# agy_focus.py — Moteur de recherche et de ciblage contextuel local FTS / Vectoriel
import os
import sys
import shutil
import chromadb
from chromadb.utils import embedding_functions

def focus_context(query, target_dir, limit=5):
    cache_dir = os.path.join(target_dir, ".agy_cache")
    if not os.path.exists(cache_dir):
        print(f"[-] Index sémantique inexistant dans {cache_dir}. Veuillez d'abord indexer le répertoire.")
        sys.exit(1)
        
    # Configuration du répertoire temporaire de contexte
    ctx_dir = "/tmp/agy_ctx"
    if os.path.exists(ctx_dir):
        try:
            shutil.rmtree(ctx_dir)
        except Exception as e:
            print(f"[-] Impossible de vider {ctx_dir} : {e}")
    os.makedirs(ctx_dir, exist_ok=True)
    
    # Connexion à la base ChromaDB locale
    client = chromadb.PersistentClient(path=cache_dir)
    emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    
    try:
        collection = client.get_collection(
            name="agy_codebase",
            embedding_function=emb_fn  # type: ignore
        )
    except Exception as e:
        print(f"[-] Erreur d'accès à la collection de cache : {e}. Lancez l'indexation.")
        sys.exit(1)
        
    # Recherche sémantique
    results = collection.query(
        query_texts=[query],
        n_results=limit
    )
    
    metadatas = []
    if results and results.get("metadatas"):
        res_meta = results.get("metadatas")
        if res_meta and res_meta[0]:
            metadatas = res_meta[0]
    
    if not metadatas:
        print("[*] Aucun contexte pertinent identifié pour cette requête.")
        sys.exit(0)
        
    print(f"[*] Fragments sémantiques identifiés : {len(metadatas)}")
    
    copied_files = set()
    for meta in metadatas:
        if not meta or not isinstance(meta, dict):
            continue
        rel_path = meta.get("filepath")
        if not isinstance(rel_path, str):
            continue
        if rel_path in copied_files:
            continue
            
        src_file = os.path.join(target_dir, rel_path)
        dest_file = os.path.join(ctx_dir, rel_path)
        
        if os.path.exists(src_file):
            os.makedirs(os.path.dirname(dest_file), exist_ok=True)
            try:
                shutil.copy2(src_file, dest_file)
                copied_files.add(rel_path)
                print(f"[+] Focus : {rel_path}")
            except Exception as e:
                print(f"[-] Échec de copie pour {rel_path} : {e}")
        else:
            print(f"[-] Fichier introuvable localement : {rel_path}")
            
    print(f"[✓] Contexte focalisé généré dans {ctx_dir} ({len(copied_files)} fichiers copiés).")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 agy_focus.py <query> <target_directory> [limit]")
        sys.exit(1)
        
    user_query = sys.argv[1]
    proj_dir = os.path.abspath(sys.argv[2])
    search_limit = int(sys.argv[3]) if len(sys.argv) > 3 else 5
    
    focus_context(user_query, proj_dir, search_limit)
