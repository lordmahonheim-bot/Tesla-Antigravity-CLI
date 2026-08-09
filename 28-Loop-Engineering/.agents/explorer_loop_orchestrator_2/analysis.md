# Technical Exploration & Architecture Recommendation Report: `tesla-loop-orchestrator`

**Milestone:** 3 (`tesla-loop-orchestrator`)  
**Role:** Explorer 2 (CLI Requirements & Architecture Recommendation)  
**Status:** Certified (Decision-Ready)  
**Target File:** `/home/lord-mahonheim/bifrost/tesla/.agents/explorer_loop_orchestrator_2/analysis.md`

---

## 1. Executive Summary

This report provides the detailed design specifications, code structure recommendations, and execution logic for the CLI Python script `scripts/tesla_loop_orchestrator.py` under Milestone 3. 

The orchestrator serves as the **Supervisor** in the decoupled loop engineering framework (*Act-Verify-Learn-Repeat*), managing the execution lifecycle, checking resource budgets, driving the state machine, managing rollback safety, and persisting the session history in the Alexandria DB.

To ensure safety and reliability on the hermetic **MIDGARD** environment (mode `CODE_ONLY`), this document synthesizes findings from preceding explorations and outlines a production-ready roadmap for the implementing agent.

---

## 2. CLI Python Script Requirements

The script `scripts/tesla_loop_orchestrator.py` must run as a native Python 3.12 executable script. It must not require any external internet dependencies.

### 2.1 CLI Argument Parsing
The CLI must expose the following command line options using Python's standard `argparse` library:

- **`-c, --contract <PATH>`** *(Mandatory)*: Path to the Loop Contract file (supports YAML and JSON).
- **`-d, --db <PATH>`** *(Optional)*: Path to the SQLite Alexandria database. Defaults to the centralized path: `Avalon/03-Resources/alexandria_brain.db` (retrieved from `memory.db_connector`).
- **`-a, --action-agent <NAME>`** *(Optional)*: The identifier of the engineering subagent to invoke for the `ACT` phase (default: `tesla-master-code`).
- **`-v, --validator <NAME>`** *(Optional)*: The identifier of the code auditor tool to invoke for the `VERIFY` phase (default: `tesla-code-auditor`).
- **`-o, --output-dir <PATH>`** *(Optional)*: Path where detailed session execution logs (JSON & Markdown) will be stored. Defaults to `/home/lord-mahonheim/bifrost/tesla/.runtime/loops/`.
- **`--dry-run`** *(Optional)*: Enables execution simulation. If set, the orchestrator parses the contract, verifies database connections, registers the loop as `RUNNING` in the database, mock-runs a single iteration cycle (generating dummy success or failure metrics), updates the database, and exits with a `PASS` status without executing the actuator, auditor, or rollback logic.
- **`--verbose`** *(Optional)*: Enables detailed print statements to stdout for debug monitoring.

### 2.2 Contract Ingestion Robustness & Fallback
The orchestrator must support ingestion of YAML contracts. However, because external packages like PyYAML (`yaml`) might be missing or fail to import under certain sandbox environments in `CODE_ONLY` mode, the orchestrator must implement a dual-fallback parser strategy:
1. **PyYAML Import Try-Catch**: Attempt to import `yaml`. If successful, parse the contract using `yaml.safe_load()`.
2. **Text-Parser Fallback**: If `yaml` cannot be imported, check if the contract file extension is `.json`. If so, parse using the standard `json.load()` module.
3. **Basic Custom YAML Parser**: If the file is YAML and `yaml` is missing, the script must parse the file line-by-line using a regex/string splitter to extract top-level keys like `contract_version`, `project`, `goal`, `max_iterations`, `financial_budget_usd`, `token_budget`, etc., ensuring basic operation is preserved.

---

## 3. Logic Engine & State Machine Transitions

The orchestrator operates a strict finite state machine (FSM) to supervise the loop.

