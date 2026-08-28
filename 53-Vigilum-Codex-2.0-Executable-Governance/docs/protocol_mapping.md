# 🗺️ Cartographie Canonique des Protocoles : Synergy Governance Executable

**Mission ID :** `SGC-EXEC-GOV-03`  
**Date :** 2026-08-27  
**Version :** 2.0.0  

---

## 1. Règle de Précédence Doctrinale
La hiérarchie d'autorité immuable s'applique :
1. `SOUL.md` (Identité et principes constitutionnels)
2. `ENGINE.md` (Raisonnement cognitif)
3. `AGENTS.md` (Gouvernance opérationnelle et orchestration)
4. `FORCE_TOOLING.md` (Gouvernance des capacités)
5. **Protocoles Canoniques Spécialisés** (`Le Conducteur Absolu v3.2.1`, `Gravure sur Marbre v2.0.0`, `Loi de Parité Absolue v2.0.0`)

---

## 2. Matrice de Mapping Opérationnel

| Nœud Local | Conducteur Absolu v3.2.1 | Gravure sur Marbre v2.0.0 | Loi de Parité Absolue | Preuve Matérielle Produite |
|---|---|---|---|---|
| **GATE N1** | Gate 0 (Authority & Reload) | Phase 0 (Authority) | §5.1 Validation de chemins | `core/gatekeeper.py`, `bin/audit_parite.py` |
| **GATE N2** | Gate 1 & Gate 2 (Contract) | Phase 1 (Closure & Contracts)| §3 Matrice composants | `core/broker/tesla_brokerd.py`, `schemas/` |
| **GATE N3** | Gate 3 & Gate 4 (Verification)| Phase 2 (Validation) | Structure / Sémantique | `core/hooks/`, `tests/test_hooks_suite.sh` |
| **GATE N4** | Gate 5 & Gate 6 (Closure) | Phase 3 (Assimilation) | §5.3 Audit Fichier par Fichier | `docs/AUDIT_REPORT.md`, `evidence/parity_*.json` |
| **SCELLEMENT**| Gate 6 (Evidence & Seal) | Phase 7 (Seal & Immutability)| Evidence Ledger | `evidence/chain_head.sha256`, `PROJECT_STATE.md` |

---

## 3. États de Transition
- **File Broker :** `CLAIMED` ➔ `AUTHORIZED` ➔ `MUTATION_STARTED` ➔ `MUTATION_COMMITTED` ➔ `VERIFIED` ➔ `RECEIPTED` ➔ `COMPLETED` (ou `FAILED`).
- **Gouvernance Mission :** `PASS` (validé), `BLOCKED` (échec gatekeeper), `STALE_STATE` (dérive fingerprint), `UNKNOWN` (élément externe non observable).

---

## 4. Extension Vigilum Codex 2.1 (RETEX Hardening — SGC-EXEC-GOV-03-R3)

| Verrou RETEX | Composant Exécutable | Contrat / Schéma | Preuve Matérielle |
|---|---|---|---|
| **Gate 2 (Mission Contract / DAG)** | `core/orchestration/orchestration_gate.py dag-verify` | `schemas/mission_graph_v2.0.schema.json` | Sceau `approval_sha256` canonique (RFC-8785-style) + `approved_by` |
| **Anti-Usurpation (Règle Absolue N°4)** | `orchestration_gate.py receipt-quorum` / `intent-guard` | `schemas/receipt_v1.0.schema.json` | Quittances physiques `runtime/subagents/receipt_<agent_id>.json` (status SUCCESS/COMPLETED) |
| **Double Track Staging $N+1$** | `bin/staging_gate.py` | Phase 4 Gravure sur Marbre | Jalon calculé sur `MVP-GITHUB/` + README anglais strict vérifié |
| **13 Piliers Mémoire** | `bin/memory_parite.py` | `schemas/memory_pillars_v2.1.schema.json` | Matrice 13/13 SHA-256, exit 0 |
| **Plafond d'Audit Max 3** | `bin/audit_cap.py` | — | SPEC LOCK atomique `O_CREAT\|O_EXCL` (exit 80) |
| **Universal Test Runner** | `bin/test_runner.py` | — | Discovery `-s tests`, ledger `evidence/test_runner_*.json` |
| **Hygiène du Creuset** | hook `08-draft-artifact-guard.sh` | — | Refus des artefacts éphémères (exit 90) |

- **Nouveaux codes de sortie guardrails :** `TESLA_EXIT_LOCK=80`, `TESLA_EXIT_ORCH=81`, `TESLA_EXIT_DRAFT=90`.
- **Exit codes orchestration gate :** `0 PASS | 1 BLOCKED | 64 USAGE | 66 UNKNOWN` (P3).
