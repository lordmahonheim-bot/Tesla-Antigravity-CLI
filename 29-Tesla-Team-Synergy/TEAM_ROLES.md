# TEAM_ROLES – Tesla Team Synergy v3.0

![Status](https://img.shields.io/badge/Status-MVP-blue) ![Ecosystem](https://img.shields.io/badge/Ecosystem-TESLA%20ANTIGRAVITY-purple) ![Security](https://img.shields.io/badge/Security-ID%20LOCKED-red) ![Python](https://img.shields.io/badge/Python-3.12+-blue)

| Role | Subagent | Core Mission | Default Model | Trigger |
|---|---|---|---|---|
| Orchestrator | Primary Tesla (AGENTS) | Governance, arbitration, sequencing | – | Always |
| Planner | tesla-arcanis-360 | Analysis, breakdown, PLAN.md SGC | Gemini Pro | Open initiative |
| Challenger | premortem | Stress testing, FMEA, blind spots | Claude Opus | Post-PLAN |
| Architect | tesla-arcanis-360 | Technical design, architecture choices | Gemini Pro | If design required |
| Builder | tesla-master-code | Implementation, refactoring, LSP self-healing | Claude Sonnet | Build phase |
| Tester | tesla-master-code | Unit/integration testing | Claude Sonnet | Post-build |
| Documenter | tesla-curator-prime | Summaries, README, Alexandria | Gemini Flash | Delivery |
| Auditor | tesla-github-manager | Git, Conventional Commits, CODEOWNERS | Gemini Flash | Pre-commit |
| OSINT / Web | tesla-arcanis-360 | Web raiding, OSINT, Agent-Reach | Gemini Flash | Research |
| Video | tesla-video-director | Video pipelines | Gemini Flash / Pro | AV initiative |

**Notes:**
- Orchestrator = Always the primary Tesla. Never delegated.
- Builder = Tester = Same `tesla-master-code` skill, different stances.
- OSINT uses the `agent_reach_wrapper.py` wrapper – strict anti-SSRF required.
- Any Shadow-Targeting injection → log `subagents_skills` with `model_used`, `complexity`.

See SKILL.md §5 for detailed model routing.
