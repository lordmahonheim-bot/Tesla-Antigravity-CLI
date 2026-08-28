# 🔒 RETEX HARDENING VIGILUM CODEX 2.1 — Paquet Exécutable (SGC-EXEC-GOV-03-R3)

**Mission ID :** `SGC-EXEC-GOV-03-R3` (RETEX Post-Déploiement)
**Date d'implémentation :** 2026-08-28
**Autorité Suprême :** Abdellah MOUHTAJ (Lord Mahonheim)
**Classification :** Correctif Exécutable — DOCTRINE VIGILUM CODEX 2.1
**Principe Directeur :** **« AUCUN MASQUAGE, VÉRITÉ FACTUELLE, ÉLÉVATION SYSTÉMIQUE. »**
**Doctrine :** *AI Proposes, Code Validates* — tout verrou du Plan d'Action Correctif (§5 du Diagnostic) est désormais un **mécanisme déterministe exécutable**, plus jamais une consigne textuelle.

---

## 1. Cartographie : 7 Erreurs → 6 Verrous Exécutables

| Erreur du Diagnostic | Verrou du Plan Correctif | Composant Exécutable | Preuve Matérielle |
|---|---|---|---|
| **E7** Théâtre d'Agents (Usurpation) | Interdiction d'Écriture Directe (Hook Multi-Agents) | `core/orchestration/orchestration_gate.py` (receipt-quorum + intent-guard) + hook `07-orchestration-gate.sh` | Quittances physiques `runtime/subagents/receipt_<agent_id>.json` exigées avant tout commit de synthèse |
| **Gate 2** Court-circuit du DAG | Validation Obligatoire du Mission Graph | `orchestration_gate.py dag-verify` | Sceau `approval_sha256` (SHA-256 canonique du DAG sans le bloc approval) + `approved_by: Lord Mahonheim` |
| **E2** Omission Phase 4 (Staging) | Double Track Staging Public ($N+1$) | `bin/staging_gate.py` (`next-milestone` / `verify`) | Jalon calculé strictement sur le registre public `MVP-GITHUB/` |
| **E3** Amnésie Mémorielle (Règle 14) | Bouclage des 13 Piliers Mémoire | `bin/memory_parite.py` | Rapport matriciel 13/13 SHA-256, code retour 0 |
| **E1** Paralysie Documentaire | Plafond d'Audit Théorique (Max 3) | `bin/audit_cap.py` | SPEC LOCK atomique `O_CREAT\|O_EXCL` à la 3ème passe (exit 80) |
| **E4** Faille d'Invocation Python | Universal Test Runner | `bin/test_runner.py` | Discovery `-s tests` (résolution absolue `sys.path`), ledger JSON dans `evidence/` |
| **E5** Encombrement du Creuset | — (hygiène) | hook `08-draft-artifact-guard.sh` + `.gitignore` (`**/runtime/`) | Refus des artefacts éphémères au commit (exit 90) |

---

## 2. Composants & Contrats Déterministes

### 2.1 Orchestration Gate — `core/orchestration/orchestration_gate.py`
Moteur 100 % stdlib (aucune dépendance : le parseur YAML strict `core/orchestration/yaml_mini.py` remplace PyYAML avec un comportement identique en tout environnement).

| Sous-commande | Rôle | Exit 0 | Exit 1 | Exit 66 |
|---|---|---|---|---|
| `dag-verify --graph <f>` | Gate 2 : structure du DAG (nœuds uniques, dépendances résolues, acyclicité de Kahn) + sceau d'approbation humain | PASS | `GRAPH_*`, `APPROVAL_*` | `GRAPH_UNPARSEABLE` |
| `receipt-quorum --graph <f> --receipts <dir> [--mission <id>]` | Règle Absolue N°4 : chaque agent du DAG doit posséder une quittance physique valide (`status ∈ {SUCCESS, COMPLETED}`) | PASS | `RECEIPT_QUORUM_MISSING` | `RECEIPTS_DIR_MISSING` |
| `intent-guard --root <dir> --target <f>...` | Hook anti-usurpation : détecte les marqueurs explicites `team_synergy: true` / `x-vigilum-team-synergy: true` (formats YAML **et** JSON) puis exige DAG scellé + quorum | PASS | `MISSION_GRAPH_NOT_DECLARED`, `GATE2_DAG_NOT_APPROVED`, `ANTI_USURPATION_RECEIPT_QUORUM_FAILED` | — |

**Registre d'activation :** `runtime/orchestration/active_mission.json` `{"mission_id": ..., "mission_graph": "chemin/relatif.yaml", "activated_by": "Lord Mahonheim"}` — ou variable `TESLA_MISSION_GRAPH`. Le registre n'est qu'un pointeur : **l'autorité est le sceau** contenu dans le graphe lui-même.

### 2.2 Schémas canoniques — `schemas/`
- `receipt_v1.0.schema.json` — contrat des quittances de sous-agents.
- `mission_graph_v2.0.schema.json` — contrat du DAG scellé (bloc `approval` obligatoire).
- `memory_pillars_v2.1.schema.json` — contrat du manifest des 13 piliers mémoire.

