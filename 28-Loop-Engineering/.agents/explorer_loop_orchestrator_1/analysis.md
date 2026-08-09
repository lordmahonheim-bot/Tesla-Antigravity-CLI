# Technical Exploration & Implementation Strategy Report: `tesla-loop-orchestrator`

**Milestone:** 3 (`tesla-loop-orchestrator`)  
**Prepared by:** Explorer 1  
**Status:** Under Review  
**Target File:** `/home/lord-mahonheim/bifrost/tesla/.agents/explorer_loop_orchestrator_1/analysis.md`

---

## Executive Summary
This report outlines the technical implementation strategy for `tesla-loop-orchestrator` (Milestone 3). It details the core architectural roles, the logic state machine (including anti-stagnation and regression checks), the Loop Contract YAML schema, rollback mechanisms, and a step-by-step uninstall procedure.

---

## 1. Architectural Roles & Decoupled Interactions

The loop engineering framework operates under a strict separation of concerns to eliminate cognitive bias (reward hacking) and guarantee sandbox safety on **MIDGARD**. The architecture partitions responsibilities into four distinct roles:

| Role | Component | Cognitive Mandate | Material Action |
| :--- | :--- | :--- | :--- |
| **Supervisor** | `tesla-loop-orchestrator` | Controls the execution lifecycle, checks budgets, pilots the state machine, evaluates loop termination, logs iterations, and retrieves learning deltas. | Reads loop contracts, updates database (`alexandria_brain.db`), controls the sequence of steps, manages file backups, and handles rollbacks. |
| **Actuator** | `tesla-master-code` (or local equivalent) | Interprets instructions and applies modifications to the target codebase. | Writes, edits, or deletes source code files. Does NOT verify its own output. |
| **Gatekeeper** | `tesla-code-auditor` | Evaluates the modified code against technical validation levels (Rungs 1 to 4) and outputs structured verdicts. | Runs Ruff, Pyright, Pytest, and Gemini-1.5-Flash. Outputs a standardized JSON report. |
| **Validator** | Lord Mahonheim (Operator) | Performs high-level human review (Rung 5). | Intervenes for final validation or to manually resolve blocked loops. |

### Decoupled Communication Protocol
1. **Contract Ingestion**: The Orchestrator ingests the Loop Contract (`loop_contract.yaml`).
2. **Phase ACT**: The Orchestrator constructs a prompt containing the **Goal** and any **Learning Deltas** (previous errors) and invokes the Actuator. The Actuator modifies files on disk.
3. **Phase VERIFY**: The Orchestrator invokes the Gatekeeper CLI, passing target file paths and context rules. The Gatekeeper performs sequential validation and returns a JSON payload:
   ```json
   {
     "verdict": "PASS | DELAY | BLOCK",
     "failed_rung": 1 | 2 | 3 | 4,
     "errors": [
       {"file": "core/cache.py", "line": 42, "message": "Undefined variable 'x'"}
     ],
     "learning_deltas": "String representing detailed logical advice for the developer."
   }
   ```
4. **Phase LEARN & REPEAT**: The Orchestrator processes the JSON, updates Alexandria tables, and determines state transitions.

---

## 2. Logic Engine & State Machine Transitions

The Orchestrator maintains the execution state within a state machine, ensuring deterministic progress, strict financial bounds, and defense against infinite loops.

```
       [Start]
          │
          ▼
     (Initialize) ──► status: RUNNING
          │
          ├─────────────────────────┐
          ▼                         ▼
   [Verify Rungs 1-4]        [Exceed Budgets / Limits]
          │                         │
          ├──────────────┐          ▼
          │ (All PASS)   │   status: BLOCK (Termination)
          ▼              ▼
    status: PASS   (Any Rung FAIL)
   (Termination)         │
                         ▼
                   [Check SHA-256 Stagnation & Regression]
                         │
                         ├─────────────────────────┐
                         ▼ (New Errors)            ▼ (Stagnation/Regression)
                   status: DELAY             status: BLOCK (Rollback & Terminate)
                         │
                         ▼
                   (Loop Iteration N+1)
```

