#!/usr/bin/env python3
# log_subagent_parser.py — Parse JSONL transcript logs, detect shadow-targeting, scrub secrets, and update SQLite DB.
import os
import json
import re
from datetime import datetime
from db_connector import get_db_connection, DEFAULT_WORKSPACE

# Robust Regexes for Scrubbing Sensitive Secrets
SCRUB_PATTERNS = [
    # AWS Access Keys & Secret Keys
    (re.compile(r"(?:AKIA|ASCA|A3T[A-Z0-9])[A-Z0-9]{16}"), "[SCRUBBED_AWS_KEY]"),
    (re.compile(r"(?<![A-Za-z0-9/+=])[A-Za-z0-9/+=]{40}(?![A-Za-z0-9/+=])"), "[SCRUBBED_AWS_SECRET]"),
    # GitHub Personal Access Tokens
    (re.compile(r"ghp_[A-Za-z0-9_]{36,255}"), "[SCRUBBED_GITHUB_TOKEN]"),
    # Slack Webhooks / API Tokens
    (re.compile(r"xox[bapr]-[0-9]{12}-[0-9]{12}-[a-zA-Z0-9]{24}"), "[SCRUBBED_SLACK_TOKEN]"),
    # JSON Web Tokens (JWT)
    (re.compile(r"eyJ[A-Za-z0-9-_=]+\.eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_+/=]+"), "[SCRUBBED_JWT]"),
    # SSH Private Keys
    (re.compile(r"-----BEGIN [A-Z ]+ PRIVATE KEY-----\n[\s\S]+?\n-----END [A-Z ]+ PRIVATE KEY-----"), "[SCRUBBED_SSH_KEY]"),
    # SSH Private Keys (inline)
    (re.compile(r"-----BEGIN [A-Z ]+ PRIVATE KEY-----[A-Za-z0-9+/=\s\n]+-----END [A-Z ]+ PRIVATE KEY-----"), "[SCRUBBED_SSH_KEY]"),
]

def scrub_text(text):
    if not text:
        return text
    scrubbed = text
    for pattern, replacement in SCRUB_PATTERNS:
        scrubbed = pattern.sub(replacement, scrubbed)
    return scrubbed

# Helper to check if a local process PID is active (Unix/Linux)
def is_pid_alive(pid):
    if not pid:
        return False
    try:
        os.kill(int(pid), 0)
        return True
    except OSError:
        return False

