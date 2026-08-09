#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tesla_loop_orchestrator.py — Supervisor CLI for Act-Verify-Learn-Repeat loop engineering.
"""

import os
import sys
import time
import uuid
import json
import random
import hashlib
import argparse
import shutil
import subprocess
from datetime import datetime
from functools import wraps
from typing import Dict, List, Any, Optional

# Try importing jsonschema and PyYAML
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

try:
    import jsonschema
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False

# Try importing database connection info from centralized memory
sys.path.insert(0, "/home/lord-mahonheim/bifrost/tesla")
try:
    from memory.db_connector import DB_PATH
    DEFAULT_DB_PATH = DB_PATH
except Exception:
    DEFAULT_DB_PATH = "/home/lord-mahonheim/bifrost/tesla/Avalon/03-Resources/alexandria_brain.db"

import sqlite3

# YAML contract schema definition
CONTRACT_SCHEMA = {
    "type": "object",
    "properties": {
        "meta": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "version": {"type": "string"},
                "project": {"type": "string"},
                "description": {"type": "string"}
            },
            "required": ["name", "version", "project"]
        },
        "execution_limits": {
            "type": "object",
            "properties": {
                "max_iterations": {"type": "integer", "minimum": 1, "maximum": 10},
                "financial_budget_usd": {"type": "number", "minimum": 0.1, "maximum": 5.0},
                "token_budget": {"type": "integer", "minimum": 1000},
                "timeout_seconds": {"type": "integer", "minimum": 10}
            },
            "required": ["max_iterations", "financial_budget_usd"]
        },
        "target": {
            "type": "object",
            "properties": {
                "files": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "directory": {"type": "string"}
            },
            "required": ["files"]
        },
        "goal": {"type": "string"},
        "verify": {
            "type": "object",
            "properties": {
                "rungs": {
                    "type": "array",
                    "items": {"type": "string", "enum": ["style", "types", "tests", "referee"]}
                },
                "strict": {"type": "boolean"},
                "custom_rules_path": {"type": "string"}
            },
            "required": ["rungs"]
        },
        "referee_config": {
            "type": "object",
            "properties": {
                "model": {"type": "string"},
                "temperature": {"type": "number", "minimum": 0.0, "maximum": 1.0}
            }
        },
        "rollback_policy": {
            "type": "object",
            "properties": {
                "strategy": {"type": "string", "enum": ["git", "shutil"]},
                "auto_rollback": {"type": "boolean"}
            },
            "required": ["strategy"]
        }
    },
    "required": ["meta", "execution_limits", "target", "goal", "verify", "rollback_policy"]
}


def with_sqlite_retry(max_retries: int = 5, base_delay: float = 0.1, max_jitter: float = 0.05):
    """
    Decorator to retry SQLite writes on OperationalError ('database is locked')
    using exponential backoff and random jitter.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except sqlite3.OperationalError as e:
                    if "locked" in str(e).lower() and retries < max_retries:
                        retries += 1
                        delay = (2 ** retries) * base_delay + random.uniform(0, max_jitter)
                        time.sleep(delay)
                    else:
                        raise
        return wrapper
    return decorator


