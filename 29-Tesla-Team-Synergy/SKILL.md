---
name: tesla-team-synergy
display_name: Tesla Mission Orchestrator
description: Tesla's multi-agent strategic orchestration meta-skill. Outputs a DAG Mission Graph, featuring model-agnostic Capability Scoring, a Scheduler, a Budget Manager, agent contracts, a state machine, and a retry/fallback policy. Recommends model / token-economy routing. AGENTS retains execution sovereignty.
injection_type: shadow-targeted
target_subagent: self
version: 4.0
status: Stable
tags: [orchestration, multi-agent, mission-graph, capability-scoring, scheduler, token-economy, model-routing, sgc, learning-loop]
license: Vigilum Codex
author: Tesla / Mahonheim
depends_on:
  - SOUL.md >=3.0
  - ENGINE.md >=1.0
  - AGENTS.md >=4.0
  - FORCE_TOOLING.md >=1.0
  - GEMINI.md >=2.0
  - shadow-targeting-method.md >=1.0
---

![Status](https://img.shields.io/badge/Status-MVP-blue) ![Ecosystem](https://img.shields.io/badge/Ecosystem-TESLA%20ANTIGRAVITY-purple) ![Security](https://img.shields.io/badge/Security-ID%20LOCKED-red) ![Python](https://img.shields.io/badge/Python-3.12+-blue)

# tesla-team-synergy – Tesla Mission Orchestrator
## SKILL.md v4.0

> Canonical Technical Name: `tesla-team-synergy`  
> Functional Title: **Tesla Mission Orchestrator**

---

## 0. Mission

Transform an SGC project into a **coordinated multi-agent team**, outputting:

1. A canonical DAG **Mission Graph**,
2. Strictly typed **agent contracts**,
3. A vendor-agnostic **Capability Scoring**,
4. A **Scheduler** encompassing parallel, series, pipeline, fan-out, and fan-in dependencies,
5. A **model routing recommendation + Budget Manager**,
6. A **Retry / Fallback / Escalation policy**,
7. A mission **State Machine**,
8. An **Alexandria learning loop**.

> [!CAUTION]
> **ABSOLUTE RULE N°4 – AGENTS delegates; it does not reimplement.**
> The Principal Agent must systematically orchestrate and invoke elite sub-agents (via `invoke_subagent` or `define_subagent`) to execute specialized tasks defined in the delegation matrix. Under no circumstances should it assume their role or perform their work in their stead. Any deviation from this rule is a major violation of Tesla governance.
>
> **Anti-Usurpation Corollary (Slash Commands Lockout):**
> Contextual injection of a specialized skill via a user command (e.g., `/tesla-github-manager`) in no way grants the Principal Agent the right to assume this identity. The Principal Agent (AGENTS) remains a pure Orchestrator. When faced with a Skill invocation, it has the mechanical and absolute obligation to:
> 1. Refrain from executing scripts, editing files, or running git commands itself.
> 2. Immediately transfer the mission and directives to a distinct entity using exclusively the `invoke_subagent` system tool.
> 3. Wait for the report from this sub-agent to relay it back.
>
> **Mission Orchestrator Specificity:**
> This skill DOES NOT DELEGATE, DOES NOT EXECUTE, AND DOES NOT SCHEDULE FOR EXECUTION.
> It produces written artifacts: Mission Graph, Plan, contracts, budget.
> Only AGENTS invokes sub-agents via `invoke_subagent` / `define_subagent`.

---

## 1. Position in the Tesla Stack

```
SOUL → ENGINE → AGENTS → Tesla Mission Orchestrator (tesla-team-synergy)
                                        ↓
                          Mission Graph / Scheduler / Capability Scoring / Budget
                                        ↓
                              Skills / MCP / Tools
```

- **ENGINE**: Reasoning
- **AGENTS**: Governance, Plan execution
- **Tesla Mission Orchestrator**: Produces the strategic Plan

---

## 2. FORCE_TOOLING Contracts

**Input**
- `project_name: string`
- `objective: string`
- `constraints: string[]`
- `preliminary_complexity: Low | Medium | High`
- `initial_budget?: {claude_pct, gemini_pct, gpt_pct}`

**Output**
- `Gestion-de-Chantiers/[NAME]_v1.0_YYYY-MM-DD.md` – 11-section SGC
- `mission_graph.yaml` – Canonical DAG
- `capability_routing.md` – Scoring + recommended model
- `scheduler_plan.md` – Sequence with dependencies
- `agent_contracts/` – 1 contract per node
- `budget_ledger.md`
- Subagents-Skills DB logged
- `MAIN_RENDUE_A_MAHONHEIM=1`

Maturity: Stable

---

## 3. Mission Graph

Team Synergy never distributes work directly. It constructs a **DAG Mission Graph**.

Example:

```
Mission: Refactor Module X
├── N1 Research
│     ├── Arcanis (OSINT)
│     └── Curator (doc)
├── N2 Architecture
│     ├── Arcanis
│     └── Premortem
├── N3 Code
│     ├── Master-Code
│     └── GitHub-Manager
└── N4 Documentation
      └── Curator
```

Canonical Format: `mission_graph.yaml`

```yaml
mission: Refactor Module X
version: 1.0
nodes:
  - id: N1
    role: Research
    agents: [tesla-arcanis-360, tesla-curator-prime]
    depends_on: []
    contract_ref: contracts/N1.yaml
  - id: N2
    role: Architecture
    agents: [tesla-arcanis-360, premortem]
    depends_on: [N1]
  - id: N3
    role: Code
    agents: [tesla-master-code, tesla-github-manager]
    depends_on: [N2]
  - id: N4
    role: Documentation
    agents: [tesla-curator-prime]
    depends_on: [N3]
```

The Mission Graph is the **Single Source of Truth**. Agents are an implementation.

---

## 4. Capability Scoring – Vendor-Agnostic Routing

We no longer blindly choose "Flash / Sonnet / Opus". We score capabilities.

Axes (0–100):
- Reasoning
- Code
- Audit
- Memory / RAG
- Cost_efficiency (100 = cheapest)
- Latency

**Capability Matrix – v4.0**

| Model | Reasoning | Code | Audit | Memory | Cost | Latency | Usage Profile |
|---|---|---|---|---|---|---|---|
| Gemini Flash | 40 | 55 | 45 | 70 | 100 | 100 | Volumetric I/O, search, doc |
| Gemini Pro | 78 | 75 | 70 | 80 | 65 | 70 | Planning, architecture |
| Claude Sonnet | 82 | 94 | 85 | 75 | 55 | 60 | Code, refactor, tests – workhorse |
| Claude Opus | 95 | 92 | 96 | 80 | 15 | 35 | Critical premortem, security arbitration – RARE |
| GPT-OSS* | 70 | 80 | 60 | 60 | 85 | 55 | Massive scaffolding – *if available* |

Selection: `score = w_reason*Reasoning + w_code*Code + w_audit*Audit - λ*cost_penalty`
with weights defined by the Mission Graph node type.

Mandatory GEMINI.md Rules BEFORE scaling up:
1. Low-Code First
2. Anti-Linear Reading: `rg`, `jq`, Tree-sitter, search_router
3. LSP Loop: `lsp_diagnostics` mandatory

See `CAPABILITY_SCORING.md` for the full matrix.

---

## 5. Scheduler

The Plan includes an explicit Scheduler.

Modes:
- **Series**: A → B → C
- **Parallel**: A || B
- **Pipeline**: Batch streaming
- **Fan-out**: 1 → N
- **Fan-in**: N → 1

Example:

```
N1 Research
   ↓
N2 Architecture  ⟷  N2b Premortem   (parallel)
   ↓
N3 Code
   ↓
N4 Tests
   ↓
N5 Doc
```

Each node declares: `depends_on`, `can_run_parallel_with`, `fan_out`, `critical_path: true/false`.

---

## 6. Agent Contracts

Each node in the Mission Graph exposes a contract:

```yaml
id: N3
agent: tesla-master-code
input: [plan_architecture.md, repo_path]
output: [patch.diff, tests_pass.log]
preconditions: [lsp_clean, git_clean]
postconditions: [tests_green, no_lsp_errors]
risks: [regression_api]
time_estimate_min: 25
cost_estimate_tokens: M
model_recommended: claude-sonnet
capability_min: {Code: 85, Reasoning: 70}
```

Team Synergy does not need to know the agent's internals, only its contract.

---

## 7. Retry / Fallback / Escalation Policy

For each node:

```
Execution
  ↓ fail?
Retry x2 – same model, tighter prompt
  ↓ still KO?
Fallback – higher model in the same family
  ex: Sonnet → Opus, Pro → Opus, Flash → Pro
  ↓ still KO?
Escalation Mahonheim – with dossier: logs, attempts, blockage hypothesis
  ↓
Traced abandonment – node marked BLOCKED in State Machine
```

Retries are logged in DB with `attempt_n`.

Never more than 2 automatic retries without model escalation.

---

## 8. Budget Manager – Token Economy v4

Each project opens a **budget envelope**:

```
Refactor X Project Budget
- Claude: 15%
- Gemini: 60%
- GPT-OSS: 25%
```

Real-time tracking in `budget_ledger.md`:

| Node | Model | Est. Tokens | Real Tokens | Group Quota Remaining |
|---|---|---|---|---|
| N1 | gemini-flash | S | … | 82% |
| N3 | claude-sonnet | M | … | 71% |

Rules:
- Quotas: Gemini / Claude / GPT-OSS groups – weekly + 5h sliding window
- Circuit-breaker <15% remaining → auto-degradation: Opus→Sonnet, Pro→Flash, logged
- Tasks >25 min segmented to control the 5h window
- Expensive calls relegated to the end of the chain, after Flash/Sonnet filtering

---

## 9. Mission State Machine

```
CREATED
  ↓
PLANNED  ← Validated Mission Graph
  ↓
RUNNING
  ├→ BLOCKED  → (retry/fallback) → RUNNING
  └→ WAITING   → external dependency
  ↓
REVIEW   ← Premortem + Economy-Premortem
  ↓
DONE
  ↓
ARCHIVED
```

Each transition is timestamped in `mission_state.json` and indexed in Alexandria.

Enables a future multi-project dashboard.

---

## 10. SGC Orchestration Protocol

Trigger: "I'm opening a [NAME] project for [objective]."

1. **Framing** – Low/Med/High complexity, initial budget envelope, role mapping
2. **Mission Graph** – Generate `mission_graph.yaml` + agent contracts
3. **Capability Scoring + Scheduler** – Annotate each node: model, cost, dependencies
4. **SGC PLAN.md** – `Gestion-de-Chantiers/[NAME]_v1.0_YYYY-MM-DD.md`, 11 sections, including routing matrix
5. **Premortem + Economy-Premortem**
   - [ ] Can Opus be replaced by Sonnet?
   - [ ] Research via Flash?
   - [ ] Volumetrics via Flash?
   - [ ] Sufficient quota? Degradation plan?
   - [ ] Shadow-targeting feasible?
6. **Execution – AGENTS delegates** according to Scheduler
7. **Retry/Fallback** applied by AGENTS upon node failure
8. **Memory Sync** – `log_subagent_parser.py` → `alexandria_brain.db`
   - `model_used, complexity, tokens_estimate, attempt_n, node_id`
9. **Handover to Mahonheim** – `MAIN_RENDUE_A_MAHONHEIM=1`, INDEX.md, PROJECT_STATE.md, Alexandria

---

## 11. Shadow-Targeting & Token-Economy

- Research / Doc → inject Arcanis / Curator in `self`, **forced Gemini Flash**
- DB Log: `injection_method='shadow-targeting'`, `model_used`, `complexity`
- Rollback: 1. Semantic deactivation / 2. Physical quarantine / 3. DB `statut='inactive'` / 4. `update_session_history.py`
- Statuses: `active | inactive | expired | failed`

---

## 12. Learning Loop – Alexandria

After each project:

```
Mission → Feedback → Performance / Quality / Time / Tokens → Lesson → Alexandria
```

Curator-Prime analyzes:
- Routing patterns that stayed within quotas
- Sonnet vs Opus success rate
- Real time vs estimated time per node type
- Retry rate per agent / model

→ Proposes adjustments to `CAPABILITY_SCORING.md` and `MODEL_ROUTING.md`

Extended DB Schema:
```sql
ALTER TABLE subagents_skills ADD COLUMN model_used TEXT;
ALTER TABLE subagents_skills ADD COLUMN complexity TEXT CHECK(complexity IN ('Low','Medium','High'));
ALTER TABLE subagents_skills ADD COLUMN tokens_estimate INTEGER;
ALTER TABLE subagents_skills ADD COLUMN node_id TEXT;
ALTER TABLE subagents_skills ADD COLUMN attempt_n INTEGER DEFAULT 1;
ALTER TABLE subagents_skills ADD COLUMN mission_state TEXT;
```

---

## 13. Delivery Checklist

- [ ] Mission Graph YAML validated
- [ ] Complete agent contracts
- [ ] Capability Scoring + recommended model per node
- [ ] Scheduler with dependencies
- [ ] Budget envelope + ledger
- [ ] Documented Retry policy
- [ ] Premortem + Economy-Premortem
- [ ] RULE N°4 respected
- [ ] LSP Loop / Low-Code / Anti-Linear Reading verified
- [ ] DB logged: model_used/complexity/tokens/node_id/attempt_n
- [ ] State Machine → DONE
- [ ] INDEX.md / PROJECT_STATE.md / Alexandria
- [ ] `MAIN_RENDUE_A_MAHONHEIM=1`

---

## 14. References

SOUL.md / ENGINE.md / AGENTS.md / FORCE_TOOLING.md / GEMINI.md / shadow-targeting-method.md / TEAM_ROLES.md / CAPABILITY_SCORING.md / MODEL_ROUTING.md

---

## CHANGELOG

**v4.0 – 2026-07-10 – Tesla Mission Orchestrator**
- Added: Canonical DAG Mission Graph
- Added: Vendor-agnostic Capability Scoring (Reasoning/Code/Audit/Memory/Cost/Latency)
- Added: Series/parallel/pipeline/fan-out/fan-in Scheduler
- Added: Agent contracts (Input/Output/Pre/Post/Risks/Time/Cost)
- Added: Retry / Fallback / Mahonheim Escalation Policy
- Added: Budget Manager with project envelope + real-time ledger
- Added: CREATED→PLANNED→RUNNING→BLOCKED/WAITING→REVIEW→DONE→ARCHIVED State Machine
- Added: Alexandria post-mission Learning Loop
- Functional Rename: **Tesla Mission Orchestrator** – technical name `tesla-team-synergy` preserved
- Preserved: Token-Economy v3, SGC, Rule N°4, Shadow-Targeting, LSP Loop

**v3.0 – 2026-07-10**
- Token-Economy v2, FORCE_TOOLING contracts, native SGC, DB migration

**v2.0**
- Initial token-economy mission

**v1.0**
- Initial multi-agent orchestration

---
`MAIN_RENDUE_A_MAHONHEIM=1`
