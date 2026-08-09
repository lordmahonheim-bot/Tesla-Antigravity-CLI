# Chantier SGC : UNDERSTAND-ANYTHING-TESLA-INTEGRATION

**Date** : 2026-07-10
**Version** : 1.0

## 1. Objectif
Auditer, étudier, analyser et rédiger un plan d'intervention sur le fichier `/home/lord-mahonheim/Documents/SyncThing/QWEN - Data/Understand Anything .txt` en parfaite harmonie avec l'écosystème Tesla et Antigravity CLI.

## 2. Contraintes
- Exécution stricte selon la chaîne pipeline (N1 -> N2 -> N3 -> N4).
- Les modifications de code doivent s'inscrire dans le standard `tesla-master-code` (wrapper LSP + Loop Engineering).
- Documentation indexée par `tesla-curator-prime` (Alexandria).

## 3. Complexité Préliminaire
**Medium/High** (Analyse de texte arbitraire + intégration d'un wrapper LSP + boucle d'ingénierie).

## 4. Mission Graph
Voir `OUTPUTS/mission_graph.yaml`

## 5. Scheduler Plan
Exécution séquentielle (Pipeline pur). Voir `OUTPUTS/scheduler_plan.md`.

## 6. Routage & Modèles (Capability Routing)
- Arcanis: Claude 3.5 Sonnet
- Curator: Claude 3.5 Sonnet / Gemini
- Premortem: GPT-4o
- Master Code: Claude 3.5 Sonnet
Voir `OUTPUTS/capability_routing.md`.

## 7. Budget & Token-économie
Allocation initiale : 60% Claude, 30% GPT, 10% Gemini.
Voir `OUTPUTS/budget_ledger.md`.

## 8. State Machine de Mission
- [ ] PREPARATION_COMPLETE
- [ ] N1_RUNNING -> N1_SUCCESS
- [ ] N2_RUNNING -> N2_SUCCESS
- [ ] N3_RUNNING -> N3_SUCCESS
- [ ] N4_RUNNING -> N4_SUCCESS
- [ ] MISSION_ACCOMPLISHED

## 9. Contrats d'Agents
Générés dans `OUTPUTS/agent_contracts/` pour N1, N2, N3, N4.

## 10. Premortem initial
Les risques d'économie de tokens ont été alloués au nœud N3, mais le risque principal est un fichier source mal formaté (`Understand Anything .txt`) causant des hallucinations chez N1.

## 11. Alexandria & Clôture
À remplir post-mission par `tesla-curator-prime`.
