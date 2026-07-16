#!/usr/bin/env python3
"""
Alexandria Core: Incremental Hybrid Indexer (V2 - Cloud-Locale)
Moteur de double indexation lexicale (FTS5) et sémantique (Gemini Cloud)
Optimisé pour MIDGARD sous la doctrine du Vigilum Codex.
"""

import os
import hashlib
import frontmatter
from dotenv import load_dotenv
load_dotenv()
from typing import List
from core.database_manager import DatabaseManager
from core.embeddings import GeminiEmbeddingProvider
from core.security import PIIScrubber

# Verrous de configuration de l'infrastructure via variables d'environnement
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.getenv("ALEXANDRIA_DB_PATH", os.path.join(BASE_DIR, "Avalon", "03-Resources", "alexandria_brain.db"))
VAULT_DIR = os.getenv("ALEXANDRIA_VAULT_DIR", os.path.join(BASE_DIR, "Avalon"))
MODEL_NAME = os.getenv("ALEXANDRIA_MODEL_NAME", "models/gemini-embedding-001")
DIMENSION = int(os.getenv("ALEXANDRIA_EMBEDDING_DIM", "768"))

# Configuration de la fragmentation (Chunking)
CHUNK_SIZE = int(os.getenv("ALEXANDRIA_CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("ALEXANDRIA_CHUNK_OVERLAP", "200"))


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


def index_file(filepath: str, db_manager: DatabaseManager, provider: GeminiEmbeddingProvider) -> None:
    """Exécute la double écriture sémantique et lexicale d'un fichier."""
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    rel_path = os.path.relpath(filepath, BASE_DIR)
    
    # 1. Analyse YAML frontmatter et Gate de Confidentialité
    is_confidential = False
    try:
        post = frontmatter.loads(content)
        metadata = post.metadata
        body = post.content
        if metadata.get("confidential") is True or metadata.get("private") is True:
            is_confidential = True
    except Exception:
        body = content
        metadata = {}

    # Exclusion et sécurité stricte par dossier et fichier spécifique
    if "02-Areas/Confidentiel/" in filepath or "liste_projets_antigravity_v3.md" in filepath:
        is_confidential = True

    # 2. Calcul du hash global du document
    hash_doc = hashlib.sha256(content.encode("utf-8")).hexdigest()

    # 3. Enregistrement du document
    mtime = os.path.getmtime(filepath)
    doc_id = db_manager.register_document(rel_path, mtime, hash_doc, is_confidential)

    # 4. Découpage en fragments
    chunks = chunk_text(body)
    if not chunks:
        return

    # 5. Traitement individuel de chaque fragment
    for idx, chunk in enumerate(chunks):
        # Nettoyage de sécurité PII
        clean_text = PIIScrubber.scrub(chunk)
        hash_chunk = generate_deterministic_id(rel_path, idx)

        # Insertion du chunk
        chunk_id = db_manager.insert_chunk(doc_id, idx, clean_text, hash_chunk)

        # Insertion dans l'index FTS5
        db_manager.insert_fts_entry(hash_chunk, rel_path, clean_text)

        # Si confidentiel, interdiction absolue d'envoyer au Cloud
        if is_confidential:
            continue

        # Vérification du cache de déduplication local
        cached_embedding = db_manager.get_cached_embedding(hash_chunk, provider.model_version)
        if cached_embedding:
            db_manager.insert_embedding(chunk_id, hash_chunk, cached_embedding, provider.dimension, provider.model_version)
            continue

        # Si non présent dans le cache local, génération via l'API Gemini
        try:
            embeddings = provider.generate_embeddings([clean_text])
            if embeddings:
                vector = embeddings[0]
                embedding_blob = vector.tobytes()
                db_manager.insert_embedding(chunk_id, hash_chunk, embedding_blob, provider.dimension, provider.model_version)
        except Exception as e:
            # Mode hors-ligne dégradé : stockage dans la file d'attente pour traitement ultérieur
            db_manager.add_to_pending(chunk_id, str(e))


def process_pending_embeddings(db_manager: DatabaseManager, provider: GeminiEmbeddingProvider) -> None:
    """Tente de vider la file d'attente des embeddings échoués."""
    pending = db_manager.get_pending_embeddings()
    if not pending:
        return
    print(f"[*] Traitement de {len(pending)} embeddings en attente (mode reprise)...")
    for item in pending:
        chunk_id = item["chunk_id"]
        text = item["text"]
        hash_chunk = item["hash_chunk"]
        try:
            embeddings = provider.generate_embeddings([text])
            if embeddings:
                vector = embeddings[0]
                embedding_blob = vector.tobytes()
                db_manager.insert_embedding(chunk_id, hash_chunk, embedding_blob, provider.dimension, provider.model_version)
                print(f"[✓] Embedding resolu pour le chunk {chunk_id}")
        except Exception as e:
            db_manager.add_to_pending(chunk_id, str(e))
            print(f"[-] Echec persistant du traitement pour le chunk {chunk_id}: {e}")


def run_hybrid_indexation() -> None:
    """Orchestre la boucle globale d'indexation incrémentale."""
    print("[*] Connexion a la base de donnees et au provider d'embeddings...")
    db_manager = DatabaseManager(DB_PATH)
    provider = GeminiEmbeddingProvider(model_name=MODEL_NAME, dimension=DIMENSION)

    # Récupération du registre des fichiers déjà indexés
    registry = db_manager.get_all_registered_files()

    indexed_count = 0
    purged_count = 0
    seen_files = set()

    print(f"[*] Analyse du coffre fort de connaissances : {VAULT_DIR}")
    for root, dirs, files in os.walk(VAULT_DIR, followlinks=True):
        # Exclusion des répertoires cachés
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for file in files:
            if file.endswith(".md") or file.endswith(".txt"):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, BASE_DIR)
                current_mtime = os.path.getmtime(full_path)
                seen_files.add(rel_path)

                # Évaluation de la condition incrémentale
                if rel_path not in registry or current_mtime != registry[rel_path]:
                    print(f"[+] Modification detectee sur : {rel_path}")
                    # Suppression propre (en cascade sur SQLite)
                    db_manager.delete_document_by_path(rel_path)
                    # Ré-indexation
                    index_file(full_path, db_manager, provider)
                    indexed_count += 1

    # Détection et purge des fichiers orphelins (supprimés physiquement)
    orphan_files = set(registry.keys()) - seen_files
    if orphan_files:
        print(f"[*] Detection de {len(orphan_files)} fichier(s) orphelin(s). Purge en cours...")
        for orphan_path in orphan_files:
            print(f"[-] Fichier supprime detecte : {orphan_path}")
            db_manager.delete_document_by_path(orphan_path)
            purged_count += 1

    # Traitement de la file d'attente des embeddings en attente (offline retry)
    try:
        process_pending_embeddings(db_manager, provider)
    except Exception as e:
        print(f"[-] Impossible de traiter les embeddings en attente : {e}")

    print(" ────── ")
    print(f"[✓] Traitement acheve avec succes sur MIDGARD.")
    print(f"    - Fichiers mis a jour / ajoutes : {indexed_count}")
    print(f"    - Fichiers orphelins purges     : {purged_count}")
    print(" ────── ")


if __name__ == "__main__":
    run_hybrid_indexation()
