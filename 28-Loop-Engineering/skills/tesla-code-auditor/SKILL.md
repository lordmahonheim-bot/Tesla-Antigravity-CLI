---
name: tesla-code-auditor
description: >
  Independent validation gatekeeper that performs multi-rung audits
  on generated code including style, static type checking, dynamic testing,
  and semantic referee validation.
version: 1.0
status: active
owner: Tesla
---

# TESLA CODE AUDITOR — MANUAL OF PROCEDURE

## 1. Identity & Core Mission
`tesla-code-auditor` is the validation gatekeeper in the Antigravity Loop Engineering framework. Its purpose is to evaluate codebase changes written by the actuator (`tesla-master-code`) against security, quality, correctness, and governance requirements before any commit is finalized.

Its fundamental mandate is to ensure an impartial, multi-rung ladder of verification that cannot be bypassed, producing structured verdicts.

## 2. 3-Rung Evaluation Protocol (Verdicts)
The auditor maps all validation diagnostics into three distinct evaluation states to drive the autonomous feedback loop:

1. **`PASS`**: Code has successfully passed all checks. No errors, security vulnerabilities, naming violations, or runtime exceptions. The loop orchestrator can safely commit the changes and progress.
2. **`DELAY`**: Code contains minor errors (syntax errors, local type errors, formatting issues, or naming/metadata warnings). These are considered correctable by the coding agent in the next iteration. The runner requests another `ACT` iteration with the learning deltas payload.
3. **`BLOCK`**: Code contains critical safety, security, or governance violations (such as `eval`/`exec`, command injections, hardcoded keys, unauthorized file system writes, git push bypasses, log truncations, or unresolved third-party package imports in `CODE_ONLY` mode). Execution halts immediately, requiring operator escalation or automated rollback to a clean state.

## 3. Execution Order & Pipeline Sequence
The master orchestrator executes four underlying checkers in the following sequence without failing-fast, in order to gather a complete set of diagnostic learning deltas:

1. **SemGrep Audit (`semgrep_audit.py`)**: Runs custom security and governance scans. Falls back to native AST-based python check if semgrep binary is absent.
2. **Pyright Audit (`pyright_audit.py`)**: Checks syntax, types, and import resolution. Falls back to python `compile` check.
3. **Smoke Audit (`smoke_test_runner.py`)**: Conducts import and dry-run execution checks to prevent runtime startup failures, with a 10-second timeout.
4. **Policy Engine (`policy_engine.py`)**: Checks directory boundaries, naming conventions, metadata schema, and log monotonicity.

## 4. Input/Output Interface Details

### CLI Arguments
```bash
python3 scripts/code_auditor.py [options] [targets]
  --files <file1> <file2> ...  Specific files to audit
  --diff <git-diff-spec>       Audit files modified since commit/branch
  --output-json <path>         Save consolidated JSON report
  --output-md <path>           Save consolidated Markdown report
```

### JSON Output Interface Contract
```json
{
  "verdict": "PASS | DELAY | BLOCK",
  "timestamp": "YYYY-MM-DDTHH:MM:SSZ",
  "rungs": {
    "SemGrep Audit": { ... },
    "Pyright Audit": { ... },
    "Smoke Audit": { ... },
    "Policy Audit": { ... }
  },
  "learning_deltas": [
    {
      "source": "SemGrep Audit",
      "file": "path/to/file.py",
      "line": 42,
      "severity": "ERROR | WARNING | CRITICAL",
      "code": "python-eval-usage",
      "message": "Use of eval() is strictly forbidden..."
    }
  ]
}
```

## 5. Rollback & Uninstall Procedures
If this skill needs to be uninstalled or reverted from the workspace:
1. Revert any modified configuration files using Git.
2. Delete the skill folder:
   ```bash
   rm -rf /home/lord-mahonheim/bifrost/tesla/.agents/skills/tesla-code-auditor/
   ```
3. Run `git status` to verify the repository is clean.
