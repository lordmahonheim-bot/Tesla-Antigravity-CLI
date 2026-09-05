# Technical Specifications and Tests - Cloud Worker (Phase 2.1)

![Status](https://img.shields.io/badge/Status-MVP-blue) ![Ecosystem](https://img.shields.io/badge/Ecosystem-TESLA%20ANTIGRAVITY-purple) ![Security](https://img.shields.io/badge/Security-ID%20LOCKED-red) ![Python](https://img.shields.io/badge/Python-3.12+-blue)

## 1. Imposed Structure
- The architecture must follow the hexagonal pattern.
- Configuration files must be in YAML format.
- The root directory must contain:
  - `src/` (business logic)
  - `tests/` (test files)
  - `scripts/` (automation scripts)
  - `infra/` (IaC, Terraform, Docker)

## 2. Linting Rules
- Mandatory linter: `flake8` and `black` (Python) or equivalent (ESLint, Prettier for Node).
- Naming conventions must respect the `snake_case` standard for variables/functions and `PascalCase` for classes.
- Maximum line length: 100 characters.
- Docstrings are mandatory for all public functions (Google or Sphinx format).

## 3. Test Success Conditions
- Minimum Test Coverage: 85% via `pytest-cov` or `nyc`.
- End-to-End (E2E) tests must pass in a containerized environment.
- Smoke Tests (worker health tests) must verify connectivity to Cloud APIs and DBs in under 5 seconds.
- The results from the `tesla-code-auditor` must lead to a `PASS` verdict (no critical fail).

## 4. Local CI/CD Rules (Pre-PR)
- A `pre-commit` hook must execute:
  - Code formatting.
  - Vulnerability scan (`bandit` or `npm audit`).
  - Fast unit tests execution.
