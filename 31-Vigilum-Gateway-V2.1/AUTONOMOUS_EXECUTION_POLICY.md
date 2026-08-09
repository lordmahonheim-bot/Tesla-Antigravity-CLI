![Status](https://img.shields.io/badge/Status-MVP-blue) ![Ecosystem](https://img.shields.io/badge/Ecosystem-TESLA%20ANTIGRAVITY-purple) ![Security](https://img.shields.io/badge/Security-ID%20LOCKED-red) ![Python](https://img.shields.io/badge/Python-3.12+-blue)

# AUTONOMOUS EXECUTION POLICY (Mode `/goal`)

This policy governs the behavior of the Orchestrator (Tesla) and all instantiated sub-agents when the `/goal` directive is activated. It aims to guarantee the total autonomy of agents by eliminating authorization deadlocks while preserving *Zero Trust* and the *Vigilum Codex*.

## 1. Pre-Authorized Workspace Perimeter
In `/goal` mode, the Antigravity system implicitly considers the following paths to be under an **`Allow`** policy by default:
- `/home/lord-mahonheim/bifrost/tesla/MVP-GITHUB/*`
- `/home/lord-mahonheim/bifrost/tesla/OUTPUTS/*`
- `/home/lord-mahonheim/bifrost/tesla/memory/*`
- `/home/lord-mahonheim/bifrost/tesla/.agents/skills/*`

The operations `write_file`, `read_file`, `mkdir`, `cp`, and `mv` are authorized within these paths without human intervention.

## 2. The "No-Ask" Rule
In accordance with Rule No. 4.1 of `AGENTS.md`:
Sub-agents are **strictly prohibited** from using the `ask_permission` tool under `/goal`.
If a required operation falls outside the pre-authorized workspace perimeter, the sub-agent must not force execution. Instead, it must use **Execution Delegation via Artifact** (Rule 7.2) and submit a formal request to the Orchestrator in `/OUTPUTS`.

## 3. Safeguards & Absolute Exceptions (Never Approved)
Even in `/goal` mode, the following actions are **NEVER** pre-authorized and require direct escalation or validation from Lord Mahonheim:
- **Remote Push:** Execution of `git push` to `origin` remains locked by Rule 7 of `AGENTS.md`.
- **Mass Destruction:** Commands such as `rm -rf /` or global deletion of root folders.
- **Privilege Escalation:** Any command involving `sudo`.
- **Exfiltration:** Non-whitelisted network requests risking the exposure of environment variables.

## 4. Activation
The activation of autonomous mode is triggered by the presence of the `/goal` command in Lord Mahonheim's prompt. At this moment, the Orchestrator shifts into `Autonomous Tier` and enforces this policy across the entire delegation chain.