def manual_yaml_load(filepath: str) -> Dict[str, Any]:
    """
    A line-by-line fallback parser for Loop Contracts when PyYAML is not present.
    """
    import re
    data = {}
    current_key = None
    sub_key = None
    multiline_accumulating = False
    multiline_buffer = []

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                continue

            # Handle multiline block accumulation
            if multiline_accumulating:
                indent = len(line) - len(line.lstrip())
                if indent > 2:
                    multiline_buffer.append(stripped)
                    continue
                else:
                    val = " ".join(multiline_buffer)
                    if current_key and sub_key:
                        data.setdefault(current_key, {})[sub_key] = val
                    elif current_key:
                        data[current_key] = val
                    multiline_accumulating = False
                    multiline_buffer = []

            # Check indentation for sub-keys
            if line.startswith(' ') or line.startswith('\t'):
                match = re.match(r'^\s+([a-zA-Z0-9_-]+)\s*:\s*(.*)$', line)
                if match and current_key:
                    k, v = match.groups()
                    v = v.strip().strip('"').strip("'")
                    if v in (">", "|"):
                        multiline_accumulating = True
                        sub_key = k
                        continue
                    
                    # Convert types
                    if v.isdigit():
                        v = int(v)
                    elif re.match(r'^\d+\.\d+$', v):
                        v = float(v)
                    elif v.lower() == 'true':
                        v = True
                    elif v.lower() == 'false':
                        v = False
                    
                    data.setdefault(current_key, {})[k] = v
                elif stripped.startswith('-') and current_key and sub_key:
                    item = stripped[1:].strip().strip('"').strip("'")
                    if current_key == 'target' and sub_key == 'files':
                        data.setdefault('target', {}).setdefault('files', []).append(item)
                    elif current_key == 'verify' and sub_key == 'rungs':
                        data.setdefault('verify', {}).setdefault('rungs', []).append(item)
            else:
                # Top level key
                match = re.match(r'^([a-zA-Z0-9_-]+)\s*:\s*(.*)$', line)
                if match:
                    current_key, v = match.groups()
                    v = v.strip().strip('"').strip("'")
                    sub_key = None
                    if v in (">", "|"):
                        multiline_accumulating = True
                        continue
                    if v:
                        if v.isdigit():
                            v = int(v)
                        elif v.lower() == 'true':
                            v = True
                        elif v.lower() == 'false':
                            v = False
                        data[current_key] = v
                    else:
                        data[current_key] = {}

        if multiline_accumulating:
            val = " ".join(multiline_buffer)
            if current_key and sub_key:
                data.setdefault(current_key, {})[sub_key] = val
            elif current_key:
                data[current_key] = val

    return data


class LoopContract:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.data = self._load()
        self._validate()

    def _load(self) -> Dict[str, Any]:
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(f"Contract file not found at: {self.filepath}")

        # Check if it is JSON
        if self.filepath.endswith('.json'):
            with open(self.filepath, 'r', encoding='utf-8') as f:
                return json.load(f)

        if HAS_YAML:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        else:
            return manual_yaml_load(self.filepath)

    def _validate(self) -> None:
        if HAS_JSONSCHEMA:
            try:
                jsonschema.validate(instance=self.data, schema=CONTRACT_SCHEMA)
            except jsonschema.ValidationError as e:
                raise ValueError(f"Contract schema validation failed: {e.message}")
        else:
            # Minimal custom validation
            for req in ["meta", "execution_limits", "target", "goal", "verify", "rollback_policy"]:
                if req not in self.data:
                    raise ValueError(f"Contract missing required section: '{req}'")

        self.name: str = self.data["meta"]["name"]
        self.project: str = self.data["meta"]["project"]
        self.version: str = self.data["meta"]["version"]
        self.goal: str = self.data["goal"]
        self.target_files: List[str] = self.data["target"]["files"]
        self.max_iterations: int = self.data["execution_limits"]["max_iterations"]
        self.financial_budget_usd: float = self.data["execution_limits"]["financial_budget_usd"]
        self.token_budget: int = self.data["execution_limits"]["token_budget"]
        self.timeout_seconds: int = self.data["execution_limits"].get("timeout_seconds", 300)
        self.rollback_strategy: str = self.data["rollback_policy"]["strategy"]
        self.auto_rollback: bool = self.data["rollback_policy"].get("auto_rollback", True)
        self.directory: str = self.data["target"].get("directory", "/home/lord-mahonheim/bifrost/tesla")


