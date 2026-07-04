#!/usr/bin/env python3
# sync_projects_list.py — Automatically consolidate project history from SGC files, SQLite DB and INDEX.md into v3.0 list.
import os
import re
import sqlite3
import shutil
from datetime import datetime

# Anonymized paths configurations
WORKSPACE = os.environ.get("TESLA_WORKSPACE", ".")
DB_PATH = os.environ.get("ALEXANDRIA_DB_PATH", os.path.join(WORKSPACE, "Avalon/03-Resources/alexandria_brain.db"))
INDEX_PATH = os.path.join(WORKSPACE, "Gestion-de-Chantiers/INDEX.md")
ARCHIVE_README_PATH = os.path.join(WORKSPACE, "Gestion-de-Chantiers/Archivage-de-Chantiers/README.md")
BASE_LIST_PATH = os.path.join(WORKSPACE, "OUTPUTS/liste_projets_antigravity_BASE.md")
V3_LIST_PATH = os.path.join(WORKSPACE, "OUTPUTS/liste_projets_antigravity_v3.md")
AVALON_V3_PATH = os.path.join(WORKSPACE, "Avalon/03-Resources/liste_projets_antigravity_v3.md")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA busy_timeout = 10000;")
    return conn

# Clean local absolute paths to prevent credential / private info leaks
def clean_absolute_paths(text):
    if not text:
        return text
    # Replace absolute home path with relative markdown workspace path
    for prefix in ("/home/lord-mahonheim/bifrost/tesla/", "/home/lord-mahonheim/"):
        text = text.replace(prefix, "")
    return text

# Parse manual notes (USER_NOTES) from existing V3 list to preserve them (bidirectional merge)
def parse_existing_user_notes():
    user_notes = {}
    target_path = V3_LIST_PATH if os.path.exists(V3_LIST_PATH) else BASE_LIST_PATH
    if not os.path.exists(target_path):
        return user_notes
        
    try:
        with open(target_path, "r", encoding="utf-8") as f:
            content = f.read()
        # Regex to capture the notes block
        pattern = r"<!-- USER_NOTES_START \[(.*?)\] -->([\s\S]*?)<!-- USER_NOTES_END \[\1\] -->"
        matches = re.findall(pattern, content)
        for proj_id, notes in matches:
            user_notes[proj_id.strip()] = notes.strip()
    except Exception as e:
        print(f"[-] Failed to parse existing user notes: {e}")
    return user_notes

