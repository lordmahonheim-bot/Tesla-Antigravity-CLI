# Original User Request

## Initial Request — 2026-07-09T23:38:20Z

Construire les deux composants manquants de l'architecture "Loop Engineering" dans l'écosystème Tesla/Antigravity sur MIDGARD :
le Skill `tesla-loop-orchestrator` (chef d'orchestre du cycle Act/Verify/Learn/Repeat avec transitions PASS/DELAY/BLOCK)
et l'Agent Évaluateur `tesla-code-auditor` (chaîne de validation multi-validateurs : SemGrep + Pyright + Smoke Tests + Policy Engine).
Ce chantier est précédé d'une Phase -1 (Capability Discovery) et d'un audit croisé obligatoire par les quatre agents d'élite.

Working directory: `/home/lord-mahonheim/bifrost/tesla`
Integrity mode: development (gouvernance Tesla et Vigilum Codex comme seule contrainte)

Reference material:
- Rapport Curation Loop Engineering : `/home/lord-mahonheim/bifrost/tesla/OUTPUTS/rapport_curation_portage_loop_engineering_v1.0.md`
- Étude de faisabilité : `/home/lord-mahonheim/bifrost/tesla/OUTPUTS/etude_faisabilite_integration_loop_library_v1.0.md`
- Référentiel SemGrep + Vigilum Codex : `/home/lord-mahonheim/Documents/SyncThing/QWEN - Data/SemGrep.txt`
- Répertoire des Skills existants : `/home/lord-mahonheim/bifrost/tesla/.agents/skills/`
- Gouvernance : `/home/lord-mahonheim/bifrost/tesla/.agents/AGENTS.md`

---

## Phase -1 — Capability Discovery (obligatoire en premier)

Avant tout travail, l'orchestrateur applique la doctrine Force-Tooling :

**Discovery → Selection → Routing**

Inventorier automatiquement et produire un fichier `OUTPUTS/capability_inventory.md` listant :
- Skills existants (`.agents/skills/`) avec leur rôle et leur statut
- MCP disponibles et leurs outils
- Outils système disponibles sur MIDGARD (Python, SemGrep, Pyright, Git…)
- Wrappers Python existants dans l'écosystème
- Règles FORCE_TOOLING et AGENTS.md en vigueur

**Objectif :** s'assurer qu'aucun composant ne soit recréé s'il existe déjà sous une autre forme.

---

## Requirements

### R1. Audit croisé de l'écosystème Tesla (Phase 0 — après Capability Discovery)

L'orchestrateur simule les quatre agents d'élite Tesla comme **personas experts distincts**, en produisant quatre rapports sectoriels indépendants avant toute synthèse. L'ordre d'exécution est imposé :

1. **Tesla-Arcanis-360** (persona) : Cartographie factuelle complète de l'écosystème actuel. Identifie les points d'insertion optimaux pour les nouveaux composants. S'appuie sur `capability_inventory.md`.
2. **Tesla-Curator-Prime** (persona) : Audit de cohérence architecturale. Vérifie l'absence de redondance avec les Skills existants. Produit les spécifications finales de chaque composant.
3. **Tesla-Master-Code** (persona) : Contribution technique — évaluation de la faisabilité d'implémentation, bibliothèques Python disponibles sur MIDGARD sans réseau, contrats d'interface entre composants.
4. **Tesla-Premortem** (persona, en dernier) : Analyse de risques AMDEC/FMEA sur les deux composants. Identifie les scénarios d'échec probables, points de fragilité et contre-mesures.

Les 4 rapports sectoriels sont déposés dans `OUTPUTS/` nommés `rapport_[agent]_loop_engineering_v1.0_[date].md`.

**Format imposé pour la synthèse consolidée** (`OUTPUTS/plan_intervention_loop_engineering_v1.0_[date].md`) :
- Un **Dependency Map** des composants (qui dépend de quoi)
- Un **Sequence Diagram** Mermaid du cycle Act/Verify/Learn/Repeat complet
- Un **Resource Allocation Table** (quel agent/skill est responsable de quelle étape)
- Le Plan d'Intervention de haut niveau avec priorités et séquençage

---

### R2. Architecture — Skill `tesla-loop-orchestrator` : SKILL.md + Loop Contract

> Note : Le nom retenu est `tesla-loop-orchestrator` (et non `tesla-loop-engineer`).
> Rationale : le Skill orchestre les boucles, il ne conçoit pas le code.
> Le vrai "Engineer" reste `tesla-master-code`.

Créer sous `/home/lord-mahonheim/bifrost/tesla/.agents/skills/tesla-loop-orchestrator/` :

**`SKILL.md`** — Manuel de procédure interne définissant :
- Le cycle Act/Verify/Learn/Repeat et les 3 transitions de flux (PASS / DELAY / BLOCK) avec leurs conditions de déclenchement
- Les rôles explicites : Artisan (`tesla-master-code`) → Orchestrateur (`tesla-loop-orchestrator`) → Auditeur (`tesla-code-auditor`)
- Les règles d'escalade vers Mahonheim
- La structure canonique du Loop Contract (voir ci-dessous)
- Respecte la structure standard des Skills Tesla (front-matter YAML + sections markdown)

**Loop Contract formalisé** — Chaque boucle exécutée par l'orchestrateur doit respecter ce schéma contractuel :
```yaml
loop_contract:
  name: [identifiant unique]
  inputs: [liste des artefacts d'entrée et leur format attendu]
  outputs: [liste des artefacts de sortie et leur format]
  exit_conditions:
    pass: [condition objective de succès]
    block: [condition de blocage irréversible]
  retry_policy:
    max_iterations: [N]
    delay_strategy: [ex: fixed / exponential]
  timeout_seconds: [durée max]
  escalation_trigger: [condition déclenchant l'escalade à Mahonheim]
```
Ce schéma rend chaque boucle interchangeable et auditable.

---

### R3. Implémentation — Orchestrateur Python + Templates

Créer dans le répertoire du Skill `tesla-loop-orchestrator/` :

**`scripts/tesla_loop_orchestrator.py`** : Orchestrateur Python natif exécutable sur MIDGARD (sans dépendances réseau). Il :
- Lit un fichier Loop Contract (YAML)
- Invoque séquentiellement les étapes Act → Verify → Learn → Repeat
- Applique les transitions PASS / DELAY / BLOCK selon le verdict de l'Auditeur
- Journalise chaque cycle dans un fichier de log structuré (JSON + Markdown)
- Expose une interface CLI (`--help`, `--contract`, `--dry-run`)

**`templates/`** : Au minimum 2 templates YAML conformes au schéma Loop Contract :
- `loop_code_generation.yaml` : boucle de génération de code avec validation SemGrep+Pyright+Smoke
- `loop_doc_writing.yaml` : boucle de rédaction documentaire avec validation par agent-juge

---

### R4. Agent Évaluateur — `tesla-code-auditor` (chaîne multi-validateurs)

> L'Auditeur n'est pas un simple wrapper SemGrep. Il orchestre une chaîne de validation complète.

Architecture cible :
```
tesla-master-code
        │  (artefact de code)
        ▼
tesla-loop-orchestrator
        │  (étape Verify)
        ▼
tesla-code-auditor
        │
        ├── SemGrep       → sécurité & anti-patterns governance Tesla
        ├── Pyright       → syntaxe, types, imports (doctrine Self-Healing existante)
        ├── Smoke Tests   → exécution minimale sans erreur
        └── Policy Engine → règles de gouvernance non-code (nommage, répertoires, logs)
        │
        ▼
  Verdict : PASS / DELAY / BLOCK
```

Créer sous `/home/lord-mahonheim/bifrost/tesla/.agents/skills/tesla-code-auditor/` :

**`SKILL.md`** : Définit le rôle de l'Auditeur, son protocole d'évaluation en 3 niveaux, l'ordre d'exécution des validateurs, et l'interface d'entrée/sortie (artefact + contexte → verdict structuré + rapport).

**`scripts/semgrep_audit.py`** : Wrapper Python autour de `semgrep`. Prend en entrée un chemin, exécute `semgrep scan`, parse les résultats JSON, et produit un verdict PASS/DELAY/BLOCK avec rapport Markdown. Se base sur `/home/lord-mahonheim/Documents/SyncThing/QWEN - Data/SemGrep.txt` et le Vigilum Codex pour définir les patterns.

**`rules/tesla_custom_rules.yaml`** : Règles SemGrep personnalisées Tesla couvrant :
- **Sécurité Python** (≥3 règles) : injection de commandes, secrets en dur, `eval()` non contrôlé, permissions fichiers excessives
- **Gouvernance Tesla** (≥2 règles) : écriture hors des répertoires autorisés, push Git sans flag d'autorisation (`--no-verify` interdit), suppression de logs/traces

**`scripts/pyright_audit.py`** : Wrapper autour de `pyright` (ou `mypy` si Pyright absent sur MIDGARD). Valide syntaxe, types et imports.

**`scripts/smoke_test_runner.py`** : Exécute une vérification minimale d'exécution (`--help` ou `--dry-run`) sur le code produit et capture les erreurs runtime.

**`scripts/policy_engine.py`** : Vérifie les règles de gouvernance non-code (conventions de nommage fichiers/dossiers, présence des métadonnées YAML obligatoires, intégrité des logs).

**`scripts/code_auditor.py`** : Script maître qui orchestre la chaîne complète (SemGrep → Pyright → Smoke → Policy) et produit le verdict PASS/DELAY/BLOCK consolidé avec rapport synthétique Markdown.

---

### R5. Intégration et cohérence de l'écosystème

Une fois les composants créés et validés :
- `AGENTS.md` est mis à jour pour référencer `tesla-loop-orchestrator` et `tesla-code-auditor` dans la Section 4 (Politique de délégation)
- `INDEX.md` du Système de Gestion de Chantiers est mis à jour
- `PROJECT_STATE.md` est mis à jour avec l'état final du chantier
- Les Open-Items résiduels sont ajoutés dans `OUTPUTS/open_items_todo-Updated.md`

---

## Acceptance Criteria

### Capability Discovery (Phase -1)
- [ ] `OUTPUTS/capability_inventory.md` est présent et liste Skills, MCP, outils système, wrappers et règles Force-Tooling

### Audit Croisé (R1)
- [ ] 4 rapports sectoriels physiquement présents dans `OUTPUTS/` nommés `rapport_[agent]_loop_engineering_v1.0_[date].md`
- [ ] 1 rapport de synthèse (`plan_intervention_loop_engineering_v1.0_[date].md`) contenant : Dependency Map, Sequence Diagram Mermaid, Resource Allocation Table, Plan d'Intervention
- [ ] Le rapport Premortem identifie ≥5 risques classifiés par criticité (Critique / Élevé / Moyen)

### Skill `tesla-loop-orchestrator` (R2 + R3)
- [ ] `SKILL.md` est présent et valide (front-matter YAML parseable, toutes les sections présentes, Loop Contract documenté)
- [ ] `tesla_loop_orchestrator.py` s'exécute sans erreur : `python3 scripts/tesla_loop_orchestrator.py --help` retourne une aide valide
- [ ] `tesla_loop_orchestrator.py` traite un Loop Contract YAML de test et produit un fichier de log JSON
- [ ] ≥2 templates YAML conformes au schéma Loop Contract sont présents et parseable sans erreur

### Agent `tesla-code-auditor` (R4)
- [ ] `SKILL.md` est présent et valide
- [ ] `semgrep_audit.py`, `pyright_audit.py`, `smoke_test_runner.py`, `policy_engine.py`, `code_auditor.py` sont présents et s'exécutent sans erreur (`--help`)
- [ ] `code_auditor.py` produit un verdict PASS/DELAY/BLOCK sur un fichier Python de test contenant ≥1 vulnérabilité connue
- [ ] `tesla_custom_rules.yaml` est valide SemGrep : `semgrep --validate --config rules/tesla_custom_rules.yaml` retourne 0 erreur
- [ ] Les règles custom couvrent ≥3 anti-patterns sécurité ET ≥2 anti-patterns gouvernance Tesla

### Intégration Écosystème (R5)
- [ ] `AGENTS.md` Section 4 référence les deux nouveaux composants
- [ ] `PROJECT_STATE.md` est mis à jour avec l'état final du chantier

---

## Definition of Done

Le chantier est clôturé uniquement lorsque **toutes** les conditions suivantes sont remplies :

- [ ] **Architecture validée** : les spécifications de R2 sont conformes aux rapports d'audit (R1) sans contradiction
- [ ] **Documentation indexée** : SKILL.md de chaque composant est lisible et autonome
- [ ] **Tests verts** : tous les Acceptance Criteria ci-dessus sont cochés
- [ ] **Aucun Open Critical** : zéro issue de criticité Critique ou Élevée non résolue dans le rapport Premortem
- [ ] **Rollback documenté** : une procédure de désinstallation/rollback est décrite dans chaque SKILL.md
- [ ] **Mémoire synchronisée** : `PROJECT_STATE.md`, `INDEX.md`, `open_items_todo-Updated.md` et `AGENTS.md` sont cohérents et à jour