### State Definition
- **`RUNNING`**: Active loop processing. The execution is in progress and limits are within budget.
- **`PASS`**: Successful termination. All verification Rungs (1 to 4) have succeeded. The modifications are committed.
- **`DELAY`**: Iteration failure but progress is being made. Triggers the next `ACT` iteration with the accumulated `learning_deltas`.
- **`BLOCK`**: Critical termination. Stagnation, regression, or budget exhaustion has occurred. Code modifications are rolled back.

### State Transition Rules
1. **Budget Check**: Before initiating iteration $N$:
   - If cumulative token cost $\ge \text{token\_budget}$ OR cumulative execution cost $\ge \$5.00$ $\rightarrow$ transition to `BLOCK` (Reason: `BUDGET_EXCEEDED`).
   - If $N > \text{max\_iterations}$ $\rightarrow$ transition to `BLOCK` (Reason: `MAX_ITERATIONS_EXCEEDED`).
2. **Rung Evaluation**: After invoking the Gatekeeper:
   - If Gatekeeper returns `PASS` $\rightarrow$ transition to `PASS`.
   - If Gatekeeper returns `DELAY`:
     - **Compute Error Hash**:
       $$\text{Hash}_N = \text{SHA256}\left(\sum (\text{error.file} + \text{str}(\text{error.line}) + \text{error.message})\right)$$
     - **Stagnation Check**: If $\text{Hash}_N == \text{Hash}_{N-1}$ $\rightarrow$ transition to `BLOCK` (Reason: `COGNITIVE_STAGNATION`).
     - **Regression Check**: If the number of failed Rungs increases, or if the number of errors increases, or if a Rung that passed in iteration $N-1$ now fails in $N$ $\rightarrow$ transition to `BLOCK` (Reason: `REGRESSION_DETECTED`).
     - **Progress Check**: If the error hash is different and no regression is found $\rightarrow$ transition to `DELAY`, extract `learning_deltas`, increment iteration count, and loop back to the `ACT` phase.

---

## 3. Loop Contract YAML Schema Specification

The Loop Contract governs execution parameters. It must be written in YAML and validate against a strict structure.

### Formal YAML Schema Definition
```yaml
$schema: "http://json-schema.org/draft-07/schema#"
type: object
properties:
  meta:
    type: object
    properties:
      name: {type: string}
      version: {type: string}
      project: {type: string}
      description: {type: string}
    required: [name, version, project]
  execution_limits:
    type: object
    properties:
      max_iterations: {type: integer, minimum: 1, maximum: 10, default: 5}
      financial_budget_usd: {type: number, minimum: 0.1, maximum: 5.0, default: 5.0}
      token_budget: {type: integer, minimum: 1000, default: 100000}
      timeout_seconds: {type: integer, minimum: 10, default: 300}
    required: [max_iterations, financial_budget_usd]
  target:
    type: object
    properties:
      files:
        type: array
        items: {type: string}
      directory: {type: string}
    required: [files]
  goal:
    type: string
  verify:
    type: object
    properties:
      rungs:
        type: array
        items: {type: string, enum: [style, types, tests, referee]}
      strict: {type: boolean, default: true}
      custom_rules_path: {type: string}
    required: [rungs]
  referee_config:
    type: object
    properties:
      model: {type: string, default: "gemini-1.5-flash"}
      temperature: {type: number, minimum: 0.0, maximum: 1.0, default: 0.0}
      prompt_override: {type: string}
  rollback_policy:
    type: object
    properties:
      strategy: {type: string, enum: [git, shutil], default: git}
      auto_rollback: {type: boolean, default: true}
    required: [strategy]
required: [meta, execution_limits, target, goal, verify, rollback_policy]
```

