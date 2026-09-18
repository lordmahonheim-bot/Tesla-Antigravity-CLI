# PLAN-QUOTIDIEN — 12 tâches d'ingénierie en adéquation avec le profil

![Status](https://img.shields.io/badge/Status-PROPOSAL%20V1-orange) ![Ecosystem](https://img.shields.io/badge/Ecosystem-TESLA%20ANTIGRAVITY-purple) ![Doctrine](https://img.shields.io/badge/Doctrine-NO%20PROOF%2C%20NO%20PASS-red) ![Charge](https://img.shields.io/badge/Charge-%3C%205h%2Fsemaine-blue)

| Paramètre | Valeur |
| :--- | :--- |
| **Version** | 1.0.0 |
| **Date du diagnostic** | 2026-09-17 |
| **Base d'audit** | `main` @ `eedce00` (13/09/2026) |
| **Destinataire** | Abdellah MOUHTAJ / LORD Mahonheim |
| **Objet** | Liste de tâches de programmation alignée sur le profil réel |
| **Priorité retenue** | Brancher le quotidien |
| **Charge cible** | < 5 h/semaine de **votre** temps (l'agent exécute) |
| **Doctrine d'ancrage** | Gravure sur Marbre 2.0 · Loi de Parité Absolue 2.0.0 · Conducteur Absolu v3.2.1 |
| **Preuve d'état courante** | `bash tools/quotidien_status.sh --tests` → **BLOCK** (voir §2) |

---

## 0. Comment lire ce document

Le §1 établit **qui vous êtes techniquement** à partir de preuves du dépôt (pas d'auto-déclaration).
Le §2 est le **diagnostic** : 8 constats, chacun reproductible par une commande.
Le §3 est **la liste** : 12 tâches en 4 blocs. Chaque tâche contient un **prompt agent prêt à coller** et une **preuve d'acceptation en une seule commande**.
Le §4 est le **planning** sur 8 semaines. Le §5 dit **ce que ce plan ne fait pas**.

> **Règle de lecture :** vous ne codez aucune de ces tâches. Vous **arbitrez**, vous **validez**, vous **exécutez la commande de preuve**. L'agent produit le reste. C'est votre politique NO-code / Low-code, appliquée à la lettre.

---

## 1. Votre profil d'ingénierie, déduit du dépôt

### 1.1 Ce que les faits établissent

| # | Fait vérifié | Source |
| :--- | :--- | :--- |
| P1 | **Vous ne codez pas** — politique explicite : *« NO-code, Low-code »*, positionnement de non-développeur | `ABOUT_ME.md` §1 |
| P2 | **Vous gouvernez** — architecte de connaissance gouvernée, opérateur de projets IA locaux | `ABOUT_ME.md` §5 |
| P3 | **Vous enseignez** — la pédagogie est le principe dominant ; explication, progression, justification des choix | `ABOUT_ME.md` §7 |
| P4 | **Vous exigez la preuve** — rejet des actions non vérifiées, des modifications silencieuses, des solutions sans rollback | `ABOUT_ME.md` §10 |
| P5 | **Vous produisez de la doctrine** — 59 dossiers de module sur disque, dont **28 sans une seule ligne exécutable** (47 %) | `tools/quotidien_status.sh` §3 |
| P6 | **Vous exécutez peu, mais avec exigence** — le module 53 porte à lui seul 27 `.py` + 23 `.sh` | comptage disque |
| P7 | **Votre force est normative** — 2 protocoles canoniques, 7 Gates, 8 phases, 10 principes | `PROTOCOLES/`, `GENESE-v1/` |
| P8 | **Votre risque est l'écart** — doctrine abondante, exécution rare, preuve non reproductible | §2 ci-dessous |

### 1.2 Le profil d'ingénierie qui en résulte

> **Vous êtes un ingénieur de la preuve, pas un ingénieur du code.**
> Votre valeur ajoutée est la **vérité vérifiable** : décider ce qui est admis, tracer ce qui est fait, certifier ce qui est publié.
> Le code n'est pour vous qu'un instrument au service de cette fonction.

**Conséquence directe sur la forme des tâches** — sept règles de conception appliquées à chacune des 12 tâches :

1. **Aucune tâche n'exige d'écrire du code vous-même.**
2. **Chaque tâche se termine par une commande unique** produisant PASS ou FAIL.
3. **Chaque tâche produit un artefact nommé**, versionnable, citable.
4. **Chaque tâche respecte P5 (No Self-Evidence)** : l'agent produit, vous validez — jamais le même acteur.
5. **Chaque tâche est réversible** : rollback explicite, jamais de suppression silencieuse (P8).
6. **Chaque tâche s'inscrit dans un Gate** existant du Conducteur Absolu (aucun protocole parallèle).
7. **Chaque tâche tient en 30 à 90 minutes de votre temps.**

---

## 2. Diagnostic — 8 constats vérifiés

Tous les constats ci-dessous sont **reproductibles** sur un clone propre. Aucun n'est une opinion.

### C1 — La baseline de gouvernance n'est pas verte sur clone propre 🔴 **bloquant**

```bash
cd 53-Vigilum-Codex-2.0-Executable-Governance && python3 bin/test_runner.py; echo "exit=$?"
```

| Mesure | Résultat observé |
| :--- | :--- |
| `verdict_global` | **FAIL** |
| `exit_code` | **1** |
| tests Python | 183 exécutés · **13 en échec** · 26 ignorés |
| suite bash hooks | 11 tests · PASS |
| cause racine | `Gate R FATAL — secret.key not found at ~/.tesla/gate2/secret.key` |

Les 13 échecs vivent tous dans `tests/test_v26_gate_r_and_staging.py` (Gate R — Evidence Reconciliation, P11).
**Fait aggravant :** avec `pynacl` installé, les **26 SKIP disparaissent** mais les **13 échecs demeurent** — ce ne sont donc pas les mêmes causes, et seul le SKIP est déclaré (`OI-03`). Les 13 échecs ne figurent dans **aucun registre**.
**Fait aggravant 2 :** `53-.../README.md` conclut `VERDICT: EXECUTABLE GOVERNANCE OPERATIONAL & PROVEN` et sa section « Running the Full Test Suite » ne cite que **2 suites sur 6** — celles qui passent. *« L'absence d'erreur n'est pas le succès » (P4).*

### C2 — Le registre canonique est désynchronisé 🔴

```bash
bash tools/quotidien_status.sh
```

| Écart | Détail |
| :--- | :--- |
| Déclaré mais absent | `13-Jules-Cloud-Integration` (dans `list.txt` **et** dans le `README.md`) |
| Présent mais non déclaré | `59-Antigravity-Workspace-MCP`, `60-WikiSkill-Ouroboros` |
| Bilan | 58 déclarés · 57 résolus · 2 non déclarés |

Violation frontale de **P6 (parité bidirectionnelle)** : amnésie *et* fantôme simultanés.

### C3 — La référence canonique du moteur décisionnel est cassée 🔴

```
GENESE-v1/AGENTS.md:58    ->  memory/Le_Conducteur_Absolu_v3.2.1.md
GENESE-v1/GEMINI.md:124   ->  memory/Le_Conducteur_Absolu_v3.2.1.md
Réalité disque            ->  memory/            N'EXISTE PAS
Copie réelle              ->  51-Conducteur-Absolu-v3.2.1/Le_Conducteur_Absolu_v3.2.1.md
```

La **couche de gouvernance opérationnelle** (celle que l'agent lit en premier) ordonne de suivre les 7 Gates d'un fichier qui n'est pas là où elle l'affirme. GATE 0 (`AUTHORITY & RELOAD COGNITIF`) est donc non résoluble en l'état.

### C4 — La CI ne prouve rien 🟠

`.github/workflows/` contient **un seul workflow**, `mirror-guard.yml` : il échoue si une PR touche `LEARN/` ou `PROTOCOLES/`. C'est un garde-fou de miroir, **pas une preuve**. Aucun test, aucun lint, aucun audit de parité n'est exécuté à la publication.

### C5 — Les automatisations déclarées pointent des ressources inexistantes 🔴

| Déclaration | Réalité |
| :--- | :--- |
| `28-Loop-Engineering/justfile` → `avalon-daemon.service`, `avalon-watcher.path`, `avalon-maintenance.timer` | **aucun** de ces 3 fichiers n'existe dans le dépôt |
| `23-Architecture-Entr/justfile:watch` → `tools/capability_bus/capability_dispatcher.sh` | répertoire `tools/capability_bus/` inexistant |
| `23-Architecture-Entr/justfile:watch` → `find memory/` | `memory/` inexistant (cf. C3) |

La mémoire croit en des ressources qui n'existent pas → **fantôme**, donc **BLOCK** au sens de la Loi de Parité.

### C6 — Le moteur de veille ne produit rien 🟠

`36-Veille-Strategique/watch.sh` déclare lui-même que son déclencheur est un placeholder :
> *« Remplacez la commande "echo ..." par votre trigger Alexandria, rsync ou git commit. »*

Il dépend de `entr`, **absent de l'environnement**. `Highlights-Outputs/` et `Strategic-Outputs/` ne contiennent qu'un `README.md`. La veille — cœur de votre branche « Intelligence Stratégique » — est outillée mais **stérile**.

### C7 — Le pont SPARK ↔ MIDGARD est un fichier unique 🟠

`58-Spark-MCP-Gateway/` = **1 seul `.py`**, sans `requirements.txt`, sans lanceur, sans test. `59-Antigravity-Workspace-MCP/` = **0 ligne exécutable**, seulement 2 rapports. Or c'est ce pont qui relierait vos déclencheurs cloud (Gemini Spark) à votre vérité locale.

### C8 — Les décisions différées attendent un signal 🟡

`OUTPUTS/open_items_todo-Updated.md` : **OI-01** (CI SLSA, différé), **OI-02** (gravure de l'invariant anti-friction, en attente souveraine), **OI-03** (courtier Ed25519, 26 tests SKIP). La PR **#4** (WikiSkill Ouroboros, self-test annoncé 14/14) est ouverte depuis le 13/09 sans fusion. La PR **#3** (dependabot `pynacl>=1.6.2`) a été **fermée sans fusion** — alors que le même dépôt subit un SKIP de 26 tests pour cette exacte dépendance.

---

## 3. La liste — 12 tâches en 4 blocs

### Vue d'ensemble

| ID | Tâche | Bloc | Issue GitHub | Votre temps | Dépend de |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Q1** | Rendre la baseline de gouvernance verte sur clone propre | A — Vérité | [#5](https://github.com/lordmahonheim-bot/Tesla-Antigravity-CLI/issues/5) | 60 min | — |
| **Q2** | Réparer la parité du registre et la référence canonique | A — Vérité | [#6](https://github.com/lordmahonheim-bot/Tesla-Antigravity-CLI/issues/6) | 45 min | — |
| **Q3** | Transformer le README en preuve : CI « Vérité du dépôt » | A — Vérité | [#7](https://github.com/lordmahonheim-bot/Tesla-Antigravity-CLI/issues/7) | 45 min | Q1, Q2 |
| **Q4** | Veille quotidienne qui produit réellement (module 36) | B — Quotidien | [#8](https://github.com/lordmahonheim-bot/Tesla-Antigravity-CLI/issues/8) | 75 min | Q3 |
| **Q5** | Mémoire de session automatique (03 → 02) | B — Quotidien | [#9](https://github.com/lordmahonheim-bot/Tesla-Antigravity-CLI/issues/9) | 60 min | Q4 |
| **Q6** | Chaîne de preuves quotidienne consultable (60) | B — Quotidien | [#10](https://github.com/lordmahonheim-bot/Tesla-Antigravity-CLI/issues/10) | 60 min | Q9 |
| **Q7** | Pont SPARK ↔ MIDGARD — décision + option A | B — Quotidien | [#11](https://github.com/lordmahonheim-bot/Tesla-Antigravity-CLI/issues/11) | 75 min | Q1 |
| **Q8** | Pack Schedules Spark (6 déclencheurs) | C — Souverain | [#12](https://github.com/lordmahonheim-bot/Tesla-Antigravity-CLI/issues/12) | 45 min | Q7 |
| **Q9** | Fusionner la PR #4 (WikiSkill Ouroboros) sous Gravure | C — Souverain | [#13](https://github.com/lordmahonheim-bot/Tesla-Antigravity-CLI/issues/13) | 30 min | Q1, Q3 |
| **Q10** | Débloquer OI-03 : courtier Ed25519 (pynacl) | C — Souverain | [#14](https://github.com/lordmahonheim-bot/Tesla-Antigravity-CLI/issues/14) | 45 min | Q1 |
| **Q11** | Réparer ou déférer les fantômes d'automatisation (C5) | D — Consolidation | [#15](https://github.com/lordmahonheim-bot/Tesla-Antigravity-CLI/issues/15) | 60 min | Q2 |
| **Q12** | Tableau de bord unique + clôture de version | D — Consolidation | [#16](https://github.com/lordmahonheim-bot/Tesla-Antigravity-CLI/issues/16) | 60 min | Q4→Q11 |

**Les 12 tâches sont publiées comme issues GitHub actionnables** — libellés `quotidien`, `preuve`, `parite`, `gouvernance`, `decision-souveraine`, jalon **« Quotidien V1 — 12 tâches »** (échéance 12/11/2026). Chaque issue contient le constat, le livrable, la preuve d'acceptation et le prompt agent prêt à coller.

**Total : ≈ 11 h de votre temps** étalées sur 8 semaines → **≈ 1 h 20 / semaine**, très en deçà de votre plafond de 5 h.

---

## BLOC A — VÉRITÉ *(prérequis non négociable)*

> **Pourquoi ce bloc en premier ?** Parce que votre doctrine l'impose : *No Proof, No Parity, No Publish*. Automatiser le quotidien sur une base dont la preuve n'est pas reproductible revient à industrialiser une incertitude. Ces trois tâches ne demandent aucune compétence algorithmique : ce sont des tâches de **gouvernail**.

---

### Q1 — Rendre la baseline de gouvernance verte sur clone propre

| Champ | Contenu |
| :--- | :--- |
| **Objectif** | Qu'un clone neuf, sans votre machine, reproduise un verdict PASS. |
| **Adéquation** | Tâche 100 % gouvernance : portabilité d'une ancre de confiance + honnêteté d'un verdict. Zéro logique métier. |
| **Constat** | C1 — `test_runner.py` → FAIL, 13 échecs, `secret.key not found` |
| **Livrable** | 1. `docs/` ou `deploy/` : procédure déterministe de la clé Control Plane. 2. `bin/gate_r.py` : accepter `--key-file` / `TESLA_CONTROL_PLANE_KEY` (comme `slsa_attestation.py` le fait déjà). 3. `README.md` §5 : les **6** suites listées, pas 2. 4. Registre des 13 échecs si l'un reste non résoluble (P8). |
| **Preuve d'acceptation** | `bash tools/quotidien_status.sh --tests` → `VERDICT : PASS` et `exit 0` |
| **Votre rôle** | Trancher **une** question : la clé de test doit-elle être *générée à la volée* (déterministe, CI-compatible) ou *injectée en secret* (souveraine, CI-dépendante) ? Recommandation de l'audit : génération à la volée pour la CI + injection souveraine pour la production. |
| **Risque** | Toucher `gate_r.py` = toucher une ancre. Rollback : `git revert <sha>`. La clé de production hors workspace n'est jamais déplacée. |
| **Durée** | 1 session (60 min de votre temps) |

**Prompt agent prêt à coller :**
```text
Mission Q1 — Baseline de gouvernance reproductible.
Contexte : bin/test_runner.py du module 53 retourne exit 1 avec 13 échecs
sur tests/test_v26_gate_r_and_staging.py. Cause racine prouvée :
"Gate R FATAL — secret.key not found at ~/.tesla/gate2/secret.key".
Contraintes : (1) ne jamais déplacer la clé souveraine hors workspace ;
(2) P3 : un état indéterminé n'est jamais un PASS ;
(3) P8 : aucune suppression silencieuse — tout échec non résolu est inscrit au registre.
Livrables : procédure de clé déterministe pour environnement propre ;
support --key-file / TESLA_CONTROL_PLANE_KEY dans bin/gate_r.py ;
section tests du README corrigée (6 suites listées) ; registre des déférés mis à jour.
Après action : exécute `bash tools/quotidien_status.sh --tests` et colle la sortie brute.
Interdiction : modifier un test pour le faire passer sans corriger la cause.
```

---

### Q2 — Réparer la parité du registre et la référence canonique

| Champ | Contenu |
| :--- | :--- |
| **Objectif** | `list.txt`, le disque, le `README.md` et les couches d'identité racontent **la même vérité**. |
| **Adéquation** | C'est littéralement la **Loi de Parité Absolue** que vous avez écrite. Tâche d'arbitrage documentaire. |
| **Constat** | C2 (13 absent / 59-60 non déclarés) + C3 (`memory/` inexistant référencé par AGENTS.md et GEMINI.md) |
| **Livrable** | 1. `list.txt` exact. 2. `README.md` — layout conforme au disque. 3. Décision tracée sur le canon de `Le_Conducteur_Absolu_v3.2.1.md`. 4. Ligne de traçabilité dans `OUTPUTS/open_items_todo-Updated.md`. |
| **Preuve d'acceptation** | `bash tools/quotidien_status.sh` → sections **1** et **2** en `[PASS]`, `exit 0` |
| **Votre rôle** | Décision souveraine : `13-Jules-Cloud-Integration` est-il **retiré du registre** (déféré tracé, P8) ou **restauré** ? Recommandation de l'audit : retrait tracé — le dossier n'existe pas, et le README le présente à tort comme livré. |
| **Risque** | Faible (documentation). Rollback : `git revert`. |
| **Durée** | 45 min |

**Prompt agent prêt à coller :**
```text
Mission Q2 — Parité canonique.
Écarts prouvés par `bash tools/quotidien_status.sh` :
 - list.txt déclare 13-Jules-Cloud-Integration : dossier ABSENT du disque
 - 59-Antigravity-Workspace-MCP et 60-WikiSkill-Ouroboros : présents NON déclarés
 - GENESE-v1/AGENTS.md:58 et GENESE-v1/GEMINI.md:124 référencent
   memory/Le_Conducteur_Absolu_v3.2.1.md — chemin inexistant
   (copie réelle : 51-Conducteur-Absolu-v3.2.1/Le_Conducteur_Absolu_v3.2.1.md)
Contraintes : P6 parité bidirectionnelle ; P8 aucune suppression silencieuse.
Pour tout retrait ou redirection, écrire la ligne de traçabilité dans
OUTPUTS/open_items_todo-Updated.md avec condition de réveil.
Après action : exécute `bash tools/quotidien_status.sh` et colle la sortie brute.
N'invente aucune décision souveraine : si un arbitrage t'est nécessaire, pose la question.
```

---

### Q3 — Transformer le README en preuve : CI « Vérité du dépôt »

| Champ | Contenu |
| :--- | :--- |
| **Objectif** | Aucune publication ne passe si la vérité du dépôt n'est pas démontrée. |
| **Adéquation** | C'est votre métier : passer d'une **promesse documentaire** à une **preuve reproductible**. L'actif de crédibilité le plus fort du dépôt. |
| **Constat** | C4 (un seul workflow, garde de miroir) + C1 (README « PROVEN » alors que le runner échoue) |
| **Livrable** | `.github/workflows/verite-du-depot.yml` exécutant `tools/quotidien_status.sh --tests` sur `ubuntu-latest`, **sans la clé souveraine** — donc en environnement propre, exactement là où Q1 doit avoir rendu le verdict vert. Sortie brute archivée en artefact. |
| **Preuve d'acceptation** | Onglet **Actions** vert sur la PR de test + l'artefact de preuve téléchargeable. |
| **Votre rôle** | Valider le principe : *la CI a le droit d'échouer* (fail-closed, P7). |
| **Risque** | Un workflow rouge peut être perçu comme un échec. Solution : le job est **le thermomètre**, pas la maladie. Rollback : suppression du fichier de workflow. |
| **Durée** | 45 min |

**Prompt agent prêt à coller :**
```text
Mission Q3 — CI « Vérité du dépôt ».
Constat : .github/workflows/ ne contient que mirror-guard.yml (garde de miroir,
aucune preuve exécutée). Le README du module 53 affirme un verdict PROVEN que
le runner ne reproduit pas sur clone propre.
À produire : .github/workflows/verite-du-depot.yml
 - déclencheur : pull_request + workflow_dispatch + schedule hebdomadaire
 - runner : ubuntu-latest (environnement PROPRE, sans clé souveraine)
 - exécution : bash tools/quotidien_status.sh --tests
 - archive de la sortie brute en artefact GitHub (preuve citable)
 - comportement : fail-closed — exit non nul => job rouge
Contraintes : aucun secret souverain dans la CI ; ne pas désactiver
la protection DNS/allowlist existante ; ne pas modifier mirror-guard.yml.
Livre aussi la preuve : crée une PR de démonstration et colle l'URL du run.
```

---

## BLOC B — LA BOUCLE QUOTIDIENNE *(votre priorité déclarée)*

> **Objectif du bloc :** une boucle qui tourne **chaque jour** — veille → mémoire → preuve — alimentée par des déclencheurs externes, sans que vous ayez à taper une commande pour l'obtenir.

---

### Q4 — Veille quotidienne qui produit réellement (module 36)

| Champ | Contenu |
| :--- | :--- |
| **Objectif** | Chaque jour, un rapport de veille structuré existe sur disque et est indexé. |
| **Adéquation** | Branche « Intelligence Stratégique » de Vigilum Codex. Vous êtes rédacteur/analyste, pas développeur : la tâche construit le **conduit**, pas le contenu. |
| **Constat** | C6 — `watch.sh` en placeholder, `entr` absent, dossiers de sortie vides |
| **Livrable** | 1. `entr` déclaré (ou remplacé par une solution sans dépendance externe). 2. `watch.sh` câblé : détection → rapport conforme à `La grille de rédaction d'un rapport analytique.md` → écriture dans `Strategic-Outputs/AAAA-MM-JJ.md`. 3. Indexation automatique via `02-Alexandria-Database`. 4. Un gabarit de rapport à remplir par vous en 10 min. |
| **Preuve d'acceptation** | Une commande unique produit le rapport du jour **et** affiche la ligne d'indexation avec son empreinte SHA-256. |
| **Votre rôle** | Valider le gabarit (30 min de lecture/arbitrage). Ensuite : vous rédigez 10 min/jour, la machine fait le reste. |
| **Risque** | Dépendance `entr` = point de rupture. L'agent doit proposer **deux** implémentations et justifier. |
| **Durée** | 75 min |

**Prompt agent prêt à coller :**
```text
Mission Q4 — Veille quotidienne productrice.
Constat : 36-Veille-Strategique/watch.sh s'auto-déclare en placeholder
("Remplacez la commande echo par votre trigger Alexandria..."),
dépend de `entr` qui n'est PAS installé, et les dossiers
Highlights-Outputs/ et Strategic-Outputs/ ne contiennent qu'un README.
Or l'asset doctrinal existe déjà : Charte_Veille_Strategique.md,
La grille de rédaction d'un rapport analytique.md, INDEX.md.
À produire : (1) chaîne de détection robuste SANS dépendance fragile,
comparée honnêtement à la voie `entr` (avantages/limites) ;
(2) génération d'un rapport quotidien conforme à la grille existante dans
Strategic-Outputs/AAAA-MM-JJ.md ; (3) indexation via 02-Alexandria-Database ;
(4) UNE SEULE commande de preuve affichant le rapport créé + son SHA-256
+ la confirmation d'indexation.
Contraintes : ne pas remplir le rapport à ma place — produire le GABARIT
et le conduit. P8 : conserver les sorties, jamais d'écrasement silencieux.
```

---

### Q5 — Mémoire de session automatique (03 → 02)

| Champ | Contenu |
| :--- | :--- |
| **Objectif** | Chaque session laisse une trace résumée, horodatée et indexée, sans intervention. |
| **Adéquation** | Votre formule : *Knowledge → Structure → Memory → Action → Governance*. La mémoire est un pilier de Vigilum Codex. |
| **Constat** | `03-Memory-MLT` déclare extraire les `transcript.jsonl` et déclencher l'indexation — aucune exécution planifiée n'existe (aucun timer, aucun `just`, aucun workflow). |
| **Livrable** | 1. Entrée quotidienne dans `SESSION_TRANSCRIPTS.md` (format structuré existant). 2. Déclenchement automatique de l'indexation Alexandria. 3. Garde-fou secret : aucune clé, aucun chemin privé dans la trace (le README du module l'exige). 4. Preuve d'idempotence : deux exécutions le même jour ne dupliquent pas. |
| **Preuve d'acceptation** | Une commande affiche : dernière entrée, empreinte, statut d'indexation, verdict d'idempotence. |
| **Votre rôle** | Valider le format de l'entrée (5 min). |
| **Risque** | Fuite d'information dans la trace. Mitigation : le scan de secrets du module 53 (`pre-commit/02-secret-scanner.sh`) doit être branché sur la trace produite. |
| **Durée** | 60 min |

**Prompt agent prêt à coller :**
```text
Mission Q5 — Mémoire de session automatique.
Constat : 03-Memory-MLT/README.md déclare extraire les transcripts locaux
et déclencher l'indexation Alexandria, mais AUCUN déclencheur planifié
n'existe dans le dépôt. La chaîne est doctrine, pas exécution.
À produire : (1) entrée quotidienne structurée dans SESSION_TRANSCRIPTS.md,
conforme au format existant ; (2) déclenchement de l'indexation
02-Alexandria-Database après écriture ; (3) passage du contenu au
scan de secrets (core/hooks/pre-commit/02-secret-scanner.sh) AVANT écriture ;
(4) preuve d'idempotence : relancer deux fois => une seule entrée.
Preuve d'acceptation : UNE commande affichant dernière entrée + SHA-256
+ statut d'indexation + verdict d'idempotence.
Contraintes : aucune donnée personnelle ou clé dans la trace ; P8 sans écrasement.
```

---

### Q6 — Chaîne de preuves quotidienne consultable (module 60)

| Champ | Contenu |
| :--- | :--- |
| **Objectif** | En une commande : « qu'a fait la machine aujourd'hui, et la chaîne de preuves est-elle intacte ? » |
| **Adéquation** | C'est le cœur de votre promesse publique : *« An un-governed agent is a liability »*. Vous vendez de la traçabilité — elle doit être consultable en 5 secondes. |
| **Constat** | `60-WikiSkill-Ouroboros` contient 11 scripts dont `trace_writer.py` et `schemas.py` — mais **aucun `self_test.py`** dans le dépôt : le self-test 14/14 annoncé vit dans la PR #4, non fusionnée. |
| **Livrable** | 1. `self_test.py` présent dans le dépôt (via Q9). 2. Commande `quotidien` listant : traces du jour, chaîne SHA-256 vérifiée, altérations détectées. 3. Verdict unique PASS/BLOCK. |
| **Preuve d'acceptation** | Commande exécutée deux fois : PASS sans altération, **BLOCK** après altération volontaire d'une trace (test négatif obligatoire). |
| **Votre rôle** | Exécuter le test négatif vous-même (2 min) — c'est le principe *Producer ≠ Validator*. |
| **Risque** | Faux PASS si la chaîne n'est pas vérifiée de bout en bout. Le test négatif est la protection. |
| **Durée** | 60 min · **Dépend de Q9** |

**Prompt agent prêt à coller :**
```text
Mission Q6 — Preuve quotidienne consultable.
Contexte : 60-WikiSkill-Ouroboros expose trace_writer.py et schemas.py
(scellement SHA-256, vérification, détection d'altération) mais le dépôt
ne contient AUCUN self_test.py — la validation annoncée vit dans la PR #4,
non fusionnée.
À produire : (1) une commande unique affichant les traces du jour, le
nouveau maillon de chaîne, et le verdict d'intégrité ; (2) un test négatif
DOCUMENTÉ : altérer une trace => verdict BLOCK obligatoire ; (3) self_test.py
versionné dans le dépôt.
Preuve d'acceptation : exécuter la commande (attendu PASS), puis altérer
une trace et relancer (attendu BLOCK), en collant les deux sorties brutes.
Contraintes : P1 No Proof No Pass ; P4 exit 0 n'est pas une preuve ;
P3 un état indéterminé n'est jamais un PASS.
```

---

### Q7 — Pont SPARK ↔ MIDGARD : décision + option A

| Champ | Contenu |
| :--- | :--- |
| **Objectif** | Rendre possibles vos tâches planifiées Google Spark **sans exposer** votre machine. |
| **Adéquation** | Décision d'architecture, pas de code : c'est exactement votre positionnement *Ops Consultant — AI Agents, CLI Workflows & Local Governance*. |
| **Constat** | C7 — `58-Spark-MCP-Gateway` = 1 fichier sans test ni lanceur ; `59-Antigravity-Workspace-MCP` = 0 ligne exécutable. |
| **Deux options, une recommandation** | **Option A — Zone de dépôt (recommandée pour vous)** : Spark écrit dans un document Google Drive dédié ; l'agent local ingère, valide (schéma + scan de secrets), puis range. Zéro tunnel, zéro port exposé, conforme Zero Trust, réalisable en une session. **Option B — Tunnel MCP** : plus puissant (l'agent cloud appelle vos outils locaux en direct), mais exige DNS, tunnel nommé, jeton, reverse proxy, et une gouvernance d'exposition. **Recommandation de l'audit : A maintenant, B après Q3** — car B sans pièce d'exposition gouvernée serait une régression de sécurité. |
| **Livrable** | 1. Décision A/B écrite et tracée. 2. Option A implémentée : dossier d'ingestion, validateur de conformité, refus fail-closed, journal. 3. `requirements.txt` + lanceur pour le module 58 (même si B est différé). |
| **Preuve d'acceptation** | Déposer un fichier de test conforme → accepté et rangé avec empreinte. Déposer un fichier non conforme (secret/faux schéma) → **refusé** avec motif. |
| **Votre rôle** | Trancher A vs B (10 min). |
| **Risque** | Exposer un port local = risque majeur. Mitigation : option A par défaut. |
| **Durée** | 75 min |

**Prompt agent prêt à coller :**
```text
Mission Q7 — Pont SPARK <-> MIDGARD.
Constat : 58-Spark-MCP-Gateway ne contient qu'un .py sans requirements.txt,
sans lanceur, sans test ; 59-Antigravity-Workspace-MCP ne contient aucun
actif exécutable (2 rapports seulement).
Objectif : permettre à des tâches planifiées Google Spark de nourrir
le système local SANS aucune exposition de port.
Option A (recommandée) : zone de dépôt Google Drive -> ingestion locale
validée (schéma + scan de secrets) -> rangement + journal + empreinte.
Option B (à évaluer, a priori différée) : tunnel MCP nommé.
Livre : (1) note de décision A/B avec avantages, limites, risques de sécurité ;
(2) implémentation de l'option retenue ; (3) requirements.txt + lanceur
pour le module 58 ; (4) preuve d'acceptation à DEUX cas :
fichier conforme accepté / fichier non conforme REFUSÉ avec motif.
Contraintes : fail-closed (P7) ; aucun secret en clair ; aucune exposition
réseau sans décision souveraine explicite.
```

---

## BLOC C — CÉRÉMONIES SOUVERAINES *(30 à 45 min chacune)*

> Ces trois tâches ne sont pas des chantiers : ce sont des **actes** qui débloquent vos propres différés. Elles ne demandent que votre décision.

---

### Q8 — Pack Schedules Spark (6 déclencheurs)

| Champ | Contenu |
| :--- | :--- |
| **Objectif** | Vos déclencheurs récurrents (brief quotidien, veille hebdo, revue de parité) existent et tournent. |
| **Adéquation** | Vous êtes utilisateur d'outils, pas développeur : la configuration est votre niveau d'intervention naturel. |
| **Livrable** | Les 6 schedules du fichier `PLAN-SPARK-SCHEDULES.md` — textes prêts à coller dans Gemini Spark, chacun relié à une tâche de ce plan. |
| **Preuve d'acceptation** | Les 6 schedules apparaissent en `Ongoing` dans la page Schedules, et le premier déclenchement produit un artefact visible. |
| **Votre rôle** | Coller les textes et vérifier la sortie du premier cycle. |
| **Prérequis** | Compte Google **personnel**, abonnement **Google AI Pro/Ultra**, **Keep Activity activé**, âge 18+. *(Disponible au Maroc : les exclusions sont EEE, Nigéria, Suisse, Royaume-Uni.)* |
| **Risque** | Croire que Spark exécute des commandes locales — **faux**. Voir §5. |
| **Durée** | 45 min |

---

### Q9 — Fusionner la PR #4 (WikiSkill Ouroboros) sous Gravure

| Champ | Contenu |
| :--- | :--- |
| **Objectif** | Le module 60 récupère son auto-validation réelle, versionnée. |
| **Adéquation** | Acte souverain pur : *Biological Gate Mahonheim*. Aucune programmation. |
| **Constat** | PR #4 ouverte depuis le 13/09 ; self-test annoncé **14/14 PASS** ; mais le dépôt ne contient aucun `self_test.py`. |
| **Livrable** | PR fusionnée, `self_test.py` **présent dans le dépôt**, sortie du self-test archivée en preuve. |
| **Preuve d'acceptation** | Le self-test s'exécute depuis un clone propre et affiche `14/14 PASS`. |
| **Votre rôle** | **Valider la fusion** après lecture de l'écart de preuve. Point de vigilance à exiger : que le self-test soit exécuté **depuis le dépôt fusionné**, pas depuis la branche de l'auteur. |
| **Durée** | 30 min |

---

### Q10 — Débloquer OI-03 : courtier Ed25519 (pynacl)

| Champ | Contenu |
| :--- | :--- |
| **Objectif** | Faire disparaître 26 tests SKIP et rétablir la capacité de délégation signée. |
| **Adéquation** | Maîtrise des dépendances techniques — un de vos piliers déclarés. |
| **Constat** | C1 : avec `pynacl 1.6.2`, **les 26 SKIP disparaissent** (vérifié). Or la PR dependabot #3 qui proposait exactement `pynacl>=1.6.2` a été **fermée sans fusion**, et `requirements.txt` déclare encore `>=1.5.0`. |
| **Livrable** | 1. `requirements.txt` aligné (`>=1.6.2`) + `requirements.lock`. 2. Procédure d'installation déclarée dans le README. 3. Registre OI-03 mis à jour. 4. **Vigilance résiduelle** : les 13 échecs de Gate R ne sont **pas** causés par pynacl (mesuré) — ne pas les confondre avec ce chantier. |
| **Preuve d'acceptation** | `bash tools/quotidien_status.sh --tests` → `skip 0` et `0 FAIL` (ou échecs résiduels explicitement tracés par Q1). |
| **Votre rôle** | Valider le relèvement de version (5 min). |
| **Durée** | 45 min |

---

## BLOC D — CONSOLIDATION

---

### Q11 — Réparer ou déférer les fantômes d'automatisation (C5)

| Champ | Contenu |
| :--- | :--- |
| **Objectif** | Aucune commande du dépôt ne pointe vers une ressource inexistante. |
| **Adéquation** | Application directe de la Loi de Parité : *mémoire ≠ exécution = Context Collapse = BLOCK*. |
| **Constat** | C5 — `avalon-daemon.service`, `avalon-watcher.path`, `avalon-maintenance.timer`, `tools/capability_bus/capability_dispatcher.sh`, `memory/` : **tous inexistants**. |
| **Livrable** | Pour chaque cible morte : **créer** (unité réelle + test) **ou** **déférer** (ligne tracée dans le registre avec condition de réveil, P8). Un `just --list` final ne doit plus rien promettre d'inexistant. |
| **Preuve d'acceptation** | Script de contrôle : toute cible `just` pointant un chemin inexistant ⇒ FAIL. Doit retourner PASS. |
| **Votre rôle** | Arbitrer : ces automatisations `avalon-*` sont-elles **voulues** ou **abandonnées** ? Recommandation de l'audit : déférer `avalon-*` (aucun actif Avalon exécutable n'existe) et **supprimer la cible morte** de `23/justfile:watch` en la remplaçant par un contrôle de parité réel. |
| **Durée** | 60 min |

---

### Q12 — Tableau de bord unique + clôture de version

| Champ | Contenu |
| :--- | :--- |
| **Objectif** | Une seule commande répond : *où en est le système aujourd'hui ?* |
| **Adéquation** | Votre §11.2 « Control Dashboard » et votre exigence de commande unique. |
| **Livrable** | 1. `just quotidien` (ou `bash tools/quotidien_status.sh --all`) agrégé : vérité du dépôt, veille du jour, mémoire du jour, intégrité des preuves, registres ouverts. 2. Rapport de clôture V1 citant chaque tâche : preuve produite ou déféré tracé. 3. Ce document passé en `status: VALIDATED`. |
| **Preuve d'acceptation** | La commande s'exécute en moins de 60 secondes et affiche un verdict global PASS/BLOCK + le nombre de registres ouverts. |
| **Votre rôle** | Signer le rapport de clôture (acte de Gravure). |
| **Durée** | 60 min |

---

## 4. Cadence réaliste — 8 semaines, < 5 h/semaine

| Semaine | Tâches | Votre temps | Jalon de sortie |
| :--- | :--- | :--- | :--- |
| **S1** | Q1 | 1 h | La baseline de gouvernance est verte et reproductible |
| **S2** | Q2 + Q3 | 1 h 30 | Le registre est vrai · la CI prouve au lieu de promettre |
| **S3** | Q4 | 1 h 15 | Le premier rapport de veille quotidien existe |
| **S4** | Q5 | 1 h | La mémoire de session s'écrit toute seule |
| **S5** | Q7 + Q8 | 2 h | Le pont cloud↔local est décidé et branché · les schedules tournent |
| **S6** | Q9 + Q10 | 1 h 15 | PR #4 fusionnée · 26 SKIP résorbés |
| **S7** | Q6 | 1 h | La preuve quotidienne est consultable et testée en négatif |
| **S8** | Q11 + Q12 | 2 h | Aucune promesse morte · tableau de bord unique · clôture V1 |
| **Total** | **12 tâches** | **≈ 11 h** | **≈ 1 h 20 / semaine** |

**Boucle d'exécution d'une tâche (6 temps, toujours identique) :**
1. Vous collez le **prompt agent**.
2. L'agent produit le livrable **et** la sortie brute de la preuve.
3. Vous lancez **vous-même** la commande de preuve (indépendance P5).
4. Verdict : **PASS** → étape 5. **FAIL** → l'agent corrige, retour en 2.
5. Vous consignez le verdict dans le registre.
6. Tâche close. Toute partie non résolue devient un **déféré tracé** (P8) — jamais une suppression silencieuse.

---

## 5. Ce que ce plan ne fait pas — et deux vérités à connaître

**Ce plan ne fait pas :**
- Il ne vous apprend pas à programmer — et ne le cherche pas : votre avantage est ailleurs.
- Il ne réécrit pas vos 28 modules documentaires en code. Il rend leur **absence d'exécution visible et assumée**, ce qui est une position défendable ; l'inverse serait une dérive silencieuse.
- Il ne touche ni à vos clés de production, ni à `~/.tesla/`, ni à votre Plan de Contrôle. La clé souveraine reste hors workspace.
- Il ne fusionne ni ne ferme rien sans votre décision explicite.

**Vérité 1 — Google Spark n'exécute rien sur MIDGARD.**
Spark tourne dans le cloud Google, avec accès à Gmail, Agenda et Drive. Il **ne peut pas** lancer une commande sur votre machine, lire `TESLA_ROOT`, ni exécuter `quotidien_status.sh`. C'est précisément pourquoi la tâche **Q7** existe : sans pont, un schedule Spark produit un artefact cloud qui attend. Avec l'option A, cet artefact devient une **entrée gouvernée** de votre système local.

**Vérité 2 — votre goulot d'étranglement n'est pas le code, c'est la preuve.**
47 % de vos modules n'ont aucune ligne exécutable, et le seul verdict public « PROVEN » du dépôt n'est pas reproductible sur clone propre. La bonne nouvelle : ces deux faits se corrigent par la **déclaration honnête** et la **portabilité**, pas par des mois de développement. C'est exactement ce que le Bloc A propose — et c'est, de très loin, l'investissement au meilleur rendement de crédibilité pour Vigilum Codex.

---

## 6. Table de correspondance doctrinale

| Tâche | Gate / Phase sollicitée | Principe protégé |
| :--- | :--- | :--- |
| Q1 | Gate 4 (Independent Verification) | P1 No Proof No Pass · P4 |
| Q2 | Phase 3.5 (Loi de Parité Absolue) | P6 Parité bidirectionnelle |
| Q3 | Phase 2 (Validation) + OI-01 | P2 Producer ≠ Validator |
| Q4 | Gate 1 (Canonical Discovery) | P8 No Silent Deletion |
| Q5 | Phase 3 (Assimilation) | Souveraineté des données locales |
| Q6 | Phase 7 (Seal) | P11 Assertion ≠ Evidence |
| Q7 | GATE 0 (Authority) | Zero Trust · Fail Closed (P7) |
| Q8 | — (déclencheurs externes) | Anti-friction (OI-02) |
| Q9 | Phase 5 (Biological Gate Mahonheim) | Autorité souveraine |
| Q10 | OI-03 + Maîtrise des dépendances | P3 Unknown ≠ Pass |
| Q11 | Loi de Parité (anti-fantôme) | P8 · P7 |
| Q12 | Phase 7 (Seal) + §11.2 Control Dashboard | Cohérence d'ensemble |

---

## 7. Annexes et fichiers liés

| Fichier | Rôle |
| :--- | :--- |
| `PLAN-SPARK-SCHEDULES.md` | Les 6 déclencheurs Gemini Spark prêts à coller |
| `tools/quotidien_status.sh` | Commande de vérité du dépôt (lecture seule, aucune mutation) |
| [Issues #5 → #16](https://github.com/lordmahonheim-bot/Tesla-Antigravity-CLI/issues) | Les 12 tâches, actionnables et labellisées |
| `OUTPUTS/open_items_todo-Updated.md` | Registre des déférés à mettre à jour par Q1, Q2, Q10, Q11 |
| `PROTOCOLES/LOI-DE-PARITE-ABSOLUE.md` | Norme de référence de Q2 et Q11 |
| `PROTOCOLES/GRAVURE-SUR-MARBRE.md` | Protocole d'exécution et de scellement |
| `GENESE-v1/AGENTS.md` | Couche de gouvernance — référence cassée traitée en Q2 |

---

## Annexe — Finalisation GitHub (2 minutes, action souveraine)

### Ce qui est déjà en place

| Élément | État |
| :--- | :--- |
| Issues **#5 → #16** | ✅ Créées — les 12 tâches, corps complet avec prompt agent |
| Libellés | ✅ Créés : `quotidien`, `preuve`, `parite`, `gouvernance`, `decision-souveraine` |
| Jalon | ✅ Créé : **« Quotidien V1 — 12 tâches »** (échéance 12/11/2026) |
| Rattachement libellés/jalon aux issues | ⚠️ **Non appliqué — limitation de l'intégration** (voir ci-dessous) |

### Le blocage rencontré, dit sans détour

L'agent qui a publié ces issues opère via une **application GitHub** dont le jeton permet de **créer** mais pas de **modifier** une issue (`403 Resource not accessible by integration`, vérifié sur trois méthodes : `gh issue edit`, `PATCH /issues/{n}` avec libellés, `PATCH /issues/{n}` avec jalon). Le rattachement a donc été refusé, y compris au moment de la création.

**Deux conséquences assumées :**
1. Les 12 issues doivent être **étiquetées et rattachées au jalon** par vous — 2 minutes dans l'interface, ou par la commande ci-dessous.
2. Une issue de test, **#18** (*« [TEST] verification libelles — a supprimer »*), a été créée pour isoler la cause. Sa suppression est également interdite au jeton de l'intégration. **Elle est à supprimer par vous** — elle ne contient aucun contenu de travail.

### Reprise en une commande (à lancer avec un jeton qui a le droit d'écriture)

```bash
cd "$TESLA_ROOT"
MS="Quotidien V1 — 12 tâches"

gh issue edit 5  --add-label preuve,gouvernance,decision-souveraine --milestone "$MS"
gh issue edit 6  --add-label parite,gouvernance,decision-souveraine --milestone "$MS"
gh issue edit 7  --add-label preuve,gouvernance                      --milestone "$MS"
gh issue edit 8  --add-label quotidien,preuve                        --milestone "$MS"
gh issue edit 9  --add-label quotidien,preuve                        --milestone "$MS"
gh issue edit 10 --add-label quotidien,preuve                        --milestone "$MS"
gh issue edit 11 --add-label quotidien,gouvernance,decision-souveraine --milestone "$MS"
gh issue edit 12 --add-label quotidien,decision-souveraine           --milestone "$MS"
gh issue edit 13 --add-label gouvernance,decision-souveraine,preuve  --milestone "$MS"
gh issue edit 14 --add-label gouvernance,preuve                      --milestone "$MS"
gh issue edit 15 --add-label parite,gouvernance,decision-souveraine  --milestone "$MS"
gh issue edit 16 --add-label quotidien,gouvernance                   --milestone "$MS"

# Issue de test à retirer (sans contenu de travail)
gh issue delete 18 --yes
```

**Alternative sans ligne de commande :** dans l'onglet *Issues*, filtrez par jalon « Quotidien V1 », sélectionnez les 12 issues, puis **Labels** et **Milestone** dans la barre d'actions groupées.

> **Note doctrinale.** Cette limite illustre exactement le principe **P2 — Producer ≠ Validator** : l'acteur qui produit n'est pas celui qui dispose de l'autorité de certification. Ici, l'agent produit les issues ; **vous** détenez le pouvoir de les étiqueter, de les rattacher et de clore #18.

---

> **Formule de clôture**
> *Ce plan ne rajoute pas de la doctrine : il rend exécutable celle qui existe déjà.*
> **No Proof, No Parity, No Publish.**
