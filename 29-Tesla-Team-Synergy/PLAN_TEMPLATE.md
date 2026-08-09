# [PROJECT-NAME]_v1.0_YYYY-MM-DD.md
<!-- SGC – AGENTS.md §11 – Tesla Mission Orchestrator v4.0 -->

![Status](https://img.shields.io/badge/Status-MVP-blue) ![Ecosystem](https://img.shields.io/badge/Ecosystem-TESLA%20ANTIGRAVITY-purple) ![Security](https://img.shields.io/badge/Security-ID%20LOCKED-red) ![Python](https://img.shields.io/badge/Python-3.12+-blue)

## 1. Objective

## 2. Scope
In / Out

## 3. Constraints

## 4. Dependencies

## 5. Mission Graph
See `mission_graph.yaml`
Summary: N1 Research → N2 Architecture → N2b Premortem → N3 Code → N4 Test → N5 Doc

## 6. Identified Risks (Premortem)

## 7. Routing Table – Capability Scoring

| Node | Role | Subagent | Model | Reasoning | Code | Audit | Cost | Complexity | Budget |
|---|---|---|---|---|---|---|---|---|---|
| N1 | Research | arcanis/curator | gemini-flash | 40 | 55 | 45 | 100 | Low | S |
| N2 | Archi | arcanis-360 | gemini-pro | 78 | 75 | 70 | 65 | Medium | M |
| N2b | Challenger | premortem | claude-opus | 95 | 92 | 96 | 15 | High | L |
| N3 | Code | master-code | claude-sonnet | 82 | 94 | 85 | 55 | Medium | M |
| N4 | Test | master-code | claude-sonnet | 82 | 94 | 85 | 55 | Medium | M |
| N5 | Doc | curator-prime | gemini-flash | 40 | 55 | 45 | 100 | Low | S |

**Budget envelope:** Gemini 60% / Claude 35% / GPT-OSS 5%

## 8. Scheduler
- Series: N1 → N2 → N2b → N3 → N4 → N5
- Parallel: –
- Critical path: N1-N5

## 9. Retry / Fallback
- max_retries: 2
- fallback_model: +1 tier
- escalation: Mahonheim

## 10. Premortem-Economy
- [ ] Opus replaceable by Sonnet?
- [ ] Research in Flash?
- [ ] Volumetrics in Flash?
- [ ] Sufficient quota? Degradation plan?
- [ ] Shadow-targeting possible?

## 11. Traceability
- Session ID:
- Mission State: PLANNED → … → DONE
- DB: model_used / complexity / tokens / node_id / attempt_n
- INDEX.md: yes/no
- PROJECT_STATE.md: yes/no
- Alexandria: yes/no

---
`MAIN_RENDUE_A_MAHONHEIM=1`
