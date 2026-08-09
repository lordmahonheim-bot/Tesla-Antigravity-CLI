# Arcanis Architecture Brief: MVP 16 & MVP 44 Loop Engineering

## Overview
Within the Loop Engineering architecture, **MVP 16 (Tesla-Master-Code)** and **MVP 44 (Tesla-Code-Auditor)** function as the core iterative development engine based on the **Vigilum Codex** doctrine of Separation of Powers. MVP 16 serves as the **Actor/Writer** while MVP 44 serves as the **Gatekeeper/Validator**.

## MVP 16 (Tesla-Master-Code)
- **Role:** Exclusive Acteur (Writer & Code Generator)
- **Function:** Responsible for synthesizing code, running pre-flight format checks (Biome, Ruff, Pyright), and emitting an authoritative `output_manifest.json` containing SHA-256 hashes of modified files.
- **Dependencies:** Relies on task goals and `learning_deltas` provided by the Loop Orchestrator. 
- **Interfaces:** CLI interface via `master_code.py` taking `--contract` and `--feedback` arguments.
- **Strict Limitation:** Forbidden from self-auditing or issuing PASS/BLOCK verdicts to prevent cognitive bias.

## MVP 44 (Tesla-Code-Auditor)
- **Role:** Gatekeeper / Validator
- **Function:** Responsible for independently validating the `output_manifest.json` produced by MVP 16. It performs a 4-level audit (including static analysis, security checks, and logic validation).
- **Dependencies:** Consumes the `output_manifest.json` from MVP 16.
- **Interfaces:** Returns a `PASS` or `DELAY` verdict along with `learning_deltas` to the Orchestrator, which are then fed back to MVP 16 if necessary.

## Interaction Flow (The Loop)
1. Orchestrator sends specs to MVP 16.
2. MVP 16 generates code and a manifest (`output_manifest.json`).
3. MVP 44 audits the code defined in the manifest.
4. If MVP 44 yields `DELAY`, it returns `learning_deltas` to the Orchestrator to trigger another iteration with MVP 16.
5. If MVP 44 yields `PASS`, the loop completes.
