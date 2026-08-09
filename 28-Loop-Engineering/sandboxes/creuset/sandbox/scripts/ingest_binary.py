#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ingest_binary.py - Pipeline d'ingestion multiformat avancée & chunking sémantique.
Prend en charge les fichiers PDF, EPUB, TXT et Audio.
Découpe les fichiers longs en fragments de 2000 mots max et génère les fiches miroirs.
"""

import os
import sys
import subprocess
import re
import datetime
from pathlib import Path

VAULT_DIR = Path("/home/lord-mahonheim/bifrost/tesla/Avalon")
RESOURCES_DIR = VAULT_DIR / "03-Resources"
CHUNKS_DIR = RESOURCES_DIR / "chunks"

def chunk_text(text, max_words=2000):
    """Découpe un texte en fragments de max_words mots maximum en respectant les fins de phrases."""
    words = text.split()
    chunks = []
    current_chunk = []
    current_word_count = 0
    
    # Séparation grossière par paragraphe d'abord pour garder la cohérence sémantique
    paragraphs = text.split("\n\n")
    
    for paragraph in paragraphs:
        paragraph_words = paragraph.split()
        if not paragraph_words:
            continue
            
        # Si ajouter ce paragraphe dépasse la limite, on ferme le chunk actuel
        if current_word_count + len(paragraph_words) > max_words:
            if current_chunk:
                chunks.append("\n\n".join(current_chunk))
                current_chunk = []
                current_word_count = 0
                
            # Si le paragraphe lui-même est plus grand que max_words, on le découpe par mots
            if len(paragraph_words) > max_words:
                sub_chunk = []
                sub_count = 0
                for word in paragraph_words:
                    sub_chunk.append(word)
                    sub_count += 1
                    if sub_count >= max_words:
                        chunks.append(" ".join(sub_chunk))
                        sub_chunk = []
                        sub_count = 0
                if sub_chunk:
                    current_chunk.append(" ".join(sub_chunk))
                    current_word_count = sub_count
            else:
                current_chunk.append(paragraph)
                current_word_count = len(paragraph_words)
        else:
            current_chunk.append(paragraph)
            current_word_count += len(paragraph_words)
            
    if current_chunk:
        chunks.append("\n\n".join(current_chunk))
        
    return chunks

def extract_pdf(filepath):
    """Extrait le texte d'un PDF en utilisant pdftotext."""
    print(f"[*] Extraction du PDF via pdftotext : {filepath.name}")
    result = subprocess.run(["/usr/bin/pdftotext", str(filepath), "-"], capture_output=True, text=True, encoding="utf-8", errors="ignore")
    if result.returncode != 0:
        raise Exception(f"Erreur pdftotext: {result.stderr}")
    return result.stdout

def extract_epub_or_docx(filepath):
    """Extrait le texte d'un fichier EPUB, HTML ou DOCX via pandoc."""
    print(f"[*] Extraction via pandoc : {filepath.name}")
    # Détecter le format d'entrée
    ext = filepath.suffix.lower().lstrip(".")
    result = subprocess.run(["/usr/bin/pandoc", "-f", ext, "-t", "markdown", str(filepath)], capture_output=True, text=True, encoding="utf-8", errors="ignore")
    if result.returncode != 0:
        raise Exception(f"Erreur pandoc: {result.stderr}")
    return result.stdout

def extract_audio_meta(filepath):
    """Récupère les métadonnées audio via ffmpeg/ffprobe et simule la transcription."""
    print(f"[*] Analyse des métadonnées audio via ffmpeg : {filepath.name}")
    # ffprobe pour récupérer la durée
    ffprobe_cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(filepath)]
    duration = "Inconnue"
    try:
        res = subprocess.run(ffprobe_cmd, capture_output=True, text=True, check=True)
        duration = f"{float(res.stdout.strip()):.2f} secondes"
    except Exception as e:
        print(f"[!] Impossible de lire la durée : {e}")
        
    meta_text = f"Fichier Audio : {filepath.name}\nFormat : {filepath.suffix}\nDurée estimée : {duration}\n\n[MOCK TRANSCRIPTION]\nCeci est une simulation de transcription automatique pour le fichier audio {filepath.name}. Whisper local n'a pas été détecté sur le PATH de la machine MIDGARD.\nLe fichier a été enregistré et indexé avec ses métadonnées."
    return meta_text

