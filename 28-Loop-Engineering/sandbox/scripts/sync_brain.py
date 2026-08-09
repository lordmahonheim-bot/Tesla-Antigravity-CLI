#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
sync_brain.py (V1) - Script d'indexation par lot (batch) pour le second cerveau SQLite FTS5.
Exclut explicitement les Archives et Meta, utilise le mode WAL et gère les busy timeouts.
Extrait les métadonnées frontmatter et les relations graphiques (liens bidirectionnels).
"""

import os
import re
import sqlite3
import frontmatter
from pathlib import Path

VAULT_DIR = Path("/home/lord-mahonheim/bifrost/tesla/Avalon")
DB_PATH = Path("/home/lord-mahonheim/bifrost/tesla/DataBase/avalon_brain.db")

# S'assurer que le répertoire de la base de données existe
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

def init_db():
    """Initialise la base de données SQLite avec FTS5 et active le mode WAL."""
    conn = sqlite3.connect(str(DB_PATH), timeout=10.0)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA busy_timeout=10000;")
    
    # Création de la table FTS5
    # Note : FTS5 ne supporte pas de clé primaire standard. Le filepath sera la clé logique.
    conn.execute("""
    CREATE VIRTUAL TABLE IF NOT EXISTS fts_vault_index USING fts5(
        filepath,
        title,
        type,          -- decision | fait | reference | tache
        tags,          -- tags concaténés (ex: "#media/audio #statut/valide")
        content,       -- contenu textuel épuré
        last_modified,
        tokenize="unicode61"
    );
    """)
    
    # Création de la table de relations du graphe
    conn.execute("""
    CREATE TABLE IF NOT EXISTS relations_graphe (
        source_path TEXT,
        target_path TEXT,
        relation_type TEXT, -- depend_de | fait_reference_a | MOC_contient
        PRIMARY KEY (source_path, target_path, relation_type)
    );
    """)
    
    conn.commit()
    conn.close()

def extract_links(content):
    """Extrait les liens Obsidian [[Lien]] ou [[Lien|Texte]] d'un texte."""
    # Pattern pour [[Nom de la note]] ou [[Nom de la note|Texte alternatif]]
    pattern = r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]'
    return [link.strip() for link in re.findall(pattern, content)]

def resolve_target_path(target_name, all_files):
    """Tente de résoudre le chemin physique d'une note cible à partir de son nom Obsidian."""
    # Chercher si le nom correspond à un fichier existant dans le dictionnaire
    target_lower = target_name.lower().replace(" ", "-")
    for filepath, title in all_files.items():
        # Vérification sur le titre de la note ou le nom du fichier
        file_stem = Path(filepath).stem.lower().replace(" ", "-")
        if file_stem == target_lower or title.lower() == target_name.lower():
            return filepath
    # Si non résolu, on retourne simplement le nom nettoyé comme chemin relatif virtuel
    return target_name

