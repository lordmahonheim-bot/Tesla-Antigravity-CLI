#!/usr/bin/env python3
# update_session_history.py — Idempotent cognitive session memory updater
import os
import json
import re
from datetime import datetime

WORKSPACE = "/home/lord-mahonheim/bifrost/tesla"
MEMORY_DIR = os.path.join(WORKSPACE, "memory")
HISTORY_FILE = os.path.join(MEMORY_DIR, "SESSION_TRANSCRIPTS.md")

conversation_id = os.environ.get("ANTIGRAVITY_CONVERSATION_ID")
if not conversation_id:
    print("[-] Error: ANTIGRAVITY_CONVERSATION_ID not set.")
    exit(1)

transcript_path = f"/home/lord-mahonheim/.gemini/antigravity-cli/brain/{conversation_id}/.system_generated/logs/transcript.jsonl"
if not os.path.exists(transcript_path):
    print(f"[-] Error: Transcript not found at {transcript_path}")
    exit(1)

# Extract interactions
interactions = []
current_user_msg = None

with open(transcript_path, "r", encoding="utf-8") as f:
    for line in f:
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
        except Exception:
            continue
        
        if entry.get("type") == "USER_INPUT":
            content = entry.get("content", "")
            match = re.search(r"<USER_REQUEST>(.*?)</USER_REQUEST>", content, re.DOTALL)
            user_text = match.group(1).strip() if match else content.strip()
            current_user_msg = user_text
        elif entry.get("type") == "PLANNER_RESPONSE":
            content = entry.get("content", "")
            if content and current_user_msg:
                interactions.append({
                    "user": current_user_msg,
                    "model": content.strip()
                })
                current_user_msg = None

if not interactions:
    print("[*] No interactions to log.")
    exit(0)

# Build current session content
date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
theme = interactions[0]["user"].split("\n")[0][:80].replace("|", "\\|").strip()

# Build Cognitive Synthesis by extracting Diagnostic & Action sections
synthesis_blocks = []
for idx, interaction in enumerate(interactions, 1):
    model_text = interaction["model"]
    diag_match = re.search(r"### Diagnostic(.*?)(### Action|### Preuve|$)", model_text, re.DOTALL)
    act_match = re.search(r"### Action(.*?)(### Preuve|### Diagnostic|$)", model_text, re.DOTALL)
    
    diag = diag_match.group(1).strip() if diag_match else "N/A"
    act = act_match.group(1).strip() if act_match else "N/A"
    
    # Keep it brief for the synthesis
    diag_short = (diag[:200] + "...") if len(diag) > 200 else diag
    act_short = (act[:200] + "...") if len(act) > 200 else act
    
    user_summary = interaction['user'].split('\n')[0][:60]
    synthesis_blocks.append(
        f"**Interaction {idx} : {user_summary}**\n"
        f"- **Diagnostic** : {diag_short}\n"
        f"- **Action** : {act_short}"
    )

synthesis_text = "\n\n".join(synthesis_blocks)

# Build detailed transcript (collapsible)
transcript_blocks = []
for idx, interaction in enumerate(interactions, 1):
    transcript_blocks.append(
        f"#### Interaction {idx}\n\n"
        f"**Opérateur (Mahonheim) :**\n> {interaction['user']}\n\n"
        f"**Tesla :**\n{interaction['model']}\n"
    )
transcript_details = "\n---\n".join(transcript_blocks)

# Read existing file
existing_content = ""
if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        existing_content = f.read()

# Build session block
session_block = (
    f"<!-- SESSION: {conversation_id} -->\n"
    f"### 📅 Session du {date_str} (ID: {conversation_id})\n"
    f"- **Thème principal** : {theme}\n\n"
    f"#### 🧠 Synthèse Cognitive\n{synthesis_text}\n\n"
    f"<details>\n<summary>📝 Transcription détaillée (cliquez pour dérouler)</summary>\n\n"
    f"{transcript_details}\n"
    f"</details>\n"
    f"<!-- END_SESSION: {conversation_id} -->"
)

# Replace or insert session block
session_pattern = rf"<!-- SESSION: {conversation_id} -->.*?<!-- END_SESSION: {conversation_id} -->"
if re.search(session_pattern, existing_content, re.DOTALL):
    new_sessions_content = re.sub(session_pattern, lambda m: session_block, existing_content, flags=re.DOTALL)
else:
    if "<!-- SESSIONS_LIST_START -->" in existing_content:
        parts = existing_content.split("<!-- SESSIONS_LIST_START -->")
        header_and_index = parts[0]
        sessions_part = parts[1].replace("<!-- SESSIONS_LIST_END -->", "").strip()
        new_sessions_content = header_and_index + "<!-- SESSIONS_LIST_START -->\n\n" + sessions_part + "\n\n" + session_block + "\n\n<!-- SESSIONS_LIST_END -->"
    else:
        new_sessions_content = (
            "# Historique des Sessions d'Interaction\n\n"
            "<!-- INDEX_START -->\n"
            "<!-- INDEX_END -->\n\n"
            "<!-- SESSIONS_LIST_START -->\n\n" + session_block + "\n\n<!-- SESSIONS_LIST_END -->"
        )

# Rebuild TOC Index
sessions_found = re.findall(
    r"<!-- SESSION: (.*?) -->\s*\r?\n### 📅 Session du (.*?)\s*\(ID: .*?\)\s*\r?\n-\s*\*\*Thème principal\*\*\s*:\s*(.*?)\r?\n",
    new_sessions_content,
    re.DOTALL
)

index_lines = ["| Date & Heure | ID Session | Thème Principal |", "| :--- | :--- | :--- |"]
for sid, sdate, stheme in sessions_found:
    index_lines.append(f"| {sdate} | `{sid[:8]}...` | {stheme} |")
index_table = "\n".join(index_lines)

index_pattern = r"<!-- INDEX_START -->.*?<!-- INDEX_END -->"
final_content = re.sub(
    index_pattern,
    lambda m: f"<!-- INDEX_START -->\n## 🗂️ Sommaire Global des Sessions\n\n{index_table}\n<!-- INDEX_END -->",
    new_sessions_content,
    flags=re.DOTALL
)

with open(HISTORY_FILE, "w", encoding="utf-8") as f:
    f.write(final_content)

print(f"[+] Cognitive memory updated in {HISTORY_FILE}")
