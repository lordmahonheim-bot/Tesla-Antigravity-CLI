# MODEL_ROUTING – Cheatsheet v4.0
# Tesla Mission Orchestrator

![Status](https://img.shields.io/badge/Status-MVP-blue) ![Ecosystem](https://img.shields.io/badge/Ecosystem-TESLA%20ANTIGRAVITY-purple) ![Security](https://img.shields.io/badge/Security-ID%20LOCKED-red) ![Python](https://img.shields.io/badge/Python-3.12+-blue)

**Capability Selection FORCE_TOOLING: Relevance > Security > Reliability > Cost > Simplicity > Reproducibility > Cognitive Economy**

Use **Capability Scoring** – see `CAPABILITY_SCORING.md`

Quick summary:

| Requirement | Model | Code Score | Cost |
|---|---|---|---|
| Research / OSINT / parsing / doc | Gemini Flash | 55 | 100 |
| Planning / Architecture | Gemini Pro | 75 | 65 |
| Code / Refactoring / Tests | Claude Sonnet | 94 | 55 |
| Critical premortem / Security | Claude Opus | 92 | 15 |
| Massive scaffolding | GPT-OSS* / Sonnet | 80 | 85 |

*if available

**Before upscaling – MANDATORY:**
1. Low-Code First
2. Anti-Linear Reading: `rg` / `jq` / Tree-sitter / search_router
3. LSP Loop: `lsp_diagnostics`

Escalation: Flash → Pro/Sonnet → Opus – document rationale.

Quotas: Gemini | Claude | GPT-OSS – weekly + 5h rolling.
Circuit-breaker <15% → Opus→Sonnet, Pro→Flash.

Eco Shadow-Targeting: Arcanis/Curator within `self`, forced Flash.

---
`MAIN_RENDUE_A_MAHONHEIM=1`
