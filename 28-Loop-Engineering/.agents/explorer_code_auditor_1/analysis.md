# Analysis Report — tesla-code-auditor Design & Recommendations

## Core Summary of Findings
This analysis report designs the architecture, custom rules, and wrapper script logic for `tesla-code-auditor` as a decoupled verification gatekeeper. The skill provides five sequential verification rungs and implements a robust local fallback static analyzer using Python's native AST module to enforce security and governance constraints on MIDGARD in a network-hermetic `CODE_ONLY` mode.

---

## 1. Context and Synthesis Plan
Based on the synthesis plan at `OUTPUTS/plan_intervention_loop_engineering_v1.0_2026-07-10.md`, the loop execution lifecycle adheres to the *Act-Verify-Learn-Repeat* model.
To prevent the write agent (`tesla-master-code`) from auto-certifying its own output, the validation process is isolated into `tesla-code-auditor`.
The target location for the skill is `.agents/skills/tesla-code-auditor/`.

The sequence is:
- **Rung 1**: Syntax style and formatting (e.g. `ruff`).
- **Rung 2**: Static analysis and security scanning (e.g. `pyright`, `semgrep` or `ast_fallback`).
- **Rung 3**: Dynamic test runner (e.g. `pytest`).
- **Rung 4**: Semantic LLM referee (e.g. `gemini-1.5-flash`).
- **Rung 5**: Operator human-in-the-loop validation (Lord Mahonheim).

---

## 2. Analysis of SemGrep and Vigilum Codex Requirements
Per `/home/lord-mahonheim/Documents/SyncThing/QWEN - Data/SemGrep.txt`, SAST tools like Semgrep are highly effective for shifting security "left" (finding bugs early in development/pre-commit). Since generative AI models tend to prioritize correctness of execution over security, they frequently introduce patterns like dynamic command execution (`eval`, `exec`), command injections (`shell=True`), hardcoded keys, and loose file permissions.
The **Vigilum Codex** requires all operations to be governed, traceable, and secure. This translates to rules preventing unauthorized codebase modification and unverified git operations.

---

## 3. Recommended Structure for `rules/tesla_custom_rules.yaml`
The Semgrep rule file should reside in `.agents/skills/tesla-code-auditor/rules/tesla_custom_rules.yaml`. The proposed YAML contains 4 Python security rules and 3 governance rules:

```yaml
rules:
  # === Python Security Rules ===
  
  - id: python-eval-usage
    pattern: eval(...)
    message: "Use of eval() is strictly forbidden due to arbitrary code execution risks."
    languages: [python]
    severity: ERROR

  - id: python-exec-usage
    pattern: exec(...)
    message: "Use of exec() is strictly forbidden due to arbitrary code execution risks."
    languages: [python]
    severity: ERROR

  - id: python-command-injection
    patterns:
      - pattern-either:
          - pattern: os.system(...)
          - pattern: os.popen(...)
          - pattern: subprocess.Popen(..., shell=True, ...)
          - pattern: subprocess.run(..., shell=True, ...)
          - pattern: subprocess.check_output(..., shell=True, ...)
    message: "Command execution with shell=True or os.system/popen is dangerous and can lead to command injection."
    languages: [python]
    severity: ERROR

  - id: python-hardcoded-secrets
    patterns:
      - pattern-either:
          - pattern: $KEY = "..."
          - pattern: $SECRET = "..."
          - pattern: $TOKEN = "..."
          - pattern: $PASSWORD = "..."
      - metavariable-regex:
          metavariable: $KEY
          regex: (?i)(api_key|secret|password|token|private_key|passwd)
    message: "Hardcoded API keys, secrets, tokens, or passwords detected."
    languages: [python]
    severity: ERROR

  - id: python-insecure-file-permissions
    patterns:
      - pattern: os.chmod($FILE, $MODE)
      - metavariable-regex:
          metavariable: $MODE
          regex: (0o777|777|0o755|755|0o666|666)
    message: "Setting overly permissive file permissions (chmod 777/755/666) is forbidden."
    languages: [python]
    severity: WARNING

  # === Governance & Vigilum Codex Rules ===

  - id: governance-unauthorized-write
    patterns:
      - pattern-either:
          - pattern: open($PATH, ...)
          - pattern: Path($PATH).write_text(...)
          - pattern: Path($PATH).write_bytes(...)
          - pattern: shutil.copy(..., $PATH)
          - pattern: shutil.move(..., $PATH)
      - metavariable-regex:
          metavariable: $PATH
          regex: "^(?!.*(\\.agents|\\.runtime|\\.temp|/tmp)).*$"
    message: "Writing or modifying files outside authorized directories (.agents/, .runtime/, .temp/, /tmp/) is prohibited."
    languages: [python]
    severity: ERROR

  - id: governance-unauthorized-git-push
    patterns:
      - pattern-either:
          - pattern: subprocess.run(["git", "push", ...], ...)
          - pattern: subprocess.Popen(["git", "push", ...], ...)
          - pattern: os.system("git push ...")
    message: "Git push operations without explicit authorization flags/approvals are prohibited under local governance."
    languages: [python]
    severity: ERROR

  - id: governance-delete-logs
    patterns:
      - pattern-either:
          - pattern: os.remove($FILE)
          - pattern: os.unlink($FILE)
          - pattern: Path($FILE).unlink(...)
      - metavariable-regex:
          metavariable: $FILE
          regex: ".*\\.log$"
    message: "Direct deletion of log files (*.log) is prohibited. Log rotation and management must go through the audit logger."
    languages: [python]
    severity: ERROR
```

