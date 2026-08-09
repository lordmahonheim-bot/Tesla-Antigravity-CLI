#!/usr/bin/env python3
"""
OPRO Test Runner (DIY) - Orchestrates the Arena tasks.
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

# Paths
BASE_DIR: Path = Path("/home/lord-mahonheim/bifrost/tesla")
MEMORY_DIR: Path = BASE_DIR / "memory"
TASKS_FILE: Path = MEMORY_DIR / "pilot_tasks_prod.json"
SCRIPTS_DIR: Path = BASE_DIR / ".agents" / "scripts"
KILL_SWITCH_SCRIPT: Path = SCRIPTS_DIR / "opro_kill_switch_monitor.sh"
WORKTREE_RUNNER: Path = SCRIPTS_DIR / "git_worktree_runner.sh"

# Add scripts dir to PYTHONPATH to import init_lancedb
sys.path.append(str(SCRIPTS_DIR))
try:
    import init_lancedb  # type: ignore
except ImportError:
    init_lancedb = None


def load_tasks(filepath: Path) -> List[Dict[str, Any]]:
    """Loads tasks from the JSON file."""
    if not filepath.exists():
        print(f"Error: Tasks file not found at {filepath}")
        sys.exit(1)
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def check_kill_switch() -> None:
    """Calls the kill-switch monitor script before each iteration."""
    if KILL_SWITCH_SCRIPT.exists():
        try:
            subprocess.run(
                [str(KILL_SWITCH_SCRIPT)],
                check=True,
                text=True,
                capture_output=True
            )
        except subprocess.CalledProcessError as e:
            print(f"Kill-Switch activated or script failed: {e.stderr}")
            sys.exit(1)
    else:
        print(f"Warning: Kill-switch monitor not found at {KILL_SWITCH_SCRIPT}")


def run_sandbox_task(task: Dict[str, Any]) -> bool:
    """Runs the task within the git worktree sandbox."""
    if not WORKTREE_RUNNER.exists():
        print(f"Warning: Sandbox runner not found at {WORKTREE_RUNNER}")
        return False

    lock_file = Path("/tmp/tesla_arena/.lancedb_done")
    lock_file.unlink(missing_ok=True)
    Path("/tmp/tesla_arena").mkdir(parents=True, exist_ok=True)

    try:
        task_id = task.get("id", task.get("task_id", "UNKNOWN"))
        initial_code = task.get("initial_code", task.get("description", ""))
        # Assuming the runner takes task ID as argument and code via stdin
        process = subprocess.Popen(
            [str(WORKTREE_RUNNER), task_id],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        
        # We need to write input to stdin, but we also want to stream stdout.
        # However, reading and writing simultaneously without deadlock is tricky.
        # Since we use communicate or just write to stdin and close it:
        if process.stdin:
            process.stdin.write(initial_code)
            process.stdin.close()

        success = True
        failed_once = False
        if process.stdout:
            for line in process.stdout:
                print(line, end="")
                if "[ARENA-FAIL]" in line:
                    success = False
                if "[ARENA-GC] Attente du verrou LanceDB" in line:
                    if not success and not failed_once:
                        store_rejected_edit(task, "Task failed in sandbox execution.")
                        failed_once = True
                    lock_file.touch()

        process.wait()
        if process.returncode != 0:
            success = False

        if not success and not failed_once:
            store_rejected_edit(task, "Task failed in sandbox execution.")
            lock_file.touch()
            
        # Ensure lock file exists to unblock trap in all scenarios (e.g. success)
        lock_file.touch()

        print(f"Task {task_id} {'succeeded' if success else 'failed'}.")
        return success
    except Exception as e:
        print(f"Task {task_id} failed with exception: {e}")
        lock_file.touch()
        return False


def store_rejected_edit(task: Dict[str, Any], error_msg: str) -> None:
    """Calls LanceDB insertion function for failed tasks."""
    task_id = task.get("id", task.get("task_id", "UNKNOWN"))
    initial_code = task.get("initial_code", task.get("description", ""))
    
    if init_lancedb and hasattr(init_lancedb, "insert_rejected_patch"):
        try:
            db = init_lancedb.init_db()
            init_lancedb.insert_rejected_patch(
                db=db,
                patch_hash=task_id,
                patch_content=initial_code,
                fitness_score=-10.0,
                rejection_reason=error_msg
            )
            print(f"Stored rejected edit for {task_id} in LanceDB.")
        except Exception as e:
            print(f"Failed to store rejected edit: {e}")
    else:
        print(f"Warning: init_lancedb module or insertion function not available. Could not store failure for {task_id}.")


def main() -> None:
    print("Starting OPRO Test Runner (DIY)...")
    tasks = load_tasks(TASKS_FILE)
    print(f"Loaded {len(tasks)} tasks.")

    for task in tasks:
        task_id = task.get("id", task.get("task_id", "UNKNOWN"))
        print(f"\n--- Processing Task: {task_id} ---")
        check_kill_switch()
        
        run_sandbox_task(task)

    print("\nOPRO Test Runner completed.")


if __name__ == "__main__":
    main()