class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._conn = None

    def get_conn(self) -> sqlite3.Connection:
        if self._conn is None:
            # Ensure directories exist
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            self._conn = sqlite3.connect(self.db_path, timeout=10.0)
            self._conn.execute("PRAGMA foreign_keys = ON;")
            self._conn.execute("PRAGMA journal_mode = WAL;")
        return self._conn

    @with_sqlite_retry()
    def init_execution(self, execution_id: str, contract: LoopContract) -> None:
        conn = self.get_conn()
        with conn:
            conn.execute(
                """
                INSERT INTO loop_executions (
                    id, project, contract_version, goal, start_time, status,
                    total_iterations, total_tokens, total_cost_usd,
                    max_iterations, token_budget, financial_budget_usd
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    execution_id,
                    contract.project,
                    contract.version,
                    contract.goal,
                    datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "RUNNING",
                    0,
                    0,
                    0.0,
                    contract.max_iterations,
                    contract.token_budget,
                    contract.financial_budget_usd
                )
            )

    @with_sqlite_retry()
    def log_iteration(self, execution_id: str, iteration: int, action: str,
                       verdict: str, deltas: Dict[str, Any],
                       tokens: int, cost: float, report_path: str) -> None:
        conn = self.get_conn()
        with conn:
            conn.execute(
                """
                INSERT INTO loop_iterations (
                    execution_id, iteration_number, timestamp, action_taken,
                    verdict, learning_deltas, tokens_used, cost_usd, report_path
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    execution_id,
                    iteration,
                    datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                    action,
                    verdict,
                    json.dumps(deltas),
                    tokens,
                    cost,
                    report_path
                )
            )
            # Update aggregates in loop_executions
            conn.execute(
                """
                UPDATE loop_executions
                SET total_iterations = ?,
                    total_tokens = total_tokens + ?,
                    total_cost_usd = total_cost_usd + ?
                WHERE id = ?
                """,
                (iteration, tokens, cost, execution_id)
            )

    @with_sqlite_retry()
    def finalize_execution(self, execution_id: str, final_status: str) -> None:
        conn = self.get_conn()
        with conn:
            conn.execute(
                """
                UPDATE loop_executions
                SET status = ?,
                    end_time = ?
                WHERE id = ?
                """,
                (final_status, datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"), execution_id)
            )

    def get_aggregate_metrics(self, execution_id: str) -> Dict[str, Any]:
        conn = self.get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT total_iterations, total_tokens, total_cost_usd FROM loop_executions WHERE id = ?",
            (execution_id,)
        )
        row = cursor.fetchone()
        if row:
            return {
                "total_iterations": row[0],
                "total_tokens": row[1],
                "total_cost_usd": row[2]
            }
        return {"total_iterations": 0, "total_tokens": 0, "total_cost_usd": 0.0}

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None


class GitRollbackHandler:
    def __init__(self, directory: str, execution_id: str, verbose: bool):
        self.directory = directory
        self.execution_id = execution_id
        self.verbose = verbose
        self.start_commit = None
        self.original_branch = None
        self.temp_branch = f"temp-loop-{execution_id[:8]}"

    def _run_git(self, args: List[str]) -> str:
        res = subprocess.run(["git"] + args, cwd=self.directory, capture_output=True, text=True)
        if res.returncode != 0:
            raise RuntimeError(f"Git command failed: git {' '.join(args)}\nError: {res.stderr}")
        return res.stdout.strip()

    def create_snapshot(self) -> None:
        if self.verbose:
            print("[*] Creating Git snapshot...")
        # Check if dirty
        status = self._run_git(["status", "--porcelain"])
        if status:
            print(f"[!] Warning: Git working tree is dirty. Saving dirty files first.")
            # stash dirty changes
            self._run_git(["stash", "--include-untracked"])
        
        self.original_branch = self._run_git(["rev-parse", "--abbrev-ref", "HEAD"])
        self.start_commit = self._run_git(["rev-parse", "HEAD"])
        
        # Create and switch to isolated temporary branch
        self._run_git(["checkout", "-b", self.temp_branch])
        if self.verbose:
            print(f"[+] Isolated execution branch '{self.temp_branch}' created at commit {self.start_commit[:7]}")

    def restore_snapshot(self) -> None:
        print("[!] Rollback triggered: resetting workspace files to original state via Git.")
        try:
            self._run_git(["reset", "--hard", self.start_commit])
            self._run_git(["checkout", self.original_branch])
            self._run_git(["branch", "-D", self.temp_branch])
            print("[+] Git workspace rolled back successfully.")
        except Exception as e:
            print(f"[-] Git rollback failed: {e}")

    def discard_snapshot(self) -> None:
        if self.verbose:
            print("[*] Discarding backup: merging changes from temporary branch...")
        try:
            self._run_git(["checkout", self.original_branch])
            # Merge temp branch changes
            self._run_git(["merge", self.temp_branch])
            self._run_git(["branch", "-D", self.temp_branch])
            if self.verbose:
                print("[+] Temporary Git branch merged and purged successfully.")
        except Exception as e:
            print(f"[-] Failed to discard/merge Git snapshot: {e}")