```
       +------------------+
       |   State: INIT    |
       +--------+---------+
                |
                v
       +------------------+
       |  State: RUNNING  | <------------------------------------+
       +--------+---------+                                      |
                |                                                |
                | (Evaluate Iteration N)                         |
                v                                                |
     [Is Limit Exceeded?]                                        |
      /              \                                           |
    YES              NO                                          |
    /                  \                                         |
   v                    v                                        |
+-------+       [Invoke Actuator + Auditor]                      |
| BLOCK |               \                                        |
+-------+                v                                       |
                     [Verdict?]                                  |
                    /    |     \                                 |
                PASS   DELAY   BLOCK                             |
                /        |       \                               |
               v         |        v                              |
           +------+      |     +-------+                         |
           | PASS |      |     | BLOCK | (Rollback & Terminate)  |
           +------+      v     +-------+                         |
                  [Check Stagnation/Regression]                  |
                  /                           \                  |
             Stagnating                     Progress             |
                /                               \                |
               v                                 v               |
           +-------+                         Update Prompt & ----+
           | BLOCK | (Rollback)              Increment Iteration
           +-------+
```

### 3.1 State Definitions
- **`INIT`**: Session instantiated, contract validated, workspace environment assessed.
- **`RUNNING`**: Active loop execution.
- **`PASS`**: Successful termination. All verification levels (Rung 1-4) succeeded. Modifications finalized.
- **`DELAY`**: Intermediate state. Validation failed, but the errors show progress and are within constraints. Next iteration scheduled.
- **`BLOCK`**: Critical termination state. Failure to progress, budget exhaustion, or error regression. Initial code state restored.

### 3.2 Transition Rules & Safety Guards
1. **Pre-Iteration Limits Evaluation**: Prior to starting iteration $N$, the orchestrator checks cumulative metrics:
   - **Financial Budget**: If `total_cost_usd >= financial_budget_usd` OR `total_cost_usd >= 5.00` (safety cap) $\rightarrow$ transition to `BLOCK` (Reason: `BUDGET_EXCEEDED`).
   - **Token Budget**: If `total_tokens >= token_budget` $\rightarrow$ transition to `BLOCK` (Reason: `TOKEN_BUDGET_EXCEEDED`).
   - **Iteration Limit**: If $N > \text{max\_iterations}$ $\rightarrow$ transition to `BLOCK` (Reason: `MAX_ITERATIONS_EXCEEDED`).

2. **Auditor Verdict Evaluation**:
   - If `verdict == "PASS"` $\rightarrow$ transition to `PASS`.
   - If `verdict == "BLOCK"` $\rightarrow$ transition to `BLOCK` (Reason: `CRITICAL_AUDIT_VERDICT`).
   - If `verdict == "DELAY"`:
     - **Stagnation Check**: The orchestrator must compute the SHA-256 hash of the errors in `learning_deltas`:
       $$\text{Hash}_N = \text{SHA256}\left(\sum (\text{error.file} + \text{str}(\text{error.line}) + \text{error.message})\right)$$
       To ensure determinism, the error list must be sorted by `file`, `line`, and `message` before string joining and hashing.
       If $\text{Hash}_N == \text{Hash}_{N-1}$ $\rightarrow$ transition to `BLOCK` (Reason: `COGNITIVE_STAGNATION`).
     - **Regression Check**: If the audit report indicates that a Rung which previously succeeded in iteration $N-1$ is now failing, or if the number of errors has increased $\rightarrow$ transition to `BLOCK` (Reason: `REGRESSION_DETECTED`).
     - **Progressive Continuation**: If the hash is new and no regression is found, transition to `DELAY`, extract the `learning_deltas`, append them to the actuator's context prompt, increment iteration $N$, and loop back.

---

## 4. SQLite Concurrency & DB Lock Mitigation

Because multiple agent tasks may attempt concurrent writes to the Alexandria database, the orchestrator must implement robust lock mitigation patterns.

### 4.1 Connection Pragmas
When establishing a connection, the orchestrator must configure the connection behavior using:
- **Write-Ahead Logging (WAL) Mode**: Enables concurrent read operations while a write transaction is executing.
- **Foreign Keys**: Enforced to ensure relational integrity between `loop_executions` and `loop_iterations`.
- **Busy Timeout**: Increased to `10000` (10 seconds) to block and wait for locks to clear instead of crashing immediately.

