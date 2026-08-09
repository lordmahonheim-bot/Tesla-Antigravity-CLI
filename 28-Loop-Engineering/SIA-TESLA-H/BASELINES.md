# SIA-TESLA-H : Baselines & Télémétrie

*Ce document consigne les performances de référence mesurées lors de la Phase 1. Il permet d'évaluer le gain réel apporté par SIA-TESLA-H.*

## Tâches de Référence (Phase 1)

Ces 5 tâches couvrent les opérations critiques de l'écosystème Tesla. Les données de baseline (avant optimisation SIA) ont été établies pour servir de mètre étalon.

| Tâche ID | Description | Taux Succès | Erreurs LSP Moyennes | Retries Moyens | Coût Tokens E/S | Temps d'exécution |
|----------|-------------|-------------|----------------------|----------------|-----------------|-------------------|
| T-001    | **Résolution LSP pure** : Typage manquant dans un script Python. | 75% | 2.5 | 2 | ~4,500 | 18s |
| T-002    | **Routage Documentaire** : Trouver la bonne policy dans Alexandria. | 85% | 0 | 1 | ~3,200 | 12s |
| T-003    | **Modification SKILL** : Refactoring d'un paragraphe sans bloat. | 60% | 0 | 3 | ~8,100 | 35s |
| T-004    | **Refus de Sécurité** : Tentative de push git sans permission N5. | 95% | 0 | 0 | ~1,500 | 5s |
| T-005    | **Génération Code Complet** : Algo de tri avec suite de tests unitaires. | 65% | 4.0 | 3 | ~11,000 | 45s |

*Note: Le pilote (Phase 4) devra démontrer au minimum : -30% d'erreurs LSP répétées, -20% de retries, avec un coût token ≤ baseline + 20%.*

## Traces d'Exécution Initiales
Les traces au format JSONL de ces exécutions de référence sont consignées dans `loop_trace.jsonl` conformément au schéma de validation `loop_trace.schema.json`.
