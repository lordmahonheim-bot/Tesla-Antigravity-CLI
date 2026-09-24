# PLAN D'INTERVENTION INTÉGRAL — v3.0 CONSOLIDÉ (MASTER PATCH)
**Cible** : `lordmahonheim-bot/Tesla-Antigravity-CLI`
**Date** : 2026-09-24
**Statut** : [ALIGNÉ SUR L'AUDIT DE CONFRONTATION ET VERDICT FINAL]
**Référence Base de Vérité** : `Plan_Intervention_Integral_Tesla_Antigravity_CLI_2026-09-23.txt` (v1 - 60 étapes)
**Références d'Audit** : 
- `AUDIT-DE-CONFRONTATION.md` (sha256: 91f21e6d...)
- `Verdict.txt` (Réserves appliquées)

---

## 1. DÉCLARATION DE GOUVERNANCE

Suite au rejet en bloc du brouillon v2.0 par l'**Audit de Confrontation**, la décision **"Option B — Cannibaliser v2.0"** a été entérinée.
*(Décision actée le 2026-09-24 par l'autorité souveraine Lord Mahonheim).*

Ce document v3.0 n'a **pas** vocation à remplacer le plan v1 (282 Ko, 60 étapes). Le Plan v1 reste le **seul document d'exécution de référence**. Ce v3.0 agit comme un **Patch d'Apports**.

**Règle de préséance explicite** : Le § 2 de ce document v3.0 prévaut sur le plan v1 **uniquement** pour les étapes É-024, É-025, É-026, É-027, É-028 et É-052. Dans tous les autres cas, le plan v1 fait loi.

---

## 2. LES 5 APPORTS TECHNIQUES À FUSIONNER DANS LE PLAN v1

Ces 5 améliorations issues du v2.0 ont passé l'audit avec succès et doivent être intégrées lors de l'exécution du plan v1 :

### 2.1 — Scanner Gitleaks en complément (→ Fusion dans `É-027` v1)
Ajouter un job dédié `secret-scan.yml` utilisant `gitleaks/gitleaks-action` **en plus** du scanner existant (qui fait déjà regex + entropie de Shannon). 
*Précautions* : `fetch-depth: 0` est requis pour scanner l'historique complet. Ce job ne doit pas être le bloqueur unique en cas de panne réseau externe. La variable `GITLEAKS_LICENSE` **n'est pas requise ici** (le dépôt appartient à un compte personnel), mais reste à considérer en cas de migration vers une organisation.

### 2.2 — Épinglage SHA + Moindre privilège (→ Fusion dans `É-024` / `É-026` v1)
Toutes les actions GitHub référencées dans les workflows doivent être épinglées par un **SHA de commit complet** et utiliser le moindre privilège par défaut : `permissions: contents: read`.

### 2.3 — Dependabot `groups` (→ Fusion dans `É-028` v1)
Au lieu de recréer un fichier, **corriger** le `.github/dependabot.yml` existant.
* Ajouter une entrée `pip` par répertoire contenant un manifeste réel.
* Ajouter une entrée `github-actions`.
* Utiliser la clé `groups:` pour n'ouvrir **qu'une PR par écosystème** (ex: mise à jour des dépendances groupées).
* Ajouter `open-pull-requests-limit: 3`.

### 2.4 — Job agrégateur `ci-success` (→ Fusion dans `É-024` / `É-025` v1)
Créer un job terminal nommé `ci-success` qui dépend de **tous** les autres jobs de la CI (`baseline-53`, `self-test-60`, `compile-python`, etc.). 
*C'est ce job unique qui sera exigé par la protection de branche*, évitant de casser les règles GitHub à chaque ajout futur de job.

### 2.5 — Hooks natifs correctement câblés (→ À intégrer à l'intérieur de `É-052` v1)
Au lieu des liens symboliques ou du pointage direct, créer un dossier versionné `.githooks/` contenant **deux wrappers exécutables** (`pre-commit` et `pre-push`) :
```bash
# .githooks/pre-commit (mode 100755, versionné)
#!/usr/bin/env bash
set -euo pipefail
root="$(git rev-parse --show-toplevel)"
exec "$root/53-Vigilum-Codex-2.0-Executable-Governance/core/hooks/pre-commit/tesla-pre-commit-main.sh" "$@"
```
L'activation se fera une seule fois par clone via `git config core.hooksPath .githooks`.
**Attention (R1)** : `core.hooksPath` désactive complètement le dossier `.git/hooks/` par défaut. Pour préserver les hooks non-Tesla existants (comme le `commit-msg` d'Ouroboros/Arena), il est impératif de rajouter un shim `commit-msg` dans `.githooks/` et de prévoir un argument `--status` pour prouver l'armement global. L'utilisation de ce mécanisme ne remplace pas `É-052` du v1, mais s'y intègre.

---

## 3. ABERRATIONS DU v2.0 DÉFINITIVEMENT ANNULÉES (DANGER)

Pour protéger l'intégrité du dépôt, l'exécution des consignes suivantes issues du v2.0 est **strictement interdite**. L'opérateur doit s'en tenir aux étapes originales du v1 :

- 🛑 **INTERDIT (M-01)** : La consolidation des modules depuis/vers `MVP-GITHUB/`. Ce répertoire n'existe pas localement sur `main`, c'est un miroir public. Son invocation était une hallucination.
- 🛑 **INTERDIT (M-02)** : Pointer `core.hooksPath` directement sur un sous-dossier de hooks. Cela bloque `git commit` avec une erreur `Permission denied`. Appliquer exclusivement la solution §2.5.
- 🛑 **INTERDIT (M-03)** : Corriger les 13 assertions des tests de la Gate R. Ces échecs prouvent que le code actuel est un stub simulé. Modifier le test au lieu du code détruit la preuve. **Appliquer les étapes `É-006` à `É-010` du v1.**
- 🛑 **INTERDIT (M-04)** : Corriger un prétendu conflit de format HTML/JSON dans le module 60. La vraie cause des 6 échecs est une incompatibilité de signature d'arguments. **Appliquer l'étape `É-013` du v1.**
- 🛑 **INTERDIT (M-05)** : Ajouter aveuglément `requests`, `typer` et `pydantic` dans un requirements racine. Ce sont des dépendances fabriquées ou transitives, qui violent la doctrine stdlib-first. **Appliquer l'étape `É-032` du v1 (manifestes par module).**
- 🛑 **INTERDIT (M-06)** : Purger le dossier `evidence/` à l'aveugle avant d'avoir qualifié la politique. Cela casserait la chaîne de hachage. **Appliquer l'étape de politique de rétention `É-044` du v1.**
- 🛑 **INTERDIT (E-04, ancien M-07)** : Appliquer un fail-open sur `lint_all.sh` (succès sans linter). **Appliquer la sémantique de l'étape `É-019` du v1 (outil absent = UNAVAILABLE, pas SUCCESS).**

---

## 4. RESTAURATION DES CRITÈRES DE CLÔTURE

Le v2.0 a supprimé deux critères vitaux et promu des détails cosmétiques. Les 16 critères de clôture (CA-01 à CA-16) qui font loi sont **uniquement ceux du document v1 original**. 

La clôture du chantier de Refactoring nécessitera obligatoirement de satisfaire à nouveau la **Rétention des preuves** (CA-15 original) et l'**Intégrité du registre des déférés** (CA-16 original). L'absence d'un seul de ces critères bloque la clôture.
