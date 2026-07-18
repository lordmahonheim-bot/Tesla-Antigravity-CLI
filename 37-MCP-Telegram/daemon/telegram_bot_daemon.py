#!/usr/bin/env python3
import os
import time
import subprocess
import urllib.request
import urllib.parse
import json

# Charger les variables d'environnement
env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                k, v = line.strip().split('=', 1)
                os.environ[k] = v

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
USER_ID = os.environ.get("TELEGRAM_ALLOWED_USER_ID")

def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    # Limitation Telegram (4096 chars). On tronque si trop long.
    if len(text) > 4000:
        text = text[:4000] + "\n\n...[TRONQUÉ]"
    
    data = json.dumps({
        "chat_id": USER_ID,
        "text": text
    }).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    try:
        urllib.request.urlopen(req)
    except Exception as e:
        print(f"Erreur d'envoi du message: {e}")

def get_updates(offset):
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?timeout=30&offset={offset}"
    try:
        with urllib.request.urlopen(url, timeout=35) as response:
            res = json.loads(response.read().decode())
            return res.get("result", [])
    except Exception as e:
        print(f"Erreur de réception: {e}")
        return []

def main():
    print("Démon Telegram démarré. ID Lock activé sur", USER_ID)
    send_message("🟢 **MIDGARD Mobile Command Center Online.**\nL'écosystème Antigravity CLI écoute vos ordres de manière souveraine.")
    offset = 0
    while True:
        updates = get_updates(offset)
        for update in updates:
            offset = update["update_id"] + 1
            if "message" in update and "text" in update["message"]:
                msg = update["message"]
                sender_id = str(msg["from"]["id"])
                text = msg["text"]
                
                # SÉCURITÉ ABSOLUE : ID LOCK
                if sender_id != str(USER_ID):
                    print(f"Intrusion bloquée depuis l'ID : {sender_id}")
                    continue
                
                send_message(f"⚙️ Transmission à MIDGARD :\n`{text}`")
                
                # Exécution d'Antigravity CLI (agy)
                try:
                    result = subprocess.run(
                        ["/home/lord-mahonheim/.local/bin/agy", "-p", text],
                        capture_output=True,
                        text=True,
                        timeout=600 # 10 minutes max pour de grosses exécutions
                    )
                    output = result.stdout if result.stdout else result.stderr
                    if not output:
                        output = "[Exécution réussie. Aucune sortie console]"
                    send_message(output)
                    
                    # SYNAPSE MÉMORIELLE (Vigilum Codex)
                    try:
                        synapse_path = "/home/lord-mahonheim/bifrost/tesla/memory/TELEGRAM_SYNAPSE.md"
                        from datetime import datetime
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        with open(synapse_path, "a", encoding="utf-8") as f:
                            f.write(f"\n### [{timestamp}] Mobile Command Center\n")
                            f.write(f"**Lord Mahonheim :** {text}\n")
                            f.write(f"**Tesla :** {output}\n")
                    except Exception as e:
                        print(f"Erreur Synapse: {e}")
                        
                except subprocess.TimeoutExpired:
                    send_message("❌ Timeout : La commande a dépassé 10 minutes.")
                except Exception as e:
                    send_message(f"❌ Erreur critique : {str(e)}")
        time.sleep(1)

if __name__ == "__main__":
    if not TOKEN or not USER_ID:
        print("Erreur : Configuration .env manquante.")
        exit(1)
    main()
