#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
archive_note.py - Gère la mutation sémantique et l'historisation des notes.
Archive l'ancienne version d'une note dans 04-Archives et met à jour l'originale
avec des liens bidirectionnels de suivi historique.
"""

import os
import sys
import shutil
import datetime
import subprocess
from pathlib import Path
import frontmatter

VAULT_DIR = Path("/home/lord-mahonheim/bifrost/tesla/Avalon")
ARCHIVES_DIR = VAULT_DIR / "04-Archives"
SCRIPTS_DIR = Path("/home/lord-mahonheim/bifrost/tesla/sandbox/scripts")

def archive_and_update(note_rel_path_str, new_content_file_or_str):
    note_path = VAULT_DIR / note_rel_path_str
    if not note_path.exists():
        print(f"[!] La note cible n'existe pas : {note_rel_path_str}")
        return False
        
    # Lire le nouveau contenu
    if os.path.exists(new_content_file_or_str):
        with open(new_content_file_or_str, "r", encoding="utf-8") as f:
            new_content = f.read()
    else:
        new_content = new_content_file_or_str

    try:
        # 1. Charger l'ancienne note
        old_post = frontmatter.load(note_path)
        old_metadata = old_post.metadata
        
        # S'assurer que le répertoire d'archivage existe
        ARCHIVES_DIR.mkdir(parents=True, exist_ok=True)
        
        # 2. Générer le nom d'archivage
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_filename = f"{note_path.stem}_archive_{timestamp}.md"
        archive_path = ARCHIVES_DIR / archive_filename
        
        # 3. Créer le post d'archive
        archive_metadata = old_metadata.copy()
        archive_metadata["statut"] = "archive"
        
        # Mettre à jour ou ajouter le tag archive
        tags_val = archive_metadata.get("tags", [])
        tags = list(tags_val) if isinstance(tags_val, (list, tuple)) else []
        if "statut/archive" not in tags:
            tags.append("statut/archive")
        archive_metadata["tags"] = tags
        
        # Écrire le fichier d'archive
        archive_post = frontmatter.Post(old_post.content)
        archive_post.metadata.update(archive_metadata)
        with open(archive_path, "w", encoding="utf-8") as f:
            f.write(frontmatter.dumps(archive_post))
            
        print(f"[+] Ancienne version sauvegardée dans : 04-Archives/{archive_filename}")
        
        # 4. Charger la nouvelle note
        # On peut parser le nouveau contenu pour récupérer ses métadonnées s'il y en a, sinon on garde le frontmatter d'origine mis à jour
        try:
            new_post = frontmatter.loads(new_content)
            new_metadata = new_post.metadata
            new_body = new_post.content
        except Exception:
            # Si le nouveau contenu ne contient pas de frontmatter valide, on conserve celui d'origine et on applique le contenu brut
            new_metadata = old_metadata.copy()
            new_body = new_content
            
        # Incrémenter la version
        version_val = old_metadata.get("version", 1.0)
        try:
            current_version = float(str(version_val))
        except ValueError:
            current_version = 1.0
        new_metadata["version"] = round(current_version + 0.1, 1)
        new_metadata["date"] = datetime.date.today().isoformat()
        
        # Ajouter le lien bidirectionnel vers l'archive dans le contenu de la nouvelle note
        rel_archive_path = archive_path.relative_to(VAULT_DIR)
        history_link = f"\n\n---\n**Historique des révisions** : [[{rel_archive_path.with_suffix('')}|Version {current_version} ({old_metadata.get('date', 'inconnue')})]]"
        new_body_with_history = new_body.rstrip() + history_link
        
        # Rédiger le post final mis à jour
        final_post = frontmatter.Post(new_body_with_history)
        final_post.metadata.update(new_metadata)
        
        # 5. Écrire temporairement la nouvelle note pour validation AST
        temp_file = note_path.with_suffix(".tmp")
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write(frontmatter.dumps(final_post))
            
        # Valider via validate_note.py
        import validate_note
        if not validate_note.validate_frontmatter(temp_file):
            print("[!] Échec de la validation AST sur la nouvelle version de la note. Annulation.")
            if temp_file.exists():
                os.remove(temp_file)
            return False
            
        # Remplacer définitivement
        if temp_file.exists():
            shutil.move(str(temp_file), str(note_path))
            
        print(f"[+] Note mise à jour vers la version {new_metadata['version']} dans {note_rel_path_str}")
        
        # 6. Déclencher le commit Git automatique de sauvegarde
        subprocess.run(["/bin/bash", str(SCRIPTS_DIR / "git_backup.sh")])
        
        # 7. Déclencher la réindexation de la base SQLite
        import sync_brain
        sync_brain.sync()
        
        return True
        
    except Exception as e:
        print(f"[!] Erreur critique lors de l'archivage/historisation : {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: archive_note.py <chemin_relatif_note_dans_vault> <nouveau_contenu_ou_chemin_fichier_contenu>")
        sys.exit(1)
        
    success = archive_and_update(sys.argv[1], sys.argv[2])
    sys.exit(0 if success else 1)
