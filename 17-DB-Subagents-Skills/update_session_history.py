#!/usr/bin/env python3
# update_session_history.py — Idempotent cognitive session memory & checkpoint updater
import os
import json
import re
import sys
import subprocess
import shutil
from datetime import datetime
from db_connector import get_db_connection, DB_PATH, WORKSPACE

MEMORY_DIR = os.path.join(WORKSPACE, "memory")
HISTORY_FILE = os.path.join(MEMORY_DIR, "SESSION_TRANSCRIPTS.md")
CHECKPOINT_FILE = os.path.join(MEMORY_DIR, "PROJECT_STATE.md")

conversation_id = os.environ.get("ANTIGRAVITY_CONVERSATION_ID")
if not conversation_id:
    print("[-] Error: ANTIGRAVITY_CONVERSATION_ID not set.")
    exit(1)

# Helper for atomic file writing
def write_atomic(filepath, content):
    temp_filepath = filepath + ".tmp"
    with open(temp_filepath, "w", encoding="utf-8") as f:
        f.write(content)
    os.replace(temp_filepath, filepath)

# Helper for creating backups
def create_backup(filepath):
    backup_dir = os.path.join(MEMORY_DIR, "backup")
    os.makedirs(backup_dir, exist_ok=True)
    if os.path.exists(filepath):
        backup_path = os.path.join(backup_dir, os.path.basename(filepath) + ".bak")
        shutil.copy2(filepath, backup_path)

# Extract Git metadata in a resilient way (handles sandboxing / execution failures)
def get_git_info(cwd):
    try:
        branch_proc = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True
        )
        branch = branch_proc.stdout.strip()
        
        commit_proc = subprocess.run(
            ["git", "log", "-1", "--oneline"],
            cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True
        )
        commit = commit_proc.stdout.strip()
        
        status_proc = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True
        )
        status_lines = [l for l in status_proc.stdout.strip().split("\n") if l.strip()]
        status = "Modifié" if status_lines else "Propre"
        
        return {
            "branch": branch,
            "commit": commit,
            "status": status,
            "accessible": True
        }
    except Exception as e:
        print(f"[-] Git extraction failed for {cwd}: {e}")
        return {
            "branch": "Indéterminée (Git inaccessible)",
            "commit": "Indéterminé (Git inaccessible)",
            "status": "Indéterminé (Git inaccessible)",
            "accessible": False
        }

