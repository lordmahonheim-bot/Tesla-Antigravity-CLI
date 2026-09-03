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

---

## 6. Extension Vigilum Codex 2.5.1 — Verrouillage de l'Orchestrateur (audit du Plan d'Intervention Correctif V2.5.0)

Source : audit du rapport `docs/PLAN_INTERVENTION_CORRECTIF_ORCHESTRATOR.md` (V2.5.0)
et du RETEX `docs/RETEX_SESSION_ORCHESTRATOR_ERRORS.md` (4 déviations).
Livrable d'audit : `OUTPUTS/Audit_Plan_V2.5.0_Et_Solution_Definitive_V2.5.1.md`.

| Phase | Verrou | Composant Exécutable | Preuve Matérielle |
|---|---|---|---|
| **1 — Anti-Usurpation Git** | Juridiction Git exclusive (`tesla-github-manager`) ; lectures pures seules autorisées à l'Orchestrateur ; fail-closed sur tout `git` non classé (alias, obfuscation `sh -c`/`sudo`/`xargs`/`$()`, occurrence non réconciliée) ; extension `gh` (API mutations) | `core/hooks/antigravity/hook_08_anti_usurpation.sh` + `core/hooks/lib/tesla_git_guard.py` | Décision JSON `deny` Exit 81 (D-007) ; 22 tests de classification + 8 tests hook end-to-end |
| **2 — Zero-Middleman / SCD** | Validation souveraine UNIVERSELLE et EXCLUSIVE par lecture du `transcript.jsonl` (SCD) ; interdiction physique d'écrire tout artefact d'autorisation (`.flag`, `.token`, `.approval`, quittances `receipt_*.json`, certificats, nonces, ledger) — sans exemption d'agent | `core/hooks/lib/tesla-scd.sh` (bibliothèque universelle), `hook_07` refactoré dessus, `core/hooks/antigravity/hook_09_zero_middleman.sh` + `core/hooks/lib/tesla_zero_middleman.py` | Décisions `deny` Exit 81 (BYPASS-01) ; cérémonie SCD complète, anti-rejeu `O_EXCL`, anti-spoofing de type — 26 tests |
| **3 — Pre-Flight Checklist Gate 0** | Vérification PROACTIVE des privilèges physiques avant outil sensible (`invoke_subagent`, mutation Git, élévation `sudo/su/pkexec/doas`) : runtime inscriptible, sonde capacités PASS (U-006), transcript SCD lisible ; élévation refusée sauf `TESLA_ALLOW_PRIVILEGE_ESCALATION=1` posé dans le terminal hôte | `core/hooks/antigravity/hook_10_gate0_preflight.sh` + `core/hooks/lib/tesla_preflight.py` | Décisions `deny` Exit 66 (P3) / 81 ; 9 tests. *Correction d'audit : « injection dans le Moteur Cognitif » du plan V2.5.0 = gouvernance par le verbe (violation P4) → remplacée par un intercepteur déterministe* |
| **4 — Pivot Cloud CI/CD (SLSA)** | Attestation de provenance SLSA v0.2 (in-toto Statement v0.1) en enveloppe DSSE signée HMAC-SHA256 par le Control Plane ; substitut déterministe du `transcript.jsonl` local en CI éphémère ; clé REFUSÉE si elle vit sous la racine du workspace (P2) | `bin/slsa_attestation.py` | `generate`/`verify` : exit 0 PASS / 1 FAIL (falsification, empreinte divergente, sujet non attesté) / 66 UNKNOWN (P3 clé absente) ; 9 tests |

Réparations de parité (P7) accompagnant l'audit :
- `orchestration_gate.py::_transcript_correlation` — ordre de résolution arbitré V2.1.3
  (ref explicite confiné → espace isolé strict → miroir local) restauré ;
  8 preuves RETEX réparées.
- `vigilum_gate_daemon.py` — diagnostic de dépendance sur stderr, exit 66 (P3).
- `requirements.txt` — PyNaCl déclarée (seule dépendance externe, courtier
  Ed25519 du Control Plane) ; 26 tests associés SKIP avec raison explicite,
  divulgés dans le ledger du runner (`tests_skipped`, `p3_disclosure`).

