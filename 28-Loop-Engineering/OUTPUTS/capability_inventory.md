# Tesla/Antigravity Loop Engineering - Capability Inventory & Environmental Discovery

**Date:** 2026-07-10  
**Agent:** worker-capability-discovery (Implementer/QA/Specialist)  
**Status:** Validated  
**Version:** 1.0  

---

## 1. Executive Summary & Objective

This document represents the official capability inventory and environment audit for the **Tesla/Antigravity Loop Engineering** project on the **MIDGARD** development workstation. Pursuant to the **AGENTS** and **FORCE_TOOLING** protocols, this discovery phase precedes all implementation to ensure that code, skills, and tools are properly discovered, mapped, and leveraged without duplication or role violation.

---

## 2. Existing Skills Inventory (`.agents/skills/`)

A total of eleven (11) cognitive skills are registered in the `.agents/skills/` directory. They provide specialized capabilities for deep research, repository management, software engineering, and AI API integration.

### Summary Table

| Skill Name | Version | Status | Owner | Core Role & Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **premortem** | 2.0 | Production | Tesla | Resilience authority; performs predictive failure analysis and risk calibrations. |
| **tesla-arcanis-360** | MASTER-v4.1 | Production | Tesla | Master intelligence agent; handles deep research, Shadow OSINT, and adversarial audits. |
| **tesla-curator-prime** | - | Active | Tesla | CKO; cognitive curation, verification, and indexing of knowledge in Alexandria/Obsidian. |
| **tesla-github-manager** | - | Active | Tesla | Expert in GitHub repository management, versioning, and security governance under Vigilum Codex. |
| **tesla-master-code** | 3.0 | Canonical (Elite) | Tesla | Canonical software engineering authority; controls code modification, execution, and validation. |
| **tesla-video-director** | 2.0 | Production | Tesla | AI video production director; orchestrates local FFmpeg and Gemini API video workflows. |
| **tesla-web-raider** | - | Production | Tesla | Sovereign of internet operations; web scraping, extraction, and automation via Webwright. |
| **gemini-api-dev** | - | Active | - | Reference guide for building applications with Gemini models and official SDKs. |
| **gemini-interactions-api**| - | Active | - | Guide for text generation, multi-turn chat, function calling, and structured outputs. |
| **gemini-live-api-dev** | - | Active | - | Reference guide for real-time WebSocket-based audio/video/text streaming. |
| **gemini-omni-flash-api** | - | Active | - | Reference guide for generative video editing and Omni Flash transition animations. |

---

### Detailed Skill Definitions

#### 1. `premortem` (Version 2.0)
* **Location:** `.agents/skills/premortem/`
* **Objective:** Acts as the resilience authority. It conducts predictive failure analysis, stress-tests, AMDEC/FMEA audits, and preventative risk assessments before major actions.

#### 2. `tesla-arcanis-360` (Version MASTER-v4.1)
* **Location:** `.agents/skills/tesla-arcanis-360/`
* **Objective:** Master intelligence agent executing Layer 1 (Deep Research), Layer 2 (Shadow OSINT), and Layer 3 (360° Analysis). Essential for initial task framing and adversarial verification.

#### 3. `tesla-curator-prime`
* **Location:** `.agents/skills/tesla-curator-prime/`
* **Objective:** Chief Knowledge Officer. Responsible for curating, fact-checking, synthesizing, and indexation of data into the Alexandria database and Obsidian Avalon vault.

#### 4. `tesla-github-manager`
* **Location:** `.agents/skills/tesla-github-manager/`
* **Objective:** Governs Git operations, PR creation, branch versioning, and repository security, operating under the Vigilum Codex.

#### 5. `tesla-master-code` (Version 3.0)
* **Location:** `.agents/skills/tesla-master-code/`
* **Objective:** Canonical authority for software development. Governs sandboxing, code styling, testing, and validation of codebase modifications on MIDGARD.

#### 6. `tesla-video-director` (Version 2.0)
* **Location:** `.agents/skills/tesla-video-director/`
* **Objective:** Directs local and API-driven video workflows. Leverages local FFmpeg utilities and remote Gemini models for editing and transcription.

