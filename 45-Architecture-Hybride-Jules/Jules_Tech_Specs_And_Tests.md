# Spécifications Techniques et Tests - Worker Cloud (Phase 2.1)

## 1. Structure Imposée
- L'architecture doit suivre le pattern hexagonal.
- Les fichiers de configuration doivent être au format YAML.
- Le dossier racine doit contenir:
  - `src/` (code métier)
  - `tests/` (fichiers de tests)
  - `scripts/` (scripts d'automatisation)
  - `infra/` (IaC, Terraform, Docker)

## 2. Règles de Linting
- Linter obligatoire: `flake8` et `black` (Python) ou équivalent (ESLint, Prettier pour Node).
- Les conventions de nommage doivent respecter le standard `snake_case` pour les variables/fonctions et `PascalCase` pour les classes.
- Longueur de ligne maximale: 100 caractères.
- Les docstrings sont obligatoires pour toutes les fonctions publiques (format Google ou Sphinx).

## 3. Conditions de Succès des Tests
- Couverture de test (Test Coverage) minimale : 85% via `pytest-cov` ou `nyc`.
- Les tests de bout en bout (E2E) doivent réussir dans un environnement conteneurisé.
- Les Smoke Tests (tests de santé du worker) doivent vérifier la connectivité aux APIs Cloud et DBs en moins de 5 secondes.
- Les résultats de l'auditeur `tesla-code-auditor` doivent aboutir au verdict `PASS` (pas de fail critique).

## 4. Règles CI/CD Locales (Avant PR)
- Un hook `pre-commit` doit exécuter:
  - Formatage de code.
  - Scan de vulnérabilités (`bandit` ou `npm audit`).
  - Lancement des tests unitaires rapides.