### 4.2 Exponential Backoff Retry Decorator
To intercept temporary `sqlite3.OperationalError` (specifically due to database locks), all SQLite write operations must be wrapped in an exponential backoff decorator with randomized jitter:

```python
import time
import random
import sqlite3
from functools import wraps

def with_sqlite_retry(max_retries: int = 5, base_delay: float = 0.1, max_jitter: float = 0.05):
    """
    Decorator that catches sqlite3.OperationalError ('database is locked')
    and retries the operation with exponential backoff and random jitter.
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
```

### 4.3 Transaction Integrity
To prevent database corruption:
- Ensure write operations use `BEGIN IMMEDIATE;` or `BEGIN EXCLUSIVE;` transaction levels.
- Always use Python's connection context managers (`with conn:`) to automate `COMMIT` on success and `ROLLBACK` on exceptions.
- Never construct raw query strings using variable interpolation. Use parameterized queries (`?` syntax).

---

## 5. Rollback & Workspace Preservation

To safeguard the codebase against partial or broken modifications, the orchestrator must guarantee transactional safety on the local files modified by the actuator.

### 5.1 Git-Based Rollback (Preferred)
If the project directory is a Git repository, the orchestrator should:
1. Check if the working tree is clean. If dirty, backup the modified files before proceeding.
2. Record the starting commit SHA: `git rev-parse HEAD`.
3. Create a temporary branch for isolation: `git checkout -b temp-loop-<execution_id>`.
4. If the loop terminates with `PASS`, merge the temporary branch into the original branch and delete the temp branch.
5. If the loop terminates with `BLOCK`, discard modifications by performing a hard reset: `git reset --hard <start_commit>` and return to the original branch.

### 5.2 Shutil-Based Rollback (Fallback)
If Git is not available, the orchestrator must perform folder-based backups:
1. Prior to any actuator modification, create a backup directory at `.runtime/backups/<execution_id>/`.
2. Copy all target files specified in the contract to this backup folder using `shutil.copy2()` (which preserves metadata).
3. If the loop ends in `PASS`, clean up the backup folder.
4. If the loop ends in `BLOCK`, copy the original files back from `.runtime/backups/<execution_id>/` to their target paths, overwriting the actuator's corrupted code.

---

## 6. Recommended Code Structure

We recommend organizing `scripts/tesla_loop_orchestrator.py` into clear, decoupled classes and functions to optimize readability and LSP compliance.

### 6.1 Database Schema (Alexandria DDL v2.0)
The orchestrator must persist data according to the revised DDL schema v2.0:

```sql
CREATE TABLE IF NOT EXISTS loop_executions (
    id TEXT PRIMARY KEY,
    project TEXT NOT NULL,
    contract_version TEXT NOT NULL,
    goal TEXT NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT,
    status TEXT NOT NULL CHECK(status IN ('PASS', 'DELAY', 'BLOCK', 'RUNNING')),
    total_iterations INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    total_cost_usd REAL DEFAULT 0.0,
    max_iterations INTEGER NOT NULL,
    token_budget INTEGER NOT NULL,
    financial_budget_usd REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS loop_iterations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    execution_id TEXT NOT NULL,
    iteration_number INTEGER NOT NULL,
    timestamp TEXT NOT NULL,
    action_taken TEXT NOT NULL,
    verdict TEXT NOT NULL CHECK(verdict IN ('PASS', 'DELAY', 'BLOCK')),
    learning_deltas TEXT, -- JSON array of serialized deltas
    tokens_used INTEGER DEFAULT 0,
    cost_usd REAL DEFAULT 0.0,
    report_path TEXT,
    FOREIGN KEY (execution_id) REFERENCES loop_executions(id) ON DELETE CASCADE
);
```

### 6.2 Key Classes and Signature Designs

