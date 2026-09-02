# 🏛️ PLAN D'INTERVENTION ULTIME : VIGILUM CODEX 2.1.3 — SOVEREIGN SHIELD
## *Verdict d'Arbitrage des 7 Réconciliations — Rebasé sur l'État Physique du Système*

**Version :** 2.1.3
**Date :** 28 Août 2026
**Autorité Suprême :** Abdellah MOUHTAJ (Lord Mahonheim)
**Classification :** Constitutionnelle & Déterministe — FAIL-CLOSED ABSOLU
**Statut Doctrinal :** **`CONTROLLED IMPLEMENTATION BASELINE — SPECIFICATION RECONCILED; RUNTIME EVIDENCE PENDING`**
**Principe Cardinal :** **« L'IA PROPOSE, LE CODE VALIDE. AUCUN MASQUAGE, VÉRITÉ FACTUELLE, ÉLÉVATION SYSTÉMIQUE. »**
**Postulat de Non-Usurpation (P-AGENT-001) :** *« Une délégation sans quittance authentique émise par le runtime est réputée non exécutée ; une synthèse sans manifeste de preuves validé est réputée non produite ; une clôture sans profil de mission respecté est réputée non clôturée. »*
**Emplacement Canonique :** `OUTPUTS/Plan_Intervention_Ultime_Vigilum_Codex_2.1.md`

---

## 1. SYNTHÈSE — V2.1.3 : RÉCONCILIATION DES 7 ARBITRAGES

La version V2.1.3 réconcilie sept points de divergence entre la spécification V2.1.2 et l'état physique du dépôt. Chaque arbitrage est tranché selon le principe « AI Proposes, Code Validates » : la règle devient un mécanisme déterministe exécutable, jamais une consigne textuelle, et toute preuve inobservable est documentée N/A — jamais un PASS implicite (P3).

---

## 2. ARBITRAGE #1 — FRONTIÈRE DE CONFIANCE RUNTIME ISOLÉE

**Dénomination :** Isolated Trusted Runtime Boundary
**Contexte :** Les journaux d'exécution bruts vivaient dans le workspace agent (`runtime/subagents/transcripts/`), donc écrits par l'agent lui-même — preuve auto-attestée.
**Règle :** Le journal runtime authentique vit HORS du workspace agent, dans `~/.tesla/runtime-evidence/<mission_id>/transcripts/` (variable `TESLA_RUNTIME_EVIDENCE`). Le workspace ne détient qu'un miroir de consultation.
**Implémentation :** `core/orchestration/orchestration_gate.py::_transcript_correlation` — ordre de résolution : (1) `transcript_ref` explicite/absolu ; (2) `TESLA_RUNTIME_EVIDENCE/<mission_id>/transcripts/` (mode strict : configuré-mais-inobservable → `RECEIPT_RUNTIME_EVIDENCE_UNOBSERVABLE`) ; (3) miroir local `transcripts/`. Journal inobservable → N/A documenté, jamais PASS.
**Vérification :** Tests `test_receipt_quorum_isolated_runtime_evidence`, `test_receipt_quorum_runtime_evidence_configured_but_unobservable`, `test_transcript_correlation_resolution_order`.
**Preuve :** Quittances corrélées depuis l'espace isolé ; BLOCKED si l'espace configuré est inobservable.

---

## 3. ARBITRAGE #2 — REGISTRE DE NONCES ISOLÉ

**Dénomination :** Isolated Nonce Registry
**Contexte :** Le registre anti-replay vivait dans le workspace agent (répertoire runtime interne), donc falsifiable par l'agent.
**Règle :** Le registre de nonces réside dans `~/.tesla/security/nonces/` (variable `TESLA_SECURITY_NONCES_DIR`), espace de sécurité isolé, mode 0700.
**Implémentation :** `core/hooks/pre-push/tesla-pre-push-main.sh` — `TESLA_SECURITY_NONCES_DIR` si définie (chmod 0700), sinon repli `<root>/runtime/nonces/` (compatibilité espaces contrôlés). Invariant `O_CREAT|O_EXCL` conservé : un nonce déjà consommé est irréversiblement refusé.
**Vérification :** Suite hooks bash (anti-replay rejoué → exit 70).
**Preuve :** Fichier de nonce en 0700 hors workspace lorsque la variable est posée.

---

## 4. ARBITRAGE #3 — CODES POSIX UNIQUES + IDENTIFIANT SÉMANTIQUE

