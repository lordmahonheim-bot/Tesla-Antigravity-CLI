#!/usr/bin/env python3
"""
Alexandria Core: Incremental Hybrid Indexer
Moteur de double indexation lexicale (FTS5) et sémantique (ChromaDB)
Calibré pour l'environnement MIDGARD (Ubuntu 24.04, 8 Go RAM, CPU pur)
"""

import os
import sqlite3
import hashlib
from typing import List, Any
import chromadb
from sentence_transformers import SentenceTransformer

# Verrous de configuration de l'infrastructure
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "alexandria_brain.db")
CHROMA_DIR = os.path.join(BASE_DIR, "database", ".chroma_vectors")
VAULT_DIR = os.path.join(BASE_DIR, "Avalon")  # Répertoire cible des fiches Markdown (Obsidian Avalon)
MODEL_NAME = "all-MiniLM-L6-v2"

# Stratégie de fragmentation (Chunking)
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100


def init_infrastructure() -> None:
    """Initialise les répertoires sous-jacents et les schémas de bases de données."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    os.makedirs(CHROMA_DIR, exist_ok=True)
    os.makedirs(VAULT_DIR, exist_ok=True)

    # Configuration du schéma SQLite d'autorité
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Table de suivi temporel pour l'indexation incrémentale
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS file_registry (
            filepath TEXT PRIMARY KEY,
            last_modified REAL NOT NULL
        )
    """)
    
    # Table virtuelle FTS5 pour la performance de la recherche lexicale pure
    try:
        cursor.execute("""
            CREATE VIRTUAL TABLE fts_vault_index USING fts5(
                chunk_id,
                filepath,
                content
            )
        """)
    except sqlite3.OperationalError:
        # La table FTS5 existe déjà nominalement
        pass
        
    conn.commit()
    conn.close()


def generate_deterministic_id(filepath: str, chunk_index: int) -> str:
    """Génère une clé pivot SHA-256 unique et reproductible par fragment."""
    key = f"{filepath}#chunk_{chunk_index}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """Découpe le contenu textuel via une fenêtre glissante normalisée."""
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
    """Élimine de manière atomique les anciennes entrées pour éviter les fragments fantômes."""
    # Purge SQLite FTS5
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM fts_vault_index WHERE filepath = ?", (filepath,))
    conn.commit()
    conn.close()

    # Purge ChromaDB Vector Store
    try:
        chroma_collection.delete(where={"filepath": filepath})
    except Exception:
        # Collection potentiellement vide lors du premier traitement
        pass


def index_file(filepath: str, chroma_collection: Any, encoder: SentenceTransformer) -> None:
    """Exécute la double écriture sémantique et lexicale d'un fichier."""
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    rel_path = os.path.relpath(filepath, BASE_DIR)
    chunks = chunk_text(content)
    
    if not chunks:
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Préparation des conteneurs pour ChromaDB Batch Insert
    chroma_ids = []
    chroma_texts = []
    chroma_metadatas = []

    for idx, chunk in enumerate(chunks):
        chunk_id = generate_deterministic_id(rel_path, idx)
        
        # Écriture Lexicale 1 : Insertion FTS5
        cursor.execute(
            "INSERT INTO fts_vault_index (chunk_id, filepath, content) VALUES (?, ?, ?)",
            (chunk_id, rel_path, chunk)
        )
        
        # Préparation Écriture Sémantique 2
        chroma_ids.append(chunk_id)
        chroma_texts.append(chunk)
        chroma_metadatas.append({"filepath": rel_path, "chunk_index": idx})

    # Calcul des embeddings en CPU local (sobriété RAM MIDGARD)
    embeddings = encoder.encode(chroma_texts, show_progress_bar=False).tolist()
    
    # Insertion de masse dans ChromaDB
    chroma_collection.add(
        embeddings=embeddings,
        documents=chunks,
        metadatas=chroma_metadatas,
        ids=chroma_ids
    )

    # Mise à jour du registre temporel d'autorité
    mtime = os.path.getmtime(filepath)
    cursor.execute(
        "INSERT OR REPLACE INTO file_registry (filepath, last_modified) VALUES (?, ?)",
        (rel_path, mtime)
    )

    conn.commit()
    conn.close()


def run_hybrid_indexation() -> None:
    """Orchestre la boucle globale d'indexation incrémentale."""
    print("[*] Initialisation des structures Alexandria...")
    init_infrastructure()

    print("[*] Connexion aux moteurs de stockage locaux...")
    # Initialisation ChromaDB Client persistant In-Process (Léger)
    chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)
    chroma_collection = chroma_client.get_or_create_collection(name="alexandria_vault")

    # Chargement du transformer sémantique
    print(f"[*] Chargement du modèle sémantique local CPU ({MODEL_NAME})...")
    encoder = SentenceTransformer(MODEL_NAME, device="cpu")

    # Chargement du registre des fichiers déjà indexés pour comparaison
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT filepath, last_modified FROM file_registry")
    registry = dict(cursor.fetchall())
    conn.close()

    indexed_count = 0
    purged_count = 0
    seen_files = set()

    print(f"[*] Analyse du coffre fort de connaissances : {VAULT_DIR}")
    for root, dirs, files in os.walk(VAULT_DIR, followlinks=True):
        # Exclusion des répertoires cachés (ex: .git, .obsidian)
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for file in files:
            if file.endswith(".md") or file.endswith(".txt"):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, BASE_DIR)
                current_mtime = os.path.getmtime(full_path)
                seen_files.add(rel_path)

                # Évaluation de la condition incrémentale Delta Temporel (stricte)
                if rel_path not in registry or current_mtime != registry[rel_path]:
                    print(f"[+] Modification détectée sur : {rel_path}")
                    purge_file_index(rel_path, chroma_collection)
                    index_file(full_path, chroma_collection, encoder)
                    indexed_count += 1
                else:
                    # Fichier intact, indexation ignorée pour préserver le CPU
                    pass

    # Détection et purge des fichiers orphelins (supprimés physiquement)
    orphan_files = set(registry.keys()) - seen_files
    if orphan_files:
        print(f"[*] Détection de {len(orphan_files)} fichier(s) orphelin(s). Purge en cours...")
        # Élimination des index lexical et sémantique de manière isolée
        for orphan_path in orphan_files:
            print(f"[-] Fichier supprimé détecté : {orphan_path}")
            purge_file_index(orphan_path, chroma_collection)
            
        # Mise à jour du registre de manière transactionnelle
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        for orphan_path in orphan_files:
            cursor.execute("DELETE FROM file_registry WHERE filepath = ?", (orphan_path,))
            purged_count += 1
        conn.commit()
        conn.close()

    print(" ────── ")
    print(f"[✓] Traitement achevé avec succès sur MIDGARD.")
    print(f"    - Fichiers mis à jour / ajoutés : {indexed_count}")
    print(f"    - Fichiers orphelins purgés     : {purged_count}")
    print(" ────── ")


if __name__ == "__main__":
    run_hybrid_indexation()
