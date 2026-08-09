# PLAN D'INTERVENTION ULTRA : SIA-TESLA-H (Self-Improving Harness)
**Statut :** Version Opérationnelle Ultime (Master Blueprint Corrigé & Validé)
**Auteur :** Tesla (Agent Principal)
**Date :** 2026-07-11

---

## 0. Doctrine Fondatrice
SIA-TESLA-H s'appuie sur quatre dogmes inébranlables pour empêcher l'emballement du système :
1. **Harness-Only Garanti** : Interdiction formelle de toucher aux poids de modèles. Le système ne produit que des propositions de patchs de Harness (prompts, workflows, SKILL, routage, politiques, mémoire).
2. **Zéro Persistance Sans Gate** : Aucune écriture directe dans `SKILL.md`, `TESLA.json` ou `FORCE_TOOLING`. Tout passe obligatoirement par le pipeline `RCA → PATCH_QUEUE → ARENA → GATE → (CANONICAL ou rollback)`.
3. **Zéro Contournement de la Gouvernance** : Impossible de désactiver l'Oversight Gate, le TGG (Tesla Governance Gateway), ni de faire des auto-push Git.
4. **Token-Frugalité Mesurable** : Respect strict du Budget Ledger (540k tokens) et des caps par mission (10–15k). Surveillance systématique du `token_burn_rate` avant/après SIA.

---

## 1. Les Piliers Architecturaux Clés

### Pilier 3 – Observabilité Totale
Chaque exécution produit un `loop_trace.jsonl` conforme à un schéma minimal strict :
- `run_id`, `task_id`, `agent_id`, `phase`, `timestamp`
- `action_type` (skill|tool|mcp|native), `capability`
- `status` (SUCCESS|FAIL|RETRY|ESCALATE)
- `duration_ms`, `token_usage` {input, output, total}
- `errors`, `lsp_diagnostics`, `artifacts[]`

### Pilier 5 – Fitness Multi-Signal (Scoring)
La décision ne repose plus uniquement sur le LSP. Fonction pondérée :
- **Pyright/LSP (20%)**, **Tests Unitaires & Smoke (25%)**, **Score Mission (20%)**, **Sécurité (15%)**, **Coût Tokens (10%)**, **Temps (5%)**, **Maintenabilité (3%)**, **Confiance/Preuve (2%)**.
- **Règles de Décision** :
  - `Score ≥ 85` ET aucun signal bloquant → **CANDIDAT PROMOTION**.
  - `70 ≤ Score < 85` → **REVUE HUMAINE/AUDITOR**.
  - `Score < 70` → **REJET**.
  - Toute violation de sécurité ou régression critique → **REJET IMMÉDIAT**.

### Pilier 10 – Garbage Collection (Anti-Semantic Bloat)
Des seuils durs sont imposés pour limiter le *Semantic Bloat* (RPN 60) :
- Taille d'un `SKILL.md` critique **≤ 8k tokens ou 150 lignes**.
- Croissance hebdomadaire **≤ +500 bytes ou +5 %**.
- **≤ 10%** des leçons candidates sont promues en CANONICAL.
- Revue de *Garbage Collection* hebdomadaire ou après 10 patchs.

### Pilier 12 – Industrialisation
Chaque capacité SIA suit un cycle de vie formel : `Draft → Experimental → Validated → Stable`. SIA-TESLA-H passera en `Validated` uniquement après un pilote réussi.

---

## 2. Le Pipeline à 8 Rôles (Ingénierie Opérationnelle)

| Rôle | Artefact Clé | Contrainte | Mapping Tesla |
|------|--------------|------------|---------------|
| **Mission Agent** | Résultats + statut | Ne modifie pas le Harness | `tesla-master-code`, `tesla-web-raider` |
| **Telemetry Collector** | `loop_trace.jsonl` | Schéma JSONL obligatoire | `tesla-loop-orchestrator` |
| **Evaluator** | `evaluation_report.json` | Score multi-signal | `tesla-code-auditor` |
| **Root Cause Analyzer** | `root_cause_report.json` | 1 cause racine principale stricte | `premortem` / N5 |
| **Optimizer (Meta-Agent)** | `patch_proposal.json` + diff | Jamais d’application directe | Meta-Agent SIA |
| **Arena Runner** | `arena_report.json` | Tests baseline + non-régression | Workspace `arena/` |
| **Validator (Gatekeeper)** | `gate_decision.json` | Décision explicite et traçable | `tesla-code-auditor` + Lord Mahonheim |
| **Memory Curator** | MAJ `LESSONS_REGISTRY.md` | Respect des seuils anti-bloat | `tesla-curator-prime` + Alexandria |

---