class ShutilRollbackHandler:
    def __init__(self, target_files: List[str], base_dir: str, execution_id: str, verbose: bool):
        self.target_files = target_files
        self.base_dir = base_dir
        self.execution_id = execution_id
        self.verbose = verbose
        self.backup_dir = os.path.join(base_dir, f".runtime/backups/{execution_id}")

    def create_snapshot(self) -> None:
        if self.verbose:
            print(f"[*] Creating folder-based backup in {self.backup_dir}...")
        os.makedirs(self.backup_dir, exist_ok=True)
        for filepath in self.target_files:
            full_path = os.path.join(self.base_dir, filepath)
            if os.path.exists(full_path):
                backup_path = os.path.join(self.backup_dir, filepath)
                os.makedirs(os.path.dirname(backup_path), exist_ok=True)
                shutil.copy2(full_path, backup_path)
                if self.verbose:
                    print(f"    Backed up: {filepath}")

    def restore_snapshot(self) -> None:
        print("[!] Rollback triggered: restoring files from folder backup.")
        for filepath in self.target_files:
            backup_path = os.path.join(self.backup_dir, filepath)
            full_path = os.path.join(self.base_dir, filepath)
            if os.path.exists(backup_path):
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                shutil.copy2(backup_path, full_path)
                if self.verbose:
                    print(f"    Restored: {filepath}")
            else:
                if os.path.exists(full_path):
                    os.remove(full_path)
                    if self.verbose:
                        print(f"    Removed newly created file: {filepath}")
        self.discard_snapshot()

    def discard_snapshot(self) -> None:
        if self.verbose:
            print("[*] Purging backup folder...")
        if os.path.exists(self.backup_dir):
            shutil.rmtree(self.backup_dir)


