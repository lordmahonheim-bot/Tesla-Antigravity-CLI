# SIA-TESLA-H : Plan d'Intervention Ultime (Harness-Only Pilot)
**Statut :** Version Master Consolidée (Fusion Apodex, RENA, ChatGPT, et Tesla-Optimal)
**Date :** 2026-07-11
**Auteur :** Tesla (Agent Principal)
**Livrable :** Ultime feuille de route d'implémentation SIA

---

## 0. Résumé Exécutif & Cadrage
Après la convergence des audits de nos meilleurs tacticiens (Apodex, RENA, ChatGPT) et la validation interne (N1-N5), l'intégration de l'auto-amélioration dans Tesla adopte un profil strict, mesurable et gouverné. 

**Nom Opérationnel : `SIA-TESLA-H`** 
Le suffixe "-H" garantit que le système est strictement **Harness-Only**. Il n'y aura aucune modification de poids de modèle. Le système fonctionnera sous la doctrine RENA : *"Moins d'auto-modification. Plus de propositions testées. Zéro persistance sans preuve."*

---

## 1. L'Architecture Augmentée (Le Pipeline à 8 Étapes)
L'ancien modèle monolithique à 3 agents évolue vers une chaîne de responsabilité spécialisée (inspirée de l'audit ChatGPT et du pipeline RENA) :

1. **ACT (Target Agent)** : L'Agent Cible (ex: `tesla-master-code`) exécute la mission et génère des traces JSON standardisées.
2. **VERIFY (Multi-Signaux)** : Le LSP (Pyright) n'est plus la seule *Fitness Function*. La vérification inclut : LSP (20%), Tests Unitaires (25%), Sécurité/Scanner (15%), Coût Tokens (10%).
3. **EVALUATE & ROOT CAUSE** : Analyse des logs pour isoler la cause racine (Prompt, Tool, Skill, ou Gouvernance) et scorer la performance de l'itération. Apprentissage par l'échec **ET** par le succès.
4. **PROPOSE (Meta-Agent)** : Génération d'un *Patch de Harness* structuré et argumenté (Pull Request locale), jamais appliqué à chaud.
5. **SANDBOX** : Le patch proposé est déployé dans un bac à sable isolé pour mesurer empiriquement le gain et s'assurer de la non-régression.
6. **GATE (Oversight)** : Le filtre décisionnel. Un patch classé "Mineur" et validé en Sandbox peut être auto-approuvé. Un patch "Majeur" ou "Critique" exige le sign-off de Lord Mahonheim.
7. **PERSIST (Memory Curator)** : Enregistrement de la leçon selon l'architecture de mémoire à 3 niveaux.
8. **MONITOR** : Évaluation continue de la dérive (Token Burn Rate, Croissance documentaire).

---

## 2. Les 4 Garde-Fous Systémiques (Mitigation Premortem)

### 2.1. Protection de la Mémoire : Architecture à 3 Niveaux (Anti-Semantic Bloat)
Pour éviter que `SKILL.md` ne devienne illisible (Semantic Bloat), la mémoire est scindée :
- **Niveau 1 (SHORT)** : Leçons temporaires liées à un run spécifique (Logs).
- **Niveau 2 (WORKING)** : `LESSONS_REGISTRY.md` (Registre transitoire des améliorations testées).
- **Niveau 3 (CANONICAL)** : `SKILL.md`. Le Meta-Agent n'ajoute pas de texte brut. Il déclenche un "Semantic Garbage Collector" qui condense et refactorise les connaissances pour respecter une taille limite stricte (+15% max par mois).

### 2.2. Taxonomie des Patchs (Anti-Hallucination)
- **Mineur :** Typo, clarification de wording → *Auto-approbation possible.*
- **Standard :** Règle comportementale courte → *Validation `tesla-code-auditor`.*
- **Majeur :** Changement de workflow ou d'outil → *Validation Humaine (Lord Mahonheim).*
- **Interdit :** Auto-push, contournement sécu, lecture de secrets → *Rejet automatique et Hard-Kill.*

### 2.3. Circuit-Breakers (Anti-Token Drain)
- **Local :** Maximum 3 retries de Self-Healing (LSP) par boucle.
- **Global :** Budget plafond imposé dans `tesla-loop-orchestrator` (ex: +20% max vs baseline).
- Coupure automatique de la boucle si le plafond est dépassé, avec remontée d'alerte.

### 2.4. Télémétrie Standardisée (Observabilité)
Création d'une couche d'observabilité indépendante avec schémas JSON stricts :
- `loop_trace.schema.json` : Suivi exhaustif du cycle ACT-VERIFY.
- `patch_proposal.schema.json` : Modélisation formelle du correctif (cause, cible, diff, risque).

---

## 3. Plan de Déploiement Opérationnel (Phasage)

### Phase 0 : Sécurisation et Baselines (J-1)
- Création de `SIA_POLICY.md` interdisant l'auto-push et la modification des poids.
- Mesure de 3 tâches de référence sans SIA pour définir la baseline (Temps, Tokens, Erreurs).

### Phase 1 : Télémétrie et Signaux (J-2/3)
- Implémentation des schémas `loop_trace` et `patch_proposal`.
- Intégration de la "Fitness Function Multi-Signaux" (LSP + Tests + Sécurité).

### Phase 2 : Le Pilote de Boucle Courte (J-4/5)
- Activation du mode `SIA-TESLA-H` uniquement sur l'agent `tesla-master-code`.
- Implémentation de l'évaluation, des circuit-breakers de retries, et du Sandboxing de vérification.

### Phase 3 : La Gouvernance de la Mémoire (J-6/7)
- Mise en place du registre `LESSONS_REGISTRY.md` et de la Patch Queue.
- Déploiement du Memory Curator (Garbage Collector) pour protéger les documents `SKILL.md`.
- Activation du système de Validation Automatique (Gate) pour les patchs classés "Mineur".

### Phase 4 : Certification et Scalabilité (J-8+)
- Analyse des métriques de la phase pilote (Taux d'acceptation des patchs, ROI tokens).
- Décision GO/NO-GO de Lord Mahonheim.
- Si GO : Extension de `SIA-TESLA-H` à `tesla-code-auditor`, puis `premortem`, puis `tesla-web-raider`.

---
**Conclusion :** Cette architecture ultime ne fait pas qu'apprendre de ses erreurs ; elle mesure, simule, valide et condense ses connaissances. Elle maintient l'humain en clé de voûte stratégique tout en automatisant l'optimisation micro-tactique. `SIA-TESLA-H` est prêt.
