# Ops Consultant — AI Agents, CLI Workflows & Local Governance
*Author:* Lord Mahonheim  
*Status:* Verified Reference (statut/valide)  
*Tagline:* "An un-governed agent is a liability; structure is the mother of security."

## Tested Environment Table
| Parameter | Value |
| :--- | :--- |
| Date | 2026-06-28 |
| Host Machine | MIDGARD |
| Operating System | Linux (Ubuntu/Debian) |
| Workspace Path | `/home/lord-mahonheim/bifrost/tesla` |
| Python Version | 3.10+ |
| Node.js Version | 18+ |
| SQLite Version | 3.37+ |

## Important Security Notice
This repository contains anonymized configuration models and utility wrappers. No active passwords, private Obsidian vaults, local database files (`*.db`, `.chroma_vectors`), or API tokens are tracked.

## Table of Contents
1. Executive Summary
2. Problem Statement
3. Product Promise
4. Core Principles Table
5. Architecture Diagram
6. Repository Layout
7. Workflow Sequence
8. Technical Stack
9. Security and Governance Rules
10. Acceptance Criteria
11. Final Verdict & Signature Sentence

## Executive Summary
Vigilum Codex is an institution-matrice dedicated to human performance, strategic intelligence, and governed local AI operations. The projects hosted within this repository form the technical infrastructure of the Tesla agent, operating locally on MIDGARD.
This repository acts as a public MVP release of the core workflow automation and governance modules. It integrates 20 subprojects ranging from static code syntax healing to secure graphical authentication wrappers, hybrid search engines, universal knowledge curation, and predictive failure diagnostics.

## Problem Statement
In previous iterations, the AI agent functioned without clear local boundaries. This resulted in multiple system level errors:
1. **Broken local paths:** Hardcoded paths (`/home/lord-mahonheim/bifrost/tesla`) rendered scripts non-portable.
2. **Context Saturation:** Linear directory sweeps overloaded the model's token cache, leading to high latency and search failures.
3. **Authentication blocks:** Background commands froze due to missing TTY prompts, and git operations were rejected due to unbound SSH key permissions.
4. **Isolated tools:** Scripts were built in isolation without common imports, causing naming collisions and dependency breakage.

## Product Promise
* **What it does:** Scaffolds a complete, documented set of local agent modules, verifying syntactic correctness, cognitive persistence, and secure execution.
* **What it does NOT do:** Route telemetry to external servers, allow direct remote branch pushing without checks, or bypass manual approvals.

## Core Principles Table
| Principle | Meaning | Impact |
| :--- | :--- | :--- |
| Local Execution | All processes run on host MIDGARD. | Guarantees complete data sovereignty. |
| Verification First | Run LSP and syntax tests before commit. | Guarantees codebase structural integrity. |
| Explicit Approval | Root modifications require operator dialog. | Retains human authority over system changes. |

## Architecture Diagram
```mermaid
graph TD
    A[Vigilum Codex Core] --> Core[Core Automation]
    A --> Gov[Governance & Auditing]
    A --> Data[Data & Memory]
    A --> Media[Media & Cloud]

    Core --> B["01-LSP-Self-Healing"]
    Core --> E["04-Web-Raider"]
    Core --> G["06-Sudo-Askpass"]
    Core --> K["10-Github-MVP-Scaffolding"]
    Core --> Q["16-Tesla-Master-Code"]

    Gov --> F["05-USB-Resilience"]
    Gov --> H["07-Strategic-Armement"]
    Gov --> I["08-Integration-Antigravity-Google-Agents-MIDGARD"]
    Gov --> J["09-Github-Governance"]
    Gov --> L["11-Tesla-Arcanis-Skill"]
    Gov --> U["20-Tesla-Premortem"]

    Data --> C["02-Alexandria-Database"]
    Data --> D["03-Memory-MLT"]
    Data --> M["12-Alexandria-RAG-Unification"]
    Data --> P["15-Obsidian-Database"]
    Data --> R["17-DB-Subagents-Skills"]
    Data --> T["19-Tesla-Curator-Prime"]

    Media --> N["13-Jules-Cloud-Integration"]
    Media --> O["14-Llama-cpp-Evaluation"]
    Media --> S["18-Tesla-Video-Director"]
```

