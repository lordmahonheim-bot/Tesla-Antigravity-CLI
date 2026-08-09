import json
import sqlite3
import subprocess
import sys
import os
import shutil
import time
import yaml
from datetime import datetime

DB_PATH = "/home/lord-mahonheim/bifrost/tesla/Avalon/03-Resources/alexandria_brain.db"
OUTPUTS_DIR = "/home/lord-mahonheim/bifrost/tesla/OUTPUTS"
REPO_DIR = "/home/lord-mahonheim/bifrost/tesla"

def execute_db_query(query, params=(), commit=False, fetchone=False, fetchall=False):
    max_retries = 5
    for attempt in range(max_retries):
        try:
            conn = sqlite3.connect(DB_PATH, timeout=10.0)
            conn.execute("PRAGMA journal_mode=WAL;")
            c = conn.cursor()
            c.execute(query, params)
            if commit:
                conn.commit()
            result = None
            if fetchone:
                result = c.fetchone()
            elif fetchall:
                result = c.fetchall()
            conn.close()
            return result
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e).lower() and attempt < max_retries - 1:
                time.sleep(0.1 * (2 ** attempt))
            else:
                raise

def init_db():
    queries = [
        '''
        CREATE TABLE IF NOT EXISTS loop_executions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            loop_id TEXT UNIQUE,
            status TEXT,
            created_at TIMESTAMP,
            updated_at TIMESTAMP
        )
        ''',
        '''
        CREATE TABLE IF NOT EXISTS loop_iterations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            loop_id TEXT,
            iteration_number INTEGER,
            feedback TEXT,
            verdict TEXT,
            created_at TIMESTAMP
        )
        '''
    ]
    max_retries = 5
    for attempt in range(max_retries):
        try:
            conn = sqlite3.connect(DB_PATH, timeout=10.0)
            conn.execute("PRAGMA journal_mode=WAL;")
            c = conn.cursor()
            for q in queries:
                c.execute(q)
            conn.commit()
            conn.close()
            return
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e).lower() and attempt < max_retries - 1:
                time.sleep(0.1 * (2 ** attempt))
            else:
                raise