#### 7. `tesla-web-raider`
* **Location:** `.agents/skills/tesla-web-raider/`
* **Objective:** Automates internet browsing, page extraction, and web tasks using the Webwright engine with dual visual validation.

#### 8. `gemini-api-dev`
* **Location:** `.agents/skills/gemini-skills/skills/gemini-api-dev/`
* **Objective:** Technical reference for Gemini 3.5/Flash model specifications, structured JSON schemas, and SDK integrations (Python, TS, Java, Go).

#### 9. `gemini-interactions-api`
* **Location:** `.agents/skills/gemini-skills/skills/gemini-interactions-api/`
* **Objective:** Guidelines for leveraging the Interactions API for chat, structured outputs, and migration from legacy `generateContent` endpoints.

#### 10. `gemini-live-api-dev`
* **Location:** `.agents/skills/gemini-skills/skills/gemini-live-api-dev/`
* **Objective:** Guidelines for WebSocket-based bidirectional audio/video live streaming, voice activity detection (VAD), and ephemeral token management.

#### 11. `gemini-omni-flash-api`
* **Location:** `.agents/skills/gemini-skills/skills/gemini-omni-flash-api/`
* **Objective:** Details generative video editing, text-to-video, and image-to-video transitions using `gemini-omni-flash-preview` with local FFmpeg processing.

---

## 3. Available MCP Servers & Tools

The system registers two (2) lazy-loaded MCP servers located under `/home/lord-mahonheim/.gemini/antigravity-cli/mcp/`.

### 1. `chrome-devtools` (Lazy-Loaded)
* **Location:** `/home/lord-mahonheim/.gemini/antigravity-cli/mcp/chrome-devtools/`
* **Role:** Web debugging, browser automation, and performance auditing.
* **Tools Available (29):**
  * `click`, `close_page`, `drag`, `emulate`, `evaluate_script`, `fill`, `fill_form`
  * `get_console_message`, `get_network_request`, `handle_dialog`, `hover`
  * `lighthouse_audit`, `list_console_messages`, `list_network_requests`, `list_pages`
  * `navigate_page`, `new_page`, `performance_analyze_insight`, `performance_start_trace`
  * `performance_stop_trace`, `press_key`, `resize_page`, `select_page`
  * `take_heapsnapshot`, `take_screenshot`, `take_snapshot`, `type_text`, `upload_file`, `wait_for`

### 2. `context7` (Lazy-Loaded)
* **Location:** `/home/lord-mahonheim/.gemini/antigravity-cli/mcp/context7/`
* **Role:** Retrieves up-to-date documentation and code snippets for libraries, frameworks, SDKs, and CLIs, bypassing outdated training data limits.
* **Tools Available (2):**
  * `resolve-library-id`: Search for a library name and retrieve its Context7 ID.
  * `query-docs`: Query the up-to-date documentation and code examples using the resolved ID.

### 3. Developed MCP Server Templates
Sources for additional custom servers are present in the codebase at `sandbox/mcp-servers-src/src/`, including templates for `everything`, `fetch`, `filesystem`, `git`, `memory`, `sequentialthinking`, and `time`.

---

## 4. Available System Tools on MIDGARD

The availability of system tools has been verified via virtual environment paths (`.venv/bin/`), repository metadata, and project task configurations (`justfile`).

| Tool | Status | Path | Verification Details |
| :--- | :--- | :--- | :--- |
| **python3** | **Active** | `/home/lord-mahonheim/bifrost/tesla/.venv/bin/python3` | System Python 3.12 verified in virtual environment. Used directly for hybrid indexing. |
| **git** | **Active** | System binary (`/usr/bin/git`) | Verified via local `.git` repository and metadata extraction scripts. Used in `justfile` git assertion rules. |
| **pyright** | **Active** | `/home/lord-mahonheim/bifrost/tesla/.venv/bin/pyright` | Present in virtualenv. Configured as part of Pyright LSP through `karellen-lsp-mcp` for closed-loop self-healing. |
| **semgrep** | **Planned (M2)** | Unverified | Not present in local `.venv/bin/`. Listed as a core dependency for the `tesla-code-auditor` planned in Milestone 2. |
| **mypy** | **Inactive** | N/A | Not found in local virtualenv; codebase validation relies on Ruff (linter) and Pyright (LSP). |

