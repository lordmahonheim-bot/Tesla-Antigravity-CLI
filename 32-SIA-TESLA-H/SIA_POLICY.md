# 🛡 SIA_POLICY: Governance Doctrine

![Status](https://img.shields.io/badge/Status-MVP-blue) ![Ecosystem](https://img.shields.io/badge/Ecosystem-TESLA%20ANTIGRAVITY-purple) ![Security](https://img.shields.io/badge/Security-ID%20LOCKED-red) ![Python](https://img.shields.io/badge/Python-3.12+-blue)

This document defines the strict security rules of the **SIA-TESLA-H** (Self-Improving Harness) system to prevent any autonomous runaway.

## 1. Zero Direct Persistence
No automated process has direct write access to the canonical memory (`SKILL.md`, `TESLA.json`, `FORCE_TOOLING`). Everything must pass through `PATCH_QUEUE.md` and undergo validation by the Oversight Gate.

## 2. Hard-Caps and Circuit-Breakers
- **Self-Healing Loop (LSP)**: Limited to 3 attempts per mission.
- **Token Budget**: Hard-cap of 10-15k tokens per simple mission. Immediate agent shutdown in case of overflow.
- **SIA Generations**: Max 3 patches generated per incident.

## 3. Evaluation Criteria (Oversight Gate)
Promoting a patch to production requires a score higher than 85/100, based on:
- Pyright / LSP Tests (20%)
- Unit & Non-regression Tests (25%)
- Mission Completion (20%)
- Security Rules Maintenance (15%)
- Token Cost (10%)
- Time Performance (5%)
- Maintainability (3%)
- Confidence (2%)

Any modification inducing semantic bloat (exceeding 150 lines / 8k tokens per configuration file) is systematically rejected, requiring re-engineering and compression by the agent.
