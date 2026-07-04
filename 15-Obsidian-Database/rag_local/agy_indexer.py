#!/usr/bin/env python3
# agy_indexer.py — Indexeur sémantique local pour RAG embarqué
import os
import sys
import subprocess
import chromadb
from chromadb.utils import embedding_functions

def get_files_to_index(directory):
    # Tente d'utiliser git pour lister les fichiers non ignorés
    try:
        result = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
            cwd=directory,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        files = [os.path.join(directory, f) for f in result.stdout.splitlines() if os.path.isfile(os.path.join(directory, f))]
        # Exclusion stricte des répertoires de build, caches et environnements virtuels
        excluded_patterns = [".venv", "node_modules", ".git", "__pycache__", ".agy_cache", ".obsidian"]
        filtered_files = []
        for f in files:
            if not any(pat in f for pat in excluded_patterns):
                filtered_files.append(f)
        return filtered_files
    except Exception:
        # Fallback sur un parcours manuel du système de fichiers
        files = []
        excluded_dirs = {".venv", "node_modules", ".git", "__pycache__", ".agy_cache", ".obsidian"}
        for root, dirs, filenames in os.walk(directory):
            # Modification de dirs in-place pour exclure les répertoires indésirables
            dirs[:] = [d for d in dirs if d not in excluded_dirs and not d.startswith('.')]
            for f in filenames:
                files.append(os.path.join(root, f))
        return files

def chunk_text(text, chunk_size=800, overlap=150):
    chunks = []
    if len(text) <= chunk_size:
        return [text]
    
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += (chunk_size - overlap)
    return chunks

def index_directory(directory, cache_dir):
    os.makedirs(cache_dir, exist_ok=True)
    
    # Initialisation du client persistent ChromaDB
    client = chromadb.PersistentClient(path=cache_dir)
    
    # Utilisation d'un modèle d'embeddings léger local (MiniLM)
    emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    
    # Récupération ou création de la collection
    collection = client.get_or_create_collection(
        name="agy_codebase",
        embedding_function=emb_fn  # type: ignore
    )
    
    files = get_files_to_index(directory)
    print(f"[*] Analyse du dossier : {directory}")
    print(f"[*] Fichiers identifiés pour indexation : {len(files)}")
    
    documents = []
    metadatas = []
    ids = []
    
    # Nettoyage de l'ancienne collection pour garantir l'idempotence
    try:
        existing = collection.get()
        if existing and existing["ids"]:
            collection.delete(ids=existing["ids"])
            print("[*] Index précédent purgé avec succès.")
    except Exception as e:
        print(f"[*] Initialisation d'une collection vierge : {e}")
        
    for filepath in files:
        try:
            # Ignorer les formats binaires évidents
            if filepath.endswith(('.png', '.jpg', '.jpeg', '.gif', '.pdf', '.zip', '.tar', '.gz', '.db', '.sqlite', '.exe', '.bin')):
                continue
                
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            if not content.strip():
                continue
                
            chunks = chunk_text(content)
            rel_path = os.path.relpath(filepath, directory)
            
            for idx, chunk in enumerate(chunks):
                documents.append(chunk)
                metadatas.append({
                    "filepath": rel_path,
                    "filename": os.path.basename(filepath),
                    "chunk_index": idx
                })
                ids.append(f"{rel_path}_chunk_{idx}")
                
        except Exception as e:
            print(f"[-] Échec de lecture pour {filepath} : {e}")
            
    # Insertion des chunks par lots
    batch_size = 500
    for i in range(0, len(documents), batch_size):
        end_idx = min(i + batch_size, len(documents))
        collection.add(
            documents=documents[i:end_idx],
            metadatas=metadatas[i:end_idx],
            ids=ids[i:end_idx]
        )
        print(f"[+] Indexation des fragments {i} à {end_idx} sur {len(documents)}...")
        
    print(f"[✓] Indexation sémantique achevée. Chunks totaux stockés : {collection.count()}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 agy_indexer.py <directory_to_index>")
        sys.exit(1)
    target_dir = os.path.abspath(sys.argv[1])
    cache_path = os.path.join(target_dir, ".agy_cache")
    index_directory(target_dir, cache_path)
