#!/usr/bin/env python3
# transcribe_local.py — Wrapper local de transcription audio/vidéo via whisper.cpp
# Usage: python3 transcribe_local.py <chemin_fichier_media> [--output <chemin_txt>]

import os
import sys
import subprocess
import tempfile
import shutil

from typing import Optional

WHISPER_ROOT = "/home/lord-mahonheim/bifrost/tesla/tools/whisper.cpp"
WHISPER_CLI = os.path.join(WHISPER_ROOT, "build/bin/whisper-cli")
MODEL_PATH = os.path.join(WHISPER_ROOT, "models/ggml-base.bin")

def print_log(msg: str):
    print(f"⚡ [TRANSCRIBE] {msg}", flush=True)

def transcribe(media_path: str, output_path: Optional[str] = None) -> int:
    if not os.path.exists(media_path):
        print_log(f"❌ Erreur: Fichier introuvable : {media_path}")
        return 1

    if not os.path.exists(WHISPER_CLI):
        print_log(f"❌ Erreur: Exécutable whisper-cli introuvable à {WHISPER_CLI}")
        return 1

    if not os.path.exists(MODEL_PATH):
        print_log(f"❌ Erreur: Modèle ggml-base.bin introuvable à {MODEL_PATH}")
        return 1

    # Création d'un fichier WAV temporaire à 16kHz mono (requis par whisper.cpp)
    temp_wav = tempfile.mktemp(suffix=".wav")
    print_log(f"Ingestion du média et ré-échantillonnage vers 16kHz WAV...")
    
    ffmpeg_cmd = [
        "ffmpeg", "-y", "-i", media_path,
        "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le",
        temp_wav
    ]
    
    try:
        subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print_log(f"❌ Erreur lors de la conversion ffmpeg : {e.stderr.decode('utf-8', errors='ignore')}")
        if os.path.exists(temp_wav):
            os.remove(temp_wav)
        return 1

    print_log("Lancement de la transcription locale (whisper.cpp CPU-only)...")
    
    # whisper-cli génère un fichier texte. On crée un préfixe temporaire pour la sortie.
    temp_out_prefix = tempfile.mktemp()
    
    whisper_cmd = [
        WHISPER_CLI,
        "-m", MODEL_PATH,
        "-f", temp_wav,
        "--output-txt",
        "--output-file", temp_out_prefix,
        "-nt" # Pas de timestamps dans le fichier texte pour garder le texte brut propre
    ]

    try:
        # Exécution sous contrôle de mémoire restreinte (processus léger)
        subprocess.run(whisper_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print_log(f"❌ Erreur lors de la transcription whisper.cpp : {e.stderr.decode('utf-8', errors='ignore')}")
        return 1
    finally:
        if os.path.exists(temp_wav):
            os.remove(temp_wav)

    generated_txt = temp_out_prefix + ".txt"
    if not os.path.exists(generated_txt):
        print_log("❌ Erreur: Le fichier de transcription n'a pas été généré.")
        return 1

    # Lecture du résultat
    with open(generated_txt, "r", encoding="utf-8") as f:
        transcription_text = f.read()

    # Nettoyage
    os.remove(generated_txt)

    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(transcription_text)
        print_log(f"✅ Transcription enregistrée dans : {output_path}")
    else:
        print("\n=== TRANSCRIPTION DU DOCUMENT ===")
        print(transcription_text.strip())
        print("=================================\n")

    return 0

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 transcribe_local.py <chemin_fichier_media> [--output <chemin_txt>]")
        sys.exit(1)

    target_media = sys.argv[1]
    target_out = None
    if len(sys.argv) >= 4 and sys.argv[2] == "--output":
        target_out = sys.argv[3]

    ret = transcribe(target_media, target_out)
    sys.exit(ret)
