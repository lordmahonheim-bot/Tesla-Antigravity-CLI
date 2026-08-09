## 2026-07-10T01:03:15Z
You are a worker agent assigned to implement Milestone 4 (`tesla-code-auditor`) for the Tesla/Antigravity Loop Engineering project.
Your working directory is: `/home/lord-mahonheim/bifrost/tesla/.agents/worker_code_auditor/`

Perform the following tasks:
1. Initialize your `progress.md` at `/home/lord-mahonheim/bifrost/tesla/.agents/worker_code_auditor/progress.md` and keep it updated.
2. Read the three explorer reports:
   - `/home/lord-mahonheim/bifrost/tesla/.agents/explorer_code_auditor_1/analysis.md`
   - `/home/lord-mahonheim/bifrost/tesla/.agents/explorer_code_auditor_2/analysis.md`
   - `/home/lord-mahonheim/bifrost/tesla/.agents/explorer_code_auditor_3/analysis.md`
3. Implement the `tesla-code-auditor` skill under `/home/lord-mahonheim/bifrost/tesla/.agents/skills/tesla-code-auditor/`:
   - `SKILL.md`: Manual of procedure, 3-rung evaluation protocol, input/output interface details, execution order (SemGrep -> Pyright -> Smoke -> Policy), rollback/uninstall procedures.
   - `rules/tesla_custom_rules.yaml`: Valid SemGrep custom rules (covering >=3 python security rules and >=2 governance rules as specified).
   - `scripts/semgrep_audit.py`: Python wrapper script around `semgrep` tool (includes AST/regex fallback if SemGrep binary is missing on MIDGARD).
   - `scripts/pyright_audit.py`: Python wrapper script around `pyright` (or `mypy` fallback) to parse lint, syntax, and import errors.
   - `scripts/smoke_test_runner.py`: Smoke runner to execute minimal help/dry-run checks on Python files and catch runtime errors.
   - `scripts/policy_engine.py`: Python engine to enforce naming conventions, metadata YAML presence, and log integrity.
   - `scripts/code_auditor.py`: Master Python script that orchestrates the entire ladder (SemGrep -> Pyright -> Smoke -> Policy) and outputs a consolidated verdict (PASS/DELAY/BLOCK) and Markdown report.
4. Verify the implementation:
   - Run `python3 scripts/code_auditor.py --help` and verify it runs without errors.
   - Validate the SemGrep custom rules config using `semgrep --validate --config rules/tesla_custom_rules.yaml` (if semgrep tool is mockable/runnable, or check syntax).
   - Run Pyright on the scripts to verify zero errors/warnings.
   - Execute the code auditor on a test Python file containing a known vulnerability to verify it produces PASS/DELAY/BLOCK verdict correctly.
5. Write a handoff report at `/home/lord-mahonheim/bifrost/tesla/.agents/worker_code_auditor/handoff.md` and message the parent with the results.

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A Forensic Auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Strictly adhere to the Tesla/Antigravity governance:
- Use only standard Python 3.12 libraries and packages in `.venv/` (no external network access).
- Check your code using Pyright or LSP tools before completion.
- Keep progress.md updated.