# Reconcile stale "running" sessions (Garbage Collector)
def garbage_collect_sessions(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT session_id, date_start FROM subagents_sessions WHERE status = 'running';")
    rows = cursor.fetchall()
    
    now = datetime.now()
    updated_count = 0
    
    for session_id, date_start_str in rows:
        try:
            # Parse start date
            date_start = datetime.strptime(date_start_str, "%Y-%m-%d %H:%M:%S")
            # If session is running for more than 24 hours
            if (now - date_start).total_seconds() > 86400:
                # We transition it to abandoned
                cursor.execute(
                    "UPDATE subagents_sessions SET status = 'abandoned', date_end = ? WHERE session_id = ?;",
                    (now.strftime("%Y-%m-%d %H:%M:%S"), session_id)
                )
                updated_count += 1
        except Exception as e:
            print(f"[-] GC error for session {session_id}: {e}")
            
    if updated_count > 0:
        print(f"[+] Garbage Collector: Marked {updated_count} stale sessions as 'abandoned'.")

def parse_transcript_and_store(conversation_id, transcript_path, parent_session_id=None):
    if not os.path.exists(transcript_path):
        print(f"[-] Transcript path does not exist: {transcript_path}")
        return False
        
    print(f"[*] Parsing transcript {transcript_path} for DB updates...")
    
    date_start_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    date_end_str = date_start_str
    
    # Read and parse JSONL lines
    interactions = []
    metadata = {
        "tokens_prompt": 0,
        "tokens_completion": 0,
        "total_tokens": 0,
    }
    
    skills_detected = [] # list of dicts: {name, target, method, score, detection}
    
    # Track hierarchy depth
    depth = 0
    
    conn = get_db_connection()
    try:
        if parent_session_id:
            cursor = conn.cursor()
            cursor.execute("SELECT execution_depth FROM subagents_sessions WHERE session_id = ?;", (parent_session_id,))
            row = cursor.fetchone()
            if row:
                depth = row[0] + 1
        
        # Parse transcript lines
        with open(transcript_path, "r", encoding="utf-8", errors="ignore") as f:
            current_user_msg = None
            
            for line in f:
                if not line.strip():
                    continue
                try:
                    entry = json.loads(line)
                except Exception:
                    continue
                
                # Check for timestamp
                timestamp = entry.get("timestamp")
                if not timestamp:
                    timestamp = date_start_str
                else:
                    # Clean ISO format to readable string
                    timestamp = timestamp.replace("T", " ").replace("Z", "")
                    if "." in timestamp:
                        timestamp = timestamp.split(".")[0]
                
                # Extract tokens info if present
                if "usage" in entry:
                    usage = entry["usage"]
                    metadata["tokens_prompt"] += usage.get("prompt_tokens", 0)
                    metadata["tokens_completion"] += usage.get("completion_tokens", 0)
                    metadata["total_tokens"] += usage.get("total_tokens", 0)
                
                # Build interaction blocks
                type_ = entry.get("type")
                if type_ == "USER_INPUT":
                    content = entry.get("content", "")
                    match = re.search(r"<USER_REQUEST>(.*?)</USER_REQUEST>", content, re.DOTALL)
                    user_text = match.group(1).strip() if match else content.strip()
                    current_user_msg = user_text
                elif type_ == "PLANNER_RESPONSE":
                    content = entry.get("content", "")
                    if content and current_user_msg:
                        # Extract diagnostic, action, and proof fields
                        diag_match = re.search(r"### Diagnostic(.*?)(### Action|### Preuve|$)", content, re.DOTALL)
                        act_match = re.search(r"### Action(.*?)(### Preuve|### Diagnostic|$)", content, re.DOTALL)
                        proof_match = re.search(r"### Preuve(.*?)(### Action|### Diagnostic|$)", content, re.DOTALL)
                        
                        diag = diag_match.group(1).strip() if diag_match else None
                        act = act_match.group(1).strip() if act_match else None
                        proof = proof_match.group(1).strip() if proof_match else None
                        
                        interactions.append({
                            "num": len(interactions) + 1,
                            "user_prompt": scrub_text(current_user_msg),
                            "agent_response": scrub_text(content),
                            "diagnostic": scrub_text(diag),
                            "action": scrub_text(act),
                            "preuve": scrub_text(proof),
                            "timestamp": timestamp
                        })
                        current_user_msg = None
                
                # Detect Shadow-Targeted Skills
                # Method 1: file_access to a skill directory
                tool_calls = entry.get("tool_calls", [])
                for call in tool_calls:
                    method_name = call.get("name")
                    args = call.get("arguments", {})
                    # Look for viewing a skill file
                    if method_name in ("view_file", "view_file_content"):
                        path = args.get("AbsolutePath", "") or args.get("TargetFile", "")
                        if "skills/" in path and "SKILL.md" in path:
                            # Extract skill name from path
                            parts = path.split("/")
                            try:
                                skill_idx = parts.index("skills")
                                if skill_idx + 1 < len(parts):
                                    skill_name = parts[skill_idx + 1]
                                    target_subagent = entry.get("role", "self")
                                    skills_detected.append({
                                        "name": skill_name,
                                        "target": target_subagent,
                                        "method": "shadow-targeting",
                                        "score": 1.0,
                                        "detection": "file_access"
                                    })
                            except ValueError:
                                pass
                                
                    # Method 3: custom MCP server invocation (api_pattern)
                    elif method_name == "call_mcp_tool":
                        server = args.get("ServerName", "")
                        tool = args.get("ToolName", "")
                        if server:
                            skills_detected.append({
                                "name": f"{server}/{tool}",
                                "target": "self",
                                "method": "shadow-targeting",
                                "score": 0.7,
                                "detection": "api_pattern"
                            })
                            
                # Method 2: System prompt heuristics (system_prompt_heuristics)
                # Look for skill triggers inside prompts
                if entry.get("source") == "SYSTEM" and "skills/" in entry.get("content", ""):
                    content = entry.get("content", "")
                    # Match pattern like: - skill-name (/path/to/skill/SKILL.md)
                    matches = re.findall(r"-\s*([a-zA-Z0-9_-]+)\s*\((.*?skills/.*?SKILL.md)\)", content)
                    for m_name, m_path in matches:
                        skills_detected.append({
                            "name": m_name,
                            "target": "self",
                            "method": "shadow-targeting",
                            "score": 0.8,
                            "detection": "system_prompt_heuristics"
                        })
                        
        # Default Theme extraction
        theme = "Analytical session"
        if interactions:
            theme = interactions[0]["user_prompt"].split("\n")[0][:100]
            
        # SQLite Transaction Wrap
        with conn:
            # 1. UPSERT session entry
            conn.execute("""
            INSERT INTO subagents_sessions (
                session_id, theme, date_start, date_end, status, 
                tokens_prompt, tokens_completion, total_tokens, execution_depth, parent_session_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(session_id) DO UPDATE SET
                theme = excluded.theme,
                date_end = excluded.date_end,
                status = excluded.status,
                tokens_prompt = excluded.tokens_prompt,
                tokens_completion = excluded.tokens_completion,
                total_tokens = excluded.total_tokens;
            """, (
                conversation_id, theme, date_start_str, date_end_str, "completed",
                metadata["tokens_prompt"], metadata["tokens_completion"], metadata["total_tokens"],
                depth, parent_session_id
            ))
            
            # 2. DELETE and RE-INSERT Tasks (to ensure fresh idempotency)
            conn.execute("DELETE FROM subagents_tasks WHERE session_id = ?;", (conversation_id,))
            
            # Read current active tasks from files to log them dynamically
            outputs_dir = os.environ.get("TESLA_OUTPUTS_DIR", os.path.join(DEFAULT_WORKSPACE, "OUTPUTS"))
            if os.path.exists(outputs_dir):
                todo_files = [
                    os.path.join(outputs_dir, f)
                    for f in os.listdir(outputs_dir)
                    if f.startswith("open_items_todo") and f.endswith(".md")
                ]
                if todo_files:
                    todo_files.sort(key=os.path.getmtime, reverse=True)
                    todo_file = todo_files[0]
                    # Parse tasks from todo list
                    with open(todo_file, "r", encoding="utf-8", errors="ignore") as tf:
                        for tf_line in tf:
                            task_match = re.match(r"-\s*\[([ xX])\]\s*(.*)", tf_line)
                            if task_match:
                                is_done = task_match.group(1).lower() == 'x'
                                task_text = scrub_text(task_match.group(2).strip())
                                conn.execute("""
                                INSERT INTO subagents_tasks (session_id, task_name, status, timestamp)
                                VALUES (?, ?, ?, ?);
                                """, (conversation_id, task_text, "done" if is_done else "todo", date_start_str))
            
            # 3. DELETE and RE-INSERT Feedbacks
            conn.execute("DELETE FROM subagents_feedback WHERE session_id = ?;", (conversation_id,))
            for inter in interactions:
                conn.execute("""
                INSERT INTO subagents_feedback (
                    session_id, interaction_num, user_prompt, agent_response, 
                    diagnostic, action, preuve, rating, notes, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """, (
                    conversation_id, inter["num"], inter["user_prompt"], inter["agent_response"],
                    inter["diagnostic"], inter["action"], inter["preuve"], None, None, inter["timestamp"]
                ))
                
            # 4. DELETE and RE-INSERT Skills
            conn.execute("DELETE FROM subagents_skills WHERE session_id = ?;", (conversation_id,))
            
            # Unique skills to prevent duplicate inserts in the same session
            seen_skills = set()
            for skill in skills_detected:
                unique_key = (skill["name"], skill["target"])
                if unique_key in seen_skills:
                    continue
                seen_skills.add(unique_key)
                
                conn.execute("""
                INSERT INTO subagents_skills (
                    skill_name, target_subagent, injection_method, session_id, 
                    date_injection, statut, notes, confidence_score, detection_method
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                """, (
                    skill["name"], skill["target"], skill["method"], conversation_id,
                    date_start_str, "active", scrub_text(f"Detected automatically via {skill['detection']}"),
                    skill["score"], skill["detection"]
                ))
                
            # 5. Garbage Collect stale sessions
            garbage_collect_sessions(conn)
            
        print(f"[+] DB successfully updated for session {conversation_id}.")
        return True
        
    except Exception as e:
        print(f"[-] Failed to update SQLite DB: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    conv_id = os.environ.get("ANTIGRAVITY_CONVERSATION_ID")
    if not conv_id:
        print("[-] ANTIGRAVITY_CONVERSATION_ID not set.")
        exit(1)
        
    home_dir = os.path.expanduser("~")
    log_path = os.path.join(home_dir, ".gemini/antigravity-cli/brain", conv_id, ".system_generated/logs/transcript_full.jsonl")
    if not os.path.exists(log_path):
        log_path = os.path.join(home_dir, ".gemini/antigravity-cli/brain", conv_id, ".system_generated/logs/transcript.jsonl")
        
    if os.path.exists(log_path):
        parse_transcript_and_store(conv_id, log_path)
    else:
        print("[-] Transcript log not found.")