### Production-Grade Example (`loop_code_generation.yaml`)
```yaml
meta:
  name: "fix-cache-lock-race"
  version: "1.0.0"
  project: "tesla-core"
  description: "Fix potential deadlocks in core cache implementation during parallel writes"

execution_limits:
  max_iterations: 5
  financial_budget_usd: 3.50
  token_budget: 80000
  timeout_seconds: 180

target:
  files:
    - "core/cache.py"
    - "tests/test_cache.py"
  directory: "/home/lord-mahonheim/bifrost/tesla"

goal: >
  Refactor the locking mechanism in core/cache.py to use double-checked locking with a timeout.
  Ensure that when a thread fails to acquire the write lock within 2.0 seconds, it raises a
  CacheLockTimeout exception instead of blocking indefinitely. Clean up all acquired locks in 
  a try-finally block. Ensure all tests in tests/test_cache.py pass.

verify:
  rungs:
    - "style"
    - "types"
    - "tests"
    - "referee"
  strict: true
  custom_rules_path: ".agents/skills/tesla-code-auditor/rules/tesla_custom_rules.yaml"

referee_config:
  model: "gemini-1.5-flash"
  temperature: 0.0

rollback_policy:
  strategy: "git"
  auto_rollback: true
```

---

## 4. Rollback & Safe Execution Procedures

To ensure that MIDGARD remains stable and free of corrupted partial changes, the Orchestrator must wrap all file changes in a strict transactional context.

### Git-Based Rollback Procedure (Preferred)
This procedure is applied when the target codebase is inside a Git repository.
1. **Pre-Execution Check**: Ensure the git working tree is clean. If uncommitted changes exist, the Orchestrator halts execution unless forced.
2. **Snapshot Stage**:
   - The Orchestrator captures the current commit hash: `git rev-parse HEAD`.
   - It creates a temporary tracking branch for the execution: `git checkout -b temp-loop-<execution_id>`.
3. **ACT Modification**: The Actuator writes modifications to files.
4. **Transition to BLOCK**: If the loop transitions to `BLOCK`:
   - The Orchestrator performs a hard reset: `git reset --hard <original_commit>`.
   - It switches back to the original branch: `git checkout <original_branch>`.
   - It deletes the temporary branch: `git branch -D temp-loop-<execution_id>`.
5. **Transition to PASS**: If the loop transitions to `PASS`:
   - The Orchestrator merges the temporary branch into the working branch: `git checkout <original_branch> && git merge temp-loop-<execution_id>`.
   - It deletes the temporary branch.

### Shutil-Based Rollback Procedure (Fallback)
This procedure is applied when Git is not available or disabled by the contract.
1. **Pre-Execution Check**: Ensure write permissions exist on the backup folder `.runtime/backups/`.
2. **Snapshot Stage**:
   - Create a snapshot folder: `.runtime/backups/<execution_id>/`.
   - For each target file, copy the original file to the snapshot folder using `shutil.copy2()`.
3. **ACT Modification**: The Actuator modifies the files in place.
4. **Transition to BLOCK**: If the loop transitions to `BLOCK`:
   - For each target file, copy the backup file back to its original location, overwriting the modified file.
   - Delete the snapshot folder `.runtime/backups/<execution_id>/`.
5. **Transition to PASS**: If the loop transitions to `PASS`:
   - Simply delete the snapshot folder `.runtime/backups/<execution_id>/` once success is confirmed.

---

## 5. Uninstall & Purge Checklist

If the `tesla-loop-orchestrator` must be uninstalled, the process must be clean and complete, leaving no orphaned resources or write locks in the SQLite database.

```
                  [Start Uninstall]
                          │
                          ▼
            (Check SQLite WAL Connection)
                          │
                          ▼
             [Drop database tables & indexes]
                          │
                          ▼
                [Purge log directories]
                          │
                          ▼
            [Remove source scripts & templates]
                          │
                          ▼
                   [Clean Git Status]
```

### Actionable Purge Protocol:
1. **Database Schema Cleanup**:
   Execute the following SQLite command to purge the relational schema and free database space in the Alexandria database file:
   ```sql
   PRAGMA foreign_keys = OFF;
   DROP TABLE IF EXISTS loop_iterations;
   DROP TABLE IF EXISTS loop_executions;
   DROP INDEX IF EXISTS idx_loop_executions_status;
   DROP INDEX IF EXISTS idx_loop_iterations_exec;
   VACUUM;
   ```
2. **Log & Backup Purge**:
   Delete the temporary execution folders on the local file system:
   ```bash
   rm -rf /home/lord-mahonheim/bifrost/tesla/.runtime/backups/
   rm -rf /home/lord-mahonheim/bifrost/tesla/logs/loop_orchestrator/
   ```
