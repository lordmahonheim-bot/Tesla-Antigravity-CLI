# Scheduler Plan - Test-Refactor-Auth

**Mode d'exécution : Série avec Parallélisme partiel en fin de chaîne**

```mermaid
graph TD
    N1[N1: Research & Architecture] --> N2[N2: Code Refactoring]
    N2 --> N3a[N3a: Premortem Audit]
    N2 --> N3b[N3b: GitHub Manager Review]
```

- **N1** : Séquentiel. Attendre fin complète.
- **N2** : Séquentiel. Dépend de N1.
- **N3a / N3b** : Fan-out parallèle après N2. Fan-in avant de marquer le chantier DONE.
