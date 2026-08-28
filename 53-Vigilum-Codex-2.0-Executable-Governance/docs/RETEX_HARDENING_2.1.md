# 🔒 RETEX HARDENING VIGILUM CODEX 2.1.1 — Paquet Exécutable (SGC-EXEC-GOV-03-R3)

**Mission ID :** `SGC-EXEC-GOV-03-R3` (RETEX Post-Déploiement)
**Date d'implémentation :** 2026-08-28
**Version Consolidée :** **2.1.1** (absorption intégrale des arbitrages MANUS / ChatGPT / RENA — Plan SOVEREIGN SHIELD)
**Autorité Suprême :** Abdellah MOUHTAJ (Lord Mahonheim)
**Classification :** Correctif Exécutable — DOCTRINE VIGILUM CODEX 2.1
**Principe Directeur :** **« AUCUN MASQUAGE, VÉRITÉ FACTUELLE, ÉLÉVATION SYSTÉMIQUE. »**
**Postulat de Non-Usurpation (P-AGENT-001) :** *« Une délégation sans quittance authentique émise par le runtime est réputée non exécutée ; une synthèse sans manifeste de preuves validé est réputée non produite ; une clôture sans profil de mission respecté est réputée non clôturée. »*
**Doctrine :** *AI Proposes, Code Validates* — tout verrou du Plan d'Action Correctif est un **mécanisme déterministe exécutable**, jamais une consigne textuelle.

---

## 1. Cartographie : 7 Erreurs → 7 Verrous Exécutables (V2.1.1)

| Erreur du Diagnostic | Verrou du Plan Correctif | Composant Exécutable | Preuve Matérielle |
|---|---|---|---|
| **E7** Théâtre d'Agents | Interdiction d'Écriture Directe + Corrélation Runtime (**D-007 / D-008**) | `core/orchestration/orchestration_gate.py` (receipt-quorum + intent-guard) + hook `07-orchestration-gate.sh` | Quittances physiques `runtime/subagents/receipt_<agent_id>.json` (quorum dynamique N/N issu du DAG approuvé) |
| **Gate 2** Court-circuit du DAG | Validation Obligatoire du Mission Graph | `orchestration_gate.py dag-verify` | Sceau `approval_sha256` (SHA-256 canonique du DAG sans le bloc approval) + `approved_by: Lord Mahonheim` |
| **E2** Omission Phase 4 | Double Track Staging Public, **profile-aware** (`public-release` / `internal-only` / `memory-assimilation`) | `bin/staging_gate.py` (`next-milestone` / `verify`) | Jalon $N+1$ calculé strictement sur `MVP-GITHUB/` ; `STAGING_NA_CONFIRMED` pour `internal-only` |
| **E3** Amnésie Mémorielle (R14) | Manifeste Déclaratif `MEMORY_MANIFEST.yaml` (**M-014**) | `bin/memory_parite.py` (manifest-driven) + hook `04-project-state-check.sh` | Rapport matriciel 13/13 SHA-256, exit 0 ; hook strict → exit 40 |
| **E1** Paralysie Documentaire | Plafond d'Audit (k ≤ 3) (**L-001**) | `bin/audit_cap.py` | SPEC LOCK atomique `O_CREAT\|O_EXCL` + état logique (exit 80 ; alias plan 71) |
| **E4** Faille d'Invocation Python | Test Runner Universel (**R-004**) | `bin/test_runner.py` | Discovery `-s tests` (résolution absolue `sys.path`), ledger JSON dans `evidence/` |
| **E5** Encombrement du Creuset | Quarantaine Atomique (**H-005**) | `bin/workspace_hygiene.py --prune` + hook `08-draft-artifact-guard.sh` + `.gitignore` | Brouillons déplacés vers `runtime/drafts/archive_<ts>/` ; git status propre |
| **E6** Incertitude LSP | Sonde Tri-State (**U-006**, P3 strict) | `bin/probe_capabilities.py` | `runtime/capability_health.json` : `PASS / FAIL / UNKNOWN-CONFINED` — jamais de PASS implicite |

---

## 2. Composants & Contrats Déterministes

### 2.1 Orchestration Gate — `core/orchestration/orchestration_gate.py`
Moteur 100 % stdlib (parseur YAML strict `core/orchestration/yaml_mini.py`, comportement identique sans PyYAML).

| Sous-commande | Rôle | Exit 0 | Exit 1 | Exit 66 |
|---|---|---|---|---|
| `dag-verify --graph <f>` | Gate 2 : structure du DAG (nœuds uniques, dépendances résolues, acyclicité de Kahn) + sceau d'approbation humain | PASS | `GRAPH_*`, `APPROVAL_*` | `GRAPH_UNPARSEABLE` |
| `receipt-quorum --graph <f> --receipts <dir> [--mission <id>]` | Règle Absolue N°4 : quorum **dynamique N/N** des agents du DAG (quittances `status ∈ {SUCCESS, COMPLETED}`) | PASS | `RECEIPT_QUORUM_MISSING` | `RECEIPTS_DIR_MISSING` |
| `intent-guard --root <dir> --target <f>...` | Hook anti-usurpation : marqueurs explicites `team_synergy: true` / `x-vigilum-team-synergy: true` (YAML **et** JSON) puis DAG scellé + quorum | PASS | `MISSION_GRAPH_NOT_DECLARED`, `GATE2_DAG_NOT_APPROVED`, `ANTI_USURPATION_RECEIPT_QUORUM_FAILED` | — |

