#!/usr/bin/env python3
"""
transcribe.py — Transcrit le flux de parole d'un fichier audio ou vidéo.
Utilise exclusivement l'API Google Gemini (Interactions & Files API).
"""

import argparse
import os
import sys
import time
from google import genai
from google.genai import types

def get_api_key(args):
    """Récupère la clé API Gemini depuis les arguments ou l'environnement."""
    if args.api_key:
        return args.api_key
    return os.environ.get("GEMINI_API_KEY")

def detect_mime_type(file_path):
    """Détermine le type MIME du fichier à partir de son extension."""
    ext = os.path.splitext(file_path)[1].lower()
    mime_map = {
        ".mp4": "video/mp4",
        ".mkv": "video/x-matroska",
        ".mov": "video/quicktime",
        ".webm": "video/webm",
        ".avi": "video/x-msvideo",
        ".mp3": "audio/mpeg",
        ".m4a": "audio/mp4",
        ".wav": "audio/wav",
        ".aac": "audio/aac",
        ".ogg": "audio/ogg",
        ".flac": "audio/x-flac",
    }
    return mime_map.get(ext, "application/octet-stream")

def main():
    parser = argparse.ArgumentParser(
        description="Transcrit l'audio d'une vidéo ou d'un fichier sonore via l'API Gemini."
    )
    parser.add_argument("file_path", help="Chemin du fichier multimédia local.")
    parser.add_argument(
        "--output", "-o",
        help="Chemin de sortie pour la transcription (défaut : affiche sur la sortie standard)."
    )
    parser.add_argument(
        "--model", "-m", default="gemini-2.5-flash",
        help="Modèle Gemini à utiliser pour la transcription (défaut : gemini-2.5-flash)."
    )
    parser.add_argument(
        "--diarization", "-d", action="store_true", default=True,
        help="Activer la distinction des différents locuteurs (diarisation)."
    )
    parser.add_argument(
        "--srt", action="store_true", default=False,
        help="Générer des sous-titres horodatés au format SRT."
    )
    parser.add_argument("--api-key", help="Clé API Gemini manuelle.")
    args = parser.parse_args()

    # 1. Vérification de l'existence du fichier
    if not os.path.exists(args.file_path):
        print(f"Erreur : Le fichier '{args.file_path}' n'existe pas.", file=sys.stderr)
        sys.exit(1)

    # 2. Clé API
    api_key = get_api_key(args)
    if not api_key:
        print("Erreur : La variable d'environnement GEMINI_API_KEY n'est pas définie.", file=sys.stderr)
        sys.exit(1)

    # 3. Type MIME et compression conseillée
    mime_type = detect_mime_type(args.file_path)
    file_size = os.path.getsize(args.file_path)
    if mime_type.startswith("video/") and file_size > 50 * 1024 * 1024:
        size_mb = file_size / (1024 * 1024)
        print(f"[*] Note : Vidéo volumineuse détectée ({size_mb:.1f} Mo).", file=sys.stderr)
        print("[*] Pour accélérer l'upload, vous pouvez extraire uniquement l'audio via ffmpeg :", file=sys.stderr)
        print(f"    ffmpeg -i \"{args.file_path}\" -vn -acodec copy audio.aac", file=sys.stderr)

    # 4. Initialisation du client
    client = genai.Client(api_key=api_key)

    # 5. Téléchargement vers la Files API
    print(f"[*] Upload de '{args.file_path}' vers Gemini Files API...", file=sys.stderr)
    try:
        uploaded_file = client.files.upload(file=args.file_path)
        print(f"[+] Fichier uploadé avec succès. ID : {uploaded_file.name}", file=sys.stderr)
        
        # Attente de l'état ACTIVE
        while uploaded_file.state.name == "PROCESSING":
            print("[*] Traitement du fichier multimédia en cours par Gemini...", file=sys.stderr)
            time.sleep(5)
            uploaded_file = client.files.get(name=uploaded_file.name)
            
        if uploaded_file.state.name == "FAILED":
            print("Erreur : L'API Gemini a échoué à traiter le fichier uploadé.", file=sys.stderr)
            sys.exit(1)
            
        print("[+] Le fichier est maintenant actif pour l'inférence.", file=sys.stderr)
    except Exception as e:
        print(f"Erreur lors de l'upload : {e}", file=sys.stderr)
        sys.exit(1)

    # 6. Formulation du prompt de transcription
    fmt_instructions = ""
    if args.srt:
        fmt_instructions = "Génère la transcription au format SRT (sous-titres de type SubRip) avec des timecodes précis (ex: 00:01:23,400 --> 00:01:26,700)."
    else:
        fmt_instructions = "Génère une transcription claire et propre sous forme de texte brut."

    diarization_inst = ""
    if args.diarization:
        diarization_inst = "Distingue les différents interlocuteurs en les préfixant de façon cohérente (ex: Locuteur 1, Locuteur 2)."

    prompt = f"""
Tu es un transcripteur professionnel. Analyse le fichier multimédia fourni.
1. Transcris verbatim l'intégralité des paroles prononcées, sans omission ni modification.
2. {diarization_inst}
3. {fmt_instructions}
4. Conserve la langue originale parlée.
Ne rajoute aucun commentaire d'introduction ou de conclusion en dehors de la transcription demandée.
"""

    # 7. Appel du modèle
    print(f"[*] Inférence en cours avec {args.model}...", file=sys.stderr)
    try:
        response = client.models.generate_content(
            model=args.model,
            contents=[uploaded_file, prompt]
        )
        transcript = response.text
    except Exception as e:
        print(f"Erreur lors de la génération de transcription : {e}", file=sys.stderr)
        transcript = None
    finally:
        # Nettoyage systématique du fichier sur l'API Files
        print("[*] Suppression du fichier temporaire sur Gemini Files API...", file=sys.stderr)
        try:
            client.files.delete(name=uploaded_file.name)
            print("[+] Nettoyage complété.", file=sys.stderr)
        except Exception as e:
            print(f"Avertissement lors du nettoyage : {e}", file=sys.stderr)

    if not transcript:
        sys.exit(1)

    # 8. Sortie
    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(transcript)
            print(f"[+] Transcription sauvegardée dans '{args.output}'.", file=sys.stderr)
        except Exception as e:
            print(f"Erreur d'écriture dans le fichier de sortie : {e}", file=sys.stderr)
            print(transcript)
    else:
        print(transcript)

if __name__ == "__main__":
    main()