```python
import os
import json
import hashlib
import sqlite3
import argparse
from typing import Dict, List, Any, Optional

class LoopContract:
    def __init__(self, data: Dict[str, Any]):
        self.name: str = data["meta"]["name"]
        self.project: str = data["meta"]["project"]
        self.version: str = data["meta"]["version"]
        self.goal: str = data["goal"]
        self.target_files: List[str] = data["target"]["files"]
        self.max_iterations: int = data["execution_limits"]["max_iterations"]
        self.financial_budget_usd: float = data["execution_limits"]["financial_budget_usd"]
        self.token_budget: int = data["execution_limits"]["token_budget"]
        self.timeout_seconds: int = data["execution_limits"]["timeout_seconds"]
        self.rollback_strategy: str = data["rollback_policy"]["strategy"]

class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path

    @with_sqlite_retry()
    def init_execution(self, execution_id: str, contract: LoopContract) -> None:
        """Inserts a new run record in loop_executions with RUNNING status."""
        pass

    @with_sqlite_retry()
    def log_iteration(self, execution_id: str, iteration: int, action: str, 
                      verdict: str, deltas: List[Dict[str, Any]], 
                      tokens: int, cost: float, report_path: str) -> None:
        """Inserts an iteration run details under loop_iterations."""
        pass

    @with_sqlite_retry()
    def finalize_execution(self, execution_id: str, final_status: str, 
                           total_iterations: int, total_tokens: int, total_cost: float) -> None:
        """Updates the loop_executions record with final status and metrics."""
        pass

class LoopOrchestrator:
    def __init__(self, contract: LoopContract, db_mgr: DatabaseManager, output_dir: str):
        self.contract = contract
        self.db_mgr = db_mgr
        self.output_dir = output_dir
        self.execution_id = self.generate_execution_id()
        self.backup_paths: Dict[str, str] = {}

    def generate_execution_id(self) -> str:
        """Generates a unique execution UUID."""
        pass

    def perform_backup(self) -> None:
        """Backs up the project target files to backup folder based on strategy."""
        pass

    def perform_rollback(self) -> None:
        """Restores files to original status if loop fails."""
        pass

    def cleanup_backups(self) -> None:
        """Removes temporary files on pass."""
        pass

    def compute_error_hash(self, errors: List[Dict[str, Any]]) -> str:
        """Computes deterministic SHA-256 hash of sorted errors."""
        sorted_errors = sorted(errors, key=lambda e: (e.get("file", ""), e.get("line", 0), e.get("message", "")))
        serialized = json.dumps(sorted_errors, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def run(self, dry_run: bool = False) -> str:
        """
        Executes the Act-Verify-Learn-Repeat loop.
        Returns final status: PASS or BLOCK.
        """
        pass
```

---

## 7. Logging and Traceability

To maintain auditability, the orchestrator must produce both structured logs (for software agents) and readable logs (for Lord Mahonheim).

### 7.1 JSON Session Log (`<output_dir>/<execution_id>_session.json`)
At the end of the run, the orchestrator writes a structured session log:
```json
{
  "execution_id": "4b68e918-a6d1-4bfe-be24-c13f6f966bd4",
  "project": "tesla_cache_optimization",
  "contract_name": "fix-cache-lock-race",
  "goal": "Refactor locking to support double-checked locks...",
  "status": "PASS",
  "total_iterations": 2,
  "metrics": {
    "total_tokens_consumed": 45320,
    "total_cost_usd": 0.006798
  },
  "iterations": [
    {
      "number": 1,
      "verdict": "DELAY",
      "action_taken": "Modified locking primitives in core/cache.py",
      "tokens_consumed": 22660,
      "cost_usd": 0.003399,
      "error_hash": "a4d3f2...a7",
      "errors": [
        {
          "file": "core/cache.py",
          "line": 42,
          "message": "Type mismatch: expected int, got str"
        }
      ]
    },
    {
      "number": 2,
      "verdict": "PASS",
      "action_taken": "Corrected variable types to integers in core/cache.py",
      "tokens_consumed": 22660,
      "cost_usd": 0.003399,
      "error_hash": "e3b0c4...27",
      "errors": []
    }
  ]
}
```

### 7.2 Markdown Execution Report (`<output_dir>/<execution_id>_report.md`)
A human-friendly report structured with:
- **Title**: `LOOP EXECUTION REPORT - [EXECUTION_ID]`
- **Metadata**: Status, Contract, Total iterations, Costs, Time.
- **Goal Statement**: Target objective.
- **Iteration History**: Table representing iterations, verdicts, and actions taken.
- **Final Verdict & Verification Proof**: Diagnostic results of Rungs 1-4.