### 2.3 Universal Test Runner — `bin/test_runner.py`
Correction définitive d'E4 : **interdiction** de `python3 -m unittest <chemin-décorrélé>` (provoke `ModuleNotFoundError` sur `53-Vigilum-Codex-2.0-...`). Le lanceur exécute exclusivement :
```bash
python3 -m unittest discover -s tests          # -t <racine> interdit : exige un top-level importable
bash tests/test_hooks_suite.sh
# optionnel : bash bin/audit_parite.sh --run-parity (N/A sur clones publics)
```
Ledger de preuve : `evidence/test_runner_<MISSION>_<ts>.json` — exit 0 **uniquement si toutes les suites exécutées sont PASS**.

### 2.4 Memory Parity — `bin/memory_parite.py`
```bash
python3 bin/memory_parite.py --root <TESLA_ROOT> [--manifest <json>] [--baseline <json>]
```
- Matrice 13/13 SHA-256 par pilier ; `--manifest` permet d'ajuster le set canonique.
- Exit **0** PASS · **1** BLOCKED (pilier absent/vide) · **2** STALE_STATE (dérive baseline) · **66** UNKNOWN (répertoire `memory/` inobservable — invariant **P3 : UNKNOWN ≠ PASS**).

### 2.5 Staging Gate — `bin/staging_gate.py`
```bash
python3 bin/staging_gate.py next-milestone --registry MVP-GITHUB/   # → N+1 strictement public
python3 bin/staging_gate.py verify --registry MVP-GITHUB/ --milestone N
python3 bin/staging_gate.py git-status --repo .                     # informatif (jamais un PASS)
```
`verify` exige : répertoire `N-*` unique, `README.md` avec badge `![Status]` + sections `## Objective`, `## Installation`, `## Security`, et au moins un répertoire d'ingénierie (`core|bin|src|tests|schemas|docs|scripts`).

### 2.6 Audit Cap / SPEC LOCK — `bin/audit_cap.py`
```bash
python3 bin/audit_cap.py --root <dir> --spec <SPEC> --max 3 --record   # passe d'audit
python3 bin/audit_cap.py --root <dir> --spec <SPEC> --max 3 --check
```
État dans `runtime/audit/` ; verrou atomique `O_CREAT|O_EXCL` (style Invariant A-003) à la 3ème passe → **SPEC LOCK** (exit 80). Toute passe supplémentaire est refusée : bascule forcée vers le code exécutable.

### 2.7 Guardrails Git — 8 checks pre-commit (au lieu de 6)
| # | Guardrail | Exit |
|---|---|---|
| 01-06 | Guardrails existants (schéma, secrets, scope, état, marbre, lint) | 10-60 |
| **07** | **Orchestration Gate** — synthèse Team-Synergy / modifications de DAG & contrats | **81** |
| **08** | **Draft Artifact Guard** — artefacts éphémères (`*.tmp`, `*.bak`, `*~`, `V3.x` non `LOCKED/FINAL/CANON/SPEC/SEALED/DIAGNOSTIC`, `.runtime/`) | **90** |

Codes ajoutés : `TESLA_EXIT_LOCK=80`, `TESLA_EXIT_ORCH=81`, `TESLA_EXIT_DRAFT=90`. Dérogation explicite et documentée : `TESLA_ALLOW_DRAFT_COMMIT=1`.

---

## 3. Preuve d'Exécution (chaîne matérielle)

```text
TEST SUITE EXECUTION SUMMARY — SGC-EXEC-GOV-03-R3
  [Python: tests/test_governance.py + tests/test_retex_hardening.py]
      Ran 30 tests (unittest discover -s tests) ......... ALL PASS
  [Bash: tests/test_hooks_suite.sh]
      9 tests (6 existants + 7 anti-usurpation + 8 draft + 9 LOCKED) ALL PASS
  [Démos déterministes]
      dag-verify      graphe scellé ......................... PASS (exit 0)
      receipt-quorum  3 agents / 3 quittances ................ PASS (exit 0)
      intent-guard    synthèse sans quittances ............... BLOCKED (exit 1)
      audit_cap       passe #3 → SPEC LOCK ................... exit 80
      staging_gate    N+1 = 13 (registre public) ............. PASS
      memory_parite   13/13 matrice SHA-256 .................. PASS (exit 0)
TOTAL TESTS: 39 | PASSED: 39 | FAILED: 0
```

Le ledger complet est généré par le runner lui-même : `evidence/test_runner_<MISSION>_<ts>.json`.

---

## 4. Procédure Opérationnelle (Ordre Canonique de Clôture)

1. **Gate 2** : présenter le DAG scellé à Lord Mahonheim → `dag-verify` PASS.
2. **Exécution** : invoquer les sous-agents via `invoke_subagent` uniquement ; recueillir les quittances physiques dans `runtime/subagents/`.
3. **Anti-usurpation** : rédiger la synthèse avec le marqueur explicite → le hook 07 ne la laisse passer qu'avec DAG scellé + quorum.
4. **Tests** : `python3 bin/test_runner.py --root . --mission <ID>` → exit 0.
5. **Mémoire** : `python3 bin/memory_parite.py --root <TESLA_ROOT>` → 13/13, exit 0.
6. **Staging** : `python3 bin/staging_gate.py verify --registry MVP-GITHUB/ --milestone $N+1` → PASS.
7. **SPEC LOCK** : `python3 bin/audit_cap.py --root <dir> --spec <ID> --record` (3 passes max).
8. **Scellement** : pre-push avec jeton signé (Invariant A-001/A-003) — publication uniquement après Biological Gate.

---

*Paquet correctif certifié conforme à la doctrine Vigilum Codex 2.0 / 2.1 — implémentation exécutable, testée et scellée dans le registre de preuves.*