def sync():
    """Parcourt le Vault, extrait les données des fichiers MD conformes et indexe dans SQLite."""
    print("[*] Démarrage de la synchronisation du Second Cerveau...")
    init_db()
    
    conn = sqlite3.connect(str(DB_PATH), timeout=10.0)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA busy_timeout=10000;")
    
    # 1. Lister tous les fichiers .md du Vault pour résolution ultérieure des liens
    all_files = {} # (relative_filepath -> title)
    md_files_to_index = []
    
    for root, dirs, files in os.walk(str(VAULT_DIR)):
        # Filtrage strict : ignorer 04-Archives et _Meta
        if "04-Archives" in root or "_Meta" in root or ".obsidian" in root:
            continue
            
        for file in files:
            if file.endswith(".md"):
                full_path = Path(root) / file
                rel_path = full_path.relative_to(VAULT_DIR)
                
                # Charger le fichier temporairement pour récupérer le titre
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        post = frontmatter.load(f)
                    title = post.get("title", full_path.stem)
                    all_files[str(rel_path)] = title
                    md_files_to_index.append((full_path, rel_path))
                except Exception as e:
                    print(f"[!] Erreur de lecture préliminaire pour {rel_path}: {e}")

    print(f"[+] {len(md_files_to_index)} fichiers identifiés pour l'indexation active.")

    # 2. Nettoyer les anciennes relations de la base pour repartir propre
    # (Puisqu'on fait une synchro par lot, on recrée les relations à chaque fois pour éviter les orphelins)
    conn.execute("DELETE FROM relations_graphe;")
    
    # 3. Traiter et indexer chaque fichier
    indexed_count = 0
    for full_path, rel_path in md_files_to_index:
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                post = frontmatter.load(f)
            
            # Extraction des métadonnées
            title = post.get("title", full_path.stem)
            note_type = post.get("type", "reference")
            
            # Gestion des tags (peut être une liste ou une string)
            tags_raw = post.get("tags", [])
            if isinstance(tags_raw, list):
                tags = " ".join([f"#{t.lstrip('#')}" for t in tags_raw])
            else:
                tags = str(tags_raw)
                
            content = post.content
            last_modified = os.path.getmtime(full_path)
            
            # Nettoyer l'index FTS5 pour ce chemin spécifique
            conn.execute("DELETE FROM fts_vault_index WHERE filepath = ?;", (str(rel_path),))
            
            # Insérer dans l'index FTS5
            conn.execute("""
            INSERT INTO fts_vault_index (filepath, title, type, tags, content, last_modified)
            VALUES (?, ?, ?, ?, ?, ?);
            """, (str(rel_path), title, note_type, tags, content, str(last_modified)))
            
            # Extraction et insertion des relations
            links = extract_links(content)
            
            # Déterminer le type de relation
            # Par défaut : fait_reference_a
            # Si le fichier source est dans _MOC : MOC_contient
            # Si le fichier source est lié par un prérequis logique : depend_de
            rel_type_default = "fait_reference_a"
            if "_MOC" in str(rel_path):
                rel_type_default = "MOC_contient"
                
            for link in links:
                target_path = resolve_target_path(link, all_files)
                
                # Détection de dépendance logique (si le contexte autour du lien contient "dépend de", "requis", "prérequis")
                # Recherche d'un motif simple dans le contenu de la note
                specific_rel_type = rel_type_default
                context_pattern = rf"(?:dépend\s+de|requis|prérequis|depend\s+on)[^\n]*?\[\[{re.escape(link)}"
                if re.search(context_pattern, content, re.IGNORECASE):
                    specific_rel_type = "depend_de"
                
                try:
                    conn.execute("""
                    INSERT OR IGNORE INTO relations_graphe (source_path, target_path, relation_type)
                    VALUES (?, ?, ?);
                    """, (str(rel_path), str(target_path), specific_rel_type))
                except sqlite3.Error as e:
                    print(f"[!] Erreur d'insertion de relation {rel_path} -> {target_path}: {e}")
            
            indexed_count += 1
            
        except Exception as e:
            print(f"[!] Échec de l'indexation de {rel_path}: {e}")
            
    conn.commit()
    
    # 4. Nettoyer les fiches obsolètes de fts_vault_index qui n'existent plus sur le disque
    # En listant tous les filepaths en base et en supprimant ceux absents du scan actuel
    cursor = conn.cursor()
    cursor.execute("SELECT filepath FROM fts_vault_index;")
    db_paths = [row[0] for row in cursor.fetchall()]
    
    current_rel_paths = {str(rel_path) for _, rel_path in md_files_to_index}
    deleted_count = 0
    for db_path in db_paths:
        if db_path not in current_rel_paths:
            conn.execute("DELETE FROM fts_vault_index WHERE filepath = ?;", (db_path,))
            deleted_count += 1
            
    conn.commit()
    conn.close()
    
    print(f"[+] Synchronisation terminée : {indexed_count} fiches indexées, {deleted_count} fiches obsolètes retirées.")

if __name__ == "__main__":
    sync()
