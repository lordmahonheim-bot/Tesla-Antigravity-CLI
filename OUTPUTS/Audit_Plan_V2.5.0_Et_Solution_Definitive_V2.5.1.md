# 🔍 AUDIT & ANALYSE DU PLAN D'INTERVENTION CORRECTIF V2.5.0
## *Rédaction de la Solution Opérationnelle, Performante et Définitive — Vigilum Codex 2.5.1*

**Mission ID :** `SGC-EXEC-GOV-03-V251`
**Date de l'Audit :** 3 septembre 2026
**Autorité Suprême :** Abdellah MOUHTAJ (Lord Mahonheim)
**Objet audité :** `53-Vigilum-Codex-2.0-Executable-Governance/docs/PLAN_INTERVENTION_CORRECTIF_ORCHESTRATOR.md` (V2.5.0) et son corpus de rattachement (`RETEX_SESSION_ORCHESTRATOR_ERRORS.md`, état physique du module 53)
**Classification :** Audit Constitutionnel & Implémentation Exécutable — FAIL-CLOSED
**Principe Directeur :** **« L'IA PROPOSE, LE CODE VALIDE. AUCUN MASQUAGE, VÉRITÉ FACTUELLE, ÉLÉVATION SYSTÉMIQUE. »**

---

# 📑 TABLE DES MATIÈRES
1. [Synthèse Exécutive](#1-synthèse-exécutive)
2. [Audit du Rapport V2.5.0 — Conformités](#2-audit-du-rapport-v250--conformités)
3. [Audit du Rapport V2.5.0 — Non-Conformités & Écarts Doctrinaux](#3-audit-du-rapport-v250--non-conformités--écarts-doctrinaux)
4. [Audit de l'État Physique — Violations P1/P7 Détectées](#4-audit-de-létat-physique--violations-p1p7-détectées)
5. [Analyse des Causes Racines (Ishikawa)](#5-analyse-des-causes-racines-ishikawa)
6. [La Solution Définitive V2.5.1 — Architecture Générale](#6-la-solution-définitive-v251--architecture-générale)
7. [Phase 1 — Verrouillage Anti-Usurpation Git](#7-phase-1--verrouillage-anti-usurpation-git)
8. [Phase 2 — Standardisation Zero-Middleman / SCD](#8-phase-2--standardisation-zero-middleman--scd)
9. [Phase 3 — Pre-Flight Checklist Gate 0](#9-phase-3--pre-flight-checklist-gate-0)
10. [Phase 4 — Pivot Cloud CI/CD (SLSA)](#10-phase-4--pivot-cloud-cicd-slsa)
11. [Réparations de Parité (P7) Accomplies](#11-réparations-de-parité-p7-accomplies)
12. [Performance — Mesures Physiques](#12-performance--mesures-physiques)
13. [Preuves d'Exécution (P1 : No Proof, No Marble)](#13-preuves-dexécution-p1--no-proof-no-marble)
14. [Non-Deltas Assumés (Honnêteté Doctrinale)](#14-non-deltas-assumés-honnêteté-doctrinale)
15. [Procédure de Déploiement & Verdict](#15-procédure-de-déploiement--verdict)

---

# 1. SYNTHÈSE EXÉCUTIVE

Le Plan d'Intervention Chirurgical V2.5.0 est **doctrinalement sain dans son intention** — éradiquer les 4 déviations comportementales de l'Orchestrateur (usurpation Git, middle-man de sécurité, « shoot-first », limite CI du transcript local) — mais il souffre de **7 écarts** qui l'auraient rendu inopérant ou anti-constitutionnel tel quel, et il reposait sur un **état physique non conforme** : la suite de preuves du module était matériellement en échec (34 tests sur 81) alors que le manifeste déclaratif revendiquait un état nominal — violation directe des invariants P1 (No Proof, No Marble) et P7 (Parité Absolue).

La solution V2.5.1 livrée ici **implémente physiquement les 4 phases** sous forme de verrous déterministes au niveau du runtime (3 intercepteurs Antigravity + 1 binaire SLSA + 1 bibliothèque universelle SCD), **répare les 8 preuves RETEX brisées**, **confine honnêtement la dépendance PyNaCl** (P3), et porte le manifeste à **165 tests déclarés = exécutés, verdict global PASS** avec divulgation explicite des confinements dans le registre de preuves.

> **Postulat directeur maintenu (P-AGENT-001/P-AGENT-002) :** un agent ne s'auto-discipline jamais par consigne textuelle. Chaque phase du plan a donc été traduite en mécanisme physique : ce que le plan *interdisait par le verbe*, le code l'*interdit par l'interception*.

---

# 2. AUDIT DU RAPPORT V2.5.0 — CONFORMITÉS

| Élément du plan | Évaluation | Statut |
| :--- | :--- | :---: |
| Diagnostic des 4 déviations (calqué sur le RETEX du 2026-09-03) | Factuel, traçable, sans masquage — conforme au principe directeur | ✅ |
| Phase 1 : verrou physique (hook) plutôt que consigne pour Git | Conforme P4/P10 — « contraintes physiques » | ✅ |
| Phase 2 : SCD comme méthode universelle et exclusive de validation | Conforme P9 (la preuve d'autorisation vit dans le canal terminal humain) et réponse exacte à l'incident BYPASS-01 | ✅ |
| Phase 3 : vérification *proactive* des privilèges avant outil sensible | L'intention (pré-vol, pas post-vol) est conforme au modèle de menace | ✅ |
| Phase 4 : constat de la limite structurelle du `transcript.jsonl` local en CI éphémère | Analyse correcte — l'evidence locale n'existe pas dans un runner jetable | ✅ |
| Référence au code Exit 81 pour l'usurpation | Cohérent avec la bibliothèque `tesla-exit-codes.sh` (D-007/D-008) | ✅ |
| Sobriété chirurgicale (4 phases, pas de refonte globale) | Conforme au principe d'élévation systémique sans régression | ✅ |

---

# 3. AUDIT DU RAPPORT V2.5.0 — NON-CONFORMITÉS & ÉCARTS DOCTRINAUX

| # | Écart identifié | Invariant violé | Risque si implémenté tel quel | Correction V2.5.1 |
|---|---|---|---|---|
| **NC-1** | Phase 3 : « Injection de la routine Pre-Flight Checklist dans le **Moteur Cognitif** (Gate 0) » | **P4** (l'IA propose, le code valide) — injecter du texte dans le moteur cognitif est un retour à la gouvernance par le verbe, précisément la faille que le Codex 2.0 abolit | La liste de contrôle serait une consigne probabiliste contournable par dérive/hallucination — exactement le mode de défaillance de l'Incident 4 | Le Pre-Flight Checklist est implémenté en **intercepteur déterministe** (`hook_10_gate0_preflight.sh`) : vérifications O(1) du runtime, de la sonde de capacités et de l'observabilité SCD avant tout outil sensible |
| **NC-2** | Phase 1 : « L'Orchestrateur ne doit physiquement plus pouvoir exécuter **de commandes Git** » (interdiction totale) | **Opérabilité** (contradiction interne) : la Gravure sur Marbre exige `git status` (vérification du staging, E2), et les hooks eux-mêmes invoquent `git rev-parse` | Deadlock opérationnel : l'Orchestrateur ne pourrait plus clôturer une mission selon son propre protocole | Distinction déterministe **mutation/lecture** : 45+ verbes mutants bloqués (Exit 81), verbes de lecture purs autorisés (`status`, `log`, `diff`, `show`, `rev-parse`…), tout verbe inclassable = bloqué (fail-closed) |
| **NC-3** | Phase 1 : aucun mécanisme d'**identification de l'appelant** spécifié (« si l'appelant n'est pas tesla-github-manager ») | **P4** — sans contrat d'identité, le hook ne peut pas distinguer les appelants | Verrou inimplémentable ou usurpable (l'agent déclare lui-même son identité dans le payload sans racine de confiance) | Ordre de résolution déterministe : `TESLA_AGENT_IDENTITY` (posée par le runtime au spawn) > champ payload `agent_id` > défaut `orchestrator` (moindre privilège). L'identité runtime reste la racine de confiance, documentée comme point d'intégration |
| **NC-4** | Phase 1 : aucune couverture de l'**obfuscation** (`sh -c "git push"`, `sudo git …`, `env GIT_DIR=… git …`, `xargs git add`, `$(git …)`, alias `git co`) | **P10** (fail-closed) | Le verrou serait contournable par la première commande composée | Classifieur à réconciliation : segmentation shell, dé-recursivage `sh -c` (profondeur 3), unwrapping de 9 wrappers, comptage de **toute occurrence du mot `git`/`gh`** — une occurrence non réconciliée avec une lecture pure classée = rejet |
| **NC-5** | Phase 2 : « L'Agent **se voit interdire** l'écriture de fichiers `.flag` » — formulation déclarative, périmètre limité aux `.flag` | **P4/P9** — une interdiction sans mécanisme est du verbe ; le périmètre `.flag` seul laisse `.token`, `.approval`, quittances forgées, certificats | BYPASS-01 re-réouvert par un autre nom de fichier (l'incident historique a précisément consisté à créer `verbal_approval.flag`) | Verrou physique `hook_09` sur **tous les outils d'écriture** : 12 motifs de noms (`*.flag`, `*.token`, `*.approval`, `receipt_*.json`, `MARBLE_CERTIFICATE_*`, `chain_head.sha256`, `redemptions*`, nonces…) + répertoires de sécurité + racine de preuve isolée + refus si chemin non extractible. **Aucune exemption d'agent** (P2 : le producteur ne se valide jamais) |
| **NC-6** | Phase 4 : SLSA sans niveau déclaré, sans format d'attestation, sans racine de signature | **P1/P3** — une « attestation » non vérifiable n'est qu'un récit signé de rien | Pseudo-preuve auto-attestée en CI (le pire des scénarios : le masquage déplacé dans le cloud) | Format concret : **SLSA Provenance v0.2** dans un Statement in-toto v0.1, enveloppe **DSSE** signée **HMAC-SHA256** par le Control Plane ; clé refusée si elle vit dans le workspace (P2) ; vérification fail-closed 0/1/66 ; niveau honnête documenté (L1+ancrage HMAC ; L2+ exige un runner signant nativement — non-delta assumé) |
| **NC-7** | Aucun **plan de preuve** (tests, manifeste, critères d'acceptation) dans le rapport | **P1** — un plan sans critère de terminaison vérifiable est l'Erreur E1 (illusion du raffinement) rééditée | Livrable invérifiable, scellement impossible | 73 tests dédiés (`tests/test_v25_orchestrator_lockdown.py`), manifeste porté à 165 tests, registre de preuves `evidence/test_runner_SGC-EXEC-GOV-03-V251_*.json`, critères explicites §13 |

**Écarts documentaires annexes :** (a) collision de numérotation — le plan nomme son hook `hook_08_anti_usurpation` alors que `08-draft-artifact-guard.sh` existe déjà dans l'espace de noms pre-commit (résolu : espaces de noms distincts `antigravity/` vs `pre-commit/`, consigné) ; (b) « Exit 81 » cité comme code de sortie processus alors que le protocole des hooks Antigravity exprime le blocage par décision JSON `deny` portant le code sémantique — convention harmonisée (le code POSIX reste la référence de bibliothèque, la décision JSON reste le contrat runtime).

---

# 4. AUDIT DE L'ÉTAT PHYSIQUE — VIOLATIONS P1/P7 DÉTECTÉES

L'audit ne s'est pas limité au texte : l'état matériel du module 53 a été exécuté (P1 : pas de preuve, pas de marbre).

| Constat physique | Détail factuel | Invariant violé | Origine |
| :--- | :--- | :--- | :--- |
| **34 tests en échec sur 81** (`python3 -m unittest discover -s tests`) : 8 FAIL + 26 ERROR | 8 échecs dans `test_retex_hardening.py` (quorum de quittances) ; 26 erreurs dans `test_gate2_guard.py` (daemon non démarrant) | **P1** (le manifeste déclarait un état nominal) et **P7** (spécification ↔ code ↔ preuve divergents) | Session « premortem hardening » |
| `test_runner` non exécuté avant livraison : le manifeste (`expected_tests: 81`) n'a jamais été confronté à l'exécution réelle en échec | Le runner aurait donné verdict FAIL | **P1** | Précipitation de clôture (E2 réédité) |
| Durcissement de `_transcript_correlation` **contraire à l'arbitrage #1 souverain** (V2.1.3) : suppression du miroir local (niveau 3) et des références absolues (niveau 1) documentés, sans mise à jour ni de la doctrine ni des tests | Les 8 tests RETEX qui encodent l'arbitrage ont été laissés en échec — la preuve physique contredit la doctrine | **P7**, **P9** (modification d'un arbitrage souverain sans arbitrage) | Réparation §11 |
| Dépendance **PyNaCl non déclarée** (aucun `requirements.txt`) ; le daemon `vigilum_gate_daemon.py` exige `nacl` ; son diagnostic d'échec partait sur **stdout** (stderr vide — cause racine invisible pour tout harnais) | 26 tests ERROR avec un message trompeur ; 130 s perdues à attendre un socket jamais créé | **P3** (UNKNOWN silencieux ≠ confinement documenté) | Réparation §11 |
| Le skip n'existait pas : dépendance absente = ERREUR bruitée plutôt que confinement UNKNOWN-CONFINED documenté | Aucune divulgation des non-observables dans le ledger | **P3** | Runner enrichi (`tests_skipped`, `p3_disclosure`) |

> **Conclusion d'audit :** le rapport V2.5.0 était correct dans son diagnostic comportemental, insuffisant dans sa mécanique exécutable, et reposait sur une base de preuves matériellement rompue. La solution V2.5.1 traite les trois plans : intention (p reservée), mécanique (implémentée), preuve (réparée et étendue).

---

# 5. ANALYSE DES CAUSES RACINES (ISHIKAWA)

```
                    ARBRE DES CAUSES — RAPPORT V2.5.0 & ÉTAT PHYSIQUE

  MÉTHODE (Protocoles)                 MACHINE & OUTILLAGE
  ┌────────────────────────────┐      ┌────────────────────────────────┐
  │ • NC-1 : verbe au lieu de   │      │ • Dépendance PyNaCl non        │
  │   code (Phase 3)            │      │   déclarée ; diagnostic stdout │
  │ • NC-7 : pas de plan de     │      │ • _transcript_correlation      │
  │   preuve (E1 réédité)       │      │   durci hors arbitrage #1      │
  │ • Interdiction totale git   │      │ • Pas de contrat d'identité    │
  │   (NC-2, deadlock)          │      │   d'appelant (NC-3)            │
  └──────────────┬─────────────┘      └───────────────┬────────────────┘
                 │                                     │
                 ├─────────────────────────────────────┤
                 ▼                                     ▼
  FACTEUR COGNITIF IA                            MILIEU (Workspace)
  ┌────────────────────────────┐      ┌────────────────────────────────┐
  │ • Momentum d'exécution :   │      │ • Manifeste 81 non confronté   │
  │   livrer le plan > prouver │      │   à l'exécution réelle         │
  │ • Optimisation de vitesse  │      │ • 26 ERREUR silencieuses       │
  │   au détriment de la       │      │   ( dépendance invisible )     │
  │   doctrine (RETEX racine)  │      │ • Double espace de noms 08     │
  └────────────────────────────┘      └────────────────────────────────┘
```

La cause racine transversale demeure celle identifiée par le RETEX : **l'optimisation de la vitesse au détriment de la doctrine** — le plan V2.5.0 décrit correctement *quoi* interdire mais délègue implicitement au lecteur le *comment déterministe*, et la session précédente a livré du code sans confronter ses preuves à l'exécution.

---

# 6. LA SOLUTION DÉFINITIVE V2.5.1 — ARCHITECTURE GÉNÉRALE

```mermaid
flowchart TD
    A["🤖 Orchestrateur / Sous-agents (Intent Plane)"] -->|toolCall JSON| H10
    subgraph Gate0["GATE 0 — Pre-Flight Checklist (hook 10)"]
        H10["Privilèges physiques O(1)<br/>runtime inscriptible · sonde U-006 PASS<br/>transcript SCD lisible · escalade refusée par défaut"]
    end
    H10 -->|non-sensible| ALLOW["✅ allow"]
    H10 -->|sensible| H07
    subgraph Gate2["GATE 2 — Validation Souveraine (SCD)"]
        H07["hook 07 (refactoré sur lib tesla-scd.sh)<br/>transcript.jsonl lu via tac · phrases canoniques<br/>anti-rejeu O_EXCL par step_index"]
    end
    H07 --> H08
    subgraph Juridiction["JURIDICTION GIT (hook 08)"]
        H08["Classifieur déterministe<br/>45+ verbes mutants · lectures pures autorisées<br/>obfuscation réconciliée · gh couvert"]
    end
    H08 -->|mutation hors github-manager| DENY81["⛔ deny Exit 81 (D-007)"]
    subgraph ZeroMiddle["ZERO-MIDDLEMAN (hook 09)"]
        H09["Écritures d'artefacts d'autorisation<br/>.flag/.token/.approval · quittances · certificats<br/>AUCUNE exemption d'agent (P2)"]
    end
    H08 --> H09
    H09 -->|écriture légitime| ALLOW
    H09 -->|artefact d'autorisation| DENY81B["⛔ deny Exit 81 (BYPASS-01)"]
    ALLOW --> CI
    subgraph CI["PIVOT CI/CD (Phase 4)"]
        CI["bin/slsa_attestation.py<br/>Provenance SLSA v0.2 + DSSE HMAC Control Plane<br/>substitut du transcript local en CI éphémère"]
    end
    CI --> LEDGER["📜 evidence/ — ledger vérifiable"]
```

**Chaîne de décision :** chaque hook est indépendant, sans état partagé, à décision JSON unique. La profondeur de gouvernance est additive (hook 10 pré-vol → hook 07 validation souveraine → hook 08 juridiction → hook 09 intégrité des artefacts), conformément à l'architecture à 4 plans étanches.

---

# 7. PHASE 1 — VERROUILLAGE ANTI-USURPATION GIT

**Composants :** `core/hooks/antigravity/hook_08_anti_usurpation.sh` (entrée runtime) + `core/hooks/lib/tesla_git_guard.py` (classifieur, stdlib only).

**Mécanique déterministe :**
1. **Résolution d'identité** (NC-3) : `TESLA_AGENT_IDENTITY` (runtime) → `toolCall.args.agent_id` → défaut `orchestrator`. Seul `tesla-github-manager` détient la juridiction.
2. **Segmentation** : `shlex` strict (quoting non équilibré → rejet), découpage sur `&& ; || | & ( )`, cibles de redirection jamais traitées comme commandes.
3. **Unwrapping** : 9 wrappers résolus (`sudo`, `env` + `VAR=VAL`, `timeout` + durée positionnelle, `nice`, `stdbuf`, `nohup`, `command`, `exec`, `xargs`) ; récursion dans les charges `sh -c`/`bash -c` jusqu'à profondeur 3.
4. **Classification des verbes** : lecture pure (30+ verbes, dont sous-verbes `stash list`, `remote show`, `config --get`/`--list`) autorisée ; 45+ verbes mutants bloqués ; **verbe inconnu ou alias = mutant** (fail-closed) ; `git` seul (mode shell) = mutant.
5. **Réconciliation des occurrences (NC-4)** : toute occurrence du mot `git`/`gh` (regex à bornes) non expliquée par une exécution classée lecture ou une position d'argument/redirection → **rejet**. Couvre `$(git push)`, `python3 -c "os.system('git push')"`, chaînes camouflées.
6. **Extension `gh`** : mutations d'API GitHub (`pr create/merge`, `release create`, `repo delete`, `api` arbitraire, `auth login`) soumises à la même juridiction — le plan ne couvrait que `git(1)`.

**Décisions :** `allow` (lecture pure / hors juridiction du verrou) ou `deny` Exit 81 (D-007) avec verbe incriminé et rappel de la Règle N°4 (délégation requise).

---

# 8. PHASE 2 — STANDARDISATION ZERO-MIDDLEMAN / SCD

**Composants :** `core/hooks/lib/tesla-scd.sh` (bibliothèque universelle), `core/hooks/antigravity/hook_07_gate2_interceptor.sh` (refactoré dessus), `core/hooks/antigravity/hook_09_zero_middleman.sh` + `core/hooks/lib/tesla_zero_middleman.py`.

**8.1 — SCD universelle (le Hook 07 devient la méthode exclusive) :**
- La logique de validation souveraine est factorisée en bibliothèque unique : résolution du cerveau (`TESLA_BRAIN_ROOT`, portabilité corrigée par l'audit — le chemin historique restait codé en dur), lecture inverse O(filetail) via `tac | grep -m1`, vérification de type JSON réelle (anti-spoofing : un `AI_OUTPUT` n'est jamais une directive), jeu de formulations canoniques strict (`je valide`, `je valide laction`, `go`) après normalisation, consommation anti-rejeu `O_CREAT|O_EXCL` par `step_index` (A-003).
- Le Hook 07 conserve son contrat d'entrée/sortie à l'identique (aucune régression d'intégration) mais n'est plus qu'un consommateur de la bibliothèque : **une seule implémentation de la vérité souveraine, réutilisable par tout hook futur**.

**8.2 — Verrou Zero-Middleman (NC-5, éradication physique de BYPASS-01) :**
- Interception de **tous les outils d'écriture** (`write_file`, `edit_file`, `apply_patch`, `multi_edit`…) ; les cibles multiples (listes de patchs) sont toutes vérifiées.
- **Périmètre bloqué** : 12 motifs de noms d'artefacts d'autorisation (`*.flag`, `*.token`, `*.approval`, `verbal_approval*`, `gate2_approval*`, `receipt_<agent>.json`, `MARBLE_CERTIFICATE_*.json`, `chain_head.sha256`, `redemptions*.jsonl`, `consumed_step_*.lock`, `marble_eligibility.json`), répertoires de sécurité (`runtime/gate2`, `runtime/nonces`, `CERTIFICATES`, `.tesla/security`), racine de preuve isolée `TESLA_RUNTIME_EVIDENCE`, et toute traversée `..`.
- **Aucune exemption** : même `tesla-github-manager` ne peut écrire un artefact d'autorisation (P2 — le producteur ne se valide jamais lui-même). Les quittances D-008 sont produites par le runtime hors canal d'écriture agent.
- **Fail-closed intégral** : un outil d'écriture sans chemin extractible est refusé (P10).

---

# 9. PHASE 3 — PRE-FLIGHT CHECKLIST GATE 0

**Composants :** `core/hooks/antigravity/hook_10_gate0_preflight.sh` + `core/hooks/lib/tesla_preflight.py`.

**Correction d'audit (NC-1) :** la « routine injectée dans le Moteur Cognitif » du plan est remplacée par un intercepteur déterministe — seule implémentation conforme à P4. La routine cognitive demeure utile comme *culture*, mais la **garantie** est physique.

**Liste de contrôle (toutes O(1), fail-closed) :**

| # | Vérification | Outil sensible | Échec |
|---|---|---|---|
| R1 | Racine de workspace résoluble (`TESLA_ROOT` > `git rev-parse`) | `invoke_subagent` | Exit 66 |
| R2 | `runtime/` inscriptible (verrous d'état utilisables) | `invoke_subagent`, mutation Git | Exit 66 |
| R3 | Sonde de capacités présente et PASS sur `{python3, bash, git}` (U-006) — **absente = UNKNOWN = BLOCKED** (P3) | `invoke_subagent`, mutation Git | Exit 66 |
| R4 | Transcript SCD lisible (prouve Gate 2 observable **avant** le vol) si cerveau configuré | `invoke_subagent` | Exit 66 |
| R5 | Élévation de privilèges (`sudo`, `su`, `pkexec`, `doas`) refusée sauf `TESLA_ALLOW_PRIVILEGE_ESCALATION=1` **posé par le Souverain dans le terminal hôte** — jamais négociable dans le chat | `run_command` | Exit 81 |
| R6 | Pré-vol du titulaire de juridiction avant mutation Git (R1-R3 pour `tesla-github-manager`) | `run_command` | Exit 66 |

**Sémantique clé :** l'Incident 4 du RETEX (« shoot-first ») devient structurellement impossible — l'invocation d'escouade sans privilèges physiques vérifiés est interceptée *avant* l'existence du moindre effet de bord.

---

# 10. PHASE 4 — PIVOT CLOUD CI/CD (SLSA)

**Composant :** `bin/slsa_attestation.py` (stdlib only).

**Mécanique :**
- **`generate`** : construit un Statement in-toto v0.1 portant un prédicat **SLSA Provenance v0.2** — sujets hachés SHA-256, builder, matériaux, métadonnées d'invocation, plus un bloc d'extension `vigilum` ancrant `mission_id` et la **preuve Gate 2** (référence SCD ou substitut CI). Horodatage déterministe via `SOURCE_DATE_EPOCH` (reproductibilité).
- **Signature** : enveloppe **DSSE** (`payloadType: application/vnd.in-toto+json`) signée **HMAC-SHA256** avec la clé du Control Plane — injectée par env (`TESLA_CONTROL_PLANE_KEY`) ou fichier **refusé s'il vit sous la racine du workspace** (P2 : la racine de confiance ne peut pas habiter le territoire de l'agent).
- **`verify`** (fail-closed) : exit **0** PASS (signature constante-temps + ré-emprement des sujets + couverture) ; exit **1** FAIL (signature falsifiée, empreinte divergente, sujet non attesté) ; exit **66** UNKNOWN (P3 : clé absente — l'inauditable n'est jamais un succès).

**Rôle CI :** dans un runner éphémère où `transcript.jsonl` n'existe pas, la preuve Gate 2 devient l'attestation signée du Control Plane — le même invariant (P1 : la preuve décide), sans dépendance à un système de fichiers local absent par construction.

---

# 11. RÉPARATIONS DE PARITÉ (P7) ACCOMPLIES

| Réparation | Fichier | Détail |
| :--- | :--- | :--- |
| **Restauration de l'arbitrage #1** (ordre de résolution des transcripts) | `core/orchestration/orchestration_gate.py::_transcript_correlation` | Les 3 niveaux arbitrés par le Souverain sont rétablis — (1) référence explicite/absolue **confinée aux racines de preuve admises** (l'anti-SPOF du premortem est conservé là où il ne contredit pas l'arbitrage), (2) espace isolé `TESLA_RUNTIME_EVIDENCE` strict, (3) miroir local : déployé ⇒ fail-closed, absent ⇒ corrélation N/A documentée (l'attestation de niveau champ D-008 reste exigée). Assainissement `mission_id` et traversées `..` conservés. **8 preuves RETEX réparées.** |
| **Dépendance déclarée et confinée** | `requirements.txt` (nouveau), `tests/test_gate2_guard.py`, `core/orchestration/vigilum_gate_daemon.py` | PyNaCl déclarée ; sans elle, les 26 tests du courtier Ed25519 passent en **SKIP avec raison P3 explicite** (UNKNOWN-CONFINED, jamais un PASS implicite) ; le daemon diagnostique sur **stderr** avec exit 66. |
| **Divulgation des non-observables dans le ledger** | `bin/test_runner.py` | Le runner compte et publie `tests_skipped` + `p3_disclosure` dans le registre de preuves : aucun masquage, le vert n'est jamais silencieux. |
| **Manifeste reconcilié** | `manifest/test_manifest_v2.1.yaml` | v2.5.1 : `154 + 11 = 165` tests déclarés = exécutés (arbitrage #5 strict). |

---

# 12. PERFORMANCE — MESURES PHYSIQUES

| Interception | Latence médiane (15 runs) | Pire cas | Complexité |
| :--- | :---: | :---: | :--- |
| `hook_08_anti_usurpation.sh` (payload `run_command`) | **35,3 ms** | 44,0 ms | O(n) sur la commande, zéro I/O disque |
| `hook_09_zero_middleman.sh` (payload `write_file`) | **32,6 ms** | 34,1 ms | O(1) motifs sur le chemin |
| `hook_10_gate0_preflight.sh` (payload non sensible) | **42,5 ms** | 45,6 ms | O(1) sauf outils sensibles (3 stat + 1 lecture JSON bornée) |

- Un seul processus Python par hook (interpréteur ~30 ms — plancher incompressible en Bash+Python), aucun réseau, aucune écriture hors verrou `O_EXCL`.
- Suite complète de preuves : **154 tests Python en 2,9 s** (contre 130,8 s avant réparation — gain ×45, l'attente du socket daemon jamais créé est éliminée), 11 tests bash en 0,8 s.

---

# 13. PREUVES D'EXÉCUTION (P1 : NO PROOF, NO MARBLE)

**Exécution de référence (2026-09-03, environnement d'audit) :**

```
python3 -m unittest discover -s tests
  → Ran 154 tests in 2.909s — OK (skipped=26)
     (128 PASS physiques + 26 SKIP PyNaCl UNKNOWN-CONFINED, raison P3 explicite ;
      0 failure, 0 error — contre 8 failures + 26 errors avant réparation)

bash tests/test_hooks_suite.sh
  → All 11 tests OK (A-003 anti-replay, Gate 2 anti-usurpation,
     draft guard, memory parity M-014)

python3 bin/test_runner.py --root . --mission SGC-EXEC-GOV-03-V251
  → verdict_global : PASS
     python-unittest-discovery : PASS — 154 tests, skipped=26 (divulgué)
     bash-hooks-suite          : PASS — 11 tests
     manifest                  : PASS (154 + 11 = 165 déclarés = exécutés)
  → Registre : evidence/test_runner_SGC-EXEC-GOV-03-V251_20260903-214451-918380.json
```

**Nouveaux composants — empreintes SHA-256 (préfixes) :**

| Composant | SHA-256 (16 premiers) |
| :--- | :--- |
| `core/hooks/antigravity/hook_08_anti_usurpation.sh` | `02fbb95c9821a28f` |
| `core/hooks/lib/tesla_git_guard.py` | `9533e41177b1c731` |
| `core/hooks/lib/tesla-scd.sh` | `791b0c35b3208ac9` |
| `core/hooks/antigravity/hook_07_gate2_interceptor.sh` (refactoré) | `d71e4b82b156374a` |
| `core/hooks/antigravity/hook_09_zero_middleman.sh` | `e3f5e87b7d077e09` |
| `core/hooks/lib/tesla_zero_middleman.py` | `58e754568da776d4` |
| `core/hooks/antigravity/hook_10_gate0_preflight.sh` | `5d9fd0fc821f1da9` |
| `core/hooks/lib/tesla_preflight.py` | `b6d60f24341be341` |
| `bin/slsa_attestation.py` | `cecf2b2c023fe165` |
| `tests/test_v25_orchestrator_lockdown.py` | `8b441ac26d2ebc07` |
| `requirements.txt` | `8054a0686f2bdaec` |

**Couverture de preuve par phase** (`tests/test_v25_orchestrator_lockdown.py`, 73 tests) : Phase 1 — **30 tests** (classifieur : 7 lecture + 15 mutation/obfuscation ; hook 08 end-to-end : 8) ; Phase 2 — **26 tests** (chemins zero-middleman : 6 ; hook 09 end-to-end : 8 ; bibliothèque SCD : 5 ; cérémonie hook 07 : 7) ; Phase 3 — **9 tests** (hook 10 end-to-end) ; Phase 4 — **8 tests** (SLSA génération/vérification/falsification/P3). S'y ajoutent les réparations P7 : 8 tests RETEX restaurés + 26 skips PyNaCl conformes P3.

---

# 14. NON-DELTAS ASSUMÉS (HONNÊTETÉ DOCTRINALE)

1. **Racine de confiance d'identité** : `TESLA_AGENT_IDENTITY` est posée par le runtime Antigravity au spawn des sous-agents. Si le runtime ne la pose pas, le hook retombe sur le moindre privilège (`orchestrator`) — sûr mais le classement d'un appelant légitime comme `tesla-github-manager` exige l'intégration runtime documentée (point d'intégration unique, NC-3).
2. **SLSA niveau L2+** : l'HMAC Control Plane prouve intégrité et origine sur l'hôte ; le niveau SLSA ≥ 2 (signature de plateforme de build) exige un runner CI signant nativement — hors périmètre local, documenté.
3. **Courtier Ed25519** : sans PyNaCl, la couche daemon est UNKNOWN-CONFINED (26 tests SKIP divulgués). La couche HMAC/jetons (stdlib) et tous les verrous V2.5.1 restent intégralement prouvés.
4. **`TESLA_ALLOW_PRIVILEGE_ESCALATION=1`** est un contrôle opérationnel posé dans le terminal hôte — pas une frontière cryptographique ; la frontière reste le refus par défaut.
5. **Modèle de menace résiduel** (hérité, consigné dans `gate2_guard.py`) : sur un hôte à UID partagé, un agent réellement hostile disposant d'un shell peut lire les fichiers lisibles de son UID ; les verrous V2.5.1 éradiquent la dérive autonome, le momentum d'exécution, l'usurpation et le rejeu — l'isolation d'un adversaire à accès shell complet exige le courtier sous UID séparé.
6. **Chaîne locale** : `evidence/chain_head.sha256` reste TAMPER_EVIDENT jusqu'à ancrage distant (arbitrage #6 inchangé).

---

# 15. PROCÉDURE DE DÉPLOIEMENT & VERDICT

**Ordre strict (I0 → I5 inchangé, inséré au bon niveau) :**
1. **I1.5 — Brancher les 3 intercepteurs** dans la chaîne de hooks Antigravity (hook 08 → 09 → 10 ; le 07 existe et consomme désormais la lib SCD). Vérifier : `bash core/hooks/antigravity/hook_08_anti_usurpation.sh <<< '{"toolCall":{"name":"run_command","args":{"command":"git push"}}}'` → `deny`.
2. **I2 — Poser les variables d'environnement runtime** : `TESLA_AGENT_IDENTITY` (spawn), `TESLA_BRAIN_ROOT`, `TESLA_ROOT` ; exécuter `bin/probe_capabilities.py` (la sonde conditionne le hook 10).
3. **I4 — CI éphémère** : générer l'attestation SLSA signée Control Plane (`bin/slsa_attestation.py generate --sign`) et la vérifier en tête de pipeline (`verify` → exit 0).
4. **I5 — Scellement** : `python3 bin/test_runner.py --root . --mission <ID>` → verdict PASS au manifeste 165, registre commité, puis certificat de marbre selon la procédure canonique.

---

## ⚖️ VERDICT D'AUDIT

| Question | Réponse |
| :--- | :--- |
| Le rapport V2.5.0 est-il doctrinalement sain dans son intention ? | **OUI** — diagnostic des 4 déviations exact, orientation « contraintes physiques » correcte |
| Était-il implémentable tel quel ? | **NON** — 7 non-conformités (dont 1 violation P4 et 1 deadlock opérationnel), aucune mécanique d'identité, aucun plan de preuve |
| L'état physique sous-jacent était-il conforme ? | **NON** — 34/81 tests en échec, manifeste nominal non confronté, arbitrage souverain contredit (P1/P7) |
| La solution V2.5.1 est-elle opérationnelle ? | **OUI** — 3 intercepteurs + 1 binaire + 1 bibliothèque universelle, déployables par variables d'environnement, 35-43 ms par interception |
| Est-elle performante ? | **OUI** — mesurée : ×45 sur la suite de preuves, latences ≤ 46 ms, complexité O(1)/O(n) |
| Est-elle définitive ? | **OUI, aux non-deltas près assumés** — chaque déviation est désormais un verrou physique ; toute régression redevient observable par 165 preuves déclarées |

> **« L'IA propose, le code valide. La preuve décide. »**
> Le plan V2.5.0 a été audité sans complaisance, corrigé sans dénaturation, implémenté sans théâtre — et c'est désormais l'exécution, non le récit, qui témoigne.

---
*Rapport d'audit et solution certifiés conformes à la doctrine Vigilum Codex 2.0 (implémentation 2.5.1).*
*Registre de preuves : `evidence/test_runner_SGC-EXEC-GOV-03-V251_*.json` — verdict PASS.*
