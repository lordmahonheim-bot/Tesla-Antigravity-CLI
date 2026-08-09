#!/usr/bin/env python3
import sys
import os
import re
import subprocess
import urllib.parse
import json
import requests

MAX_CHARS = 16000  # Limite de sécurité pour économiser les tokens (~4000 tokens)

def clean_text(text):
    """Nettoie le texte en supprimant les lignes blanches excessives et espaces inutiles."""
    # Supprimer les lignes blanches consécutives
    text = re.sub(r'\n\s*\n', '\n\n', text)
    # Limiter le nombre de caractères
    if len(text) > MAX_CHARS:
        text = text[:MAX_CHARS] + "\n\n... [Contenu tronqué pour économiser les tokens] ..."
    return text.strip()

def clean_vtt_subtitles(vtt_path):
    """Nettoie les sous-titres VTT de YouTube (souvent très répétitifs)."""
    if not os.path.exists(vtt_path):
        return None
    
    with open(vtt_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    cleaned_lines = []
    seen = set()
    
    for line in lines:
        line = line.strip()
        # Ignorer les en-têtes VTT et les marqueurs temporels
        if not line or line.startswith("WEBVTT") or line.startswith("Kind:") or line.startswith("Language:") or "-->" in line:
            continue
        
        # Supprimer le formatage HTML ou styles
        line = re.sub(r'<[^>]+>', '', line)
        # Éviter les répétitions successives de phrases
        if line not in seen:
            cleaned_lines.append(line)
            seen.add(line)
            
    return "\n".join(cleaned_lines)

def fetch_youtube_subtitles(url):
    """Récupère les sous-titres YouTube via yt-dlp."""
    print("[Wrapper] Extraction des sous-titres YouTube via yt-dlp...")
    
    # Extraire l'ID vidéo pour le nom de fichier temporaire
    parsed_url = urllib.parse.urlparse(url)
    video_id = None
    if parsed_url.hostname in ('youtu.be', 'www.youtu.be'):
        video_id = parsed_url.path[1:]
    elif parsed_url.hostname in ('youtube.com', 'www.youtube.com'):
        query = urllib.parse.parse_qs(parsed_url.query)
        video_id = query.get('v', [None])[0]
        
    if not video_id:
        video_id = "temp_yt_video"
        
    out_template = f"/tmp/{video_id}"
    
    # Lancer le téléchargement de la description + métadonnées
    cmd_meta = ["yt-dlp", "--dump-json", url]
    meta_json = ""
    try:
        res = subprocess.run(cmd_meta, capture_output=True, text=True, timeout=15)
        if res.returncode == 0:
            meta = json.loads(res.stdout)
            meta_json = f"Titre: {meta.get('title')}\nChaîne: {meta.get('uploader')}\nDescription:\n{meta.get('description')}\n\n"
    except Exception as e:
        print(f"[Wrapper] Avertissement: Impossible d'extraire la description: {e}")

    # Essayer de télécharger les sous-titres
    cmd_sub = [
        "yt-dlp", "--write-sub", "--write-auto-sub", 
        "--sub-lang", "fr,en,zh-Hans", "--skip-download", 
        "-o", out_template, url
    ]
    try:
        subprocess.run(cmd_sub, capture_output=True, text=True, timeout=20)
    except Exception as e:
        return meta_json + f"[Wrapper] Erreur lors de l'extraction des sous-titres: {e}"

    # Trouver le fichier VTT généré
    subtitles = ""
    vtt_found = False
    for filename in os.listdir("/tmp"):
        if filename.startswith(video_id) and filename.endswith(".vtt"):
            vtt_path = os.path.join("/tmp", filename)
            subtitles = clean_vtt_subtitles(vtt_path)
            vtt_found = True
            # Nettoyage du fichier temporaire
            try:
                os.remove(vtt_path)
            except:
                pass
            break
            
    if vtt_found and subtitles:
        return meta_json + "--- Sous-titres extraits ---\n" + subtitles
    else:
        return meta_json + "[Wrapper] Aucun fichier de sous-titres valide n'a pu être extrait pour cette vidéo."

def fetch_jina_reader(url):
    """Méthode de repli universelle et performante via Jina Reader."""
    print(f"[Wrapper] Lecture de la page via Jina Reader: {url}")
    headers = {
        "User-Agent": "agent-reach-wrapper/1.0"
    }
    # Jina Reader accepte optionnellement une clé API si configurée en env, sinon fonctionne en public
    jina_key = os.environ.get("JINA_API_KEY")
    if jina_key:
        headers["Authorization"] = f"Bearer {jina_key}"
        
    try:
        resp = requests.get(f"https://r.jina.ai/{url}", headers=headers, timeout=20)
        if resp.status_code == 200:
            return resp.text
        else:
            return f"[Wrapper] Erreur de lecture Jina Reader (HTTP {resp.status_code}): {resp.text[:500]}"
    except Exception as e:
        return f"[Wrapper] Échec de la connexion Jina Reader: {e}"

def fetch_v2ex(url):
    """Extraction via l'API publique de V2EX si URL correspondante."""
    print(f"[Wrapper] Extraction V2EX...")
    # Tenter de détecter s'il s'agit d'un topic
    match = re.search(r'v2ex.com/t/(\d+)', url)
    if match:
        topic_id = match.group(1)
        try:
            # Récupérer les détails du topic
            t_resp = requests.get(f"https://www.v2ex.com/api/topics/show.json?id={topic_id}", timeout=10)
            # Récupérer les commentaires
            r_resp = requests.get(f"https://www.v2ex.com/api/replies/show.json?topic_id={topic_id}", timeout=10)
            
            output = ""
            if t_resp.status_code == 200:
                topic_data = t_resp.json()[0]
                output += f"Titre: {topic_data.get('title')}\nAuteur: {topic_data.get('member', {}).get('username')}\n"
                output += f"Contenu:\n{topic_data.get('content')}\n\n--- Commentaires ---\n"
            
            if r_resp.status_code == 200:
                replies = r_resp.json()
                for i, reply in enumerate(replies[:15]):  # Limiter aux 15 premiers commentaires pour économiser les tokens
                    output += f"#{i+1} [{reply.get('member', {}).get('username')}]: {reply.get('content')}\n"
            return output if output else fetch_jina_reader(url)
        except Exception as e:
            print(f"[Wrapper] Erreur V2EX API: {e}")
            
    return fetch_jina_reader(url)

def fetch_social_or_fallback(url, platform):
    """Tente d'appeler les outils locaux de scrapers (OpenCLI/twitter/rdt) sinon repli sur Jina Reader."""
    print(f"[Wrapper] Plateforme sociale détectée : {platform}. Vérification des backends...")
    
    # 1. Tenter d'utiliser les variables d'environnement optionnelles pour les cookies
    cookies = os.environ.get(f"{platform.upper()}_COOKIES")
    
    # 2. Routage vers l'outil
    if platform == "twitter":
        try:
            res = subprocess.run(["which", "twitter"], capture_output=True, text=True)
            if res.returncode == 0:
                print("[Wrapper] Twitter CLI disponible, interrogation de la ressource...")
                match = re.search(r'status/(\d+)', url)
                if match:
                    tweet_id = match.group(1)
                    res_tweet = subprocess.run(["twitter", "show", tweet_id], capture_output=True, text=True, timeout=15)
                    if res_tweet.returncode == 0:
                        return res_tweet.stdout
        except Exception as e:
            print(f"[Wrapper] Échec d'interrogation Twitter CLI: {e}")
            
    elif platform == "reddit":
        try:
            res = subprocess.run(["which", "rdt"], capture_output=True, text=True)
            if res.returncode == 0:
                print("[Wrapper] Reddit rdt-cli disponible...")
                parsed = urllib.parse.urlparse(url)
                res_reddit = subprocess.run(["rdt", "thread", parsed.path], capture_output=True, text=True, timeout=15)
                if res_reddit.returncode == 0:
                    return res_reddit.stdout
        except Exception as e:
            print(f"[Wrapper] Échec d'interrogation Reddit CLI: {e}")

    # Fallback universel vers Jina Reader (qui contourne les blocages de base pour Twitter/Reddit)
    return fetch_jina_reader(url)

def main():
    if len(sys.argv) < 2:
        print("Usage: python agent_reach_wrapper.py <URL>")
        sys.exit(1)
        
    url = sys.argv[1]
    parsed_url = urllib.parse.urlparse(url)
    
    # Vérification anti-SSRF de sécurité (confinement strict)
    hostname = parsed_url.hostname
    if not hostname:
        print("[Wrapper] URL invalide ou absente.")
        sys.exit(1)
        
    if hostname in ("localhost", "127.0.0.1", "::1") or hostname.startswith("192.168.") or hostname.startswith("10.") or hostname.startswith("172.16."):
        print("[Wrapper] Sécurité : Navigation vers les hôtes locaux ou privés bloquée.")
        sys.exit(1)
        
    # Cascade d'extraction selon la plateforme
    result = ""
    try:
        if "youtube.com" in hostname or "youtu.be" in hostname:
            result = fetch_youtube_subtitles(url)
        elif "v2ex.com" in hostname:
            result = fetch_v2ex(url)
        elif "twitter.com" in hostname or "x.com" in hostname:
            result = fetch_social_or_fallback(url, "twitter")
        elif "reddit.com" in hostname:
            result = fetch_social_or_fallback(url, "reddit")
        elif "bilibili.com" in hostname or "b23.tv" in hostname:
            result = fetch_jina_reader(url)
        else:
            result = fetch_jina_reader(url)
    except Exception as e:
        result = f"[Wrapper] Erreur inattendue de traitement: {e}\nTentative de repli..."
        result += "\n" + fetch_jina_reader(url)
        
    # Nettoyage et envoi sur stdout
    print(clean_text(result))

if __name__ == "__main__":
    main()
