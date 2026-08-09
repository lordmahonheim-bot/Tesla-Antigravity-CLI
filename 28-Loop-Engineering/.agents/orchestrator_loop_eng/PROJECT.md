# Project: Tesla/Antigravity Loop Engineering

## Architecture
This project implements the loop engineering framework in the Tesla/Antigravity ecosystem on Midgard.
Components:
1. `tesla-loop-orchestrator` (Skill): A coordination component executing the Act/Verify/Learn/Repeat cycle with transitions PASS/DELAY/BLOCK.
2. `tesla-code-auditor` (Agent/Skill Evaluator): An evaluation component executing a multi-validator chain (SemGrep, Pyright, Smoke Tests, Policy Engine) to provide validation verdicts.

Data Flow:
- `tesla-loop-orchestrator` parses a Loop Contract (YAML).
- It runs the Act phase, then calls `tesla-code-auditor` in the Verify phase.
- `tesla-code-auditor` runs validation tools, compiles findings, and returns a verdict (PASS/DELAY/BLOCK) and a report.
- `tesla-loop-orchestrator` performs transitions, logging, and potentially repeats the cycle or blocks/escalates.

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | Phase -1: Capability Discovery | Automatically inventory skills, MCP, system tools, and custom rules into `capability_inventory.md` | None | DONE |
| 2 | Phase 0: Multi-Persona Audit | 4 independent audit reports and 1 consolidated synthesis plan | M1 | DONE |
| 3 | R2 & R3: `tesla-loop-orchestrator` | Create `SKILL.md`, Python CLI orchestrator, Loop Contract schema, templates, logs | M2 | DONE |
| 4 | R4: `tesla-code-auditor` | Create `SKILL.md`, SemGrep rules & wrappers, Pyright wrapper, Smoke runner, Policy engine, master auditor script | M2 | DONE |
| 5 | R5: Integration & Verification | Update global `AGENTS.md`, SGC `INDEX.md`, `PROJECT_STATE.md`, open items. End-to-end verification. | M3, M4 | DONE |

## Interface Contracts
### `tesla-loop-orchestrator` ↔ `tesla-code-auditor`
- Interface: CLI / Python API.
- Input: Path to target codebase/file, audit context / rules.
- Output: Verdict (PASS/DELAY/BLOCK) and detailed report (Markdown).

## Code Layout
- `.agents/skills/tesla-loop-orchestrator/`
  - `SKILL.md` (manual, roles, transitions)
  - `scripts/tesla_loop_orchestrator.py` (CLI, runner)
  - `templates/`
    - `loop_code_generation.yaml` (template)
    - `loop_doc_writing.yaml` (template)
- `.agents/skills/tesla-code-auditor/`
  - `SKILL.md` (validation protocol)
  - `scripts/`
    - `code_auditor.py` (orchestrator)
    - `semgrep_audit.py` (SemGrep wrapper)
    - `pyright_audit.py` (Pyright wrapper)
    - `smoke_test_runner.py` (Smoke runner)
    - `policy_engine.py` (Policy engine)
  - `rules/`
    - `tesla_custom_rules.yaml` (SemGrep rules)