3. **Remove Skill Directories & Scripts**:
   Delete files associated with the Loop Orchestrator skill:
   ```bash
   rm -rf /home/lord-mahonheim/bifrost/tesla/.agents/skills/tesla-loop-orchestrator/
   ```
4. **Verify Git Tree**:
   Run `git status` to ensure all generated artifacts are successfully removed and the repository state is clean.

---

## 6. Technical Implementation Sketches (Pseudo-code)

These sketches provide the concrete structures that the implementer should follow when creating the Python CLI orchestrator.

### 6.1 Database Connection with Exponential Retry and WAL Mode
```python
import sqlite3
import time
import random

def get_db_connection(db_path: str, max_retries: int = 5) -> sqlite3.Connection:
    retry_count = 0
    while True:
        try:
            conn = sqlite3.connect(db_path, timeout=5.0)
            # Enable WAL mode for parallel readers during writes
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA foreign_keys=ON;")
            return conn
        except sqlite3.OperationalError as e:
            if "locked" in str(e).lower() and retry_count < max_retries:
                retry_count += 1
                # Exponential backoff with random jitter
                sleep_time = (2 ** retry_count) * 0.1 + random.uniform(0, 0.05)
                time.sleep(sleep_time)
            else:
                raise e
```

### 6.2 Cognitive Stagnation Comparator
```python
import hashlib
import json

def calculate_error_hash(errors: list) -> str:
    """
    errors is a list of dictionaries: [{"file": str, "line": int, "message": str}]
    """
    # Sort keys to ensure deterministic serialization
    serialized_errors = json.dumps(errors, sort_keys=True).encode('utf-8')
    return hashlib.sha256(serialized_errors).hexdigest()
```

### 6.3 State Machine Controller Loop
```python
def run_orchestrator_loop(contract: dict):
    execution_id = generate_uuid()
    db_conn = get_db_connection("database/alexandria_brain.db")
    
    # Initialize execution in DB
    initialize_execution_record(db_conn, execution_id, contract)
    
    previous_hash = None
    previous_error_count = None
    
    rollback_handler = get_rollback_handler(contract['rollback_policy'])
    rollback_handler.create_snapshot()
    
    try:
        for iteration in range(1, contract['execution_limits']['max_iterations'] + 1):
            if budget_exceeded(execution_id):
                update_execution_status(db_conn, execution_id, "BLOCK")
                rollback_handler.restore_snapshot()
                return "BLOCK", "Budget Exceeded"
                
            # Step ACT: call tesla-master-code
            apply_modifications(contract['goal'], get_learning_deltas(db_conn, execution_id))
            
            # Step VERIFY: call tesla-code-auditor
            audit_result = run_code_auditor(contract['target']['files'])
            
            # Store iteration metrics
            current_hash = calculate_error_hash(audit_result.get('errors', []))
            save_iteration_record(db_conn, execution_id, iteration, audit_result, current_hash)
            
            if audit_result['verdict'] == "PASS":
                update_execution_status(db_conn, execution_id, "PASS")
                rollback_handler.discard_snapshot()
                return "PASS", "Success"
                
            elif audit_result['verdict'] == "DELAY":
                # Stagnation check
                if previous_hash and current_hash == previous_hash:
                    update_execution_status(db_conn, execution_id, "BLOCK")
                    rollback_handler.restore_snapshot()
                    return "BLOCK", "Cognitive Stagnation"
                
                # Regression check
                current_error_count = len(audit_result.get('errors', []))
                if previous_error_count and current_error_count > previous_error_count:
                    update_execution_status(db_conn, execution_id, "BLOCK")
                    rollback_handler.restore_snapshot()
                    return "BLOCK", "Regression Detected"
                
                previous_hash = current_hash
                previous_error_count = current_error_count
                
        # If loop finishes without PASS
        update_execution_status(db_conn, execution_id, "BLOCK")
        rollback_handler.restore_snapshot()
        return "BLOCK", "Max Iterations Reached"
        
    except Exception as e:
        update_execution_status(db_conn, execution_id, "BLOCK")
        rollback_handler.restore_snapshot()
        raise e
```
