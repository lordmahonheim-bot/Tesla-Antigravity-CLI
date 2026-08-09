---
type: reference
tags: [shadow-targeting, technical-documentation, security, status/valid]
date: 2026-07-03
version: 1.0
---

![Status](https://img.shields.io/badge/Status-MVP-blue) ![Ecosystem](https://img.shields.io/badge/Ecosystem-TESLA%20ANTIGRAVITY-purple) ![Security](https://img.shields.io/badge/Security-ID%20LOCKED-red) ![Python](https://img.shields.io/badge/Python-3.12+-blue)

# 📑 TECHNICAL SPECIFICATION: SHADOW-TARGETING METHOD
**Subject:** Secure injection and tracking of subagent skills under Antigravity CLI  
**Doctrine:** Vigilum Codex  

---

## 1. Method Principle
**Shadow-Targeting** is a hot-injection method for skills into the default subagents of the Antigravity CLI. 

On the Pro paid plan ($20/month), the platform restricts the creation or deployment of additional custom subagents. The method consists of configuring isolated skill sets, then injecting them as integrated capabilities (via the `self` execution variable or the direct import of `SKILL.md` instruction files) into one of the 3 native subagents of the environment, allowing them to overcome their functional barriers without violating the physical constraints of the pricing plan.

---

## 2. Nomenclature and Naming Conventions
To preserve the modularity of the ecosystem, the following rule applies:

*   **Principle of Independence**: Each skill or subagent must remain strictly independent of the others, whether in its creation, naming, or functions.
*   **Name Structure**: The name of the directory and the skill must exactly match the created agent, without a dependency prefix (e.g., `tesla-web-raider`).
*   **Metadata Header**: The associated `SKILL.md` file must declare in its YAML frontmatter:
    ```yaml
    injection_type: shadow-targeted
    target_subagent: self
    ```
*   **Database Injection Flag**: In the [alexandria_brain.db](file:///home/lord-mahonheim/bifrost/tesla/Avalon/03-Resources/alexandria_brain.db) database, the `subagents_skills` table must carry the value `injection_method = 'shadow-targeting'`.

---

## 3. Compliance Risks & Terms of Service (TOS)
*   **Risk Analysis**: Shadow-Targeting exploits the native file import and instruction features of the Antigravity CLI. It does not modify the platform's executable binary, does not decompile its code, and does not use any security bypass exploits.
*   **Risk Level**: **Negligible**. The action is akin to a legitimate contextual injection of prompts and tools within a local sandbox.
*   **Mitigation Policy**:
    1. Never attempt to bypass the platform's API volume or request call limitations via flooding scripts.
    2. Transparently document calls to ensure traceability of modifications.

---

## 4. Removal and Rollback Procedure
In the event of a semantic malfunction, an infinite request loop, or behavioral drift of the target subagent:

1.  **Semantic Deactivation**: Remove the skill directory reference from the system prompt of the subagent (in `.agents/[SUBAGENT].md`).
2.  **Physical Deletion**: Move the skill directory out of the indexing directory (`.agents/skills/`) to a temporary quarantine folder.
3.  **Database Update**: Execute the database status update to change the state to `expired` or `failed` in the `subagents_skills` table:
    ```sql
    UPDATE subagents_skills SET statut = 'inactive', notes = 'Rollback command triggered' WHERE skill_name = '[SKILL_NAME]' AND session_id = '[SESSION_ID]';
    ```
4.  **Re-synchronization**: Run the `update_session_history.py` command to regenerate the semantic index and certify the return to a nominal state.