**Registre d'activation :** `runtime/orchestration/active_mission.json` ou `TESLA_MISSION_GRAPH`. L'autorité est le **sceau** contenu dans le graphe.

### 2.2 Schémas canoniques — `schemas/`
- `receipt_v1.0.schema.json` · `mission_graph_v2.0.schema.json` · `memory_pillars_v2.1.schema.json`.

### 2.3 Manifeste Mémoire Déclaratif — `manifest/memory_manifest_v2.1.yaml`
Arbitrage #4 (ChatGPT/MANUS/RENA) : **plus aucun pilier codé en dur à l'exécution**. Le scrutateur `bin/memory_parite.py` résout le manifeste dans l'ordre :
1. `--manifest <file>` (explicite)
2. `<TESLA_ROOT>/memory/MEMORY_MANIFEST.yaml`
3. `<module>/manifest/memory_manifest_v2.1.yaml` (manifest canonique livré — 13 piliers)
4. fallback intégré (13 canoniques)

```bash
python3 bin/memory_parite.py --root <TESLA_ROOT> [--manifest <f>] [--baseline <json>]
```
Exit : **0** PASS · **1** BLOCKED · **2** STALE_STATE · **66** UNKNOWN (P3). Câblé au hook **04** (mode strict `TESLA_ENFORCE_MEMORY_PARITY=1` → exit **40** à la moindre désynchronisation ; `UNKNOWN` documenté, jamais masqué).

### 2.4 Hygiène & Quarantaine Atomique — `bin/workspace_hygiene.py` (H-005)
```bash
python3 bin/workspace_hygiene.py --root <dir>            # report : BLOCKED si brouillons (exit 1)
python3 bin/workspace_hygiene.py --root <dir> --prune    # quarantaine atomique → PASS (exit 0)
```
Cibles : `OUTPUTS/*_V\d+.*.md` non canoniques, `.tmp/.bak/.orig/.swp/*~`, `runtime/capability-health/*.json` (+ `.runtime/` hérité). Les finals canoniques (`LOCKED/FINAL/CANON/SPEC/SEALED/DIAGNOSTIC`) ne sont **jamais** quarantainés. Déplacement atomique `os.replace` (même filesystem) vers `runtime/drafts/archive_<timestamp>/`.

### 2.5 Sonde Tri-State — `bin/probe_capabilities.py` (U-006)
```bash
python3 bin/probe_capabilities.py --root <dir> [--tool pyright] [--required pyright] ...
```
Statuts formels : **PASS** (présent + smoke test exit 0) · **FAIL** (présent mais dégradé) · **UNKNOWN-CONFINED** (non observable). Verdict global : PASS (0) si tout PASS ; FAIL (1) si un requis FAIL ; UNKNOWN (66) sinon — **P3 strict, un UNKNOWN n'est jamais un PASS**. Preuve : `runtime/capability_health.json`.

### 2.6 Audit Cap / SPEC LOCK — `bin/audit_cap.py` (L-001)
État dans `runtime/audit/` ; verrou atomique `O_CREAT|O_EXCL` à la 3ᵉ passe → **SPEC LOCK** (exit 80, alias plan 71). Toute passe supplémentaire refusée.