class LoopOrchestrator:
    def __init__(self, contract: LoopContract, db_mgr: DatabaseManager,
                 action_agent: str, validator: str, output_dir: str, verbose: bool):
        self.contract = contract
        self.db_mgr = db_mgr
        self.action_agent = action_agent
        self.validator = validator
        self.output_dir = output_dir
        self.verbose = verbose
        self.execution_id = str(uuid.uuid4())
        self.iteration_history = []

        if contract.rollback_strategy == "git":
            self.rollback_handler = GitRollbackHandler(contract.directory, self.execution_id, verbose)
        else:
            self.rollback_handler = ShutilRollbackHandler(contract.target_files, contract.directory, self.execution_id, verbose)

    def compute_error_hash(self, errors: List[Dict[str, Any]]) -> str:
        """
        Computes deterministic SHA-256 hash of sorted errors.
        """
        sorted_errors = sorted(errors, key=lambda e: (e.get("file", ""), e.get("line", 0), e.get("message", "")))
        serialized = json.dumps(sorted_errors, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def write_json_log(self, status: str) -> str:
        metrics = self.db_mgr.get_aggregate_metrics(self.execution_id)
        log_data = {
            "execution_id": self.execution_id,
            "project": self.contract.project,
            "contract_name": self.contract.name,
            "goal": self.contract.goal,
            "status": status,
            "total_iterations": metrics["total_iterations"],
            "metrics": {
                "total_tokens_consumed": metrics["total_tokens"],
                "total_cost_usd": metrics["total_cost_usd"]
            },
            "iterations": self.iteration_history
        }
        os.makedirs(self.output_dir, exist_ok=True)
        json_path = os.path.join(self.output_dir, f"{self.execution_id}_session.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2)
        return json_path

    def write_markdown_report(self, status: str, reason: str = "") -> str:
        metrics = self.db_mgr.get_aggregate_metrics(self.execution_id)
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        md_content = f"""# LOOP EXECUTION REPORT - {self.execution_id}

## Metadata
- **Status**: {status}
- **Termination Reason**: {reason if reason else 'N/A'}
- **Contract**: {self.contract.name} (v{self.contract.version})
- **Project**: {self.contract.project}
- **Total Iterations**: {metrics["total_iterations"]} / {self.contract.max_iterations}
- **Token Usage**: {metrics["total_tokens"]} / {self.contract.token_budget}
- **Cost (USD)**: ${metrics["total_cost_usd"]:.6f} / ${self.contract.financial_budget_usd:.2f}
- **Report Date**: {now_str}

## Goal Statement
{self.contract.goal}

## Iteration History

| Iteration | Verdict | Action Taken | Tokens Used | Cost (USD) | Error Hash |
| :--- | :--- | :--- | :--- | :--- | :--- |
"""
        for it in self.iteration_history:
            md_content += f"| {it['number']} | {it['verdict']} | {it['action_taken']} | {it['tokens_consumed']} | ${it['cost_usd']:.6f} | {it['error_hash'][:10]}... |\n"

        md_content += "\n## Diagnostics & Rung Verdicts\n"
        if self.iteration_history:
            last_it = self.iteration_history[-1]
            md_content += f"### Last Iteration (# {last_it['number']}) Verdict: **{last_it['verdict']}**\n"
            if last_it.get("errors"):
                md_content += "#### Failed Errors:\n"
                for err in last_it["errors"]:
                    md_content += f"- **{err.get('file', 'unknown')}** (line {err.get('line', '?')}): {err.get('message', '')}\n"
            else:
                md_content += "No errors reported.\n"
        else:
            md_content += "No iterations performed.\n"

        os.makedirs(self.output_dir, exist_ok=True)
        md_path = os.path.join(self.output_dir, f"{self.execution_id}_report.md")
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        return md_path

    def run_dry_run(self) -> str:
        print("[*] Running dry-run simulation...")
        self.db_mgr.init_execution(self.execution_id, self.contract)
        
        # Simulate single iteration passing
        sim_errors = []
        sim_hash = self.compute_error_hash(sim_errors)
        sim_tokens = 500
        sim_cost = 0.01
        
        action_desc = "Simulated dry-run loop execution"
        
        # Log dry-run iteration
        self.iteration_history.append({
            "number": 1,
            "verdict": "PASS",
            "action_taken": action_desc,
            "tokens_consumed": sim_tokens,
            "cost_usd": sim_cost,
            "error_hash": sim_hash,
            "errors": sim_errors
        })
        
        self.db_mgr.log_iteration(
            self.execution_id,
            1,
            action_desc,
            "PASS",
            {"errors": sim_errors, "advice": "Dry-run simulation success"},
            sim_tokens,
            sim_cost,
            "MOCK_REPORT_PATH"
        )
        
        self.db_mgr.finalize_execution(self.execution_id, "PASS")
        
        json_path = self.write_json_log("PASS")
        md_path = self.write_markdown_report("PASS", "DRY_RUN_SIMULATION")
        
        print(f"[+] Dry-run simulation finished successfully.")
        print(f"    JSON Log: {json_path}")
        print(f"    Markdown Report: {md_path}")
        return "PASS"

    def _invoke_actuator(self, learning_deltas: str) -> str:
        """
        Calls the actuator component using python subprocess.
        """
        # Look for executable script under skills/tesla-master-code/scripts/
        script_dir = f"/home/lord-mahonheim/bifrost/tesla/.agents/skills/{self.action_agent}/scripts"
        script_path = None
        if os.path.exists(script_dir):
            scripts = [f for f in os.listdir(script_dir) if f.endswith('.py')]
            if scripts:
                script_path = os.path.join(script_dir, scripts[0])

        if not script_path or not os.path.exists(script_path):
            # Try workspace fallback or raise error
            raise FileNotFoundError(f"Actuator script not found under skill {self.action_agent}")

        if self.verbose:
            print(f"[*] Invoking actuator script: {script_path}")

        cmd = [
            sys.executable,
            script_path,
            "--goal", self.contract.goal,
            "--learning-deltas", learning_deltas,
            "--files", ",".join(self.contract.target_files)
        ]
        
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            raise RuntimeError(f"Actuator execution failed with code {res.returncode}.\nOutput: {res.stdout}\nError: {res.stderr}")
        
        return f"Actuator executed successfully. Output: {res.stdout.strip()[:100]}"

    def _invoke_validator(self) -> Dict[str, Any]:
        """
        Calls the validator component using python subprocess and parses JSON output.
        """
        script_dir = f"/home/lord-mahonheim/bifrost/tesla/.agents/skills/{self.validator}/scripts"
        script_path = None
        if os.path.exists(script_dir):
            scripts = [f for f in os.listdir(script_dir) if f.endswith('.py')]
            if scripts:
                script_path = os.path.join(script_dir, scripts[0])

        if not script_path or not os.path.exists(script_path):
            raise FileNotFoundError(f"Validator script not found under skill {self.validator}")

        if self.verbose:
            print(f"[*] Invoking validator script: {script_path}")

        cmd = [
            sys.executable,
            script_path,
            "--files", ",".join(self.contract.target_files)
        ]
        
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            raise RuntimeError(f"Validator execution failed with code {res.returncode}.\nOutput: {res.stdout}\nError: {res.stderr}")

        try:
            return json.loads(res.stdout.strip())
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Validator output is not valid JSON. Content: {res.stdout}\nParse Error: {e}")

    def run(self) -> str:
        print(f"[*] Starting Loop Orchestrator session: {self.execution_id}")
        self.db_mgr.init_execution(self.execution_id, self.contract)

        self.rollback_handler.create_snapshot()

        previous_hash = None
        previous_failed_rung = 0
        previous_error_count = 0
        learning_deltas_str = ""

        status = "RUNNING"
        reason = ""

        try:
            for iteration in range(1, self.contract.max_iterations + 1):
                print(f"\n--- Iteration {iteration} / {self.contract.max_iterations} ---")
                
                # 1. Pre-Iteration limits check
                metrics = self.db_mgr.get_aggregate_metrics(self.execution_id)
                if metrics["total_cost_usd"] >= self.contract.financial_budget_usd:
                    status = "BLOCK"
                    reason = "BUDGET_EXCEEDED"
                    break
                if metrics["total_cost_usd"] >= 5.00:
                    status = "BLOCK"
                    reason = "SAFETY_LIMIT_EXCEEDED"
                    break
                if metrics["total_tokens"] >= self.contract.token_budget:
                    status = "BLOCK"
                    reason = "TOKEN_BUDGET_EXCEEDED"
                    break

                # 2. ACT Phase
                print(f"[*] ACT phase: invoking {self.action_agent}...")
                action_taken = self._invoke_actuator(learning_deltas_str)
                print(f"[+] ACT response: {action_taken}")

                # 3. VERIFY Phase
                print(f"[*] VERIFY phase: invoking {self.validator}...")
                audit_result = self._invoke_validator()
                
                verdict = audit_result.get("verdict", "BLOCK")
                failed_rung = audit_result.get("failed_rung", 0)
                errors = audit_result.get("errors", [])
                learning_deltas_str = audit_result.get("learning_deltas", "")
                
                tokens_used = audit_result.get("tokens_used", 0)
                cost_usd = audit_result.get("cost_usd", 0.0)

                current_hash = self.compute_error_hash(errors)
                error_count = len(errors)

                print(f"[+] Verdict: {verdict} (Failed Rung: {failed_rung}, Errors: {error_count})")

                # Track iteration history
                self.iteration_history.append({
                    "number": iteration,
                    "verdict": verdict,
                    "action_taken": action_taken,
                    "tokens_consumed": tokens_used,
                    "cost_usd": cost_usd,
                    "error_hash": current_hash,
                    "errors": errors
                })

                # Log to SQLite
                self.db_mgr.log_iteration(
                    self.execution_id,
                    iteration,
                    action_taken,
                    verdict,
                    {"errors": errors, "advice": learning_deltas_str},
                    tokens_used,
                    cost_usd,
                    os.path.join(self.output_dir, f"{self.execution_id}_iteration_{iteration}.json")
                )

                # 4. FSM Transitions
                if verdict == "PASS":
                    status = "PASS"
                    reason = "SUCCESS"
                    break
                elif verdict == "BLOCK":
                    status = "BLOCK"
                    reason = "CRITICAL_AUDIT_VERDICT"
                    break
                elif verdict == "DELAY":
                    # Stagnation check
                    if previous_hash and current_hash == previous_hash:
                        status = "BLOCK"
                        reason = "COGNITIVE_STAGNATION"
                        break

                    # Regression check
                    if error_count > previous_error_count:
                        status = "BLOCK"
                        reason = "REGRESSION_DETECTED_ERROR_COUNT"
                        break
                    if failed_rung < previous_failed_rung:
                        status = "BLOCK"
                        reason = "REGRESSION_DETECTED_FAILED_RUNG"
                        break

                    # Progressive iteration setup
                    previous_hash = current_hash
                    previous_error_count = error_count
                    previous_failed_rung = failed_rung
                else:
                    status = "BLOCK"
                    reason = f"UNKNOWN_VERDICT_{verdict}"
                    break

            # Check if iterations limit exceeded
            if status == "RUNNING":
                status = "BLOCK"
                reason = "MAX_ITERATIONS_EXCEEDED"

        except Exception as e:
            status = "BLOCK"
            reason = f"UNHANDLED_EXCEPTION: {str(e)}"
            print(f"[-] Error during execution loop: {e}")
            raise e
        finally:
            self.db_mgr.finalize_execution(self.execution_id, status)
            
            # Write final reports
            json_path = self.write_json_log(status)
            md_path = self.write_markdown_report(status, reason)
            print(f"\n[*] Execution finalized with status: {status} (Reason: {reason})")
            print(f"    JSON Log: {json_path}")
            print(f"    Markdown Report: {md_path}")

            # Enforce rollback policy
            if status == "BLOCK":
                if self.contract.auto_rollback:
                    self.rollback_handler.restore_snapshot()
                else:
                    print("[!] Auto-rollback is disabled in contract. Workspace left modified.")
            else:
                self.rollback_handler.discard_snapshot()

        return status


def main():
    parser = argparse.ArgumentParser(description="Tesla/Antigravity Loop Orchestrator CLI")
    parser.add_argument("-c", "--contract", required=True, help="Path to the Loop Contract (YAML or JSON)")
    parser.add_argument("-d", "--db", default=DEFAULT_DB_PATH, help=f"Path to SQLite Alexandria database (default: {DEFAULT_DB_PATH})")
    parser.add_argument("-a", "--action-agent", default="tesla-master-code", help="Actuator subagent (default: tesla-master-code)")
    parser.add_argument("-v", "--validator", default="tesla-code-auditor", help="Validator subagent (default: tesla-code-auditor)")
    parser.add_argument("-o", "--output-dir", default="/home/lord-mahonheim/bifrost/tesla/.runtime/loops/", help="Directory to store run logs (default: .runtime/loops/)")
    parser.add_argument("--dry-run", action="store_true", help="Simulate a single passing iteration without running tools or modifying files")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose log printing to stdout")

    args = parser.parse_args()

    try:
        contract = LoopContract(args.contract)
    except Exception as e:
        print(f"[-] Contract loading error: {e}")
        sys.exit(1)

    db_mgr = DatabaseManager(args.db)
    
    orchestrator = LoopOrchestrator(
        contract=contract,
        db_mgr=db_mgr,
        action_agent=args.action_agent,
        validator=args.validator,
        output_dir=args.output_dir,
        verbose=args.verbose
    )

    try:
        if args.dry-run:
            status = orchestrator.run_dry_run()
        else:
            status = orchestrator.run()
        
        sys.exit(0 if status == "PASS" else 1)
    except Exception as e:
        print(f"[-] Fatal error during orchestrator execution: {e}")
        sys.exit(2)
    finally:
        db_mgr.close()


if __name__ == "__main__":
    main()
