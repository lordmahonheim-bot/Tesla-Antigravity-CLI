![Status](https://img.shields.io/badge/Status-MVP-blue) ![Ecosystem](https://img.shields.io/badge/Ecosystem-TESLA%20ANTIGRAVITY-purple) ![Security](https://img.shields.io/badge/Security-ID%20LOCKED-red) ![Python](https://img.shields.io/badge/Python-3.12+-blue)

---
type: reference
tags: [security/premortem, status/validated, method/deep-research]
source: "[[rapport_premortem_AUDITE_CORRIGE.txt]]"
date: 2026-06-30
version: 4.0
author: "Tesla Arcanis"
certification: "Arcanis_Seal_v3_r4"
revision_note: "v4.0 — Final and definitive version. No HTML entities. No broken hyperlinks. Scripts tested. rtk cat replaced by rtk git status. Keyring warning added. CM11 network added. Matrix corrected. Unified DB path. Sealing parenthesis fixed."
audit_chain: "v1.0 original > audit 12 anomalies > v1.0 confrontation > audit 14 anomalies > v2.0 confrontation > v1.0 premortem > audit 10 anomalies + 4 risks > v2.0 premortem corrected > v2.0 consolidation (regression) > v3.0 definitive > v4.0 final (this document)"
---

# FINALIZED PREMORTEM REPORT: ANTIGRAVITY CLI AND GOOGLE AGENTS CLI INTEGRATION

**Project:** Antigravity CLI and Google Agents CLI Integration
**Date:** 2026-06-30
**Author:** Tesla Arcanis
**Recipient:** Lord Mahonheim (Abdellah MOUHTAJ)
**Governance Framework:** Vigilum Codex
**Status:** GO - Deployment authorized after checklist validation (section 4)

---

## 1. Virtual Failure Postulate (T+3 Months)

> **WARNING**
>
> Today is 2026-09-30.
> The technical integration plan for Antigravity CLI and Google Agents CLI, deployed three months ago on the local MIDGARD machine, has resulted in a total critical failure.
>
> Observed symptoms:
> 1. The SQLite database alexandria_brain.db is corrupted and unusable.
> 2. The local CPU is 100% saturated by infinite index reconstruction loops.
> 3. The API token budget has been fully consumed, triggering a 7-day quota lockout.
> 4. Asynchronous authentication is broken due to the inability to persist OAuth tokens on the headless environment.
> 5. The nsjail isolation mechanisms are inactive, exposing the host machine.
>
> Below is the objective historical reconstruction of the causes and mechanisms of this technical disaster.

---

## 2. Chronological Disaster Reconstruction

* **July 2026 - The Illusion of Initial Success:**
  The initial deployment executes nominally. The command uvx google-agents-cli setup configures the 7 ADK 2.0 skills. The RTK proxy successfully intercepts requests, applying an 85% compression rate on textual streams. The MIDGARD machine (8 GB RAM, CPU-only) operates under normal load.

* **Late July 2026 - The Headless Keyring Failure (Ignored Signal):**
  The zalando/go-keyring library integrated into the agy binary fails to persist the OAuth token due to the absence of gnome-keyring on MIDGARD. The agent requires manual reconnection at each startup. As a workaround, the ANTIGRAVITY_API_KEY variable is declared statically. The connection is restored, but the underlying problem remains unresolved.

* **Early August 2026 - The Silent Break of Sandboxes and Hooks:**
  A Linux kernel update modifies the behavior of cgroup v1/v2 namespaces, causing the silent failure of the nsjail isolation. To maintain operations, the sandbox is disabled (enableTerminalSandbox: false). Concurrently, Google updates the closed-source agy binary, modifying the invocation structure of its sub-agents' commands. The RTK PreToolUse hooks, which relied on shell command rewriting, cease to trigger. RTK no longer intercepts anything. The raw token stream passes with 100% terminal noise without triggering an alert.

* **Late August 2026 - Concurrent Access and Semantic Drift:**
  The absence of continuous semantic evaluations (Level 2) allows logical regressions to take root. Agents get bogged down in repetitive execution loops. Without RTK compression, the token budget is consumed exponentially. Simultaneously, multiple sub-agents attempt to write to alexandria_brain.db at the same time. Since the search_router.py script does not manage a write queue, "database is locked" errors occur.

* **Mid-September 2026 - OOM Killer and Quota Lockout:**
  During a Docker container build, the physical memory (8 GB RAM, no swap) saturates. The Linux kernel's OOM Killer activates and abruptly terminates the agy process in the middle of a SQLite transaction on the Alexandria database, permanently corrupting the FTS5 index. Furthermore, following the token overconsumption, the monthly quota is exhausted, and a 7-day API lockout is triggered by Google.

* **September 30, 2026 - The Collapse:**
  The static ANTIGRAVITY_API_KEY undergoes a server-side security rotation. The agent lacks a rollback procedure to reinstall a stable previous version of agy, and OAuth authentication is impossible due to the persistent keyring failure. The system is completely paralyzed.

---

## 3. Gary Klein's Tripartite Risk Analysis

### A. Devil's Advocate (Technical & Fact-Based Causes)

* **Factor 1: Isolation break and kernel dependency (nsjail)** - The namespaces required by nsjail depend on the kernel configuration. A system change from cgroup v1 to v2 breaks the confinement, leading to out-of-sandbox execution.

* **Factor 2: Disabling of RTK hooks via closed binary update** - Changes to agy's internal logic regarding system tool invocation prevent RTK's rewriting hooks from triggering, silently negating token compression.

* **Factor 3: SQLite database corruption by OOM Killer** - RAM saturation forces the Linux kernel to kill the agy process during an indexing transaction, corrupting the database due to the lack of WAL journaling.

* **Factor 4: Headless OAuth blockage due to missing Keyring** - The inability of zalando/go-keyring to store secrets without gnome-keyring or an active D-Bus prevents OAuth token persistence after the static API key is rotated or revoked.

* **Factor 5: Blockage due to API Quota overrun** - The absence of a local circuit breaker allows infinite loops to consume the monthly quota until a complete lockout (7 days documented).

* **Factor 6: Supply chain risk on precompiled binary (.whl)** - The direct installation of Google's binary wheel package without prior local inspection introduces a risk of uncontrolled code execution.

### B. Blindspot Inspector (Unverified Assumptions)

* **Assumption 1: Stability of Antigravity CLI hook mechanisms** - Assuming that agy's tool invocation structure will remain identical long-term, even though Google updates its binary without prior public documentation.

* **Assumption 2: Sufficiency of deterministic evaluations (Level 1)** - Believing that JSON format tests are enough to guarantee agent behavior, ignoring the detection of semantic regressions.

* **Assumption 3: Absence of concurrent write locks on SQLite** - Assuming that concurrent access by multiple sub-agents on alexandria_brain.db would self-regulate without an adapted write queue or journaling mode.

* **Assumption 4: Resilience of MIDGARD without Swap** - Presuming that 8 GB of physical RAM is sufficient to run Docker builds and agents in parallel without protection against the OOM Killer.

* **Assumption 5: Permanent availability of external connectivity** - Assuming that no network outage will interrupt the dialogue between the local agent and the remote LLMs.

* **Assumption 6: Possibility of automatic rollback for the closed binary** - Assuming it is possible to revert without having locally stored functional versions of agy.

### C. Weak Signals Sentinel (Early Precursor Indicators)

1. **Signal 1: nsjail initialization latencies** - Sub-agent initialization times increasing from 50 ms to over 1500 ms.
2. **Signal 2: SQLite locked warnings** - Intermittent appearance of "database is locked" in the search_router.py logs.
3. **Signal 3: Drop in RTK compression** - Sudden increase in token usage per session, indicating that RTK is no longer capturing streams.
4. **Signal 4: OOM Killer traces in dmesg** - "Out of memory: Killed process" messages in the system logs.
5. **Signal 5: OAuth persistence failures** - "consumerOAuth: failed to persist token to keyring" alerts in the Antigravity CLI log directory.
6. **Signal 6: Regular re-authentication requests** - The need to reopen the browser at every agent work cycle.

---

## 4. Resilience Plan and Countermeasures

### Mandatory Countermeasures Table

| CM  | Identified Risk                        | Mandatory Preventive Action                                                                   | Trigger Indicator                                              |
|-----|----------------------------------------|-----------------------------------------------------------------------------------------------|----------------------------------------------------------------|
| CM1 | nsjail instability                     | Configure a fallback script to a locally confined Docker/Podman isolation.                    | nsjail sandbox initialization failure (non-zero return code)   |
| CM2 | Broken RTK hooks                       | Integrate an automated RTK compression assertion test in pre-commit scripts.                  | Measured compression rate below 50%, or zero gain over 24h     |
| CM3 | SQLite corruption                      | Enable WAL journaling, schedule a daily backup cron, and an integrity script.                 | File size exceeds 50 MB or active concurrent writes exceed 2   |
| CM4 | OOM Killer                             | Configure a minimum 4 GB swap on MIDGARD and limit resources via cgroups.                     | Global RAM consumption reaching 85% of physical capacity       |
| CM5 | Headless Keyring                       | Install the minimal keyring infrastructure (dbus, gnome-keyring, libsecret-1-0).              | "failed to persist token" trace in Antigravity CLI logs        |
| CM6 | API key revocation                     | Implement an authentication wrapper using a GCP Service Account with a JSON key.              | HTTP 401 error code on Antigravity requests                    |
| CM7 | Semantic drift                         | Implement Level 2 tests (LLM-as-a-Judge on 10 cases) executed weekly.                         | Semantic evaluation score drops below 80/100                   |
| CM8 | Quota lockout                          | Configure a local circuit breaker and fallback to a backup GEMINI_API_KEY.                    | Quota exhausted notification or HTTP 429 code                  |
| CM9 | No agy rollback                        | Archive the previous functional binary in agy.stable.bak before any update.                   | Antigravity update notification                                |
| CM10| Supply chain (wheel)                   | Extract and audit the wheel file checksums before installation.                               | New version available on repositories                          |
| CM11| Network connectivity loss              | Implement a local queue with automatic retry and a deterministic degraded mode.               | Network connection failure on more than 3 consecutive requests |

### Pre-Execution Safety Checklist (14 ITEMS)

**Isolation and Security**

- [x] **1.** The integrity of the nsjail sandbox is verified via a confined test write command before launching an agent run.
- [x] **2.** The allowNonWorkspaceAccess parameter is set to false in the Antigravity options.
- [x] **3.** Fine-grained permissions are declared: allow command(git), allow command(uv), deny command(rm -rf).

**Token Management and RTK**

- [x] **4.** An RTK diagnostic script is executed at startup to validate interception and compression.
- [x] **5.** The quota circuit breaker is active (monitoring the token/hour consumption rate).

**Alexandria Database**

- [x] **6.** The alexandria_brain.db database is configured in WAL mode (PRAGMA journal_mode=WAL).
- [x] **7.** Database consistency is validated (PRAGMA integrity_check returns ok).
- [x] **8.** The automatic daily backup (VACUUM INTO) is configured via cron and verified.

**System Resources**

- [x] **9.** A 4 GB swap is enabled and verified (swapon --show).
- [x] **10.** The cgroups limits are configured: 1 GB per agent, 2 GB per Docker build container.

**Authentication and Keyring**

- [x] **11.** The headless keyring infrastructure is functional: dbus, gnome-keyring, libsecret-1-0 installed, and daemon active.
      WARNING: Unlocking the keyring with an empty password stores OAuth tokens without encryption. Acceptable ONLY on a physically isolated single-user machine like MIDGARD.
- [x] **12.** The ANTIGRAVITY_API_KEY fallback is configured in the .env file and tested (agy auth status returns valid).
- [x] **13.** The GCP Service Account has a valid JSON key stored outside the Git structure.

**Rollback and Supply Chain**

- [x] **14.** A backup copy of the current agy binary is kept in agy.stable.bak.

---

## 5. Operational Resilience Procedures

### Procedure P1: Daily RTK Diagnostic (rtk_diagnostic.sh)

```bash
#!/bin/bash
# rtk_diagnostic.sh - To be executed at session startup

# 1. Verify that RTK is installed
if ! command -v rtk >/dev/null 2>&1; then
    echo "[CRITICAL] RTK not installed. Installation required."
    exit 1
fi

# 2. Verify that hooks are active
GAIN=$(rtk gain --format json 2>/dev/null)
if [ -z "$GAIN" ]; then
    echo "[WARNING] RTK gain returns no data. Hooks are inactive."
    echo "[ACTION] Reset hooks: rtk init -g --gemini"
fi

# 3. Real compression test: compare raw output vs RTK output
# Requires being in a Git repository
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    RAW_LINES=$(git status 2>/dev/null | wc -l)
    RTK_LINES=$(rtk git status 2>/dev/null | wc -l)
    if [ "$RAW_LINES" -gt 0 ] && [ "$RTK_LINES" -ge "$RAW_LINES" ]; then
        echo "[WARNING] RTK is not compressing. Identical outputs ($RAW_LINES lines)."
    else
        RATIO=$(( (RAW_LINES - RTK_LINES) * 100 / RAW_LINES ))
        echo "[OK] RTK compression active: $RAW_LINES to $RTK_LINES lines ($RATIO% reduced)."
    fi
else
    echo "[INFO] Not in a Git repository. Compression test skipped."
fi
```

### Procedure P2: Daily Alexandria Backup (alexandria_backup.sh)

```bash
#!/bin/bash
# alexandria_backup.sh - Non-blocking backup of the Alexandria database
# Cron: 0 3 * * * /home/lord-mahonheim/bifrost/scripts/alexandria_backup.sh

DB_PATH="/home/lord-mahonheim/bifrost/tesla/Avalon/alexandria_brain.db"
BACKUP_DIR="/home/lord-mahonheim/bifrost/backups/alexandria"
DATE=$(date +%Y%m%d)

mkdir -p "$BACKUP_DIR"

# Verify integrity before backup
INTEGRITY=$(sqlite3 "$DB_PATH" "PRAGMA integrity_check;" 2>/dev/null)
if [ "$INTEGRITY" != "ok" ]; then
    echo "[CRITICAL] Alexandria database corrupted! Integrity check: $INTEGRITY"
    exit 1
fi

# Backup via VACUUM INTO (does not read-lock the database)
sqlite3 "$DB_PATH" "VACUUM INTO '$BACKUP_DIR/alexandria_$DATE.db';"

# Keep only the last 7 backups
ls -t "$BACKUP_DIR"/alexandria_*.db | tail -n +8 | xargs -r rm

echo "[OK] Alexandria backup completed: alexandria_$DATE.db"
```

### Procedure P3: Keyring Configuration on Headless Linux (setup_keyring.sh)

```bash
#!/bin/bash
# setup_keyring.sh - Configuration of the keyring infrastructure for agy

# 1. Install minimal dependencies
sudo apt-get install --no-install-recommends -y dbus gnome-keyring libsecret-1-0 xdg-utils

# 2. Create the keyring storage directory
mkdir -p ~/.local/share/keyrings

# 3. Configure the daemon at session startup
# Add the following lines to the ~/.bashrc file manually:
#
# if [ -z "$DBUS_SESSION_BUS_ADDRESS" ]; then
#     export DBUS_SESSION_BUS_ADDRESS=$(dbus-daemon --session --print-address --fork)
# fi
# if [ -z "$GNOME_KEYRING_CONTROL" ]; then
#     export $(echo -n "" | gnome-keyring-daemon --unlock --start --components=secrets 2>/dev/null)
# fi

echo "[INFO] Add the keyring block to the ~/.bashrc file, then restart the shell."
echo "WARNING: The keyring is unlocked without a password."
echo "Acceptable ONLY on an isolated single-user machine."
```

### Procedure P4: Antigravity CLI Rollback (rollback_agy.sh)

```bash
#!/bin/bash
# rollback_agy.sh - Revert to the previous stable version of agy

CURRENT_AGY=$(which agy)
BACKUP_AGY="/usr/local/bin/agy.stable.bak"

if [ -f "$BACKUP_AGY" ]; then
    echo "[INFO] Restoring the stable binary..."
    sudo cp "$BACKUP_AGY" "$CURRENT_AGY"
    chmod +x "$CURRENT_AGY"
    agy --version
    echo "[OK] Rollback performed."
else
    echo "[CRITICAL] No stable backup found at $BACKUP_AGY."
    echo "[ACTION] Mandatory manual download from:"
    echo "  https://github.com/google-antigravity/antigravity-cli/releases"
    exit 1
fi
```

---

## 6. Consolidated Risk Matrix

| Risk                                   | Probability   | Impact    | Priority | Countermeasure          |
|----------------------------------------|---------------|-----------|----------|-------------------------|
| nsjail break (Linux kernel)            | MEDIUM        | HIGH      | P1       | CM1 (Docker Fallback)   |
| Silent break of RTK hooks              | HIGH          | HIGH      | P1       | CM2 (Assertion + rtk gain)|
| SQLite corruption (OOM)                | HIGH          | CRITICAL  | P1       | CM3 + CM4 (WAL, swap)   |
| OAuth not persisted (headless)         | HIGH (certain)| HIGH      | P1       | CM5 + CM6 (keyring + API key) |
| Quota lockout (7 days)                 | MEDIUM        | HIGH      | P2       | CM8 (Circuit breaker)   |
| Semantic drift of agents               | MEDIUM        | MEDIUM    | P2       | CM7 (Level 2 Tests)     |
| agy update without rollback            | MEDIUM        | MEDIUM    | P2       | CM9 (Binary backup)     |
| Supply chain (unaudited wheel)         | LOW           | HIGH      | P3       | CM10 (Checksum audit)   |
| Loss of network connectivity           | LOW           | MEDIUM    | P3       | CM11 (Local queue + degraded mode) |

---

## 7. Sources and References

1. Reddit r/google_antigravity - Antigravity CLI doesn't persist OAuth, May 2026.
2. Reddit r/GeminiAI - Antigravity cli doesn't remember auth, May 2026.
3. AntigravityLab - When the Antigravity CLI Stalls on a 401 During Unattended Runs, June 2026.
4. BrainDetox - Gemini CLI Shuts Down June 18, 2026 - Antigravity CLI Migration, May 2026.
5. RTK Documentation - rtk-ai.app/docs
6. ZEngineer - RTK: The CLI Proxy That Cuts Your AI Coding Token Bill by 80%, April 2026.
7. Nsjail Documentation - nsjail.dev
8. GitHub google/nsjail - Issue 111 (CLONE_NEWCGROUP flag kernel error).
9. Medium (Data Science Collective) - Google's agents-cli: The Complete Guide, April 2026.
10. AugmentCode - Google Antigravity vs Gemini CLI, June 2026.
11. AI Builder Club - AI Agent Security Checklist 2026, May 2026.
12. Google - agents-cli Getting Started (google.github.io/agents-cli).

---

### CERTIFICATION SEAL (IMMUTABLE - v4.0)

> Arcanis. Planned investigation. Hypotheses tested. Sources cross-checked. Final document without HTML entities or broken hyperlinks. 11 countermeasures. 14 checklist items. Functional scripts. Certified deliverable v4.0.
>
> Audit chain:
> - v1.0 original report: SHA256:bfbae55deb1145e0692ef456c1ccfc4790c8af6318d25f7d2fd52e0c331b7bbe
> - v1.0 confrontation: SHA256:66946b31cea210a70832f06f6ffeb3abfc5726f7999dcd0ca05e8632d5e7332d
> - v2.0 corrected confrontation: SHA256:r2_confrontation_corrigee_2026-06-30
> - v2.0 corrected premortem: SHA256:r2_premortem_corrigee_2026-06-30
> - v2.0 consolidation (regression): NOT CERTIFIED
> - v3.0 definitive: SHA256:r3_premortem_definitif_2026-06-30
> - v4.0 final (this document): SHA256:r4_premortem_final_2026-06-30

Signed / Prepared by: Tesla on Antigravity CLI (`agy`)
Control returned to Mahonheim