### 2.7 Staging Gate — `bin/staging_gate.py` (S-002)
`next-milestone` (N+1 strictement public) · `verify` (README anglais strict + sous-dossiers d'ingénierie) · `git-status` (informatif, jamais PASS). Profile-aware : `internal-only` → `STAGING_NA_CONFIRMED`.

### 2.8 Universal Test Runner — `bin/test_runner.py` (R-004)
`python3 -m unittest discover -s tests` (jamais `-t <racine>` ni `-m unittest <chemin-décorrélé>`) + `bash tests/test_hooks_suite.sh`. Ledger : `evidence/test_runner_<MISSION>_<ts>.json`.

### 2.9 Guardrails Git — 8 checks pre-commit
| # | Guardrail | Exit |
|---|---|---|
| 01-06 | Schéma, secrets, scope, **état + parité mémoire (M-014 strict)**, marbre, lint | 10-60 |
| **07** | **Orchestration Gate** — synthèse Team-Synergy / DAG & contrats (Gate 2 + quorum D-007/D-008) | **81** (alias plan 73) |
| **08** | **Draft Artifact Guard** — artefacts éphémères | **90** |

**Table de réconciliation des codes (physique ↔ plan V2.1.1) :**

| Plan V2.1.1 | Physique commité | Sémantique |
|---|---|---|
| `71 ERR_SPEC_LOCKED` | `80 TESLA_EXIT_LOCK` | alias L-001 |
| `72 ERR_PUBLIC_STAGING_MISSING` | pipeline `staging_gate.py` (exit 1) | alias S-002 |
| `73 ERR_AGENT_THEATER_DETECTED` | `81 TESLA_EXIT_ORCH` | alias D-007/D-008 |
| `90 ERR_WORKSPACE_CLUTTER` | `90 TESLA_EXIT_DRAFT` | H-005 + hook 08 |
| `66 STAT_CAPABILITY_UNKNOWN` | `66 TESLA_EXIT_UNKNOWN` | P3 (UNKNOWN ≠ PASS) |

---

## 3. Preuve d'Exécution (chaîne matérielle)

```text
TEST SUITE EXECUTION SUMMARY — SGC-EXEC-GOV-03-R3 (V2.1.1)
  [Python: tests/test_governance.py + tests/test_retex_hardening.py]
      Ran 38 tests (unittest discover -s tests) ......... ALL PASS
  [Bash: tests/test_hooks_suite.sh]
      11 tests (6 existants + orchestration + draft + LOCKED + mémoire M-014) ALL PASS
  [Démos déterministes]
      dag-verify       graphe scellé ......................... PASS (exit 0)
      receipt-quorum   quorum dynamique N/N ................... PASS (exit 0)
      intent-guard     synthèse sans quittances ............... BLOCKED (exit 1)
      audit_cap        passe #3 → SPEC LOCK ................... exit 80
      staging_gate     N+1 = 13 (registre public) ............. PASS
      memory_parite    13/13 manifeste déclaratif ............. PASS (exit 0)
      probe_capabilities  requis PASS · pyright UNKNOWN-CONFINED  PASS(0)/UNKNOWN(66) — P3
      workspace_hygiene   report BLOCKED → --prune PASS ....... 1 → 0
TOTAL TESTS: 49 | PASSED: 49 | FAILED: 0
```

Le ledger complet est généré par le runner : `evidence/test_runner_<MISSION>_<ts>.json`.

---

## 4. Équation d'Éligibilité au Marbre (Profile-Aware)

$$\text{MARBLE\_ELIGIBLE} = \text{WORK\_VALIDATED} \land \text{MEMORY\_PARITY\_PASS} \land \text{HYGIENE\_PASS} \land \text{PROBE\_VALID} \land \text{RECEIPTS\_CORRELATED} \land \text{PROFILE\_REQUIREMENTS\_PASS}$$

$$\text{PROFILE\_REQUIREMENTS\_PASS} = \begin{cases} \text{STAGING\_N1\_PASS} \land \text{PUBLICATION\_AUTH} & \text{si } closure\_profile = \text{public-release} \\ \text{STAGING\_NA\_CONFIRMED} & \text{si } closure\_profile = \text{internal-only} \\ \text{MEMORY\_ASSIMILATION\_PASS} & \text{si } closure\_profile = \text{memory-assimilation} \end{cases}$$

`WORK_VALIDATED` = 50 % du cycle seulement : il n'autorise jamais le scellement (machine d'états `DRAFT → CONTRACTED → G2_APPROVED → EXECUTING → WORK_VALIDATED → EVIDENCE_VALIDATED → STAGING_VALIDATED → HUMAN_AUTHORIZED → SEALED`).

---

## 5. Procédure Opérationnelle (Ordre Canonique de Clôture)

1. **Contrat** : `runtime/contracts/mission_contract.json` (mission_id, closure_profile, required_nodes, max_documentation_rounds=3).
2. **Gate 2** : DAG scellé approuvé par Lord Mahonheim → `dag-verify` PASS.
3. **Exécution** : `invoke_subagent` uniquement ; quittances physiques `runtime/subagents/` (quorum N/N corrélé).
4. **Anti-usurpation** : synthèse avec marqueur explicite → hook 07 ne la laisse passer qu'avec DAG + quorum.
5. **Tests** : `python3 bin/test_runner.py --root . --mission <ID>` → exit 0.
6. **Mémoire** : `python3 bin/memory_parite.py --root <TESLA_ROOT>` → 13/13, exit 0.
7. **Sonde** : `python3 bin/probe_capabilities.py --root <dir>` → statuts formels (P3).
8. **Hygiène** : `python3 bin/workspace_hygiene.py --root <dir> --prune` → PASS.
9. **Staging** : `python3 bin/staging_gate.py verify --registry MVP-GITHUB/ --milestone $N+1` (profil public) ou `STAGING_NA_CONFIRMED`.
10. **SPEC LOCK** : `python3 bin/audit_cap.py --root <dir> --spec <ID> --record` (3 passes max).
11. **Scellement** : pre-push avec jeton signé (A-001/A-003) — publication uniquement après Biological Gate.

---

*Paquet correctif V2.1.1 certifié conforme à la doctrine Vigilum Codex 2.0 / 2.1 — implémentation exécutable, testée (49/49) et scellée dans le registre de preuves.*
