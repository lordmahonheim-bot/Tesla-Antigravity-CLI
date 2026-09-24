# PLAN D'INTERVENTION INTÉGRAL (v2.0 AUDITÉ & OPTIMISÉ)
**Cible** : `lordmahonheim-bot/Tesla-Antigravity-CLI`
**Date** : 2026-09-24
**Statut** : [CERTIFIÉ PAR TEAM-SYNERGY]
**Validation PREMORTEM** : 85% (GO sous conditions de mitigation intégrées)

![Status](https://img.shields.io/badge/Status-MVP-blue) ![Ecosystem](https://img.shields.io/badge/Ecosystem-TESLA%20ANTIGRAVITY-purple) ![Security](https://img.shields.io/badge/Security-ID%20LOCKED-red) ![Python](https://img.shields.io/badge/Python-3.12+-blue)

---

## 1. RÉSULTAT FINAL VISÉ (TARGET STATE)

L'objectif de cette intervention est de rétablir la **chaîne de preuve déterministe** du dépôt et d'atteindre un état de gouvernance automatisée exemplaire. 

À l'issue de ce plan, le dépôt devra garantir **6 INVARIANTS (V1-V6)** vérifiés par **16 CRITÈRES D'ACCEPTATION (CA-01 à CA-16)** :
- **V1 (Vérité d'Exécution)** : Aucun faux-positif. Les tests ne passent que si le code est réellement éprouvé.
- **V2 (Reproductibilité)** : Toute preuve de validation (Ledger) est reproductible à l'identique sur un clone vierge.
- **V3 (Parité Absolue)** : Le manifeste descriptif et la réalité du code sont alignés au bit près.
- **V4 (Sécurité et Étanchéité)** : Aucun chemin personnel (`/home/lord-mahonheim/...`), scan de secrets via `gitleaks` (Fail-Closed).
- **V5 (Automatisation unifiée)** : CI/CD GitHub Actions centralisée, utilisant `uv workspaces` et Ruff, avec un job de synthèse unique.
- **V6 (Friction Minimisée)** : Mise à jour par lots (Dependabot Groups), pas de PR exigée pour le compte souverain, installation des hooks native (`core.hooksPath`).

---

## 2. INVENTAIRE DES DIAGNOSTICS ET ÉCARTS (D-01 à D-35)

L'audit terrain a confirmé 33 des 34 diagnostics initiaux et a identifié un nouvel angle mort bloquant (D-35).

### 2.1 Les Bloquants et Majeurs
- **D-01** : 13 tests du module 53 échouent (Gate R).
- **D-02** : Le ledger V263 n'est pas reproductible.
- **D-08** : Références `memory/` cassées (le dossier de vérité pointe vers le vide).
- **D-18** : Un fichier Python de base ne compile pas (f-string mal formée).
- **D-35 [NOUVEAU]** : Les modules sont disloqués entre la racine et le répertoire `MVP-GITHUB/`, cassant les chemins d'exécution et les promesses de la CI.

### 2.2 Les Failles Systémiques & CI/CD
- **D-13** : CI actuelle décorative, ne validant aucune preuve.
- **D-14** : Hooks git existants mais jamais armés automatiquement.
- **D-27** : Script de secret-scanning obsolète (boucle grep au lieu d'un outil dédié).
- **D-28** : Dépendances tierces incomplètes et non groupées (risque de saturation).

---

## 3. GUIDE D'EXÉCUTION CHRONOLOGIQUE (É-000 à É-060)

L'exécution est séquencée pour éviter la *Lassitude Souveraine* (M-13). Les Phases 0, 1 et 2 sont regroupées dans un seul cycle de validation, limitant le nombre de micro-PRs inutiles.

### PHASE 0 : FONDATIONS ET RÉSOLUTION DE L'ANGLE MORT (É-000 à É-002)
> **Objectif** : Stabiliser le terrain avant toute exécution de code.

- **É-000 (Urgence D-35)** : Harmoniser les chemins. Déplacer et consolider les modules cibles (53, 60, etc.) depuis `MVP-GITHUB/` vers leur emplacement canonique ou adapter tous les scripts pour cibler systématiquement `MVP-GITHUB/`.
- **É-001 (Hygiène Git)** : Clôturer manuellement la PR #21 et l'Issue #18 qui sont obsolètes. Nettoyer les fichiers résiduels (`.DS_Store`, traces d'audits passés) et compléter le `.gitignore`.
- **É-002 (Bootstrap des Hooks)** : Créer un fichier `Makefile` à la racine contenant la cible `setup` exécutant `git config core.hooksPath "MVP-GITHUB/53-Vigilum-Codex-2.0-Executable-Governance/core/hooks"`. Cela remplace le lourd script `install_hooks.sh` par une directive Git native et déterministe (Mitigation M-14).

### PHASE 1 : RÉTABLISSEMENT DE LA VÉRITÉ DOCTRINALE (É-003 à É-012)
> **Objectif** : Réparer les tests et la Gate R pour que la vérité d'exécution (V1) soit fiable.

- **É-003 (Injection de Clé)** : Modifier `gate_r.py` pour supporter une cascade de clés (Environnement → Fichier → Génération Éphémère en CI).
- **É-004 (Correction des Mocks)** : Corriger les 13 assertions cassées dans `test_runner.py` et `test_v26_gate_r_and_staging.py`.
- **É-005 (Réparation des Références)** : Mettre à jour les fichiers de documentation (ex: `AGENTS.md`) pour retirer ou corriger les références cassées vers le dossier `memory/` (D-08).
- **É-006 (Purge de l'Evidence)** : Implémenter et exécuter `prune_evidence.py` pour vider les vieux ledgers obsolètes du dossier `evidence/`.
- **É-007 (Nouveau Ledger)** : Relancer la suite complète et commiter le nouveau ledger V264 reproductible.

### PHASE 2 : FIXES CODE ET DÉPENDANCES (É-013 à É-020)
> **Objectif** : Que 100% du code Python compile et que l'environnement soit reproductible.

- **É-013 (F-String Fix)** : Réparer l'erreur de compilation ligne 264 dans `update_session_history.py` (via l'extraction dans une variable intermédiaire propre).
- **É-014 (Module 60 Ouroboros)** : Corriger les conflits de format (HTML vs JSON markdown) causant les 6 échecs du `self_test.py`.
- **É-015 (Requirements Exhaustif)** : Créer un `requirements.txt` (ou `pyproject.toml` unifié via `uv`) consolidé incluant explicitement `requests`, `pydantic`, `typer` et toutes les 17+ bibliothèques identifiées par l'audit technique.
- **É-016 (Nettoyage des Chemins Locaux)** : Remplacer toutes les occurrences de `/home/lord-mahonheim/` par des chemins relatifs ou variables d'environnement (`$HOME` / `$TESLA_ROOT`).

### PHASE 3 : MISE EN PLACE DE LA NOUVELLE CI/CD (É-021 à É-026)
> **Objectif** : Automatiser la gouvernance avec les standards 2026.

- **É-021 (Workflow Gouvernance)** : Créer `.github/workflows/baseline.yml` exécutant en parallèle : `baseline-53`, `self-test-60`, `compile-python`. Ajouter un **Job de Synthèse obligatoire** (`ci-success`) agissant comme l'unique Status Check exigé par la protection de branche.
- **É-022 (Scanner Gitleaks)** : Créer `.github/workflows/security.yml` utilisant l'action officielle `gitleaks-action` (Fail-Closed dur) en remplacement des scripts grep maison.
- **É-023 (Workflow Lint Unifié)** : Implémenter Ruff. Modifier `lint_all.sh` pour éviter le crash en cas d'erreur de lint : utiliser `ruff check . || RUFF_STATUS=$?` pour assurer la collecte du statut de tous les outils sans masquer le verdict final.
- **É-024 (Dependabot Groupé)** : Créer `.github/dependabot.yml` avec la fonctionnalité `groups` pour fusionner les mises à jour en une seule PR par module, évitant la saturation cognitive (Mitigation M-13 & M-16).
- **É-025 (Sécurisation OpenSSF)** : Pinner toutes les actions GitHub de la CI (ex: `actions/checkout`) sur leur hash SHA-1 entier et forcer le moindre privilège (`permissions: contents: read`).

### PHASE 4 : PARAMÉTRAGE DU DÉPÔT (É-027 à É-030)
> **Objectif** : Cadenasser la forteresse.

- **É-027 (Protection de Branche)** : Configurer `main` pour exiger le check de statut `ci-success` et des commits signés. (Exception : ne pas exiger de PR pour les commits directs du souverain).
- **É-028 (Run Final)** : Vérifier que toutes les badges du README reflètent la réalité (Retirer les badges Python 3.10/3.14 contradictoires).

---

## 4. AMÉLIORATIONS ET OPTIMISATIONS FUTURES (ÉTAT DE L'ART)

Une fois ce plan exécuté et le dépôt stabilisé, l'intégration des standards SLSA 3 / Sigstore / in-toto est recommandée :
- **O-01** : Transition des clés HMAC locales vers **Sigstore (Cosign/Rekor)** pour générer des attestations de provenance OIDC dématérialisées.
- **O-02** : Migration totale de la logique Bash vers **uv workspaces** pour un environnement Python instantané et unifié.

---

## 5. VALIDATION FINALE (LES 16 CRITÈRES D'ACCEPTATION)

L'exécution du plan sera jugée achevée si et seulement si ces 16 points sont vérifiés sur un clone vierge :

- [ ] **CA-01** : `python3 bin/test_runner.py` renvoie verdict_global PASS.
- [ ] **CA-02** : Preuve committée strictement reproductible.
- [ ] **CA-03** : `self_test.py` du Module 60 affiche 14/14 PASS.
- [ ] **CA-04** : `quotidien_status.sh` sort avec code 0 (PASS).
- [ ] **CA-05** : `audit_parite.py` sort avec code 0 sur le clone conforme.
- [ ] **CA-06** : La CI est verte (le job `ci-success` valide la PR).
- [ ] **CA-07** : `lint_all.sh` exécute Ruff et retourne un code de fail si la dette augmente (Fail-Closed).
- [ ] **CA-08** : Compilation de 100% du code (`python3 -m compileall -q .` exit 0).
- [ ] **CA-09** : Aucun chemin personnel dur (`/home/lord-mahonheim`) ne subsiste.
- [ ] **CA-10** : Fichier `requirements.txt` exact et complet.
- [ ] **CA-11** : Gitleaks fonctionnel (aucun secret en clair n'est toléré).
- [ ] **CA-12** : Hook pré-commit configuré via `git config core.hooksPath`.
- [ ] **CA-13** : PR de test Dependabot déclenchée et groupée avec succès.
- [ ] **CA-14** : Les 4 workflows de base s'exécutent en moins de 3 minutes.
- [ ] **CA-15** : Le répertoire `MVP-GITHUB/` est consolidé sans conflit d'adressage (D-35 résolu).
- [ ] **CA-16** : Tous les badges du README reflètent un statut dynamique réel.

***
**Document consolidé et certifié par l'Agent Principal Tesla** suite au déploiement de la Team-Synergy (Phase 0, 1, 2) sous la doctrine du Vigilum Codex.
