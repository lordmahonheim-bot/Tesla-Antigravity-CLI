# Analysis Report — Pyright & Smoke Test Runner Design for tesla-code-auditor

## Executive Summary
This analysis establishes the technical requirements, parsing logic, and architectural designs for two core components of the `tesla-code-auditor` validation chain (Rungs 2 and 3): the **Pyright Wrapper** (`scripts/pyright_audit.py`) and the **Smoke Test Runner** (`scripts/smoke_test_runner.py`). Under strict `CODE_ONLY` network isolation constraints, this design maps parsing outcomes directly to state transitions (`PASS`, `DELAY`, `BLOCK`) to optimize iteration efficiency and prevent infinite loops.

---

## 1. Pyright Wrapper Design (`scripts/pyright_audit.py`)

The Pyright wrapper is responsible for Rung 2 static type validation. It verifies that code written by `tesla-master-code` compiles, has correct types, and resolves imports without syntax regressions.

### 1.1 CLI Interface & Execution Logic
The wrapper script must execute Pyright in a non-blocking subprocess, passing files/directories to scan and requesting JSON-formatted diagnostics.

* **Binary Location**: `/home/lord-mahonheim/bifrost/tesla/.venv/bin/pyright` (Verified version: `1.1.411`).
* **Subprocess Command**:
  ```bash
  /home/lord-mahonheim/bifrost/tesla/.venv/bin/pyright --outputjson [TARGET_PATHS]
  ```
* **Execution Guard**: Pyright returns `0` on success and `1` on type/syntax errors. To prevent wrapper crash or uncaught `CalledProcessError`, the subprocess execution must catch exceptions and check `stdout` regardless of the exit code:
  ```python
  import subprocess
  import sys

  try:
      result = subprocess.run(
          [pyright_path, "--outputjson"] + target_paths,
          capture_output=True,
          text=True,
          check=False
      )
      stdout = result.stdout
      stderr = result.stderr
      returncode = result.returncode
  except Exception as e:
      # Critical system fallback
      stdout = ""
      stderr = str(e)
      returncode = 2
  ```

### 1.2 JSON Parsing & Normalized Schema Mapping
When `--outputjson` is passed, Pyright outputs a JSON object to `stdout`. The wrapper parses this object to extract error diagnostics and format them into the standard **Learning Deltas** payload format for the orchestrator.

#### Pyright JSON Output Structure:
```json
{
  "version": "1.1.411",
  "time": "1720569600000",
  "summary": {
    "filesAnalyzed": 3,
    "errorCount": 2,
    "warningCount": 1,
    "informationCount": 0
  },
  "generalDiagnostics": [
    {
      "file": "/home/lord-mahonheim/bifrost/tesla/core/cache.py",
      "severity": "error",
      "message": "Expression of type \"str\" cannot be assigned to parameter of type \"int\"",
      "rule": "reportGeneralTypeIssues",
      "range": {
        "start": { "line": 41, "character": 15 },
        "end": { "line": 41, "character": 18 }
      }
    }
  ]
}
```

#### Normalized Mapping to Learning Deltas:
1. **0-to-1 Indexing Correction**: Pyright lines and characters in `range.start` are **0-indexed**. The wrapper must add `1` to the line number to align with standard editor/error logging (1-indexed).
2. **Relative Pathing**: Convert absolute paths in the `file` field to paths relative to the workspace root using `os.path.relpath(diag["file"], workspace_root)`.
3. **Fields Extraction**:
   - `file`: `os.path.relpath(diag["file"], workspace_root)`
   - `line`: `diag["range"]["start"]["line"] + 1`
   - `severity`: `diag["severity"].upper()` (e.g. `'ERROR'`, `'WARNING'`)
   - `code`: `diag.get("rule", "pyright_error")`
   - `message`: `diag["message"]`

#### Standard Output Schema:
```json
{
  "verdict": "PASS | DELAY | BLOCK",
  "rung_reached": 2,
  "summary": "Type verification completed with N errors.",
  "timestamp": "2026-07-10T02:00:00Z",
  "learning_deltas": [
    {
      "file": "core/cache.py",
      "line": 42,
      "severity": "ERROR",
      "code": "reportGeneralTypeIssues",
      "message": "Expression of type \"str\" cannot be assigned to parameter of type \"int\""
    }
  ]
}
```

### 1.3 Text-based Fallback Parser
If Pyright crashes, fails to produce JSON, or stderr contains errors, a text-based parser utilizing regex extracts diagnostics from raw string outputs:
```python
# Match: /path/to/file.py:42:15 - error: Message (ruleName)
pattern = re.compile(r"^(?P<file>.+?):(?P<line>\d+):(?P<col>\d+) - (?P<severity>error|warning): (?P<message>.+?)(?: \((?P<code>\w+)\))?$")
```

### 1.4 Verdict Mapping Logic
The wrapper maps diagnostics to the state machine verdicts `PASS`, `DELAY`, or `BLOCK` using these rules:

| Condition | Verdict | Rationale |
| :--- | :--- | :--- |
| **No errors (`errorCount == 0`)** | `PASS` | All types, imports, and syntax checks succeeded. |
| **Syntax Errors** | `DELAY` | Invalid syntax code. Easily correctable by the developer agent in the next iteration. |
| **Local Type Errors** | `DELAY` | Parameter mismatches, missing local attributes, etc. Correctable by code editing. |
| **Local Import Errors** | `DELAY` | Misspelled imports of files inside the repository. Correctable by developer edit. |
| **Third-Party Import Errors** | `BLOCK` | Unresolved imports of packages not in the local `.venv`. Under `CODE_ONLY` restrictions, no external installation is possible; this requires immediate escalation to Mahonheim. |

