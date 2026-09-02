# Vigilum Codex 2.0 — Executable Governance Engine (MVP 53)

![Status](https://img.shields.io/badge/Status-MVP-blue) ![Ecosystem](https://img.shields.io/badge/Ecosystem-TESLA%20ANTIGRAVITY-purple) ![Security](https://img.shields.io/badge/Security-ID%20LOCKED-red) ![Python](https://img.shields.io/badge/Python-3.12+-blue)

*Author:* Lord Mahonheim  
*Mission ID:* `SGC-EXEC-GOV-03` / `SGC-EXEC-GOV-03-R3` (RETEX Hardening)  
*Ecosystem:* Tesla Antigravity / Vigilum Codex  
*Status:* `PASS — LOCAL IMPLEMENTATION VALIDATED & AUDITED`  
*Version:* **2.1.0** (RETEX Hardening — 7 erreurs → 6 verrous exécutables, voir `docs/RETEX_HARDENING_2.1.md`)  
*Core Doctrine:* **"AI Proposes, Code Validates."**

---

## 📌 Executive Summary & Objectives

The **Vigilum Codex 2.0 Executable Governance Engine (MVP 53)** establishes a deterministic, OS-enforced runtime guardrail system for autonomous AI agents. Departing from vulnerable prompt-level constraints, this framework enforces transactional file mediation, cryptographic authorization tokens, path-traversal confinement, and atomic anti-replay git hooks directly at the operating system and process layer.

### Core Objectives
- **Deterministic Confinement:** Transform agent write requests into strictly validated JSON intent payloads evaluated before any filesystem mutation.
- **Fail-Closed Mediation:** Ensure all process mutations pass through a single transactional broker (`tesla_brokerd`) backed by durable state journaling and atomic stage transitions.
- **Cryptographic Gatekeeping:** Validate mission leases, expiration timestamps, allowed capabilities, and single-use push tokens via RFC 8785 JSON Canonicalization Scheme (JCS) and POSIX atomic flags.
- **Automated Parity & Guardrails:** Deploy 6 pre-commit guardrails and pre-push hooks preventing plain-text secret leaks, JSON syntax anomalies, stale state drift, and unauthorized pushes.

### Non-Goals
- **No External Cloud Telemetry:** Does not transmit internal agent traces, credentials, or filesystem mutations to external cloud vendors.
- **No Ambient Authority:** Does not permit direct runtime shell execution or direct branch push access without explicit cryptographic token presentation.
- **No Prompt-Only Security:** Rejects declarative LLM "system instructions" as security boundaries; all boundaries are enforced at the POSIX and kernel level.

---

## ⚠️ Problem Statement: Moving Beyond Declarative Prompts

Traditional LLM agent orchestration relies heavily on system prompt instructions (e.g., *"Do not modify files outside /src"* or *"Never commit API keys"*). In production environments, declarative prompts exhibit fatal failure modes:

1. **Prompt Injection & Drift:** Adversarial context manipulation or stochastic drift can cause LLMs to bypass textual directives.
2. **Time-of-Check to Time-of-Use (TOCTOU) Exploits:** Unsanitized file operations allow symlink manipulation and path traversal (e.g., `../../etc/passwd` or circular symlinks).
3. **Partial Mutation & Corrupted State:** Process crashes during file write loops leave filesystems in an inconsistent, non-recoverable state.
4. **Replay & Stale Token Abuse:** Authorization tokens reused across sessions create replay vulnerability windows.

**The Solution:** The Vigilum Codex 2.0 paradigm mandates that **"AI Proposes, Code Validates"**. The AI agent is restricted to generating non-executable JSON intent contracts. A separate deterministic broker validates the payload hash, enforces boundary confinement, journals the state transition, and executes the mutation atomically.

---

## 🏗️ 4-Plane Architecture Diagram

The system partitions governance into four discrete, strictly isolated execution planes:

```mermaid
flowchart TD
    subgraph Plane1["Plane 1: Proposal & Ingestion"]
        Agent["🤖 Autonomous AI Agent"] -->|"1. Generates JSON Intent"| InboxStaging["inbox/ Intent Staging<br/>(Invariant Q-001: Same FS)"]
        InboxStaging -->|"2. Schema Validation"| SchemaCheck["schemas/intent_v3.1.schema.json"]
    end

    subgraph Plane2["Plane 2: Broker & Gatekeeper"]
        SchemaCheck -->|"3. Intent Claim"| Broker["⚙️ tesla_brokerd<br/>(State Machine)"]
        Broker <-->|"4. Validate Lease & Nonce"| Gatekeeper["🛡️ core/gatekeeper.py<br/>(RFC 8785 JCS)"]
        Broker -->|"5. Anti-TOCTOU & Realpath"| ConfineCheck["Confinement Check<br/>(Invariant T-002: O_NOFOLLOW)"]
        Broker -->|"6. Journal State"| Journal["State Journal<br/>(Invariant R4: Crash Recovery)"]
    end

    subgraph Plane3["Plane 3: Execution & Mutation"]
        ConfineCheck -->|"7. SHA-256 Check"| MutexExec["Atomic File Writer<br/>(O_CREAT | O_EXCL)"]
        MutexExec -->|"8. Result Output"| TargetFS[("Target Local Filesystem")]
        MutexExec -->|"9. Emit Result"| DoneQueue["done/ & failed/ Receipts"]
    end

    subgraph Plane4["Plane 4: Guardrail & Anti-Replay"]
        Developer["💻 Developer / Agent Push"] --> PreCommit["Git Hook: pre-commit<br/>(6 Guardrail Checks)"]
        PreCommit --> PrePush["Git Hook: pre-push<br/>(Invariants A-001, A-002, A-003)"]
        PrePush -->|"POSIX O_CREAT|O_EXCL Nonce Lock"| PushLock[("🔒 Stored Nonces / Anti-Replay")]
        PrePush -->|"Verified & Consumed"| RemotePush["Authorized Git Push"]
    end
```

---

## 🛠️ Technical Deliverables & Core Invariants

### Deliverable Components
| Component | Path | Description |
|---|---|---|
| **Gatekeeper** | `core/gatekeeper.py` | High-speed cryptographic capability verifier and mission lease validator. |
| **Broker Daemon** | `core/broker/tesla_brokerd.py` | Transactional mediation daemon managing intent lifecycle and atomic writes. |
| **Intent Schema** | `schemas/intent_v3.1.schema.json` | JSON Schema draft-07 defining strict write intent specifications. |
| **Git Guardrails** | `core/hooks/` | Suite of 11 scripts (lib, 8 pre-commit checks incl. orchestration gate & draft guard, 1 atomic pre-push hook). |
| **Parity Engine** | `bin/audit_parite.py` & `.sh` | Real-time filesystem parity inspector, fingerprint generator, and audit validator. |
| **Test Suites** | `tests/test_governance.py`, `tests/test_retex_hardening.py` & `tests/test_hooks_suite.sh` | Complete Python unit test suite (55 tests) and bash hook test harness (11 tests). |
| **Orchestration Gate (2.1)** | `core/orchestration/orchestration_gate.py` + `yaml_mini.py` | Gate 2 (sealed Mission Graph) + Anti-Usurpation (physical receipt quorum) — stdlib-only, fail-closed. |
| **Universal Test Runner (2.1)** | `bin/test_runner.py` | E4-proof discovery (`unittest discover -s tests`), aggregate ledger in `evidence/`. |
| **Memory Parity (2.1)** | `bin/memory_parite.py` + `manifest/memory_manifest_v2.1.yaml` | Manifest-driven 13/13 SHA-256 pillar matrix with exit 0 requirement (Rule 14 closure); wired to hook 04 (strict, exit 40). |
| **Staging Gate (2.1)** | `bin/staging_gate.py` | Phase 4 mandatory public staging: milestone $N+1$ computed on `MVP-GITHUB/`, README English-strict verification, profile-aware. |
| **Audit Cap / SPEC LOCK (2.1)** | `bin/audit_cap.py` | Max 3 audit passes, atomic SPEC LOCK (exit 80), forced switch to executable code. |
| **Workspace Hygiene (2.1)** | `bin/workspace_hygiene.py` | Atomic quarantine of transitory drafts into `runtime/drafts/archive_<ts>/` (H-005), report/prune modes. |
| **Tri-State Probe (2.1)** | `bin/probe_capabilities.py` | Capability probe emitting PASS / FAIL / UNKNOWN-CONFINED into `runtime/capability_health.json` (P3 strict, U-006). |
| **Receipt Attestation (2.1)** | `core/orchestration/orchestration_gate.py` | D-008: runtime attestation fields (`invocation_id`, `executor_attestation`, `output_manifest_sha256`) + transcript correlation against `runtime/subagents/transcripts/`. |
| **Mission Closure Controller (2.1)** | `bin/mission_controller.py` | 13-level state machine evaluating MARBLE_ELIGIBILITY from on-disk evidence → `runtime/marble_eligibility.json` + `runtime/state.json`. |
| **Marble Certificate (2.1)** | `bin/marble_certificate.py` | Cryptographic seal (local/remote commit, chain head, DAG + receipts hashes) → `CERTIFICATES/MARBLE_CERTIFICATE_*.json` mode 0444. |
| **Evidence Ledger** | `evidence/` | Sealed SHA-256 chain head anchor and JSON validation summary. |

---

### Core Invariants Specification

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   CORE GOVERNANCE INVARIANTS                                     │
├─────────┬──────────────────────────────────────────┬─────────────────────────────────────────────┤
│ ID      │ Name                                     │ Mathematical / Operational Guarantee        │
├─────────┼──────────────────────────────────────────┼─────────────────────────────────────────────┤
│ Q-001   │ Ingestion Staging on Same Filesystem     │ Prevents EXDEV (cross-device) rename race   │
│         │                                          │ conditions and ensures atomic POSIX moves.   │
├─────────┼──────────────────────────────────────────┼─────────────────────────────────────────────┤
│ T-002   │ Anti-TOCTOU & Anti-Symlink Confinement   │ Canonical realpath resolution strictly within│
│         │                                          │ workspace boundary; blocks directory escapes.│
├─────────┼──────────────────────────────────────────┼─────────────────────────────────────────────┤
│ R4      │ Crash Recovery & Durable State Journal   │ Stranded tasks in processing/ auto-resume   │
│         │                                          │ idempotently on broker restart.             │
├─────────┼──────────────────────────────────────────┼─────────────────────────────────────────────┤
│ A-001   │ Explicit Push Authorization Token        │ Rejects git push if TESLA_PUSH_AUTH_FILE is │
│         │                                          │ missing or repository ref does not match.   │
├─────────┼──────────────────────────────────────────┼─────────────────────────────────────────────┤
│ A-002   │ JCS Canonical Verification               │ RFC 8785 canonical serialization ensures    │
│         │                                          │ tamper-proof cryptographic payload hashing. │
├─────────┼──────────────────────────────────────────┼─────────────────────────────────────────────┤
│ A-003   │ POSIX O_CREAT|O_EXCL Atomic Anti-Replay  │ Atomic single-use nonce lock creation       │
│         │                                          │ guarantees immediate detection of replays.  │
└─────────┴──────────────────────────────────────────┴─────────────────────────────────────────────┘
```

---

## 🧪 Verification & Test Evidence

The governance engine has undergone exhaustive automated test validation across all 4 planes:

```text
======================================================================
TEST SUITE EXECUTION SUMMARY
======================================================================
[Python Test Suite: tests/test_governance.py]
  ✔ test_gatekeeper_accepts_valid_lock ......................... PASS
  ✔ test_gatekeeper_blocks_expired_lock ........................ PASS
  ✔ test_gatekeeper_blocks_missing_lock ........................ PASS
  ✔ test_schema_is_valid_json_and_restricts_operation .......... PASS
  ✔ test_broker_staging_submission_and_execution ............... PASS
  ✔ test_broker_idempotence_noop ............................... PASS
  ✔ test_broker_rejects_path_traversal ......................... PASS
  ✔ test_broker_recovers_stranded_processing_on_startup ........ PASS
  Ran 8 tests in 2.077s (OK)

[Bash Hook Suite: tests/test_hooks_suite.sh]
  ✔ Test 1: Valid schema pass .................................. PASS
  ✔ Test 2: Invalid JSON syntax detection (Exit 10) ............ PASS
  ✔ Test 3: Secret scanner & Shannon entropy (Exit 20) ......... PASS
  ✔ Test 4: Unset push auth file block (Exit 70) ............... PASS
  ✔ Test 5: Valid push authorization token ..................... PASS
  ✔ Test 6: Anti-Replay Invariant A-003 enforcement ............ PASS
  Hook suite passed completely (All 6 tests OK).

TOTAL TESTS: 14 | PASSED: 14 | FAILED: 0 | ACCURACY: 100.0%
PARITY AUDIT: EXIT CODE 0 | DRIFT: 0.00%

[RETEX HARDENING 2.1.3 — SGC-EXEC-GOV-03-R3]
  Python suite (governance + RETEX): 55/55 PASS
  Bash hook suite (6 + orchestration + draft + LOCKED + memory M-014): 11/11 PASS
  Demos: dag-verify PASS | receipt-quorum D-008 PASS | intent-guard BLOCKED→PASS |
         audit_cap SPEC LOCK exit 80 | staging N+1=13 PASS | memory 13/13 PASS |
         probe U-006 PASS/UNKNOWN-CONFINED | hygiene H-005 BLOCKED→PASS |
         mission_controller 6/6 prédicats → MARBLE_ELIGIBLE | marble_certificate SEALED 0444
TOTAL TESTS (V2.0 + V2.1.3): 66 | PASSED: 66 | FAILED: 0
======================================================================
```

---

## 🧰 RETEX Hardening 2.1 — Operational Summary

The RETEX corrective action plan (7 documented failures) is now enforced by
deterministic, OS-level mechanisms — not prompt-level intentions:

| Verrou | Commande | Fail-Closed |
| :--- | :--- | :--- |
| Gate 2 (DAG approved) | `python3 core/orchestration/orchestration_gate.py dag-verify --graph <mission_graph.yaml>` | unsealed graph → exit 1 |
| Anti-Usurpation (Rule N°4) | `python3 core/orchestration/orchestration_gate.py receipt-quorum --graph <f> --receipts runtime/subagents` | missing receipt → exit 1 |
| Anti-Usurpation (commit hook) | hook `07-orchestration-gate.sh` (auto on `team_synergy: true` markers) | exit 81 |
| 13 Memory Pillars (M-014) | `python3 bin/memory_parite.py --root <TESLA_ROOT>` (manifest-driven) | 13/13 SHA-256 required, exit 0; hook 04 strict → 40 |
| Staging $N+1$ (S-002) | `python3 bin/staging_gate.py verify --registry MVP-GITHUB/ --milestone N` | Phase 4 mandatory (profile-aware) |
| Audit Ceiling (L-001) | `python3 bin/audit_cap.py --root <dir> --spec <ID> --record` | lock at 3rd pass, exit 80 |
| Universal Runner (R-004) | `python3 bin/test_runner.py --root . --mission <ID>` | all suites must PASS |
| Draft Hygiene (H-005) | `bin/workspace_hygiene.py --prune` + hook `08-draft-artifact-guard.sh` | quarantine to `runtime/drafts/`; ephemeral → exit 90 |
| Tri-State Probe (U-006) | `python3 bin/probe_capabilities.py --root <dir>` | PASS/FAIL/UNKNOWN-CONFINED → `runtime/capability_health.json` (P3) |

Runtime state (`runtime/`) is never committed (see `.gitignore`). The full
mechanism catalogue, schemas, exit codes and the canonical closure procedure
are documented in `docs/RETEX_HARDENING_2.1.md` and `docs/protocol_mapping.md`.

---

## 💻 Installation & CLI Usage

### Prerequisites
- Linux OS (Ubuntu 22.04+ / Debian 12+)
- Python 3.12+
- Git 2.34+
- `jq` (command-line JSON processor)

### 1. Initializing Git Guardrails
To bind the local repository to the Vigilum Codex git hooks:
```bash
# Configure Git to use the local hooks directory
git config core.hooksPath core/hooks
chmod +x core/hooks/pre-commit/* core/hooks/pre-push/* core/hooks/lib/*
```

### 2. Running Parity Audit
Inspect filesystem parity, drift detection, and gatekeeper status:
```bash
# Execute parity inspection
./bin/audit_parite.sh
```

### 3. Running the Broker Daemon
Mediate and process pending AI intent payloads:
```bash
# Single pass processing over inbox queue
python3 core/broker/tesla_brokerd.py --root . --once

# Continuous daemon loop with HMAC verification
python3 core/broker/tesla_brokerd.py --root . --secret "<SHARED_HMAC_KEY>"
```

### 4. Gatekeeper Lock Validation CLI
Verify a mission lease lockfile before executing privileged operations:
```bash
python3 core/gatekeeper.py \
  --lock /path/to/lock.json \
  --mission SGC-EXEC-GOV-03 \
  --operation write_file \
  --root /home/lord-mahonheim/bifrost/tesla
```

### 5. Running the Full Test Suite
```bash
# Run unit tests
python3 tests/test_governance.py

# Run hook and anti-replay tests
bash tests/test_hooks_suite.sh
```

---

## 🔒 Security & Governance Guidelines

1. **Immutable Audit Anchor:** The cryptographic seal is anchored in `evidence/chain_head.sha256` (`feb5a0bd14e350d34af4d799f535fd4cd107076194136f2274b9c94917cbb6ab`). Any modification to upstream specifications breaks chain parity.
2. **Single-Use Push Tokens:** Pushes to remote origins require generating an explicit token containing an unconsumed nonce, written to `TESLA_PUSH_AUTH_FILE`. Reusing an authorization token results in immediate rejection with exit code `70`.
3. **Secret Entropy Filtering:** Commits containing strings with high Shannon entropy or standard API key signatures (AWS, GitHub, Slack, JWT, RSA/SSH private keys) are halted at `pre-commit` phase.

---

## 📜 Final Verdict & Citation

```text
VERDICT: EXECUTABLE GOVERNANCE OPERATIONAL & PROVEN
"An un-governed agent is a liability; structure is the mother of security."
```