---

## 4. Recommended Wrapper Script `scripts/semgrep_audit.py` & AST Fallback
Because MIDGARD operates in a network-hermetic `CODE_ONLY` environment, external tools might not be easily installable. If `semgrep` is missing, the wrapper script `scripts/semgrep_audit.py` must fallback to a custom python-based AST analysis parser using Python's native `ast` library.

### AST Fallback Architecture
The fallback engine parses the source code into an AST tree and traverses nodes using an `ast.NodeVisitor`.

#### Targeted AST Nodes & Check Logic:
1. **Dynamic Execution & Command Injection**:
   - Node: `ast.Call`.
   - Action: If the func is an `ast.Name` with `id` in `('eval', 'exec', 'compile')`, trigger violation.
   - Action: If the func matches `os.system` or `os.popen`, trigger violation.
   - Action: If the func matches `subprocess` module functions (`run`, `Popen`, `call`, `check_output`), iterate over `node.keywords`. If a keyword has `arg='shell'` and value is `ast.Constant` with a truthy value (like `True`), trigger violation.

2. **Hardcoded Secrets**:
   - Node: `ast.Assign`.
   - Action: Check targets. If target variable is an `ast.Name` whose `id` matches key patterns (`api_key`, `secret`, `password`, `token`, `private_key`, `passwd`, case-insensitive) AND the value is an `ast.Constant` with a string value, trigger violation.

3. **Insecure Permissions**:
   - Node: `ast.Call`.
   - Action: Check if the function is `os.chmod`. Inspect arguments. If the mode argument is an `ast.Constant` integer matching patterns (such as octal permissions checking `0o777`, `0o755`, `0o666`), trigger violation.

4. **Unauthorized Directory Writes**:
   - Node: `ast.Call`.
   - Action: Detect file creation and write attempts. If func matches `open`, `Path.write_text`, `Path.write_bytes`, `shutil.copy`, `shutil.move`.
   - Action: Inspect the path argument (the first positional argument). If it is a string constant, check if its resolved path resides outside `.agents/`, `.runtime/`, `.temp/`, and `/tmp/`. If yes, trigger violation.

5. **Unauthorized Git Push**:
   - Node: `ast.Call` and `ast.List` / `ast.Constant`.
   - Action: If a call targets `subprocess` or `os.system`, inspect the command argument.
   - Action: If it is a string literal containing `"git push"` or an list of constants containing both `"git"` and `"push"`, trigger violation.

6. **Log Deletion**:
   - Node: `ast.Call`.
   - Action: Check if the function matches `os.remove`, `os.unlink`, or `Path.unlink`.
   - Action: If the argument points to a file path ending in `.log`, trigger violation.

---

## 5. Loop Integration and Verdict Propagation
The wrapper script outputs a standard JSON structure on stdout or writes to a file:
```json
{
  "verdict": "PASS",
  "violations": [],
  "learning_deltas": []
}
```
If violations are found, `verdict` is set to `DELAY` (if progressing/correctable) or `BLOCK` (if stagnating, repeating same hash, or failing a crucial governance policy).
The violations list includes:
- `rule_id`: Identifier of the rule violated.
- `file`: Path to the audited file.
- `line`: Line number of the violation.
- `message`: Warning message.

This JSON is consumed directly by the `tesla-loop-orchestrator` to determine state transitions.