## 3. L'Architecture de la Mémoire (3 Niveaux)
1. **SHORT MEMORY** : Supporté par `loop_trace.jsonl`. Observations éphémères liées au run. Pas d'usage direct par les prompts.
2. **WORKING MEMORY** : `PATCH_QUEUE.md` & `LESSONS_REGISTRY.md`. Leçons candidates et patchs testés en arena.
3. **CANONICAL MEMORY** : `SKILL.md` et Alexandria. Seules les leçons testées, scorées et validées y entrent.

> **Règle absolue d'Écriture :** Le Méta-Agent a l'interdiction formelle d'ajouter "une phrase de plus" au bas d'un SKILL. Il doit systématiquement **refactoriser** l'ensemble du document pour maintenir la taille sous les seuils.

---

## 4. Garde-Fous Systèmes (Circuit-Breakers)

### 4.1 Hard-Caps Locaux
- **Boucle courte LSP** : `max_lsp_retries = 3` par mission.
- **Patchs par incident** : 1 patch principal + 1 alternative maximum.
- **Générations SIA par mission** : 3 maximum.
- **Durée** : Boucle courte (5–10 min max), Boucle longue (20–30 min max).

### 4.2 Hard-Caps Globaux (Liés au Budget Ledger)
- **Budget Global du Chantier** : 540k tokens I/O.
- **Cap par mission simple** : 10–15k tokens ou baseline + 20% (hard-codé dans `tesla-loop-orchestrator`).
- **Alertes N5 (Premortem)** déclenchées immédiatement si :
  - Taux de rejet Gate > 30 %.
  - Le *token burn rate* par tâche augmente de >20 % post-intégration SIA.

---

## 5. Roadmap d'Exécution et Critères de Sortie

### Phase 0 : Gel et Cadrage Sécuritaire (Jour 1)
- **Objectif** : Aucune autopersistance possible.
- **Actions** : Création de `SIA_POLICY.md`, `PATCH_QUEUE.md`, `LESSONS_REGISTRY.md`. Segmentation de `settings.json` en profils (`readonly`, `dev_arena`, `sensitive`, etc.).
- **Critère de Sortie** : Impossibilité pour un agent d'écrire dans un fichier canonique sans passer par la Gate.

### Phase 1 : Télémétrie & Baselines (Jours 2–3)
- **Objectif** : Mesurer avant de modifier.
- **Actions** : Exécuter 5-10 tâches de référence sans SIA. Mesurer temps, tokens, erreurs. Définir `loop_trace.schema.json`.
- **Critère de Sortie** : `BASELINES.md` complet. Chaque tâche pilote possède un `loop_trace` conforme.

### Phase 2 : Boucle Courte - Self-Healing LSP (Jours 4–5)
- **Objectif** : Rendre robuste la boucle `ACT → VERIFY`.
- **Actions** : Brancher `karellen-lsp-mcp` sur `tesla-master-code`. Fixer `max_retries = 3`. Aucune modification du Harness.
- **Critère de Sortie** : Diminution visible des erreurs LSP répétées sans explosion de tokens ni boucle infinie.

### Phase 3 : Boucle Longue & Arena (Jours 6–10)
- **Objectif** : Fermer le cycle complet sans toucher au canonique.
- **Actions** : Implémenter RCA, Meta-Agent et Arena. Implémenter la Gate (auto-gate pour mineur, Auditor pour standard, Mahonheim pour majeur).
- **Critère de Sortie** : Au moins un cycle `incident → patch → arena → rejet/acceptation` exécuté avec succès.

### Phase 4 : Pilote Gouverné sur `tesla-master-code` (Jours 11–20)
- **Objectif** : Preuve de valeur en conditions réelles contrôlées.
- **Actions** : Choix de 10 tâches Python. Exécution croisée (Baseline vs Boucle courte vs Boucle Longue complète).
- **Critères de Succès** :
  - `-30 %` minimum d'erreurs LSP répétées.
  - `-20 %` de retries moyens.
  - Taux de succès stable ou meilleur.
  - Coût tokens `≤ baseline + 20 %`.
  - 0 régression critique, 0 violation de sécurité, 0 patch appliqué hors-Gate.
  - Taux d'acceptation des patchs `≥ 70 %`, Rejet Gate `< 30 %`.
  - `SKILL.md` maintenu sous les 8k tokens / 150 lignes.

### Phase 5 : Industrialisation (Post-Pilote)
- **Objectif** : Extension mesurée du périmètre.
- **Actions** : N5 rafraîchit l'analyse Premortem. N3 certifie l'architecture. Passage de SIA-TESLA-H de `Experimental` à `Validated`.
- **Critère de GO/NO-GO** : 10 missions réussies, gains validés, Semantic Bloat maîtrisé. Déploiement progressif sur `tesla-code-auditor` puis `premortem`.