**Dénomination :** Unique POSIX Exit Codes
**Contexte :** Le plan V2.1.2 déclarait des alias numériques `71/72/73` en plus des codes canoniques — deux encodages pour une même condition, source de divergence de parsing.
**Règle :** Un code POSIX = une condition. Unicité stricte des exports numériques ; les identifiants sémantiques sont documentés en commentaire.
**Implémentation :** `core/hooks/lib/tesla-exit-codes.sh` — 12 exports numériques uniquement : `0,10,20,30,40,50,60,66,70,80,81,90` ; identifiants sémantiques : `ERR_SPEC_LOCKED`→80 (L-001), `ERR_AGENT_THEATER`→81 (D-007/D-008), `ERR_PUBLIC_STAGING_MISSING`→exit 1 de `staging_gate.py` (outil-spécifique).
**Vérification :** Tests `test_exit_code_library_has_no_numeric_aliases` / `test_exit_code_library_semantic_ids_present` ; `grep` négatif sur `71/72/73` dans les exports.
**Preuve :** Bibliothèque sourcée ; aucun export numérique `71/72/73`.

---

## 5. ARBITRAGE #4 — PROBE_VALID CONTEXTUALISÉ PAR PROFIL / CONTRAT

**Dénomination :** Contextualized PROBE_VALID
**Contexte :** L'ensemble REQUIS de la sonde tri-state était codé en dur (défaut global), indépendant du profil de clôture et des agents requis.
**Règle :** L'ensemble REQUIS de `PROBE_VALID` est piloté par le contrat de mission (`required_capabilities`), c'est-à-dire par le profil et les agents requis — jamais un défaut codé en dur.
**Implémentation :** `bin/mission_controller.py::_probe_valid(root, contract)` — `required_override` issu du contrat ; capacités requises absentes du fichier de preuve → re-sonde immédiate fail-closed ; optionnels ∈ {PASS, UNKNOWN-CONFINED} ; `UNKNOWN` documenté, jamais PASS (P3).
**Vérification :** Tests `test_probe_valid_contextualized_from_contract` (required_set = `["python3", "bash"]`) et `test_probe_valid_blocks_on_contract_missing_capability`.
**Preuve :** `runtime/marble_eligibility.json` — `equation_terms.PROBE_VALID.detail.required_set` reflète le contrat.

---

## 6. ARBITRAGE #5 — COMPTES DE TESTS DEPUIS MANIFESTE DÉCLARATIF

**Dénomination :** Declarative Test Manifest
**Contexte :** Les comptes de tests étaient narratifs (README), donc divergents de l'exécution réelle.
**Règle :** « 100% des tests déclarés au manifeste — aucun comptage narratif » : le runner charge `manifest/test_manifest_v2.1.yaml`, compare comptes exécutés vs déclarés ; écart → verdict FAIL fail-closed.
**Implémentation :** `bin/test_runner.py` — `load_test_manifest` / `manifest_mismatches` câblés dans `run()` ; manifeste déclaratif : `python-unittest-discovery=55`, `bash-hooks-suite=11`, `total_tests=66`.
**Vérification :** Tests `test_runner_passes_when_manifest_matches` / `test_runner_fails_when_manifest_declares_more` ; exécution réelle `python3 bin/test_runner.py --root .` → verdict PASS avec `test_manifest.verdict: PASS`.
**Preuve :** Ledger `evidence/test_runner_*.json` avec bloc `test_manifest`.

---

## 7. ARBITRAGE #6 — TAMPER_EVIDENT vs IMMUTABLE

