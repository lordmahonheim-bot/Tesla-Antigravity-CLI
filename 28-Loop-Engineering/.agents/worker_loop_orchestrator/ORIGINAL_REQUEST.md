## 2026-07-10T00:37:20Z
You are a worker agent assigned to implement Milestone 3 (`tesla-loop-orchestrator`) for the Tesla/Antigravity Loop Engineering project.
Your working directory is: `/home/lord-mahonheim/bifrost/tesla/.agents/worker_loop_orchestrator/`

Perform the following tasks:
1. Initialize your `progress.md` at `/home/lord-mahonheim/bifrost/tesla/.agents/worker_loop_orchestrator/progress.md` and keep it updated.
2. Read the three explorer reports:
   - `/home/lord-mahonheim/bifrost/tesla/.agents/explorer_loop_orchestrator_1/analysis.md`
   - `/home/lord-mahonheim/bifrost/tesla/.agents/explorer_loop_orchestrator_2/analysis.md`
   - `/home/lord-mahonheim/bifrost/tesla/.agents/explorer_loop_orchestrator_3/analysis.md`
3. Implement the `tesla-loop-orchestrator` skill under `/home/lord-mahonheim/bifrost/tesla/.agents/skills/tesla-loop-orchestrator/`:
   - `SKILL.md`: Manual of procedure, roles, state machine, transitions, YAML contract schema, rollback/uninstall procedures.
   - `scripts/tesla_loop_orchestrator.py`: Python CLI implementation that parses YAML contracts, executes Act/Verify/Learn/Repeat, writes JSON/Markdown logs, handles SQLite concurrent write retry backoff (WAL mode/retry decorator), and implements error hashing for anti-stagnation detection.
   - `templates/loop_code_generation.yaml` and `templates/loop_doc_writing.yaml`: Templates conforming to the schema.
4. Verify the database updates (tables `loop_executions` and `loop_iterations` in Alexandria DB) and ensure migrations are applied safely.
5. Verify the orchestrator:
   - Run `python3 scripts/tesla_loop_orchestrator.py --help` and verify output.
   - Run a test run (dry-run or real test) of the orchestrator to verify it processes a contract and writes structured logs.
6. Write a handoff report at `/home/lord-mahonheim/bifrost/tesla/.agents/worker_loop_orchestrator/handoff.md` and message the parent with the results.

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A Forensic Auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Strictly adhere to the Tesla/Antigravity governance:
- Use only standard Python 3.12 libraries and packages in `.venv/` (no external network access).
- Check your code using Pyright or system tools before completion.
- Keep progress.md updated.
