# Spécification Technique : Interface Abstraite `cloud-execution-worker`

## Contexte (Phase 1.2)
La création de l'interface abstraite locale `cloud-execution-worker` permet de découpler l'exécution des tâches du moteur d'exécution distant, intégrant directement cette capacité au sein de l'environnement MIDGARD sans dépendre de l'infrastructure de Jules.

## Rôle et Responsabilités
- **Abstraction de l'Exécution** : Agit comme une interface unifiée (API ou module local) pour l'exécution asynchrone des tâches (scripts, calculs, analyses de code).
- **Autonomie de MIDGARD** : Remplace les appels dépendants de Jules par un routage local ou des pools de workers isolés (ex: via subprocess, Docker local, ou des files d'attente internes).
- **Isolation des Processus** : Garantit que les exécutions de tâches n'impactent pas les processus principaux de l'orchestrateur.

## Architecture et Intégration à MIDGARD (Sans Jules)
1. **Gestionnaire de File (Queue Manager)** : 
   `cloud-execution-worker` s'appuie sur une file d'attente locale (ex: Redis ou simple file en mémoire) hébergée dans l'écosystème MIDGARD.
2. **Worker Pool (Pool de Processus)** : 
   Les instances de l'interface abstraite instancient des workers locaux (ex: `multiprocessing` en Python ou conteneurs éphémères) pour exécuter le code de manière sécurisée.
3. **Interfaces (I/O)** :
   - **Input** : Reçoit un payload JSON standardisé (ID tâche, commande/code, environnement).
   - **Output** : Retourne un statut de complétion, un code de sortie, les flux stdout/stderr, et un temps d'exécution (similaire à une exécution cloud, mais géré localement).
4. **Indépendance** : 
   La logique de routage supprime toute référence aux endpoints de l'API de Jules. Le worker est auto-suffisant, rapportant directement les résultats au système de monitoring de MIDGARD.

## Spécification de l'Interface (Pseudocode)
```python
class CloudExecutionWorkerAbstract:
    def submit_task(self, task_payload: dict) -> str:
        # Valide et pousse la tâche dans la file locale MIDGARD
        pass

    def get_status(self, task_id: str) -> dict:
        # Interroge le statut de l'exécution (PENDING, RUNNING, COMPLETED, FAILED)
        pass

    def fetch_logs(self, task_id: str) -> str:
        # Récupère les logs d'exécution de la tâche isolée
        pass
```