Codes sémantiques mobilisés (aucun nouveau code numérique — arbitrage #3 respecté) :
`81` (D-007 usurpation/BYPASS-01), `66` (P3 UNKNOWN), `10` (schéma), `0` (succès prouvé).

Manifeste : `154 + 11 = 165` tests déclarés (`manifest/test_manifest_v2.1.yaml` v2.5.1).

---

## 7. Extension Vigilum Codex 2.6.1 — Verdict du Plan de Haut Niveau V2.6.0

Source : verdict d'audit du « PLAN D'INTERVENTION DE HAUT NIVEAU (V2.6.0) »
(consolidation RENA/ChatGPT/Claude). Livrable :
`OUTPUTS/Verdict_Audit_Plan_V2.6.0.md`. Deltas admissibles implémentés :

| Delta du plan V2.6.0 | Composant Exécutable | Preuve Matérielle |
|---|---|---|
| **Phase 2 — usurpation de staging** (cp/mv, corrigé : blocage ciblé par destination, jamais aveugle) | `core/hooks/lib/tesla_git_guard.py` (tables `TRANSFER_COMMANDS` + `GOVERNANCE_DESTINATION_SEGMENTS`, formes `-t`/`--target-directory=`) | Verdict `STAGING_MUTATION` → deny Exit 81 pour tout appelant hors `tesla-github-manager` ; destinations couvertes : `MVP-GITHUB/`, `Archives-MVP-GITHUB/`, `CERTIFICATES/`, `evidence/`, `runtime/gate2`, `runtime/contracts`, `.git`, `.tesla` ; 8 tests classifieur + 3 tests hook |
| **Phase 5 — P11 & Gate R** (Evidence Reconciliation, corrigé : registre produit par l'outil déterministe, signature via machinerie HMAC/DSSE) | `bin/gate_r.py` + P11 gravé au Titre III | `reconcile` : manifeste ↔ ledger (comptes, verdict, skips divulgués) ↔ attestation DSSE signée Control Plane → `runtime/contracts/mission_truth.json` (verdict RECONCILED) ; sorties 0/50/66 ; 12 tests |
| **Phase 5 — integrité du registre de vérité** | `core/hooks/lib/tesla_zero_middleman.py` (motifs `mission_truth.json` + `runtime/contracts`) | Écriture agent du registre physiquement bloquée (hook 09, Exit 81) ; 3 tests |
| **Phase 1 — déférérence tracée (P8)** | `OUTPUTS/open_items_todo-Updated.md` (OI-01/OI-02/OI-03) | Câblage CI du SLSA différé, actif conservé (la Gate R dépend de sa machinerie HMAC/DSSE) ; gravure ENGINE.md proposée avec formulation corrigée (OI-02) |

Rejets motivés du plan V2.6.0 (détail dans le verdict) :
- **Phase 4 telle quelle** (artefact pré-vol généré par l'Orchestrateur) :
  auto-attestation circulaire — réintroduction de BYPASS-01, violation P2.
  L'intention est déjà matérialisée par le hook 10 V2.5.1 (vérifications
  déterministes directes, sans artefact agent).
- **Phase 6 telle quelle** (invariant anti-friction absolu « hors-chat = invalide ») :
  contredit la racine de confiance (clé Control Plane, cérémonies, A-001).
  Formulation corrigée gravée au changelog : l'anti-friction lie l'agent,
  jamais le Souverain.
- **Renommage hook_09_anti_usurpation** : la collision invoquée est un faux
  problème (espaces de noms `antigravity/` vs `pre-commit/` disjoints) et le
  renommage créerait une collision réelle avec `hook_09_zero_middleman`
  (V2.5.1). Numérotation V2.5.1 maintenue.
- **« Annulation » de la Phase 4 V2.5.0** : remplacée par un déféré tracé
  (voir ci-dessus) — la suppression de l'actif casserait la Gate R.