**Dénomination :** Tamper-Evident vs Immutable Classification
**Contexte :** Le terme « immuable » était appliqué indistinctement à la preuve locale (re-calculable) et au certificat distant (ancré).
**Règle :** Classification explicite : la preuve locale `evidence/chain_head.sha256` est **TAMPER_EVIDENT** (vérifiable par re-calcul, mutable jusqu'à ancrage) ; le certificat de marbre ancré côté distant (`--remote-commit`, POST_PUB_VERIFIED) est **IMMUTABLE** — jamais auto-attesté.
**Implémentation :** `bin/marble_certificate.py` — `seal_class` / `seal_note` / `status` (`SEALED_TAMPER_EVIDENT` ↔ `SEALED_IMMUTABLE`) ; `bin/audit_parite.py` — bloc `seal_classification` dans le ledger de parité.
**Vérification :** Tests `test_certificate_sealed_after_eligibility` (TAMPER_EVIDENT) et `test_certificate_remote_anchor_is_immutable` (IMMUTABLE avec ancre distante).
**Preuve :** `CERTIFICATES/MARBLE_CERTIFICATE_*.json` scellé 0444 avec `seal_class` explicite.

---

## 8. ARBITRAGE #7 — ORDONNANCEMENT DES INCRÉMENTS DE DÉPLOIEMENT

**Dénomination :** Deployment Increment Ordering
**Contexte :** L'ordre de déploiement I0→I1→I2→I3→I4→I5 devait être explicitement ordonné et non-bypassable.
**Règle :** Ordre strict de déploiement : **I0** baseline contrôlée → **I1** binaire du Codex exécutable (`mission_controller`, `marble_certificate`) → **I2** runner universel + garde-fous hooks (exit codes normalisés) → **I3** quittances D-008 corrélées (runtime evidence, transcripts) → **I4** staging `$N+1$` (`staging_gate.py`) → **I5** scellage marbre + ancre distante (`IMMUTABLE`).
**Implémentation :** Cartographié dans `docs/protocol_mapping.md` (§5) ; chaque incrément possède un composant exécutable et une preuve matérielle — l'ordre est documenté, chaque étape est verrouillée par son hook.
**Vérification :** Cohérence du mapping protocole ↔ composant ↔ preuve.
**Preuve :** `docs/protocol_mapping.md` §5 — ligne Arbitrage #7.

---

## 9. MATRICE DES CODES D'ERREUR POSIX & RACINE DE CONFIANCE

| Code | Condition | Identifiant Sémantique |
|---|---|---|
| 0 | Succès | `TESLA_EXIT_OK` |
| 10 | Schéma invalide | `TESLA_EXIT_SCHEMA` |
| 20 | Secret manquant | `TESLA_EXIT_SECRET` |
| 30 | Périmètre violé | `TESLA_EXIT_SCOPE` |
| 40 | État de projet invalide | `TESLA_EXIT_STATE` |
| 50 | Éligibilité Marbre refusée | `TESLA_EXIT_MARBLE` |
| 60 | Lint / format invalide | `TESLA_EXIT_LINT` |
| 66 | Inobservable (P3) | `TESLA_EXIT_UNKNOWN` |
| 70 | Push refusé (anti-replay) | `TESLA_EXIT_PUSH` |
| 80 | SPEC LOCK (plafond d'audit, L-001) | `ERR_SPEC_LOCKED` |
| 81 | Théâtre d'agents (D-007/D-008) | `ERR_AGENT_THEATER` |
| 90 | Brouillon interdit au commit (H-005) | `TESLA_EXIT_DRAFT` |

Alias numériques `71/72/73` : **supprimés** (V2.1.3 arbitrage #3). `ERR_PUBLIC_STAGING_MISSING` : exit 1 de `bin/staging_gate.py` (outil-spécifique, S-002).

**Racine de confiance :** signature biologique du Lord Mahonheim (hors périmètre agent), ancrée par le contrôleur de clôture (HUMAN_AUTHORIZED) et le certificat de marbre IMMUTABLE côté distant.

---

## 10. NON-DELTAS ASSUMÉS (PÉRIMÈTRE HORS AGENT)

1. **Signature biologique** elle-même — opération physique du Lord, non automatisable par l'agent ; la délégation est enregistrée via `--authorized`.
2. **Journal runtime distant** (`~/.tesla/runtime-evidence/`) — hors workspace agent ; l'agent enregistre la règle stricte et la corrélation, la production du journal relève du daemon runtime déployé côté machine.
3. **Piliers mémoire à la racine du dépôt** (`memory/`, `runtime/`, `MVP-GITHUB/`, `.agents/`, `AGENTS.md`) — rémanents du monorepo source, absents du paquet 53- ; documentés, jamais masqués.

---

## 11. VERDICT ATTENDU

**Statut doctrinal :** `CONTROLLED IMPLEMENTATION BASELINE — SPECIFICATION RECONCILED; RUNTIME EVIDENCE PENDING`
**Critères d'acceptation :** implémentation physique pour les éléments dans le workspace ; documentation honnête pour les éléments de confiance hors workspace ; preuves commitées et poussées ; jugement explicite avec non-deltas résiduels nommés.