#### Algorithm to Distinguish Local vs Third-Party Import Errors:
If `diag["rule"] == "reportMissingImports"`:
1. Extract the module name from the error message (e.g., from `"Import 'requests' could not be resolved"`, module is `requests`).
2. Check if the module is part of Python's standard library (e.g. `sys.builtin_module_names` or standard library namespaces). If yes $\rightarrow$ `DELAY` (it is a standard import issue).
3. Check if a folder or file matching the root module name exists inside the repository workspace (e.g., `import core.cache` matches `core/`). If yes $\rightarrow$ `DELAY` (it is a local module).
4. If it is neither standard nor present locally, it is a missing third-party dependency. Map the verdict immediately to `BLOCK` with the message `"Missing external dependency: {module}. Package installation is forbidden in CODE_ONLY mode."`

---

## 2. Smoke Test Runner Design (`scripts/smoke_test_runner.py`)

A smoke test executes the target file or entrypoint minimally to verify that it compiles, imports, and launches without throwing runtime exceptions (e.g., circular imports, missing variables at module scope, syntax errors not caught by linters).

### 2.1 Smoke Runner Strategies
The smoke test runner supports two validation modes depending on whether the target is an executable script or a module library.

1. **Dry-Run / Help Invocation (`--help` or `-h`)**:
   - Executes: `python3 [TARGET_PATH] --help`
   - Suitable for CLI tools, daemons, or scripts.
   - Captures whether the command runs, parses arguments, and exits with code `0`.
2. **Import Verification Check (`import_test`)**:
   - Executes: `python3 -c "import [MODULE_PATH]"`
   - Suitable for utility libraries, database wrappers, or API routes.
   - Verifies that loading the file does not crash due to circular imports or module-level exceptions.

### 2.2 Execution Sandbox & Timeout Guard
To prevent infinite loops or server blocking hangs (e.g., if the target starts a local server instead of exiting), the subprocess runner must enforce a **strict timeout**:
```python
try:
    result = subprocess.run(
        ["python3", target_path, "--help"],
        capture_output=True,
        text=True,
        timeout=10,  # 10-second ceiling
        env={"SMOKE_TEST_MODE": "1", **os.environ}
    )
except subprocess.TimeoutExpired as te:
    # Handle hang as failure
    verdict = "BLOCK"  # Or DELAY, but hangs usually indicate active loops
```

### 2.3 Python Traceback Parser
If the target crashes (non-zero exit code), the runner parses `stderr` to extract the traceback details and maps them to `learning_deltas`.

#### Traceback Extraction Logic:
A Python traceback ends with the exception type and details, preceded by the call stack:
```text
Traceback (most recent call last):
  File "scripts/smoke_target.py", line 15, in <module>
    main()
  File "scripts/smoke_target.py", line 8, in main
    res = 1 / 0
ZeroDivisionError: division by zero
```
* **Regex for Traceback Line**:
  `r'File "(?P<file>.+?)", line (?P<line>\d+), in (?P<func>.+)'`
* **Parsing Algorithm**:
  1. Split `stderr` into lines.
  2. Find the last line matching the format `[ExceptionClass]: [Message]` (e.g. `ZeroDivisionError: division by zero`, `ModuleNotFoundError: No module named 'x'`).
  3. Scan backwards to locate the last occurring `File "...", line ...` pattern. This points directly to the line of code that threw the unhandled exception.
  4. Extract `file`, `line`, exception name, and message to populate the `learning_deltas`.

### 2.4 Smoke Test Verdict Mapping
Smoke tests evaluate runtime behavior:

| Runtime Result | Verdict | Rationale |
| :--- | :--- | :--- |
| **Exit Code `0`** | `PASS` | Target imported or printed help successfully. |
| **Runtime Crash (`returncode != 0`)** | `DELAY` | ZeroDivisionError, NameError, ImportError. Correctable by code adjustments. |
| **Missing Dependency Crash** | `BLOCK` | `ModuleNotFoundError` for packages outside standard library/repo. |
| **Process Hang (Timeout)** | `BLOCK` | The target file did not exit. Indicates infinite recursion or server startup blockage. |

---

## 3. Integration with the Validation Ladder

The output of `pyright_audit.py` and `smoke_test_runner.py` is compiled by `code_auditor.py` to dictate the loop transition:

```
[Actuator Writes Code]
        │
        ▼
[ Ruff Style & Formatting ] (Rung 1)
        │ 
        ├─► FAIL ──► Verdict: DELAY (Exit early, don't run type checks)
        ▼ SUCCESS
[ Pyright Type Validation ] (Rung 2)
        │
        ├─► FAIL ──► Verdict: DELAY / BLOCK (Exit early, don't run tests)
        ▼ SUCCESS
[ Smoke Test Execution ] (Rung 3a)
        │
        ├─► FAIL ──► Verdict: DELAY / BLOCK (Exit early, don't run unit tests)
        ▼ SUCCESS
[ pytest Unit Tests ] (Rung 3b)
        │
        ├─► FAIL ──► Verdict: DELAY (Exit early)
        ▼ SUCCESS
[ Gemini Semantic Juge ] (Rung 4)
        │
        ├─► FAIL ──► Verdict: DELAY
        ▼ SUCCESS
[ PASS / Transition to Rung 5 ]
```

This strict cascade prevents CPU waste and test contamination. The orchestrator receives the structured payloads, saves iteration context to Alexandria SQLite database, and computes errors hashes to prevent doom-loops.