## Repository Layout
```text
MVP-GITHUB/
├── .gitignore
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── LICENSE
├── MY_COMPANY.md
├── README.md
├── SECURITY.md
├── SUPPORT.md
├── 01-LSP-Self-Healing/
├── 02-Alexandria-Database/
├── 03-Memory-MLT/
├── 04-Web-Raider/
├── 05-USB-Resilience/
├── 06-Sudo-Askpass/
├── 07-Strategic-Armement/
├── 08-Integration-Antigravity-Google-Agents-MIDGARD/
├── 09-Github-Governance/
├── 10-Github-MVP-Scaffolding/
├── 11-Tesla-Arcanis-Skill/
├── 12-Alexandria-RAG-Unification/
├── 13-Jules-Cloud-Integration/
├── 14-Llama-cpp-Evaluation/
├── 15-Obsidian-Database/
├── 16-Tesla-Master-Code/
├── 17-DB-Subagents-Skills/
├── 18-Tesla-Video-Director/
├── 19-Tesla-Curator-Prime/
└── 20-Tesla-Premortem/
```

## Workflow Sequence
1. The developer triggers updates within a project folder.
2. Code edits are checked by `01-LSP-Self-Healing` via local pyright diagnostics, and pre-flight lints are enforced by `16-Tesla-Master-Code`.
3. Successful revisions are documented and indexed using `02-Alexandria-Database` and the RAG indexers of `15-Obsidian-Database`.
4. Action logs and subagent sessions are consolidated into `03-Memory-MLT` and `17-DB-Subagents-Skills` databases.
5. High-level evaluations (`14-Llama-cpp-Evaluation`), cloud computations (`13-Jules-Cloud-Integration`), and media ingestion (`18-Tesla-Video-Director`) are dispatched as needed.
6. All system or push actions must abide by the rules configured in `09-Github-Governance` and staged cleanly via `10-Github-MVP-Scaffolding`.
7. Knowledge synthesis, document verification, and citation archives are managed and certified by `19-Tesla-Curator-Prime` before integration into the Obsidian Avalon vault.
8. Predictive failure scenarios, AMDEC/FMEA assessments, and dynamic risk graph entries are mapped and certified by `20-Tesla-Premortem` before critical systems execution.

## Feature Highlights (v3.0.0)
*   **SQLite Safe Mode (`mode=rw`):** Centralized `db_connector.py` database wrapper enforces read-write only constraints by default. This blocks scripts from silently creating blank SQLite files on disk if the primary database is missing, ensuring configuration consistency.
*   **Active Log Rotation:** The session history manager automatically archives older transcript blocks (>15 days) from the working markdown logs to a local `/backup/transcripts_archive` directory to save token context size.
*   **Context & Secret Protection:** The subagent transcript logs parser dynamically scrubs AWS, GitHub, Slack, JWT, and SSH private keys using regex filters, ensuring no secret keys are tracked in the database or session markdown history.

## Technical Stack
* **Languages:** Python 3.10+, Bash (Shell)
* **Frameworks:** Playwright, Sentence-Transformers
* **Storage:** SQLite FTS5, ChromaDB (local)
* **Testing:** Pyright LSP

## Security and Governance Rules
* Isolation: Tools must run within the designated user privileges.
* Zero Network Autonomy: The agent cannot add remotes, commit keys, or push code without explicit manual authorization.
* Backup Protocol: Commits must always be preceded by local git status checks to exclude caches and databases.

## Acceptance Criteria
* All 20 subprojects exist and are fully populated.
* Pyright reports 0 errors across all Python files.
* Local repository branch versioning is initialized on `feature/premortem-master-mvp`.

## Final Verdict & Signature Sentence
**VERDICT: OPERATIONAL SYSTEM STABILIZED**  
*"Precision in structure brings governance in execution."*
