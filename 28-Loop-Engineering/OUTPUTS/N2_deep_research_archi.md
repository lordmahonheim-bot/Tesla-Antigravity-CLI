# SIA-TESLA : Architecture de l'Outil (Self-Improving AI)

## 1. Vision et Principes Directeurs
L'intégration du paradigme SIA (Self-Improving AI) dans l'écosystème Tesla vise à automatiser l'optimisation des performances des sous-agents sans verser dans la sur-ingénierie. Conformément à la doctrine Vigilum Codex et à l'état de l'art 2026, cette architecture se concentre exclusivement sur l'**amélioration du Harness** (prompts, logique d'orchestration, mémoire, outils) et non sur la modification des poids des modèles (weights), trop coûteuse et risquée en environnement local (MIDGARD).

**Lignes directrices :** Pragmatisme, modularité, auditabilité (Oversight), et réutilisation de l'arsenal existant.

## 2. Architecture Modulaire (Paradigme à 3 Agents)
Le système SIA pour Tesla s'articule autour de trois rôles fondamentaux, directement mappés sur les concepts d'Orchestrateur et de Skills :

1. **L'Agent Cible (Task-Specific Agent)**
   * *Rôle :* Exécute les tâches opérationnelles (ex. `tesla-master-code`, `tesla-web-raider`).
   * *Responsabilité :* Générer des traces d'exécution riches, des logs d'erreurs, et reporter l'utilisation des outils.
   
2. **L'Agent Évaluateur (Improvement Agent)**
   * *Rôle :* Fonction d'analyse (Fitness Function) basée sur les logs.
   * *Responsabilité :* Détecter les inefficacités (boucles infinies, hallucinations d'outils, dérives sémantiques) et mesurer le taux de succès par rapport aux critères initiaux de la mission.
   
3. **Le Méta-Agent d'Optimisation (Meta-Agent)**
   * *Rôle :* Ingénierie du Harness.
   * *Responsabilité :* Formuler des modifications structurelles (réécriture d'un prompt réflexif, ajustement d'un sous-workflow, injection de mémoire persistante) pour corriger les failles identifiées par l'Évaluateur.

## 3. Flux Opérationnel (Closed-Loop Evolution)
L'auto-amélioration fonctionne en cycle continu, intégré au flux `ACT-VERIFY-LEARN-REPEAT` géré par `tesla-loop-orchestrator` :

1. **Phase d'Exécution :** L'Orchestrateur délègue une mission à l'Agent Cible.
2. **Télémétrie :** Les logs d'exécution (erreurs LSP, succès/échec de recherche) sont centralisés.
3. **Diagnostic :** L'Évaluateur analyse les goulots d'étranglement (ex: "Le subagent répète la même commande erronée").
4. **Synthèse et Patch :** Le Meta-Agent génère une version optimisée du comportement de l'Agent Cible (ex: ajout d'une consigne anti-répétition dans le `SKILL.md`).
5. **Validation (Oversight Gate) :** Le patch n'est **jamais** appliqué à chaud. Il est soumis en tant qu'artefact ou "Pull Request locale" pour validation humaine (Lord Mahonheim) ou par un gatekeeper strict (`tesla-code-auditor`).

## 4. Stratégie de Résolution des Défis (État de l'Art)
* **Contre l'Amnésie :** Les optimisations validées sont systématiquement gravées dans la base de connaissance *Alexandria* ou directement dans les documents canoniques des Skills (ex: `SKILL.md`), garantissant une mémoire persistante des "leçons apprises".
* **Contrôle et Alignement :** Instauration d'un "Improvement Oversight Layer". Aucune modification du Harness ne peut contourner la validation par l'Agent Principal ou l'humain.
* **Évaluation Rigoureuse :** Avant de fusionner un patch, le système exécute des tests de non-régression via des environnements bac à sable pour éviter toute dégradation des performances existantes.

## 5. Pragmatisme et Low-Code
Pour éviter toute sur-ingénierie, l'implémentation de SIA-TESLA ne nécessite pas la création de nouveaux frameworks complexes :
* **Réutilisation :** Les rôles d'Évaluateur et de Meta-Agent peuvent être temporairement endossés par les processus analytiques existants (ex: `premortem`, `tesla-loop-orchestrator`).
* **Focus Immédiat :** Commencer par "Reflective Prompt Evolution" (l'agent qui suggère de meilleures instructions pour lui-même à la fin d'une tâche échouée) avant d'envisager la génération autonome de code complexe pour ses propres outils.

---
*Ce document définit le cadre conceptuel opérationnel. Aucune exécution scriptée n'a été implémentée prématurément.*
