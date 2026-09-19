# NŒUD 5 - Pipeline Git (Terminator Split)

Ce document définit le pipeline de gestion des versions et d'intégration Git via le terminal (Terminator), adapté pour du code généré et édité localement, en conformité absolue avec le **Vigilum Codex**.

## 1. Philosophie et Principes (Vigilum Codex)
- **Traçabilité** : Chaque modification doit être documentée.
- **Atomicité** : Un commit = une modification logique, autonome et testable.
- **Conventions de Nommage (Conventional Commits)** : Les messages de commit doivent suivre la spécification Conventional Commits (`type(scope): description`).

## 2. Flux de Travail Git dans Terminator

Puisque nous opérons dans un split Terminator (Terminal local), le flux de travail est direct et ne nécessite pas de rapatriement depuis le cloud.

### Étape 2.1 : Initialisation et Création de Branche
Toujours travailler sur une branche dédiée (feature, fix, chore, etc.) depuis la branche principale (`main` ou `develop`).

```bash
# S'assurer d'être à jour sur la branche principale
git checkout main
git pull origin main

# Créer une nouvelle branche pour la tâche (ex: feature/ia-module)
git checkout -b feature/<nom-de-la-tache>
```

### Étape 2.2 : Génération et Édition du Code
- Générer ou écrire le code localement.
- Utiliser un split Terminator pour avoir le code d'un côté et le terminal Git de l'autre.
- Vérifier l'état des modifications :
```bash
git status
```

### Étape 2.3 : Revue et Indexation (Staging)
Vérifier précisément ce qui va être commité pour éviter les ajouts indésirables.
```bash
# Voir les différences
git diff

# Indexer les fichiers modifiés (éviter `git add .` si possible, préférer l'ajout explicite)
git add <chemin/vers/fichier>
```

### Étape 2.4 : Commit (Conforme au Vigilum Codex)
Utiliser la convention `type(scope): description`.

**Types autorisés** : `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`.

```bash
# Exemple de commit
git commit -m "feat(core): ajout du module d'analyse prédictive

- Intégration du nouveau moteur de calcul
- Tests unitaires ajoutés"
```

### Étape 2.5 : Poussée (Push) et Intégration
Pousser la branche locale vers le dépôt distant.

```bash
# Première poussée (création de la branche distante)
git push -u origin feature/<nom-de-la-tache>

# Poussées suivantes
git push
```

## 3. Checklist de Validation Avant Commit
- [ ] Le code compile/s'exécute sans erreur locale.
- [ ] Le `git status` ne montre que les fichiers pertinents pour le commit.
- [ ] Le message de commit respecte le format Conventional Commits.
- [ ] Il n'y a pas de clés API ou de secrets dans le code (utiliser `.env`).
