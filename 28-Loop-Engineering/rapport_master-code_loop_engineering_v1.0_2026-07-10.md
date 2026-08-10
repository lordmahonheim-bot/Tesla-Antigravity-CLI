![Status](https://img.shields.io/badge/Status-MVP-blue) ![Ecosystem](https://img.shields.io/badge/Ecosystem-TESLA%20ANTIGRAVITY-purple) ![Security](https://img.shields.io/badge/Security-ID%20LOCKED-red) ![Python](https://img.shields.io/badge/Python-3.12+-blue)

# Technical Evaluation and Contract Specification Report: Loop Engineering
**Author:** Tesla Master Code (Chief Software Engineering Agent)  
**Recipient:** Lord Mahonheim  
**Issue Date:** July 10, 2026  
**Mission Status:** Mission completed and successful  
**Version:** v1.0  

---

## 1. Local Ecosystem Diagnostic (MIDGARD)

In accordance with the conclusions of the **Tesla Arcanis-360** analysis report (`rapport_arcanis_loop_engineering_v1.0_2026-07-10.md`) and the **Tesla Curator Prime** curation report (`rapport_curator_loop_engineering_v1.0_2026-07-10.md`), we have conducted a technical feasibility audit for the deployment of Loop Engineering (the iterative *Act-Verify-Learn-Repeat* cycle).

### Direct Observations and Environmental Constraints:
1. **Hermetic Network (`CODE_ONLY` Mode):** The MIDGARD station has no external network access. All software dependencies must be resolved locally or rely on existing ones.
2. **Local Absence of Semgrep in the venv:** The `semgrep` tool is not provisioned in the `.venv/bin/` virtual directory. Any direct invocation by the code auditor will fail without a workaround strategy or static offline provisioning.
3. **Absence of Relational Tables in Alexandria:** The SQLite database `alexandria_brain.db` (located in `/home/lord-mahonheim/bifrost/tesla/database/`) does not yet implement the `loop_executions` and `loop_iterations` tables required for loop state persistence.
4. **Self-Certification Bias:** `tesla-master-code` is the executor of code modifications. If the same agent evaluates its own changes, the risk of "reward hacking" is critical. The independence of `tesla-code-auditor` from `tesla-master-code` is therefore an architectural imperative.

---

## 2. Technical Feasibility Evaluation

The deployment is **technically feasible** locally, provided the following mitigation measures are respected for the identified constraints.

### Risk & Mitigation Summary Table

| Constraint / Risk | Impact | Mitigation Measure | Status |
| :--- | :--- | :--- | :--- |
| No internet access (`CODE_ONLY`) | Impossible to install libraries on the fly. | Leverage standard Python 3.12 libraries and packages already present in the `.venv` (`chromadb`, `sentence_transformers`, `google-genai`). | **Validated** |
| Semgrep missing in `.venv` | Failure of static security validation (Rung 2). | **Hybrid Strategy:** Design of a local AST validator relying on the native Python `ast` module combined with regular expressions to simulate Tesla rules, pending the offline static provisioning of the Semgrep wheel (`.whl`). | **Validated** |
| Cognitive stagnation (Doom Loop) | The coding agent loops endlessly on the same error message. | The orchestrator compares the SHA-256 hash of the previous error report with the new one. In case of stagnation (identical error messages on two consecutive iterations) $\rightarrow$ Transition to `BLOCK`. | **Specified** |
| Alexandria SQLite Concurrency | Database lock errors (`database is locked`) if multiple loops run simultaneously. | Implementation of a retry mechanism with exponential backoff in the orchestrator. | **Specified** |
| Reward Hacking (Rung 4) | The coding agent deceives the semantic judge model. | Cognitive dissociation: Mandatory configuration of distinct models for action and judgment (e.g., Gemini 1.5 Flash for the judge, Claude 3.5 Sonnet for the actuator). | **Specified** |

---

## 3. Inventory of Locally Available Python Libraries

Since all script and wrapper executions must occur without network access, we list below the local libraries on MIDGARD usable for the orchestrator and the auditor.

### 3.1 Standard (Native) Libraries

* **`sqlite3`:** Relational engine used for local loop state persistence and integration with Alexandria.
* **`json`:** Used for serializing/deserializing the audit payload and "Learning Deltas".
* **`subprocess`:** Essential for securely and isolatedly launching validation tools (`ruff`, `pyright`, `pytest`, `deno`, `wasmtime`).
* **`hashlib`:** Used to calculate file and error message signatures to detect regressions and stagnation.
* **`argparse`:** Used to structure the CLI interfaces of the orchestrator and the auditor.
* **`datetime`:** For timestamping iterations and persistence.
* **`re`:** Used to parse lint and type reports, and extract faulty lines.
* **`shutil`:** For creating security backups before modification and restoring in case of blockage (`BLOCK`).
* **`ast`:** Used as a local and hermetic alternative to structurally analyze Python files and detect anti-patterns without requiring Semgrep.
* **`typing`:** Ensures strict typing of Python code (compliant with the Ruff/Pyright doctrine).

### 3.2 Third-Party Libraries Validated in the `.venv`

* **`google.genai` / `google-genai`:** The official Google GenAI SDK for accessing local Rung 4 Gemini models (Referee Judge).
* **`chromadb` & `sentence_transformers`:** Used for local semantic search in the Alexandria database.
* **`yaml` (PyYAML):**
  * *Robustness Note (Fallback):* Should the `yaml` package experience an import failure in certain sub-environments, the orchestrator must support the native ingestion of loop contracts in **JSON** format via the standard `json` library. Furthermore, a minimalist parser for textual YAML files (which converts keys like `contract_version`, `goal`, etc., into a Python dictionary) will be integrated as a backup.

---

## 4. Relational Persistence Schema (Alexandria DDL Version 2.0)

To ensure the structural persistence of loop states from one session to the next and feed Alexandria's global memory, the relational schema of the `alexandria_brain.db` SQLite database is extended with the following version 2.0:

```sql
-- DDL Extension Schema Version 2.0
-- Integration of Loop Engineering into the Alexandria database

CREATE TABLE IF NOT EXISTS loop_executions (
    id TEXT PRIMARY KEY,
    project TEXT NOT NULL,
    contract_version TEXT NOT NULL,
    goal TEXT NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT,
    status TEXT NOT NULL CHECK(status IN ('PASS', 'DELAY', 'BLOCK', 'RUNNING')),
    total_iterations INTEGER DEFAULT 0,
    total_token_cost REAL DEFAULT 0.0,
    max_iterations INTEGER NOT NULL,
    token_budget REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS loop_iterations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    execution_id TEXT NOT NULL,
    iteration_number INTEGER NOT NULL,
    timestamp TEXT NOT NULL,
    action_taken TEXT NOT NULL,
    verdict TEXT NOT NULL CHECK(verdict IN ('PASS', 'DELAY', 'BLOCK')),
    learning_deltas TEXT, -- Serialized JSON containing the structured list of errors
    token_cost REAL DEFAULT 0.0,
    report_path TEXT,
    FOREIGN KEY (execution_id) REFERENCES loop_executions(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_loop_executions_status ON loop_executions(status);
CREATE INDEX IF NOT EXISTS idx_loop_iterations_exec ON loop_iterations(execution_id);
```

---

## 5. Interface Contracts and CLI Specifications

The exchanges between `tesla-loop-orchestrator` (Supervisor) and `tesla-code-auditor` (Independent Gatekeeper) rely on immutable and documented interface formats.

### 5.1 Orchestrator CLI Specification (`tesla-loop-orchestrator`)

The orchestrator reads the loop contract, drives the writing agent, and invokes the auditor.
* **Canonical Command:** `python3 scripts/loop_orchestrator.py [OPTIONS]`
* **Arguments:**
  * `-c, --contract <PATH>`: (Required) Path to the loop contract file (YAML or JSON).
  * `-d, --db <PATH>`: Path to the Alexandria SQLite database (default: `database/alexandria_brain.db`).
  * `-a, --action-agent <NAME>`: Name of the engineering and writing agent (default: `tesla-master-code`).
  * `-v, --validator <NAME>`: Name of the invoked validation auditor (default: `tesla-code-auditor`).
  * `-o, --output-dir <PATH>`: Output directory for iteration reports (default: `.runtime/loops/`).
  * `--verbose`: Enables detailed debugging logs.

### 5.2 Auditor CLI Specification (`tesla-code-auditor`)

The auditor analyzes the produced code without modifying it and generates a standardized JSON report.
* **Canonical Command:** `python3 scripts/code_auditor.py [OPTIONS]`
* **Arguments:**
  * `-f, --files <PATH> [<PATH> ...]`: List of source files to audit.
  * `-d, --dir <PATH>`: Entire directory to audit.
  * `--config <PATH>`: Configuration file for lint/security rules (default: `.agents/skills/tesla-code-auditor/rules/tesla_custom_rules.yaml`).
  * `-r, --rungs <RUNG> [<RUNG> ...]`: Validation rungs to execute (default: `1 2 3 4`).
  * `--test-cmd <CMD>`: Custom command for Rung 3 (default: `pytest`).
  * `--referee-model <MODEL>`: LLM model used for Rung 4 semantic validation (default: `gemini-1.5-flash`).
  * `-j, --output-json <PATH>`: (Required) Output path for the resulting JSON payload.

---

### 5.3 Loop Contract Payload (Orchestrator Input)

The contract defines the targets and budgets of the engineering task.
* **YAML Format (`loop_contract.yaml`):**
```yaml
contract_version: "1.0"
project: "tesla_cache_optimization"
goal: |
  Optimize the cache invalidation function in core/cache.py.
  The code must support concurrent cleanup and pass all unit tests.
validators:
  - name: rung_1_lint
    enabled: true
  - name: rung_2_static
    enabled: true
    config:
      rules_file: ".agents/skills/tesla-code-auditor/rules/tesla_custom_rules.yaml"
  - name: rung_3_tests
    enabled: true
    config:
      command: "pytest tests/test_cache.py"
  - name: rung_4_semantic
    enabled: true
    config:
      referee_model: "gemini-1.5-flash"
limits:
  max_iterations: 5
  token_budget: 0.05  # Financial budget in dollars for semantic evaluation
  iteration_timeout_seconds: 300
```

---

### 5.4 Auditor Diagnostic Payload (Auditor Output $\rightarrow$ Orchestrator Input)

This standardized structured format allows the orchestrator to make its transition decision.
* **JSON Format (`audit_report.json`):**
```json
{
  "verdict": "DELAY",
  "rung_reached": 2,
  "summary": "Pyright compilation check failed on 1 count. Style & Format checks passed.",
  "timestamp": "2026-07-10T01:05:00Z",
  "validators": {
    "style_check": {
      "status": "SUCCESS",
      "tool_used": "ruff",
      "raw_output": "All lints cleared."
    },
    "static_analysis": {
      "status": "FAILED",
      "tool_used": "pyright",
      "raw_output": "error: Expression of type 'str' cannot be assigned to parameter 'max_size' of type 'int'"
    },
    "unit_tests": {
      "status": "SKIPPED",
      "tool_used": "pytest",
      "raw_output": ""
    },
    "semantic_validation": {
      "status": "SKIPPED",
      "tool_used": "referee_llm",
      "raw_output": ""
    }
  },
  "learning_deltas": [
    {
      "file": "core/cache.py",
      "line": 42,
      "severity": "ERROR",
      "code": "pyright_type_error",
      "message": "Type mismatch: expected int, got str in parameter 'max_size'"
    }
  ]
}
```

---

## 6. Key Function Signatures (Python API)

To guide Phase 2 development, we define the typed signatures and logical contracts of the functions within the Python modules.

### 6.1 `scripts/loop_orchestrator.py`
```python
from typing import Dict, List, Any, Optional

def load_contract(contract_path: str) -> Dict[str, Any]:
    """
    Loads the loop contract (YAML or JSON).
    Integrates a backup parser in case PyYAML is missing.
    Raises:
        FileNotFoundError: If the contract does not exist.
        ValueError: If the contract is malformed.
    """
    pass

def initialize_run_in_db(contract: Dict[str, Any], db_path: str) -> str:
    """
    Creates a unique record in loop_executions and generates a UUID4.
    """
    pass

def record_iteration(
    execution_id: str, 
    iteration_num: int, 
    action: str, 
    verdict: str, 
    deltas: List[Dict[str, Any]], 
    cost: float, 
    report_path: str, 
    db_path: str
) -> None:
    """
    Inserts metadata of the active iteration and its Learning Deltas (JSON).
    Handles fault tolerance with retry in case of SQLite database lock.
    """
    pass

def check_stagnation(new_deltas: List[Dict[str, Any]], prev_deltas: List[Dict[str, Any]]) -> bool:
    """
    Compares the content of the current iteration's learning deltas with the previous one.
    Returns True if the error messages and locations are rigorously identical.
    """
    pass

def generate_learning_prompt(goal: str, deltas: List[Dict[str, Any]]) -> str:
    """
    Formats an enriched prompt message containing the initial goal as well as
    the exact indications (files, lines, errors) of the validation failures.
    """
    pass

def run_loop(contract_path: str, db_path: str) -> str:
    """
    Main loop function (Act-Verify-Learn-Repeat).
    Returns the final verdict ('PASS' or 'BLOCK').
    """
    pass
```

### 6.2 `scripts/code_auditor.py`
```python
from typing import Dict, List, Any

def run_rung_1_style(files: List[str]) -> Dict[str, Any]:
    """
    Executes 'ruff check' on the list of files.
    Returns a dictionary containing the status (SUCCESS/FAILED) and lints.
    """
    pass

def run_rung_2_static(files: List[str], rules_path: str) -> Dict[str, Any]:
    """
    Executes 'pyright' for type checking.
    Executes the local AST scanner (or Semgrep) for Tesla security rules.
    """
    pass

def run_rung_3_dynamic(test_command: str) -> Dict[str, Any]:
    """
    Runs the unit test suite in an isolated process (subprocess).
    Captures stdout/stderr outputs and the return code (exit code).
    """
    pass

def run_rung_4_semantic(
    files: List[str], 
    goal: str, 
    referee_model: str
) -> Dict[str, Any]:
    """
    Invokes the Gemini API with the google-genai client to have the code validated
    by an independent LLM Judge (anti-bypass analysis and logical adequacy).
    """
    pass

def consolidate_audit(
    results: Dict[str, Dict[str, Any]], 
    rung_reached: int
) -> Dict[str, Any]:
    """
    Takes the raw results of each executed rung and formulates the final JSON
    diagnostic payload containing the overall verdict ('PASS', 'DELAY', 'BLOCK')
    and the structured Learning Deltas.
    """
    pass
```

---

## 7. Detailed Implementation Plan (Phase 2 & 3)

The deployment will be structured around five sequential implementation phases.

### Phase 1: Alexandria DDL Update (Immediate)
* **Action:** Modify `memory/db_init.py` to include DDL Version 2.0.
* **Verification:** Run `./init_alexandria.sh` or execute `just index` to validate that the tables are operational in SQLite.

### Phase 2: Development of the Technical Guardian (`tesla-code-auditor`)
* **Action:** Write `scripts/code_auditor.py`.
* **Backup AST Component:** Development of a local static analyzer based on the native `ast` module to compensate for the absence of Semgrep. It will analyze control structures and raise alerts on empty functions or `try-except` blocks catching the generic `Exception` without processing.
* **Verification:** Run a test audit on a dummy file intentionally containing a type and style error.

### Phase 3: Development of the Supervisor (`tesla-loop-orchestrator`)
* **Action:** Write `scripts/loop_orchestrator.py` containing the logical state machine (`PASS`, `DELAY`, `BLOCK`) and the stagnation/regression checks.
* **Verification:** Loop simulation with pre-filled audit reports to verify the proper behavior of the state machine.

### Phase 4: Rung 4 - Integration of the Judge Model (Referee)
* **Action:** Configuration of semantic validation via the `google-genai` SDK, specifying the `gemini-1.5-flash` model distinct from the coding agent.
* **Verification:** Simulation of a prompt injection in the source code (e.g., adding `# bypass test validation`) to validate detection by the judge.

### Phase 5: Unit Testing and Integration Campaign
* **Action:** Write unit tests (`tests/test_loop_orchestrator.py` and `tests/test_code_auditor.py`) validating the disconnected behavior of the entire system.
* **Verification:** Successful execution of tests with `pytest`.

---

## 8. Curation and Closure

In accordance with the governance doctrine of **Tesla Curator Prime**, this technical report freezes the interface contracts and concludes the technical evaluation phase. The transition to the physical writing of the code is ready and validated.

Signed / Done by: Tesla on Antigravity CLI  
Handed back to Mahonheim  