# Extract active tasks from the todo log
def extract_active_todos():
    outputs_dir = os.path.join(WORKSPACE, "OUTPUTS")
    todo_file = None
    if os.path.exists(outputs_dir):
        todo_files = [
            os.path.join(outputs_dir, f)
            for f in os.listdir(outputs_dir)
            if f.startswith("open_items_todo") and f.endswith(".md")
        ]
        if todo_files:
            todo_files.sort(key=os.path.getmtime, reverse=True)
            todo_file = todo_files[0]
    
    if not todo_file:
        todo_file = os.path.join(WORKSPACE, "OUTPUTS/open_items_todo-Updated.md")
        
    if not os.path.exists(todo_file):
        return "- Aucun fichier de tâches actives trouvé."
    try:
        with open(todo_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        active_section = []
        in_active = False
        for line in lines:
            if "## 📅 Tâches Actives" in line:
                in_active = True
                continue
            if "## 🗂️ Historique des Items Clos" in line:
                in_active = False
                break
            if in_active:
                active_section.append(line)
        
        content = "".join(active_section).strip()
        return content if content else "- Aucune tâche active répertoriée."
    except Exception as e:
        return f"- Échec d'extraction des tâches actives : {e}"

# Automatically trigger codebase semantic indexing
print("[*] Automatically triggering codebase semantic indexing...")
try:
    index_script = os.path.join(WORKSPACE, "sandbox/scripts/index_codebase.py")
    subprocess.run([sys.executable, index_script], check=True)
except Exception as e:
    print(f"[-] Codebase indexing failed: {e}")

home_dir = os.path.expanduser("~")
transcript_path = os.path.join(home_dir, ".gemini/antigravity-cli/brain", conversation_id, ".system_generated/logs/transcript_full.jsonl")
if not os.path.exists(transcript_path):
    transcript_path = os.path.join(home_dir, ".gemini/antigravity-cli/brain", conversation_id, ".system_generated/logs/transcript.jsonl")
if not os.path.exists(transcript_path):
    print(f"[-] Error: Transcript not found at {transcript_path}")
    exit(1)

# Extract interactions
interactions = []
current_user_msg = None

with open(transcript_path, "r", encoding="utf-8", errors="ignore") as f:
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

# Build Cognitive Synthesis
synthesis_blocks = []
diag_short = "N/A"
act_short = "N/A"
for idx, interaction in enumerate(interactions, 1):
    model_text = interaction["model"]
    diag_match = re.search(r"### Diagnostic(.*?)(### Action|### Preuve|$)", model_text, re.DOTALL)
    act_match = re.search(r"### Action(.*?)(### Preuve|### Diagnostic|$)", model_text, re.DOTALL)
    
    diag = diag_match.group(1).strip() if diag_match else "N/A"
    act = act_match.group(1).strip() if act_match else "N/A"
    
    diag_short = (diag[:200] + "...") if len(diag) > 200 else diag
    act_short = (act[:200] + "...") if len(act) > 200 else act
    
    user_summary = interaction['user'].split('\n')[0][:60]
    synthesis_blocks.append(
        f"**Interaction {idx} : {user_summary}**\n"
        f"- **Diagnostic** : {diag_short}\n"
        f"- **Action** : {act_short}"
    )

synthesis_text = "\n\n".join(synthesis_blocks)

# Build detailed transcript
transcript_blocks = []
for idx, interaction in enumerate(interactions, 1):
    transcript_blocks.append(
        f"#### Interaction {idx}\n\n"
        f"**Opérateur (Mahonheim) :**\n> {interaction['user']}\n\n"
        f"**Tesla :**\n{interaction['model']}\n"
    )
transcript_details = "\n---\n".join(transcript_blocks)

# Read existing history content
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

# Replace or insert session block in SESSIONS_LIST
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

# Build and inject the "Last Known State" block to prevent "First-Match Bias"
last_state_block = (
    f"<!-- LAST_STATE_START -->\n"
    f"## ⚓ Dernier État Connu (Session ID: {conversation_id})\n"
    f"- **Date & Heure** : {date_str}\n"
    f"- **Thème principal** : {theme}\n"
    f"- **Dernier Diagnostic** : {diag_short.replace('\n', ' ')}\n"
    f"- **Dernière Action** : {act_short.replace('\n', ' ')}\n"
    f"👉 [Consulter la fiche d'ancrage universelle (PROJECT_STATE.md)](file://{CHECKPOINT_FILE})\n"
    f"<!-- LAST_STATE_END -->"
)

if "<!-- LAST_STATE_START -->" in final_content:
    final_content = re.sub(r"<!-- LAST_STATE_START -->.*?<!-- LAST_STATE_END -->", lambda m: last_state_block, final_content, flags=re.DOTALL)
else:
    # Insert right under the main title
    final_content = final_content.replace(
        "# Historique des Sessions d'Interaction\n\n",
        f"# Historique des Sessions d'Interaction\n\n{last_state_block}\n\n"
    )

# Rotate and archive old session transcripts
def rotate_and_archive_sessions(content_to_rotate):
    archive_dir = os.path.join(MEMORY_DIR, "backup/transcripts_archive")
    os.makedirs(archive_dir, exist_ok=True)
    
    lines = content_to_rotate.splitlines()
    in_code_block = False
    session_blocks = []
    current_session_id = None
    current_session_lines = []
    other_content_lines = []
    
    for line in lines:
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            
        if not in_code_block:
            session_start_match = re.match(r"^<!-- SESSION:\s*(.*?)\s*-->", line.strip())
            session_end_match = re.match(r"^<!-- END_SESSION:\s*(.*?)\s*-->", line.strip())
            
            if session_start_match:
                current_session_id = session_start_match.group(1)
                current_session_lines = [line]
                continue
            elif session_end_match:
                if current_session_id and session_end_match.group(1) == current_session_id:
                    current_session_lines.append(line)
                    session_blocks.append((current_session_id, "\n".join(current_session_lines)))
                    current_session_id = None
                    current_session_lines = []
                    continue
                    
        if current_session_id:
            current_session_lines.append(line)
        else:
            other_content_lines.append(line)
            
    active_session_blocks = []
    archived_months = set()
    now = datetime.now()
    
    for sid, stext in session_blocks:
        date_match = re.search(r"### 📅 Session du ([0-9-]{10} [0-9:]{8})", stext)
        is_old = False
        session_date_str = ""
        
        if date_match:
            session_date_str = date_match.group(1)
            try:
                sdate = datetime.strptime(session_date_str, "%Y-%m-%d %H:%M:%S")
                if (now - sdate).days > 15:
                    is_old = True
            except Exception as e:
                print(f"[-] Date parse error: {e}")
                
        if sid == conversation_id:
            is_old = False
            
        if is_old and session_date_str:
            month_str = session_date_str[:7]
            archived_months.add(month_str)
            archive_filename = f"transcripts_{month_str}.md"
            archive_path = os.path.join(archive_dir, archive_filename)
            
            archive_content = ""
            if os.path.exists(archive_path):
                with open(archive_path, "r", encoding="utf-8") as af:
                    archive_content = af.read()
            else:
                archive_content = f"""---
type: reference
tags: [memoire/archive, statut/valide]
date: {session_date_str[:10]}
version: 1.0
---

# 🗃️ ARCHIVES DES SESSIONS - {month_str}
*Ce fichier contient l'historique complet et immuable des sessions d'interactions du mois de {month_str} sur MIDGARD.*

<!-- SESSIONS_LIST_START -->
<!-- SESSIONS_LIST_END -->
"""
            
            session_pattern = rf"<!-- SESSION: {sid} -->.*?<!-- END_SESSION: {sid} -->"
            if re.search(session_pattern, archive_content, re.DOTALL):
                archive_content = re.sub(session_pattern, lambda m: stext, archive_content, flags=re.DOTALL)
            else:
                if "<!-- SESSIONS_LIST_START -->" in archive_content:
                    parts = archive_content.split("<!-- SESSIONS_LIST_START -->")
                    header = parts[0]
                    sessions = parts[1].replace("<!-- SESSIONS_LIST_END -->", "").strip()
                    archive_content = header + "<!-- SESSIONS_LIST_START -->\n\n" + sessions + "\n\n" + stext + "\n\n<!-- SESSIONS_LIST_END -->"
                else:
                    archive_content += "\n\n" + stext
                    
            write_atomic(archive_path, archive_content)
            print(f"[+] Archived session {sid} into {archive_filename}")
        else:
            active_session_blocks.append(stext)
            
    active_sessions_str = "\n\n".join(active_session_blocks)
    reconstructed_content = "\n".join(other_content_lines)
    
    if "<!-- SESSIONS_LIST_START -->" in reconstructed_content:
        parts = reconstructed_content.split("<!-- SESSIONS_LIST_START -->")
        header = parts[0]
        footer_parts = parts[1].split("<!-- SESSIONS_LIST_END -->")
        footer = footer_parts[1] if len(footer_parts) > 1 else ""
        reconstructed_content = header + "<!-- SESSIONS_LIST_START -->\n\n" + active_sessions_str + "\n\n<!-- SESSIONS_LIST_END -->" + footer
        
    archive_links_lines = ["\n## 🗃️ Archives de Session (Obsidian Avalon)", "*Sessions de plus de 15 jours déchargées de la mémoire de travail active pour économie de tokens.*", ""]
    all_archive_files = [f for f in os.listdir(archive_dir) if f.startswith("transcripts_") and f.endswith(".md")]
    all_archive_files.sort(reverse=True)
    
    if all_archive_files:
        for filename in all_archive_files:
            m_str = filename.replace("transcripts_", "").replace(".md", "")
            path_abs = os.path.join(archive_dir, filename)
            archive_links_lines.append(f"- **Archive {m_str}** : [[{filename.replace('.md', '')}]] — [Fichier direct](file://{path_abs})")
    else:
        archive_links_lines.append("- *Aucune archive historique créée pour le moment.*")
        
    archive_links_block = "\n".join(archive_links_lines)
    
    if "## 🗃️ Archives de Session" in reconstructed_content:
        reconstructed_content = re.sub(
            r"## 🗃️ Archives de Session.*?(?=<!-- SESSIONS_LIST_START -->|$)",
            archive_links_block + "\n\n",
            reconstructed_content,
            flags=re.DOTALL
        )
    else:
        reconstructed_content = reconstructed_content.replace(
            "<!-- SESSIONS_LIST_START -->",
            archive_links_block + "\n\n<!-- SESSIONS_LIST_START -->"
        )
        
    active_sessions_found = re.findall(
        r"<!-- SESSION: (.*?) -->\s*\r?\n### 📅 Session du (.*?)\s*\(ID: .*?\)\s*\r?\n-\s*\*\*Thème principal\*\*\s*:\s*(.*?)\r?\n",
        reconstructed_content,
        re.DOTALL
    )
    index_lines = ["| Date & Heure | ID Session | Thème Principal |", "| :--- | :--- | :--- |"]
    for sid, sdate, stheme in active_sessions_found:
        index_lines.append(f"| {sdate} | `{sid[:8]}...` | {stheme} |")
    index_table = "\n".join(index_lines)
    
    reconstructed_content = re.sub(
        r"<!-- INDEX_START -->.*?<!-- INDEX_END -->",
        f"<!-- INDEX_START -->\n## 🗂️ Sommaire des Sessions Actives\n\n{index_table}\n<!-- INDEX_END -->",
        reconstructed_content,
        flags=re.DOTALL
    )
    
    return reconstructed_content

# Apply rotation
final_content = rotate_and_archive_sessions(final_content)

# Create backups before applying updates
create_backup(HISTORY_FILE)
create_backup(CHECKPOINT_FILE)

# Apply atomic updates
write_atomic(HISTORY_FILE, final_content)
print(f"[+] Cognitive memory updated in {HISTORY_FILE}")

# Build and write the PROJECT_STATE.md checkpoint
git_main = get_git_info(WORKSPACE)
git_mvp = get_git_info(os.path.join(WORKSPACE, "MVP-GITHUB"))
active_todos = extract_active_todos()

project_state_content = f"""---
type: reference
tags: [memoire/checkpoint, statut/valide]
date: {datetime.now().strftime("%Y-%m-%d")}
---

# ⚓ ANCRE COGNITIVE DE LA DERNIÈRE SESSION
**LIRE EN PRIORITÉ ABSOLUE AU DÉMARRAGE**

## 1. Contexte Système de Reprise
- **Dernière Session Active** : {conversation_id}
- **Dernier Modèle Enregistré** : Gemini 3.5 Flash (Medium) (Tesla)
- **Horodatage de Clôture** : {date_str}
- **Environnement** : MIDGARD (Linux, Antigravity CLI)

## 2. Preuves Git de l'État Réel du Workspace
- **Workspace Principal** ([tesla/](file://{WORKSPACE})) :
  - *Branche active* : `{git_main['branch']}`
  - *Dernier commit* : `{git_main['commit']}`
  - *Statut local* : {git_main['status']}
- **Dépôt MVP-GITHUB** ([MVP-GITHUB/](file://{os.path.join(WORKSPACE, "MVP-GITHUB")})) :
  - *Branche active* : `{git_mvp['branch']}`
  - *Dernier commit* : `{git_mvp['commit']}`
  - *Statut de synchronisation distant* : {git_mvp['status']} (Dépôt publié sur [lordmahonheim-bot/Tesla-Antigravity-CLI](https://github.com/lordmahonheim-bot/Tesla-Antigravity-CLI))

## 3. État des Tâches Actives (Issu du journal des Open-Items)
{active_todos}

## 4. Règles Permanentes Critiques (Vigilum Codex)
- Langue des dépôts publics : Anglais strict.
- Adressage nominal de l'opérateur : **Lord Mahonheim** (proscrire "User" ou "Utilisateur").
- Utilisation exclusive des credentials explicitement délégués. Pas de scan exploratoire du dossier `~/.ssh`.
- **Mémoire Universelle** : À chaque prise de contact, lire en priorité absolue `memory/PROJECT_STATE.md` et citer l'ID de la session active pour attester de ton auto-briefing.

---
*Fiche d'Ancrage actualisée automatiquement sur MIDGARD par Tesla.*
"""

write_atomic(CHECKPOINT_FILE, project_state_content)
print(f"[+] Memory checkpoint updated in {CHECKPOINT_FILE}")

# Automatically trigger subagents database parsing and tracking
print("[*] Automatically triggering subagents database parsing and logging...")
try:
    parser_script = os.path.join(MEMORY_DIR, "log_subagent_parser.py")
    subprocess.run([sys.executable, parser_script], check=True)
except Exception as e:
    print(f"[-] Subagents database parsing failed: {e}")

# Automatically trigger projects list synchronization
print("[*] Automatically triggering projects list synchronization...")
try:
    sync_script = os.path.join(MEMORY_DIR, "sync_projects_list.py")
    subprocess.run([sys.executable, sync_script], check=True)
except Exception as e:
    print(f"[-] Projects list synchronization failed: {e}")