# Parse projects 1 to 14 (Base) from the BASE file
def get_base_projects_content():
    if not os.path.exists(BASE_LIST_PATH):
        return ""
    try:
        with open(BASE_LIST_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        # Extract section between the section headers
        match = re.search(
            r"(## 📅 Les Projets Fondateurs[\s\S]*?)(---\s*\*Registre d'activité|$)", 
            content
        )
        if match:
            return clean_absolute_paths(match.group(1).strip())
    except Exception as e:
        print(f"[-] Failed to read base projects from BASE file: {e}")
    return ""

# Parse the maximum project number in the base list to resume sequential numbering
def get_next_project_number(base_content):
    numbers = [int(n) for n in re.findall(r"###\s*(\d+)\s*\.\s*Projet", base_content)]
    if numbers:
        return max(numbers) + 1
    return 15


# Scan SGC directory to find cahier des charges files for each active / closed project
def get_sgc_project_files():
    project_files = {}
    sgc_dirs = [
        os.path.join(WORKSPACE, "Gestion-de-Chantiers"),
        os.path.join(WORKSPACE, "Gestion-de-Chantiers/Archivage-de-Chantiers")
    ]
    
    for sgc_dir in sgc_dirs:
        if not os.path.exists(sgc_dir):
            continue
        for file in os.listdir(sgc_dir):
            # Matches formats like DB-SUBAGENTS-SKILLS_v1.3_2026-07-03.md
            match = re.match(r"^([A-Z0-9_-]+)_v[0-9.]+_([0-9-]{10})\.md$", file)
            if match:
                proj_name = match.group(1)
                # Keep the newest file per project name (highest version)
                full_path = os.path.join(sgc_dir, file)
                if proj_name not in project_files or os.path.getmtime(full_path) > os.path.getmtime(project_files[proj_name]):
                    project_files[proj_name] = full_path
    return project_files

# Parse description and objectives from a project's cahier des charges file
def parse_project_details(filepath):
    details = {
        "description": "Objectif et usage non documentés.",
        "realisations": []
    }
    if not os.path.exists(filepath):
        return details
        
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            
        # Parse Description Section (between Section 2 header and Section 3 header or separator)
        desc_match = re.search(r"## 2\. Description([\s\S]*?)(## 3\.|$)", content)
        if desc_match:
            desc_text = desc_match.group(1).strip()
            details["description"] = clean_absolute_paths(desc_text)
            
        # Parse TODO list (completed items in Section 6 or Criteria of closure in Section 10)
        todo_match = re.search(r"## 6\. TODO List([\s\S]*?)(## 7\.|$)", content)
        if todo_match:
            todo_text = todo_match.group(1).strip()
            completed_tasks = re.findall(r"-\s*\[[xX]\]\s*(.*)", todo_text)
            for task in completed_tasks:
                details["realisations"].append(clean_absolute_paths(task.strip()))
                
        # Also check Criteria of closure (Section 10) for completed deliverables
        closing_match = re.search(r"## 10\. Critères de Clôture([\s\S]*?)(## 11\.|$)", content)
        if closing_match:
            closing_text = closing_match.group(1).strip()
            completed_criteria = re.findall(r"-\s*\[[xX]\]\s*(.*)", closing_text)
            for crit in completed_criteria:
                cleaned_crit = clean_absolute_paths(crit.strip())
                if cleaned_crit not in details["realisations"]:
                    details["realisations"].append(cleaned_crit)
                    
    except Exception as e:
        print(f"[-] Error parsing details from {filepath}: {e}")
    return details

# Synchronize the project list file
def sync_list():
    print("[*] Starting projects list synchronization...")
    user_notes = parse_existing_user_notes()
    base_section = get_base_projects_content()
    project_files = get_sgc_project_files()
    
    # Parse INDEX.md to get active project IDs and names
    active_projects = []
    if os.path.exists(INDEX_PATH):
        try:
            with open(INDEX_PATH, "r", encoding="utf-8") as f:
                for line in f:
                    if "## 🗃️ Chantiers Archivés" in line:
                        break
                    # Match line like: | 001 | Plan d'Armement Pluridisciplinaire | 🟡 En validation |
                    match = re.match(r"\|\s*([0-9]{3})\s*\|\s*([A-Za-z0-9_-]+.*?)\s*\|.*", line)
                    if match:
                        proj_id = match.group(1)
                        proj_name = match.group(2).strip()
                        proj_key = proj_name.upper().replace(" ", "-").replace("'", "-")
                        active_projects.append((proj_id, proj_name, proj_key))
        except Exception as e:
            print(f"[-] Failed to read active projects from INDEX: {e}")
            
    # Parse ARCHIVE_README.md to get archived projects
    archived_projects = []
    if os.path.exists(ARCHIVE_README_PATH):
        try:
            with open(ARCHIVE_README_PATH, "r", encoding="utf-8") as f:
                for line in f:
                    match = re.match(r"\|\s*([0-9]{3})\s*\|\s*([A-Za-z0-9_-]+.*?)\s*\|.*", line)
                    if match:
                        proj_id = match.group(1)
                        proj_name = match.group(2).strip()
                        proj_key = proj_name.upper().replace(" ", "-").replace("'", "-")
                        if (proj_id, proj_name, proj_key) not in active_projects:
                            archived_projects.append((proj_id, proj_name, proj_key))
        except Exception as e:
            print(f"[-] Failed to read archived projects: {e}")
            
    # Combine active and archived SGC chantiers
    consolidated_projects = sorted(active_projects + archived_projects, key=lambda x: x[0])
    
    # Query SQLite database for extra verification on completed tasks
    db_tasks = {}
    if os.path.exists(DB_PATH):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT session_id, task_name, status FROM subagents_tasks WHERE status='done';")
            for session_id, task_name, status in cursor.fetchall():
                if session_id not in db_tasks:
                    db_tasks[session_id] = []
                db_tasks[session_id].append(clean_absolute_paths(task_name))
            conn.close()
        except Exception as e:
            print(f"[-] Database tasks query failed: {e}")
            
    # Rebuild consolidated chantiers list
    chantiers_blocks = []
    
    def find_matching_file(p_name, p_key):
        for k in (p_key, p_key.replace("-", ""), p_name.upper().replace(" ", "-")):
            if k in project_files:
                return project_files[k]
        for k, filepath in project_files.items():
            if k in p_key or p_key in k:
                return filepath
        tokens = [t.upper() for t in re.findall(r"[a-zA-Z0-9]{3,}", p_name) if t.upper() not in ("DEEP", "SUBAGENT", "AGENT")]
        if tokens:
            best_match = None
            max_score = 0
            for k, filepath in project_files.items():
                score = sum(1 for token in tokens if token in k)
                if score > max_score:
                    max_score = score
                    best_match = filepath
            if max_score >= 1:
                return best_match
        return None

    EXCLUDE_PROJECT_IDS = {"001", "002", "003"}
    archived_ids = {x[0] for x in archived_projects}
    next_num = get_next_project_number(base_section)

    for proj_id, proj_name, proj_key in consolidated_projects:
        if proj_id in EXCLUDE_PROJECT_IDS:
            continue
        if proj_id not in archived_ids:
            continue
            
        file_path = find_matching_file(proj_name, proj_key)
                
        # Parse details
        details = {"description": "Objectif et usage non documentés.", "realisations": []}
        if file_path:
            details = parse_project_details(file_path)
            
        # Enrich completed tasks from SQLite DB if the session matches
        if os.path.exists(DB_PATH):
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT session_id FROM subagents_sessions WHERE theme LIKE ? OR session_id LIKE ?;", 
                    (f"%{proj_name}%", f"%{proj_id}%")
                )
                matching_sessions = [r[0] for r in cursor.fetchall()]
                conn.close()
                for sid in matching_sessions:
                    if sid in db_tasks:
                        for dtask in db_tasks[sid]:
                            if dtask not in details["realisations"]:
                                details["realisations"].append(dtask)
            except Exception as e:
                pass
                
        # Build Markdown section
        desc_list = details["description"].split("\n")
        desc_markdown = "\n".join([f"* {line.lstrip('* ').strip()}" for line in desc_list if line.strip()])
        
        realisations_markdown = ""
        if details["realisations"]:
            realisations_markdown = "\n".join([f"    * {r}" for r in details["realisations"]])
        else:
            realisations_markdown = "    * Réalisations techniques en cours."
            
        # Re-inject USER_NOTES if present
        notes_markdown = ""
        if proj_id in user_notes:
            notes_markdown = (
                f"\n<!-- USER_NOTES_START [{proj_id}] -->\n"
                f"{user_notes[proj_id]}\n"
                f"<!-- USER_NOTES_END [{proj_id}] -->\n"
            )
        else:
            notes_markdown = (
                f"\n<!-- USER_NOTES_START [{proj_id}] -->\n"
                f"*Notes de cadrage manuelles de Lord Mahonheim (complétées à la volée s'il y a lieu).*\n"
                f"<!-- USER_NOTES_END [{proj_id}] -->\n"
            )
            
        chantiers_blocks.append(
            f"### {next_num}. Projet : {proj_name}\n"
            f"*   **Objectif & Usage :**\n{desc_markdown}\n"
            f"*   **Réalisations techniques :**\n{realisations_markdown}\n"
            f"{notes_markdown}"
        )
        next_num += 1
        
    consolidated_section = "\n\n".join(chantiers_blocks)
    
    # Construct complete V3 output content
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    v3_content = f"""---
type: reference
tags: [gestion/projets, technique/synthese, statut/valide]
source: "[[SESSION_TRANSCRIPTS.md]]"
date: {date_str}
version: 3.0
---

# LISTE EXHAUSTIVE DES PROJETS TESLA SUR ANTIGRAVITY (V3)
**Date de mise à jour :** {date_str}  
**Analyste :** Tesla (sur Antigravity CLI)  
**Destinataire :** Lord Mahonheim (Abdellah MOUHTAJ)

Ce document dresse la cartographie et la structure étanche de nos réalisations communes pour interdire toute confusion opérationnelle.

---

{base_section}

---

## 📅 Nouveaux Chantiers (SGC)

{consolidated_section}

---
*Registre d'activité et de classification validé localement sur MIDGARD par Tesla.*

Signé / Fait par : Tesla sur Antigravity CLI  
Main rendue à Mahonheim"""
    
    # Save the file with backup rotation
    backup_dir = os.path.join(WORKSPACE, "memory/backup")
    os.makedirs(backup_dir, exist_ok=True)
    
    if os.path.exists(V3_LIST_PATH):
        for i in range(8, -1, -1):
            old_bak = os.path.join(backup_dir, f"liste_projets_antigravity_v3.md.bak.{i}")
            new_bak = os.path.join(backup_dir, f"liste_projets_antigravity_v3.md.bak.{i+1}")
            if os.path.exists(old_bak):
                os.replace(old_bak, new_bak)
        shutil_bak = os.path.join(backup_dir, "liste_projets_antigravity_v3.md.bak.0")
        shutil.copy2(V3_LIST_PATH, shutil_bak)
        
    # Atomic write to main V3 location
    temp_v3_path = V3_LIST_PATH + ".tmp"
    with open(temp_v3_path, "w", encoding="utf-8") as f:
        f.write(v3_content)
    os.replace(temp_v3_path, V3_LIST_PATH)
    
    # Also write to Avalon resources
    os.makedirs(os.path.dirname(AVALON_V3_PATH), exist_ok=True)
    shutil.copy2(V3_LIST_PATH, AVALON_V3_PATH)
    
    print(f"[+] Projects list successfully synchronized and saved to {V3_LIST_PATH} and {AVALON_V3_PATH}")

if __name__ == "__main__":
    sync_list()
