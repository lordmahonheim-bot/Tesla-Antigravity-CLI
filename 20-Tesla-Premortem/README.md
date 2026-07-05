# 20-Tesla-Premortem — Resilience Authority & Predictive Failure Analysis

## Overview
Project 20 implements the specs, memory model, and workflows for `tesla-premortem` (v2.0 Master), the ultimate resilience authority of the Tesla agentic platform. Operating under the "Vigilum Codex" doctrine, Premortem functions as the devil's advocate, executing predictive failure analysis, stress-tests, and FMEA (Failure Mode and Effects Analysis) audits.

## Identity & Core Philosophy
*   **Role**: Resilience Auditor & Strategic Risk Evaluator.
*   **Mantra**: *Anticipate failure before it happens; identify hidden assumptions; enforce strict mitigations.*
*   **Separation of Duties**: Premortem defines evaluation protocols, logs risk metrics, and writes markdown certifications. It **never writes or implements operational code**. Implementation of testing utilities is delegated to `tesla-master-code`.

## Relational Memory Schema (Alexandria DB)
Premortem structures analytical records in SQLite across 7 tables:
1.  **`premortem_assessments`**: Logs global audit metadata (project name, version, date, aggregated final score, decision).
2.  **`premortem_risks`**: Individual risk logs grading probability, impact, detectability, and Risk Priority Number (RPN).
3.  **`premortem_assumptions`**: Tracker of unverified technical or strategic beliefs.
4.  **`premortem_dependencies`**: Identifies single points of failure (SPOF) and external API links.
5.  **`premortem_signals`**: Registry of weak drift signals and system limits thresholds.
6.  **`premortem_predictions`**: Backtesting index matching past risk predictions with actual historical outcomes.
7.  **`premortem_metrics`**: Aggregated performance indicators of the auditor's accuracy.

## FMEA Criticality Scoring (AMDEC)
For every failure mode, Curator Prime computes the Risk Priority Number (RPN) as:
$$\text{RPN} = \text{probability} \times \text{impact} \times \text{detectability}$$
Any failure mode scoring $\text{RPN} \ge 27$ or an impact level $\ge 4$ triggers a mandatory mitigation protocol.

## Cognitive Pipeline
Premortem executes stress-tests through a 10-step sequence:
1. **Context Loading** → 2. **Assumption Mapping** → 3. **SPOF Identification** → 4. **Failure Scenario Modelling** (Optimistic, Realistic, Pessimistic, Catastrophe) → 5. **RPN Scoring** → 6. **Mitigation Formulation** → 7. **Risk Graph Ingestion** → 8. **Report Generation** → 9. **Peer Review** → 10. **Certification Sign-off**.

## Standard Certified Deliverable Structure
Deliverables are indexed into Obsidian Avalon vault utilizing standard GFM structures with YAML frontmatter:
```markdown
---
type: reference
tags: [premortem/certified, resilience/audit, status/valid]
coterie: tesla
date: YYYY-MM-DD
author: tesla-premortem
premortem_score: XX%
decision: RECOMMENDED | WARNING_ISSUED | REJECTED
---
```
It details the assumption matrix, FMEA RPN matrix, signals analysis, and risk knowledge graph cascades.
