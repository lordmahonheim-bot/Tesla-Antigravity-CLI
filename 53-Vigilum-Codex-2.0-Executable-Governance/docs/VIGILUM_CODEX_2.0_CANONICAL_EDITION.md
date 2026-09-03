---
title: "VIGILUM CODEX"
subtitle: "Constitution de Gouvernance Exécutable & Matrice de Preuve"
doctrine_version: "2.0.0"
implementation_version: "2.4.0"
status: "CONTROLLED IMPLEMENTATION BASELINE — RUNTIME EVIDENCE PENDING"
date: "2026-09-03"
author: "Abdellah MOUHTAJ — Lord Mahonheim"
ecosystem: "Tesla / Bifrost / MIDGARD"
classification: "Constitutionnelle — FAIL-CLOSED"
supersedes: ["VIGILUM_CODEX_v1.0", "VIGILUM_CODEX_Fiche_Technique_v1.0"]
---

![Status](https://img.shields.io/badge/Status-BASELINE-blue) ![Version](https://img.shields.io/badge/Version-2.4.0-yellow) ![Doctrine](https://img.shields.io/badge/Doctrine-Vigilum%20Codex-purple) ![Governance](https://img.shields.io/badge/Governance-FAIL--CLOSED-red)

# 🏛️ VIGILUM CODEX
## *Doctrine Majeure 2.0.0 — Révision Opérationnelle 2.4.0*

> *« L’IA propose. Le système détermine si la proposition peut être exécutée. La preuve décide si le résultat est admis. L'autorité humaine engage. »*

> **Axiome ratifié (V2.6.2 — plan consolidé V2.6.1) :** *« L'IA propose, l'outil déterministe valide, l'OS restreint. **L'agent ne génère jamais sa propre preuve.** »*
> Corollaire opérationnel de P2/P11 : toute preuve d'aptitude, d'autorisation ou d'exécution est produite par un outil déterministe ou par le Plan de Contrôle, jamais par l'agent qu'elle concerne. Hiérarchie de confiance assumée : les hooks et variables d'environnement sont des garde-fous **opérationnels** ; la séparation de privilèges absolue (UID/GID) relève de l'OS et demeure un chantier tracé (OI-03).

---

## 📌 PRÉAMBULE — RUPTURE ÉPISTÉMOLOGIQUE

Le **Vigilum Codex 2.0** établit le cadre constitutionnel de gouvernance de l’écosystème Tesla.
La doctrine 2.0 acte la fin de la *Gouvernance par le Verbe*. Son objectif est de concevoir un système déterministe garantissant la validité matérielle des actions.

> **Principe de Déterminisme :**
> Toute règle critique susceptible d'être contrôlée automatiquement doit être matérialisée par un mécanisme déterministe. Toute règle non automatisable doit définir son autorité compétente, son mode de vérification et sa preuve d'application.

$$
\text{AUTHORITY} \rightarrow \text{POLICY} \rightarrow \text{INTENT} \rightarrow \text{EXECUTION} \rightarrow \text{EVIDENCE} \rightarrow \text{STATE}
$$

---

## TITRE I — IDENTITÉ, HÉRITAGE ET VISUALITÉ

### 1.1 Continuité de la Version 1.0
Bien que réécrit sous forme exécutable, le Codex perpétue l'institution-matrice originelle, fondée sur trois branches inaliénables :
1. **Performance Humaine :** Excellence, posture, standardisation premium (Humain).
2. **Intelligence Stratégique :** Transformation de l'information en décision.
3. **Opérations IA Gouvernées :** L'IA comme infrastructure maîtrisable, jamais comme centre.

L'esthétique du Codex maintient le sceau originel (Œil / Géométrie / Codex). Le corpus normatif (32 lois `[VC-*]` à ce jour) est délégué au registre `LEARN/CARTOGRAPHIE_APPRENTISSAGES_INTEGRALE.md`. Ce registre est encadré par `VC-META-01` (imposant les statuts `PROPOSED`/`CANONICAL`/`SUPERSEDED`) et `VC-META-02` (imposant un bloc `[EVIDENCE_CHAIN]` par loi) pour garantir des ID immuables.

---

## TITRE II — L'ARCHITECTURE À 4 PLANS ÉTANCHE

Le Codex repose sur une séparation stricte des pouvoirs. Aucun plan ne peut usurper la fonction d'un autre.

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. CONTROL PLANE (Plan de Contrôle & Autorisation)                          │
│    • Autorité : Lord Mahonheim                                              │
│    • Clé d'Autorité : [EXTERNAL — injectée au runtime via env chiffré]      │
│    • Rôle : Définit les politiques, autorise ou interdit les publications   │
├──────────────────────────────────────┬──────────────────────────────────────┤
│ 2. INTENT PLANE (Plan d'Intention & Agents)                                 │
│    • Acteurs : Sous-agents de l'écosystème (Attestation PID/Namespace)      │
│    • Rôle : Formulent des intentions structurées (sans autorité de push)    │
├──────────────────────────────────────┬──────────────────────────────────────┤
│ 3. EXECUTION PLANE (Plan d'Exécution & Mécanismes)                          │
│    • Composants : Brokers locaux, hooks Git, démons système                 │
│    • Rôle : Vérifie la conformité, confine l'action, mute l'état            │
├──────────────────────────────────────┬──────────────────────────────────────┤
│ 4. EVIDENCE PLANE (Plan de Preuve & Intégrité)                              │
│    • Composants : Moteurs d'audit, journaux, chaînes de hachage             │
│    • Rôle : Prouve, qualifie et enregistre l'état canonique                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## TITRE III — LES PRINCIPES INVIOLABLES DE GOUVERNANCE

Toute violation d'un invariant bloquant suspend immédiatement la progression. La reprise exige correction, re-validation et production de nouvelles preuves.

1. **P1 — NO PROOF, NO MARBLE :** Aucun statut de conformité, de validation, de publication vérifiée ou de scellement ne peut être accordé sans preuve correspondant au niveau de contrôle requis.
2. **P2 — PRODUCER ≠ VALIDATOR :** Aucun producteur ne peut s'attribuer seul un statut de validation indépendante. Pour les contrôles critiques, la validation doit être réalisée par un mécanisme ou une autorité distincte selon les frontières de confiance définies par la politique applicable.
3. **P3 — UNKNOWN ≠ PASS :** L'incertitude ne peut être convertie en succès. UNKNOWN sur une condition classée bloquante implique BLOCKED. Les contrôles non bloquants doivent être explicitement marqués.
4. **P4 — L'IA PROPOSE, LE CODE VALIDE :** Les décisions critiques de mutation d'état ne dépendent pas de l'auto-évaluation narrative d'un LLM, mais de vérifications déterministes (AST, Lints, Hashes).
5. **P5 — CONFINEMENT :** Toute mutation est strictement bornée au workspace (anti-TOCTOU, `O_NOFOLLOW`). N'entrave pas l'I/O réseau (Egress/Ingress) en lecture seule (ex: OSINT).
6. **P6 — ANTI-REJEU :** Toute autorisation consomme un nonce unique atomique.
7. **P7 — LOI DE PARITÉ ABSOLUE :** Cohérence stricte et auditée entre état, preuve, et mémoire.
8. **P8 — NO SILENT DELETION :** La suppression d'une information de gouvernance ou de l'historique doit être traçée.
9. **P9 — SOUVERAINETÉ HUMAINE :** Les décisions souveraines ne peuvent être auto-attribuées par un agent.
10. **P10 — FAIL-CLOSED :** $\text{FAIL} \lor \text{BLOCKED} \Rightarrow \text{NO PROGRESSION}$.
11. **P11 — ASSERTION ≠ EVIDENCE (V2.6.1) :** Toute affirmation narrative concernant une preuve (« N/N tests passent », « déployé », « validé ») ne constitue pas une preuve. Seul un artefact d'exécution vérifiable — ledger signé, empreinte, quittance — fait foi ; un rapport déclaratif non corrélé à un registre physique est réputé non validé. Enforcement déterministe : **Gate R** (Evidence Reconciliation, `bin/gate_r.py`) avant l'état `MARBLE_ELIGIBLE`.
12. **P-AGENT-001 (Anti-Théâtre) :** Une délégation sans quittance authentique (attestation cryptographique liant l'identité à l'isolation PID/Namespace) est réputée non exécutée (Anti-Sybil).

---

## TITRE IV — INVARIANTS D'INGÉNIERIE & MACHINE D'ÉTATS

### 4.1 Invariants du Noyau (Baseline Technique)
- **Q-001 (Ingestion Atomique) :** Traitement en `.staging/`, `fsync`, puis `rename` atomique.
- **T-002 (Anti-TOCTOU) :** Résolution `realpath` bornée, refus des symlinks.
- **R4 (Idempotence) :** Résilience aux crashs locales. *Exception : les opérations réseau consommant un nonce (A-003) sont exclues du self-healing automatique pour éviter un deadlock d'autorisation.*
- **A-001 (Push Auth) :** Jeton d'autorisation explicite exigé pour accès réseau protégé.
- **A-002 (Signatures Différenciées) :** Vérification canonique JCS (RFC 8785) pour les intentions JSON internes. Signatures GPG/SSH exigées pour les commits Git finaux ("Vigilant mode").
- **A-003 (Anti-Rejeu Local) :** Consommation POSIX `O_CREAT|O_EXCL` des nonces empêchant le rejeu local de l'exécution.

### 4.2 La Bibliothèque des Codes POSIX
| Code | Condition | Code | Condition |
|:---:|---|:---:|---|
| **0** | `TESLA_EXIT_OK` (Succès prouvé) | **60** | `TESLA_EXIT_LINT` |
| **10** | `TESLA_EXIT_SCHEMA` | **66** | `TESLA_EXIT_UNKNOWN` |
| **20** | `TESLA_EXIT_SECRET` | **70** | `TESLA_EXIT_PUSH` (Anti-rejeu) |
| **30** | `TESLA_EXIT_SCOPE` | **80** | `ERR_SPEC_LOCKED` (Plafond d'audit) |
| **40** | `TESLA_EXIT_STATE` (Parité) | **81** | `ERR_AGENT_THEATER` (Usurpation) |
| **50** | `TESLA_EXIT_MARBLE` | **90** | `TESLA_EXIT_DRAFT` (Brouillon commité) |

### 4.3 Machine d'États à 13 Niveaux
L'ordre garantit que la génération de preuve (mutation de staging) précède logiquement sa validation :
`DRAFT` ➔ `CONTRACTED` ➔ `G2_APPROVED` ➔ `EXECUTING` ➔ `WORK_VALIDATED` ➔ `STAGING_COMPLETED` ➔ `EVIDENCE_VALIDATED` ➔ `MARBLE_ELIGIBLE` ➔ `HUMAN_AUTHORIZED` ➔ `PUBLISHING` ➔ `PUBLISHED` ➔ `POST_PUB_VERIFIED` ➔ `SEALED`

$$
\text{MARBLE\_ELIGIBLE} = \text{WORK\_VALIDATED} \land \text{STAGING\_COMPLETED} \land \text{EVIDENCE\_VALIDATED} \land \text{MEMORY\_PARITY\_PASS} \land \text{HYGIENE\_PASS} \land \text{RECEIPTS\_CORRELATED}
$$

---

## TITRE V — LA PARITÉ ET LA CHAÎNE DE PREUVE

### 5.1 Loi de Parité Absolue
Audit post-mission garantissant l'absence d'amnésie et de fantômes :
- Requiert `grep -F -w` **après normalisation stricte** (UTF-8 NFC, CRLF -> LF).
- Comptage exact exigé contre manifeste (ex: `test_manifest_v2.1.yaml` requiert formellement `66` tests).
- *Anti-Deadlock d'Auto-référence* : Les artefacts de preuve (dont `chain_head.sha256`) sont strictement exclus du hachage de la parité mémoire.

### 5.2 Chaîne de Preuve & Scellement
Pour prévenir toute attaque de canonicalisation (injection aux limites), la concaténation utilise des délimiteurs stricts (`:`):
$$H_n = \text{SHA256}(H_{n-1} \parallel \text{':'} \parallel E_n \parallel \text{':'} \parallel M_n)$$
**Limitation de la garantie :** Une *hash-chain* isolée n'est que *tamper-evident*.
Pour renforcer la résistance à la réécriture rétroactive, la chaîne doit être ancrée dans un domaine distant (`--remote-commit`). Sur GitHub, cet ancrage requiert l'activation impérative des **règles de protection de branche** (interdiction stricte des `push --force` et suppressions).
*Note de sécurité :* Le paramétrage Unix `0444` appliqué localement ne constitue qu'une *Soft Immutability* (Local Read-Only Protection).

---

## TITRE VI — DOCTRINE DE DÉFAILLANCE (RETEX AMDEC)

L'échec documenté est un actif de gouvernance, consigné sans suppression :

| Défaillance (RETEX) | Impact | Verrou Exécutable Intégré |
| :--- | :---: | :--- |
| **E1 : Illusion d'audit infini** | 🟠 | **L-001 (SPEC LOCK)** : Plafond d'audit à 3 itérations (Exit 80). |
| **E2 : Omission de Staging** | 🔴 | **S-002 (Staging Gate)** : Jalon public $N+1$ obligatoire. |
| **E3 : Amnésie Mémorielle** | 🔴 | **M-014 (Parité)** : Vérification normalisée des piliers (Exit 40). |
| **E4 : Faille Invocation Python** | 🟡 | **R-004 (Universal Runner)** : Path `unittest discover -s tests`. |
| **E5 : Prolifération Brouillons** | 🟡 | **H-005 (Hygiène)** : Quarantaine vers `runtime/drafts/` (Exit 90). |
| **E6 : Angle mort LSP** | 🟠 | **U-006 (Tri-State Probe)** : Enregistrement strict de l'observabilité. |
| **E7 : Théâtre d'Agents** | 🔴 | **D-007/D-008 (Anti-Usurpation)** : Quorum de quittances PID exigé (Exit 81). |

---

## ANNEXE A — POLITIQUE DE ROUTAGE COGNITIF

*Ce registre est une annexe opérationnelle mutable, et ne constitue pas le socle constitutionnel.*
Afin de préserver le système, l'allocation des modèles d'inférence doit respecter des profils :
1. **Raisonnement Lourd (Orchestration) :** Cible les modèles Foundation de classe Pro/Opus.
2. **I/O, Parsing & Vitesse :** Cible les API Ultra-Légères de classe Flash.
3. **Audit Impartial (Gate 4) :** Privilégie un mécanisme de validation déterministe distinct du producteur. L'utilisation d'un LLM n'est qu'un rôle de conseiller sémantique ; les conclusions finales doivent être justifiées par des preuves matérielles, indépendamment du raisonnement probabiliste.
4. **Opérations Souveraines :** Restreint l'exécution à des moteurs Open-Weights locaux.

---

## CHANGELOG INSTITUTIONNEL

* **V1.0 :** [EXTERNAL — Fiche Technique fondatrice non versionnée dans ce dépôt].
* **V2.0 :** Bascule vers la Gouvernance Exécutable. Architecture à 4 Plans. P1-P10.
* **V2.1.3 :** Implémentation du RETEX E1-E7. Machine d'états à 13 niveaux et 12 codes POSIX.
* **V2.2.0 :** Séparation formelle Doctrine/Implémentation. Précision sur le scellement `0444`.
* **V2.3.0 :** Affinage logique de P2, P3. Formalisation de l'ancrage distant de la chaîne.
* **V2.4.0 (Actuelle) :** Résolution des deadlocks systémiques et cryptographiques. Application de l'AMDEC préventif : réordonnancement de la FSM (Staging avant Evidence), isolation du hachage, protection de branche distante, neutralisation des attaques de canonicalisation SHA-256 et sécurisation anti-Sybil.
* **V2.5.1 :** Audit du Plan d'Intervention Correctif V2.5.0 et verrouillage déterministe de l'Orchestrateur : juridiction Git exclusive (hook 08 + classifieur fail-closed), standardisation SCD/Zero-Middleman (bibliothèque `tesla-scd.sh`, hook 09 — éradication physique de BYPASS-01), Pre-Flight Checklist Gate 0 en intercepteur déterministe (hook 10 — la version « injection cognitive » du plan était une violation P4), attestations SLSA/DSSE pour le pivot CI/CD éphémère (`slsa_attestation.py`). Réparations de parité P7 : ordre de résolution des transcripts restauré (arbitrage #1), dépendance PyNaCl déclarée et confinée P3, divulgation des skips dans le ledger du runner. Manifeste : 165 tests déclarés.
* **V2.6.1 :** Verdict d'audit du Plan de Haut Niveau V2.6.0. Gravure du principe **P11 (Assertion ≠ Evidence)** avec enforcement exécutable **Gate R** (`bin/gate_r.py` : manifeste ↔ ledger ↔ signature Control Plane, registre `runtime/contracts/mission_truth.json` émis par l'outil déterministe — jamais par l'agent, écriture agent bloquée par le hook 09). Extension de la juridiction anti-usurpation aux transferts de fichiers vers les espaces de gouvernance (`cp`/`mv`/`install`/`rsync` — blocage ciblé par destination, jamais aveugle). Invariant Cognitif Anti-Friction gravé en **formulation corrigée** (l'anti-friction lie l'agent, jamais les prérogatives souveraines du Plan de Contrôle — la formulation absolue du plan est rejetée). Déférérence tracée (P8) : câblage CI du SLSA différé (`OUTPUTS/open_items_todo-Updated.md`), actif conservé — la Gate R en dépend.
* **V2.6.2 :** Verdict du Plan Consolidé V2.6.1 (RENA/ChatGPT) — **convergence ratifiée** : chaque assertion du plan a été vérifiée contre l'état physique du dépôt (P11) et correspond à l'implémentation livrée. Gravure de l'**axiome ratifié** (« l'agent ne génère jamais sa propre preuve ») au préambule, avec hiérarchie de confiance assumée (garde-fous opérationnels vs séparation UID/GID, OI-03). Delta exécutable extrait : **détection d'usurpation d'identité** (contradiction runtime/payload → deny Exit 81 avant toute évaluation de juridiction). Formulation consolidée de l'Invariant Anti-Friction adoptée (OI-02 v2). Divergences arbitrées : maintien de la défense en profondeur du hook 09 (domaines **et** motifs d'artefacts — l'abandon des motifs rouvrirait la falsification de quittances/certificats sans preuve de fragilité) ; répertoire `authority/` différé par Scope Lock.