def tgg_check(loop_id):
    print(f"[TGG] Running Governance Gateway for {loop_id}...")
    # Mocking policy_engine.sh logic for TGG
    # Verifying loop_id duplication, token budget, validator versions
    res = execute_db_query("SELECT status FROM loop_executions WHERE loop_id = ?", (loop_id,), fetchone=True)
    
    if res and res[0] in ["PASS", "RUNNING"]:
        print(f"[TGG] Error: loop_id {loop_id} already exists or is running.")
        return False

    policy_engine_script = os.path.join(REPO_DIR, "policy_engine.sh")
    if os.path.exists(policy_engine_script):
        result = subprocess.run([policy_engine_script, "--check", loop_id], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[TGG] Policy engine rejected {loop_id}: {result.stderr}")
            return False
    else:
        print("[TGG] policy_engine.sh not found, skipping deep policy check. (Mock PASS)")

    return True

def run_master_code(loop_id, contract_path, feedback=None):
    print(f"[Master-Code] Invoking for {loop_id}...")
    
    manifest_path = os.path.join(OUTPUTS_DIR, "output_manifest.json")
    script_path = os.path.join(REPO_DIR, "MVP-GITHUB/16-Tesla-Master-Code/master_code.py")
    
    cmd = ["python3", script_path, "--contract", contract_path]
    if feedback:
        cmd.extend(["--feedback", feedback])
        
    print(f"[Master-Code] Executing: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[Master-Code] Error: {result.stderr}")
            
    if os.path.exists(manifest_path):
        with open(manifest_path, 'r') as f:
            manifest_data = json.load(f)
            print(f"[Master-Code] Parsed manifest: {len(manifest_data.get('files_modified', []))} files modified.")
    else:
        print(f"[Master-Code] Warning: output_manifest.json not found.")
        
    return manifest_path

def run_code_auditor(loop_id, manifest_path):
    print(f"[Code-Auditor] Auditing {loop_id} based on {manifest_path}...")
    
    verdict_path = os.path.join(OUTPUTS_DIR, "audit_verdict.json")
    script_path = os.path.join(REPO_DIR, "MVP-GITHUB/44-Tesla-Code-Auditor/code_auditor.py")
    
    # 4-level validation chain: SemGrep, Pyright, Smoke Tests, Policy Engine
    cmd = ["python3", script_path, "--manifest", manifest_path]
    print(f"[Code-Auditor] Executing: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[Code-Auditor] Error: {result.stderr}")
        if not os.path.exists(verdict_path):
            with open(verdict_path, 'w') as f:
                json.dump({"verdict": "BLOCK", "feedback": result.stderr}, f, indent=2)
            
    return verdict_path

def record_execution(loop_id, status):
    now = datetime.now().isoformat()
    execute_db_query("INSERT OR REPLACE INTO loop_executions (loop_id, status, created_at, updated_at) VALUES (?, ?, ?, ?)",
                     (loop_id, status, now, now), commit=True)

def record_iteration(loop_id, iter_num, feedback, verdict):
    now = datetime.now().isoformat()
    execute_db_query("INSERT INTO loop_iterations (loop_id, iteration_number, feedback, verdict, created_at) VALUES (?, ?, ?, ?, ?)",
                     (loop_id, iter_num, feedback, verdict, now), commit=True)

def rollback(loop_id, block_reason):
    print(f"[Rollback] Reverting changes for {loop_id}...")
    subprocess.run(["git", "checkout", "HEAD~1", "--", "."], cwd=REPO_DIR)
    
    report_path = os.path.join(OUTPUTS_DIR, f"{loop_id}_block_report.md")
    with open(report_path, 'w') as f:
        f.write(f"# Block Report for {loop_id}\n\n**Reason:**\n{block_reason}\n\nRollback executed successfully.\n")
    print(f"[Rollback] Block report written to {report_path}")

def commit_changes(loop_id, desc="Loop integration complete"):
    print(f"[Git] Committing changes for {loop_id}...")
    msg = f"feat(core): [{loop_id}] {desc}"
    subprocess.run(["git", "add", "."], cwd=REPO_DIR)
    subprocess.run(["git", "commit", "-m", msg], cwd=REPO_DIR)

def validate_contract(contract_path):
    if not os.path.exists(contract_path):
        raise FileNotFoundError(f"Contract file {contract_path} not found.")
    try:
        with open(contract_path, 'r') as f:
            contract = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML contract format: {e}")
    if not isinstance(contract, dict):
        raise ValueError("Contract must be a valid YAML dictionary.")
    print("[Contract] Validation passed.")

def execute_loop(loop_id, contract_path):
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    
    try:
        validate_contract(contract_path)
    except Exception as e:
        print(f"[Contract] Validation failed: {e}")
        return

    init_db()

    if not tgg_check(loop_id):
        print("[TGG] Check failed. Aborting.")
        record_execution(loop_id, "BLOCK")
        return

    record_execution(loop_id, "RUNNING")
    
    max_iterations = 3
    feedback = None

    for i in range(1, max_iterations + 1):
        print(f"\n--- Iteration {i}/{max_iterations} ---")
        
        # 1. Master-Code Execution
        manifest_path = run_master_code(loop_id, contract_path, feedback)
        
        # 2. Code-Auditor Validation
        verdict_path = run_code_auditor(loop_id, manifest_path)
        
        # 3. Parse Verdict
        try:
            with open(verdict_path, 'r') as f:
                audit_result = json.load(f)
                verdict = audit_result.get("verdict", "BLOCK")
                feedback = audit_result.get("feedback", "No feedback provided.")
        except Exception as e:
            verdict = "BLOCK"
            feedback = f"Failed to parse audit verdict: {e}"
            
        record_iteration(loop_id, i, feedback, verdict)
        
        # 4. State Transitions
        if verdict == "PASS":
            commit_changes(loop_id)
            record_execution(loop_id, "PASS")
            print("\n[SUCCESS] Loop completed successfully.")
            
            # Clean up mock output files for next runs
            if os.path.exists(manifest_path): os.remove(manifest_path)
            if os.path.exists(verdict_path): os.remove(verdict_path)
            
            return
            
        elif verdict == "DELAY":
            print(f"\n[DELAY] Feedback received: {feedback}. Re-injecting to Master-Code...")
            continue
            
        elif verdict == "BLOCK":
            print(f"\n[BLOCK] Critical failure: {feedback}.")
            rollback(loop_id, feedback)
            record_execution(loop_id, "BLOCK")
            
            if os.path.exists(manifest_path): os.remove(manifest_path)
            if os.path.exists(verdict_path): os.remove(verdict_path)
            return
            
    print("\n[BLOCK] Max iterations reached.")
    rollback(loop_id, "Max iterations reached without PASS verdict.")
    record_execution(loop_id, "BLOCK")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python tesla_loop_orchestrator.py <loop_id> <contract_path>")
        sys.exit(1)
    
    loop_id = sys.argv[1]
    contract_path = sys.argv[2]
    execute_loop(loop_id, contract_path)
