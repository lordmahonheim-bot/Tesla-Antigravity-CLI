# Capability Scoring – Tesla Mission Orchestrator v4.0

![Status](https://img.shields.io/badge/Status-MVP-blue) ![Ecosystem](https://img.shields.io/badge/Ecosystem-TESLA%20ANTIGRAVITY-purple) ![Security](https://img.shields.io/badge/Security-ID%20LOCKED-red) ![Python](https://img.shields.io/badge/Python-3.12+-blue)

Routing no longer selects a model name. It selects the best capability.

## Axes (0–100)

- **Reasoning**: planning, arbitration, complex synthesis
- **Code**: generation / refactoring / tests, LSP quality
- **Audit**: premortem, security, contradiction detection
- **Memory / RAG**: long context, documentary research
- **Cost_efficiency**: 100 = cheapest in tokens/quota
- **Latency**: 100 = fastest

## Matrix v4.0

| Model | Reasoning | Code | Audit | Memory | Cost | Latency | $/1M tok out (indicative) |
|---|---|---|---|---|---|---|---|
| Gemini Flash | 40 | 55 | 45 | 70 | 100 | 100 | ~ |
| Gemini Pro | 78 | 75 | 70 | 80 | 65 | 70 | ~ |
| Claude Sonnet | 82 | 94 | 85 | 75 | 55 | 60 | ~ |
| Claude Opus | 95 | 92 | 96 | 80 | 15 | 35 | ~ |
| GPT-OSS* | 70 | 80 | 60 | 60 | 85 | 55 | ~ |

* GPT-OSS: if available in the Antigravity environment, otherwise fallback to Sonnet.

## Selection

For a node N with requirements `req = {Reasoning, Code, Audit}`:

```
score(model) = w_r*Reasoning + w_c*Code + w_a*Audit + w_m*Memory
               - λ * cost_penalty
```

Weights per role:

| Role | w_r | w_c | w_a | w_m | λ |
|---|---|---|---|---|---|
| Research | 0.2 | 0.1 | 0.2 | 0.5 | 1.5 |
| Architecture | 0.5 | 0.2 | 0.2 | 0.1 | 0.8 |
| Code | 0.2 | 0.6 | 0.1 | 0.1 | 0.8 |
| Premortem | 0.4 | 0.1 | 0.5 | 0.0 | 0.4 |
| Documentation | 0.3 | 0.0 | 0.1 | 0.6 | 1.5 |

Choose the model with the maximum score that satisfies the `capability_min` of the agent contract.

If group quota < 15%: apply cost penalty x2 → automatic degradation Opus→Sonnet, Pro→Flash.

## Quick Mapping (v3 compatibility)

- Research / OSINT / parsing → Flash  (Cost 100, Memory 70)
- Planning / Archi → Pro  (Reasoning 78)
- Code / Tests → Sonnet  (Code 94)
- Critical premortem → Opus  (Audit 96)
- Doc / README → Flash

GEMINI.md rules always have priority: Low-Code First, Anti-Linear Reading, LSP Loop.

---
`MAIN_RENDUE_A_MAHONHEIM=1`