def ingest_file(file_path_str):
    filepath = Path(file_path_str)
    if not filepath.exists():
        print(f"[!] Fichier introuvable : {filepath}")
        return False
        
    ext = filepath.suffix.lower()
    text = ""
    media_type = "text"
    
    if ext == ".pdf":
        text = extract_pdf(filepath)
        media_type = "pdf"
    elif ext in [".epub", ".docx", ".html"]:
        text = extract_epub_or_docx(filepath)
        media_type = "epub"
    elif ext in [".mp3", ".wav", ".m4a", ".ogg"]:
        text = extract_audio_meta(filepath)
        media_type = "audio"
    elif ext in [".txt", ".md"]:
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
        media_type = "text"
    else:
        print(f"[!] Format non pris en charge : {ext}")
        return False
        
    if not text.strip():
        print("[!] Aucun texte n'a pu être extrait du fichier.")
        return False
        
    # S'assurer que les dossiers de destination existent
    RESOURCES_DIR.mkdir(parents=True, exist_ok=True)
    
    # Création du nom de base pour les fiches
    clean_name = re.sub(r'[^a-zA-Z0-9_-]', '_', filepath.stem)
    fiche_principale_path = RESOURCES_DIR / f"{clean_name}.md"
    
    # Découpage sémantique
    chunks = chunk_text(text)
    print(f"[+] Découpage en {len(chunks)} fragments effectué.")
    
    # Créer les dossiers de chunks
    note_chunks_dir = CHUNKS_DIR / clean_name
    note_chunks_dir.mkdir(parents=True, exist_ok=True)
    
    chunk_links = []
    for i, chunk_content in enumerate(chunks, 1):
        chunk_file = note_chunks_dir / f"chunk_{i}.md"
        rel_chunk_path = chunk_file.relative_to(VAULT_DIR)
        
        # Écrire le fragment
        with open(chunk_file, "w", encoding="utf-8") as f:
            f.write(f"---\ntype: reference\ntags: [media/{media_type}/fragment]\nstatut: valide\nparent: \"[[03-Resources/{clean_name}]]\"\n---\n")
            f.write(f"# Fragment {i} - {filepath.stem}\n\n")
            f.write(chunk_content)
            f.write(f"\n\n---\nRetour à la fiche principale : [[03-Resources/{clean_name}]]")
            
        chunk_links.append(f"- [[03-Resources/chunks/{clean_name}/chunk_{i}|Fragment {i}]]")
    
    # Écrire la fiche principale
    with open(fiche_principale_path, "w", encoding="utf-8") as f:
        f.write(f"---\ntype: reference\ntags: [media/{media_type}, statut/a-valider]\ndate: {datetime.date.today().isoformat()}\nsource: \"[[Fichier source: {filepath.name}]]\"\nstatut: a-valider\nversion: 1.0\n---\n")
        f.write(f"# Fiche Miroir : {filepath.stem}\n\n")
        f.write(f"**Fichier d'origine** : `{filepath.name}`  \n")
        f.write(f"**Taille** : {filepath.stat().st_size / 1024:.2f} Ko  \n")
        f.write(f"**Date d'ingestion** : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n\n")
        f.write("## Résumé Exécutif / Métadonnées\n")
        f.write(f"Ce document est une fiche miroir sémantique du fichier binaire `{filepath.name}`. ")
        f.write(f"Le contenu a été segmenté en {len(chunks)} fragments pour optimiser l'indexation et la lecture LLM.\n\n")
        f.write("## Index des fragments sémantiques\n")
        f.write("\n".join(chunk_links))
        f.write("\n\n---\n")
        
    print(f"[+] Fiche miroir principale créée dans : {fiche_principale_path.relative_to(VAULT_DIR)}")
    
    # Déclencher la synchronisation sémantique SQLite
    print("[*] Déclenchement de la réindexation de la base SQLite...")
    try:
        # Importer localement le script sync_brain
        sys.path.append(str(Path(__file__).parent))
        import sync_brain
        sync_brain.sync()
    except Exception as e:
        print(f"[!] Échec du déclenchement automatique de sync_brain : {e}")
        
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: ingest_binary.py <chemin_du_fichier_a_ingerer>")
        sys.exit(1)
    
    success = ingest_file(sys.argv[1])
    sys.exit(0 if success else 1)
