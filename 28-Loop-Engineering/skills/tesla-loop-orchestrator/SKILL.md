---
name: tesla-loop-orchestrator
description: >
  Controls the execution lifecycle, checks budgets, pilots the state machine,
  evaluates loop termination, logs iterations, and retrieves learning deltas.
version: 1.0
status: production
owner: Tesla
---

# TESLA LOOP ORCHESTRATOR

## 1. Identity & Core Mission
`tesla-loop-orchestrator` is the **Supervisor** component in the decoupled Loop Engineering framework. Its mission is to drive the *Act-Verify-Learn-Repeat* cycle in an autonomous, safe, and resource-bounded manner.

Its fundamental operating mandate is: **Manage loop execution states, respect financial and token budgets, enforce rollback/transaction boundaries, and avoid stagnation/regression.**

### Separation of Responsibilities
- **Supervisor (`tesla-loop-orchestrator`)**: Controls state machine transitions, evaluates constraints, executes rollback procedures, logs iterations to the database, and stores Markdown/JSON traces.
- **Actuator (`tesla-master-code`)**: Performs the codebase edits (`ACT` phase) based on goals and learning deltas.
- **Gatekeeper (`tesla-code-auditor`)**: Evaluates modified code (`VERIFY` phase) and provides JSON reports detailing rungs, error types, line locations, and learning deltas.
- **Validator (Lord Mahonheim)**: Operator who can inspect execution logs, review state machine verdicts, and perform final integration verification.

---

## 2. Logic Engine & State Machine

The loop execution state machine runs deterministically across four states:

- **`INIT`**: Ingests and validates the Loop Contract. Checks starting code workspace state.
- **`RUNNING`**: Iterates through the ACT-VERIFY-LEARN-REPEAT stages.
- **`PASS`**: Successful termination. All verification levels (Rung 1-4) succeeded. Backup files are cleaned up.
- **`DELAY`**: Temporary iteration failure but progress is being made (i.e. error list is different and there is no regression). The loop repeats with updated prompt learning deltas.
- **`BLOCK`**: Critical termination state. Failure to resolve the issue due to:
  - Budget/Limits exceeded (iteration count, token limit, financial limit).
  - Cognitive Stagnation (error hash matches previous iteration).
  - Regression (increased error count, or failure of a previously passing rung).
  When transitioning to `BLOCK`, all file modifications are rolled back to the initial state.

---

## 3. Loop Contract YAML Schema

A Loop Contract governs the execution. It must validate against the following JSON schema representation:

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
  rollback_policy:
    type: object
    properties:
      strategy: {type: string, enum: [git, shutil], default: git}
      auto_rollback: {type: boolean, default: true}
    required: [strategy]
required: [meta, execution_limits, target, goal, verify, rollback_policy]
```

---

## 4. Rollback & Workspace Preservation

To maintain workspace stability, the orchestrator implements transactional boundaries for file changes:

### 4.1 Git-Based Rollback
If `rollback_policy.strategy` is `git`:
1. **Pre-Check**: Ensure the Git tree is clean. If dirty, backup dirty changes first or abort.
2. **Snapshot**: Capture the current commit hash: `git rev-parse HEAD`.
3. **Execution**: Create a temporary branch `temp-loop-<execution_id>`.
4. **On PASS**: Merge the temporary branch back and delete it.
5. **On BLOCK**: Discard changes by doing `git reset --hard <start_hash>`, return to original branch, and delete the temporary branch.

### 4.2 Shutil-Based Rollback
If `rollback_policy.strategy` is `shutil`:
1. **Pre-Check**: Create a directory at `.runtime/backups/<execution_id>/`.
2. **Snapshot**: Copy all contract-specified target files into the backup directory using `shutil.copy2()`.
3. **On PASS**: Delete the backup directory `.runtime/backups/<execution_id>/`.
4. **On BLOCK**: Overwrite target files by copying them back from `.runtime/backups/<execution_id>/`.

---

## 5. Uninstall & Purge Procedure

If `tesla-loop-orchestrator` must be uninstalled, execute the following actions:

1. **Database Schema Cleanup**:
   Run SQLite drop scripts:
   ```sql
   PRAGMA foreign_keys = OFF;
   DROP TABLE IF EXISTS loop_iterations;
   DROP TABLE IF EXISTS loop_executions;
   DROP INDEX IF EXISTS idx_loop_executions_status;
   DROP INDEX IF EXISTS idx_loop_iterations_exec;
   VACUUM;
   ```
2. **Log & Backup Purge**:
   Delete backup and loop directories:
   ```bash
   rm -rf /home/lord-mahonheim/bifrost/tesla/.runtime/backups/
   rm -rf /home/lord-mahonheim/bifrost/tesla/.runtime/loops/
   ```
3. **Remove Skill Directory**:
   ```bash
   rm -rf /home/lord-mahonheim/bifrost/tesla/.agents/skills/tesla-loop-orchestrator/
   ```
4. **Verify Git Tree**: Run `git status` to ensure a clean workspace.