*Note on command execution constraint:* Global system binary paths could not be verified via shell command invocation (`which`) due to interactive permission timeouts. However, localized venv paths, `justfile` commands, and local git configurations confirm active availability for `python3`, `git`, and `pyright`.

---

## 5. Existing Python & Shell Wrappers

The codebase features several utility wrappers that encapsulate external binary executions.

### 1. Git Wrapper (`get_git_info`)
* **File:** `/home/lord-mahonheim/bifrost/tesla/memory/update_session_history.py`
* **Mechanism:** Subprocess execution of git queries:
  * `git rev-parse --abbrev-ref HEAD`
  * `git log -1 --oneline`
  * `git status --porcelain`
* **Purpose:** Resiliently extracts git metadata (active branch, commit hash, local status) under sandboxing or execution failures.

### 2. Task Orchestrator (`justfile`)
* **File:** `/home/lord-mahonheim/bifrost/tesla/justfile`
* **Mechanism:** Standard `just` task runner encapsulating tool calls:
  * `ruff` for python syntax and formatting check.
  * `biome` for JS/TS/CSS/JSON formatting and checking.
  * `deno` for isolated JS/TS runtime sandboxing.
  * `wasmtime` for executing WASM binaries.
  * `tree-sitter` for structural file AST parsing.

### 3. Planned Wrappers (Milestone 2 - `tesla-code-auditor`)
The design documents identify the following wrappers to be built in Milestone 2:
* `scripts/semgrep_audit.py`: Python wrapper around `semgrep scan` to produce JSON/Markdown reports.
* `scripts/pyright_audit.py`: Python wrapper around `pyright` type checks.
* `scripts/smoke_test_runner.py`: Orchestrator for sandbox test scripts.
* `scripts/policy_engine.py`: Validator for style and architecture rules.
* `scripts/code_auditor.py`: Consolidates the multi-validator chain.

---

## 6. Governance Framework & FORCE_TOOLING Rules

The operational behavior of the agent is strictly constrained by two core files.

### 1. `AGENTS.md` (Version 4 - Canonical)
* **Separation of Concerns:** Imposes clear boundaries between SOUL (Identity), ENGINE (Reasoning), AGENTS (Orchestration), Skills (Expertise), MCP (Connectivity), and Tools (Execution).
* **Rule N°4 (Absolute Delegation):** Tesla must delegate specialized tasks to subagents (`invoke_subagent` or `define_subagent`) rather than re-implementing logic.
* **Système de Gestion de Chantiers (SGC):** Governs project creation, caching, Obsidian indexing, and central board updates in `Gestion-de-Chantiers/`.
* **Sync Rule (MVP-GITHUB):** Mandates sequential copy, commit, and push actions between local folders and the public `MVP-GITHUB/` repository.
* **Open-Items tracking:** Requires recording incomplete items in `OUTPUTS/open_items_todo-Updated.md`.

### 2. `FORCE_TOOLING.md` (Version 1.0.0 - Canonical)
* **Capability Discovery first:** No orchestration allowed without prior discovery of documents, skills, MCPs, and tools.
* **Selection Policy:** Evaluates options on security, cost, reliability, and cognitive economy. Always selects the simplest option.
* **Lifecycle State Machine:** Governs progression of capabilities through Draft $\rightarrow$ Experimental $\rightarrow$ Validated $\rightarrow$ Stable $\rightarrow$ Deprecated $\rightarrow$ Archived.
* **User Escalation:** Mandates explicit authorization for destructive actions or where options have divergent consequences.

### 3. `GEMINI.md` Rules
* **Low-Code Rule:** Optimize the existing environment first. Writing scripts is a last resort.
* **Anti-Lecture Linéaire:** Restricts full linear text reads. Prompts must use `rg`, `jq`, or AST parsers.
* **Anti-Hallucination/Self-Healing:** All Python code must be checked by the Pyright language server via `karellen-lsp-mcp` before being executed or committed.
