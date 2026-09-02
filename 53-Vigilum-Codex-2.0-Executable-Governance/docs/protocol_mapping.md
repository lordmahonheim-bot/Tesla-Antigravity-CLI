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

## 4. Extension Vigilum Codex 2.1.1 (RETEX Hardening — SGC-EXEC-GOV-03-R3)

| Verrou RETEX | Composant Exécutable | Contrat / Schéma | Preuve Matérielle |
|---|---|---|---|
| **Gate 2 (Mission Contract / DAG)** | `core/orchestration/orchestration_gate.py dag-verify` | `schemas/mission_graph_v2.0.schema.json` | Sceau `approval_sha256` canonique (RFC-8785-style) + `approved_by` |
| **Gate 2 Délégation (SPINOFF-DIAG-GATE2-BYPASS)** | `core/orchestration/gate2_guard.py` (`issue-token` / `pre-flight` / `consume` / `status`) | jeton `G2T-1` HMAC-SHA256, secret hors workspace (`TESLA_GATE2_SECRET` / `~/.tesla/gate2/secret.key` 0600) | Pré-vol **pur** idempotent + liaison (mission, `graph_sha256`, fenêtre, nonce) + anti-rejeu `O_CREAT\|O_EXCL` (A-003) + grand livre chaîné `runtime/gate2/redemptions.jsonl` (`GATE2_LEDGER_CHAIN_BROKEN` si falsifié) |
| **Anti-Usurpation (D-007/D-008)** | `orchestration_gate.py receipt-quorum` / `intent-guard` | `schemas/receipt_v1.0.schema.json` | Quittances physiques `runtime/subagents/receipt_<agent_id>.json` (quorum N/N) |
| **Double Track Staging $N+1$ (S-002)** | `bin/staging_gate.py` | Phase 4 Gravure sur Marbre | Jalon calculé sur `MVP-GITHUB/` + README anglais strict vérifié |
| **Piliers Mémoire Manifeste (M-014)** | `bin/memory_parite.py` + hook 04 | `manifest/memory_manifest_v2.1.yaml` + `schemas/memory_pillars_v2.1.schema.json` | Matrice 13/13 SHA-256, exit 0 ; hook strict → 40 |
| **Plafond d'Audit Max 3 (L-001)** | `bin/audit_cap.py` | — | SPEC LOCK atomique `O_CREAT\|O_EXCL` (exit 80 — `ERR_SPEC_LOCKED`) |
| **Universal Test Runner (R-004)** | `bin/test_runner.py` | — | Discovery `-s tests`, ledger `evidence/test_runner_*.json` |
| **Hygiène & Quarantaine (H-005)** | `bin/workspace_hygiene.py --prune` + hook 08 | — | Brouillons → `runtime/drafts/archive_<ts>/` ; exit 90 au commit |
| **Sonde Tri-State (U-006)** | `bin/probe_capabilities.py` | — | `runtime/capability_health.json` : PASS/FAIL/UNKNOWN-CONFINED (P3) |
| **Corrélation Runtime D-008** | `orchestration_gate.py` (validate_receipt + `_transcript_correlation`) | `schemas/receipt_v1.0.schema.json` (v1.1) | Quittances attestées (`invocation_id`, `executor_attestation`, `output_manifest_sha256`, `transcript_ref` corrélé au journal `runtime/subagents/transcripts/`) |
| **Mission Closure Controller** | `bin/mission_controller.py` | — | `runtime/marble_eligibility.json` + `runtime/state.json` (machine 13 états) |
| **Certificat de Marbre Crypto** | `bin/marble_certificate.py` | hook 05 (`CERTIFICATES/*.json`) | `CERTIFICATES/MARBLE_CERTIFICATE_*.json` scellé 0444 (ancres commits/hashes) |

- **Codes de sortie guardrails (V2.1.3 — arbitrage #3) :** 12 codes canoniques uniquement — `TESLA_EXIT_OK=0`, `SCHEMA=10`, `SECRET=20`, `SCOPE=30`, `STATE=40`, `MARBLE=50`, `LINT=60`, `UNKNOWN=66`, `PUSH=70`, `LOCK=80`, `ORCH=81`, `DRAFT=90` ; identifiants sémantiques en commentaire (`ERR_SPEC_LOCKED`→80, `ERR_AGENT_THEATER`→81, `ERR_PUBLIC_STAGING_MISSING`→exit 1 de `staging_gate.py`). Alias numériques `71/72/73` supprimés (code unique par défaut).
- **Exit codes orchestration gate :** `0 PASS | 1 BLOCKED | 64 USAGE | 66 UNKNOWN` (P3).

---

## 5. Extension Vigilum Codex 2.1.3 (7 Arbitrages — SGC-EXEC-GOV-03-R3)

| # | Arbitrage | Composant Exécutable | Preuve Matérielle / Classe |
|---|---|---|---|
| 1 | **Frontière de confiance runtime isolée** | `orchestration_gate.py::_transcript_correlation` | `TESLA_RUNTIME_EVIDENCE/<mission_id>/transcripts/` (strict : configuré-mais-inobservable → `RECEIPT_RUNTIME_EVIDENCE_UNOBSERVABLE`) ; miroir local de consultation ; N/A jamais PASS (P3) |
| 2 | **Registre de nonces isolé** | `core/hooks/pre-push/tesla-pre-push-main.sh` | `TESLA_SECURITY_NONCES_DIR` (mode 0700) sinon `<root>/runtime/nonces/` ; anti-replay `O_CREAT\|O_EXCL` conservé |
| 3 | **Codes POSIX uniques + identifiants sémantiques** | `core/hooks/lib/tesla-exit-codes.sh` | 12 exports numériques (`0,10,20,30,40,50,60,66,70,80,81,90`) ; alias `71/72/73` supprimés ; IDs sémantiques documentés |
| 4 | **PROBE_VALID contextualisé** | `bin/mission_controller.py::_probe_valid` | Ensemble REQUIS piloté par `required_capabilities` du contrat de mission (profil/agents), jamais un défaut codé en dur ; capacité requise non observée → re-sonde fail-closed |
| 5 | **Comptes depuis manifeste déclaratif** | `bin/test_runner.py` + `manifest/test_manifest_v2.1.yaml` | `55 + 11 = 66` tests déclarés ; écart compté < déclaré → verdict FAIL (`TEST_MANIFEST`) |
| 6 | **TAMPER_EVIDENT vs IMMUTABLE** | `bin/marble_certificate.py`, `bin/audit_parite.py` | Local `evidence/chain_head.sha256` = `TAMPER_EVIDENT` (re-calculable) ; certificat ancré distant (`--remote-commit`, POST_PUB_VERIFIED) = `IMMUTABLE` — jamais auto-attesté |
| 7 | **Ordonnancement des incréments de déploiement** | Plan + hooks (ordre strict, non-bypassable) | **I0** baseline contrôlée → **I1** binaire du Codex exécutable (`mission_controller`, `marble_certificate`) → **I2** runner universel + garde-fous hooks (exit codes normalisés) → **I3** quittances D-008 corrélées (runtime evidence, transcripts) → **I4** staging `$N+1$` (`staging_gate.py`) → **I5** scellage marbre + ancre distante (`IMMUTABLE`) |

- **Statut doctrinal V2.1.3 :** `CONTROLLED IMPLEMENTATION BASELINE — SPECIFICATION RECONCILED; RUNTIME EVIDENCE PENDING`.
- **Non-deltas assumés (hors périmètre agent) :** signature biologique elle-même, journal runtime distant hors workspace, piliers mémoire à la racine du dépôt (E3).
