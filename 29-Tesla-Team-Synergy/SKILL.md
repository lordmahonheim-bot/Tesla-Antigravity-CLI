---
name: tesla-team-synergy
display_name: Tesla Mission Orchestrator
description: Meta-skill d'orchestration stratégique multi-agents Tesla. Produit un Mission Graph DAG, avec Capability Scoring indépendant des modèles, Scheduler, Budget Manager, contrats d'agents, state machine, et politique retry/fallback. Recommande le routage modèle / token-economy. AGENTS reste souverain pour l'exécution.
injection_type: shadow-targeted
target_subagent: self
version: 4.0
status: Stable
tags: [orchestration, multi-agent, mission-graph, capability-scoring, scheduler, token-economy, model-routing, sgc, learning-loop]
license: Vigilum Codex
author: Tesla / Mahonheim
depends_on:
  - SOUL.md >=3.0
  - ENGINE.md >=1.0
  - AGENTS.md >=4.0
  - FORCE_TOOLING.md >=1.0
  - GEMINI.md >=2.0
  - shadow-targeting-method.md >=1.0
---

# tesla-team-synergy – Tesla Mission Orchestrator
## SKILL.md v4.0

> Nom technique canonique : `tesla-team-synergy`  
> Titre fonctionnel : **Tesla Mission Orchestrator**

---

## 0. Mission

Transformer un chantier SGC en **équipe multi-agents coordonnée**, en produisant :

1. un **Mission Graph** DAG canonique,
2. des **contrats d'agents** typés,
3. un **Capability Scoring** indépendant des vendors,
4. un **Scheduler** avec dépendances parallèle/série/pipeline/fan-out/fan-in,
5. une **recommandation de routage modèle + Budget Manager**,
6. une **politique Retry / Fallback / Escalade**,
7. une **State Machine de mission**,
8. une **boucle d'apprentissage Alexandria**.

> [!CAUTION]
> **RÈGLE ABSOLUE N°4 – AGENTS délègue, il ne réimplémente pas.**
> L'Agent Principal doit systématiquement orchestrer et invoquer les sous-agents d'élite (via `invoke_subagent` ou `define_subagent`) pour exécuter une tâche spécialisée définie dans la table de délégation. En aucun cas il ne doit endosser leur rôle ou exécuter leur travail à leur place. Toute dérogation à cette règle est une violation majeure de la gouvernance Tesla.
>
> **Corollaire Anti-Usurpation (Verrouillage des Commandes Slash) :**
> L'injection contextuelle d'une compétence spécialisée via une commande utilisateur (ex: `/tesla-github-manager`) ne donne en aucun cas le droit à l'Agent Principal de s'approprier cette identité. L'Agent Principal (AGENTS) demeure un Orchestrateur pur. Face à l'invocation d'un Skill, il a l'obligation mécanique et absolue de :
> 1. Ne procéder à aucune exécution de script, d'édition de fichier ou de commande git lui-même.
> 2. Transférer immédiatement la mission et les directives à une entité distincte en utilisant exclusivement l'outil système `invoke_subagent`.
> 3. Attendre le rapport de ce sous-agent pour vous le restituer.
>
> **Spécificité du Mission Orchestrator :**
> Ce skill NE DÉLÈGUE PAS, N'EXÉCUTE PAS, NE SCHEDULE PAS À L'EXÉCUTION.
> Il produit des artefacts écrits : Mission Graph, Plan, contrats, budget.
> Seul AGENTS invoque les sous-agents via `invoke_subagent` / `define_subagent`.

---

## 1. Position dans la pile Tesla

```
SOUL → ENGINE → AGENTS → Tesla Mission Orchestrator (tesla-team-synergy)
                                        ↓
                          Mission Graph / Scheduler / Capability Scoring / Budget
                                        ↓
                              Skills / MCP / Tools
```

- **ENGINE** : raisonnement
- **AGENTS** : gouvernance, exécution du Plan
- **Tesla Mission Orchestrator** : produit le Plan stratégique

---

## 2. Contrats FORCE_TOOLING

**Entrée**
- `chantier_nom: string`
- `objectif: string`
- `contraintes: string[]`
- `complexité_préliminaire: Low | Medium | High`
- `budget_initial?: {claude_pct, gemini_pct, gpt_pct}`

**Sortie**
- `Gestion-de-Chantiers/[NOM]_v1.0_AAAA-MM-JJ.md` – SGC 11 sections
- `mission_graph.yaml` – DAG canonique
- `capability_routing.md` – scoring + modèle recommandé
- `scheduler_plan.md` – séquence avec dépendances
- `agent_contracts/` – 1 contrat par nœud
- `budget_ledger.md`
- DB Subagents-Skills loggée
- `MAIN_RENDUE_A_MAHONHEIM=1`

Maturité : Stable

---

## 3. Mission Graph

Team Synergy ne distribue jamais directement le travail. Il construit un **Mission Graph DAG**.

Exemple :

```
Mission: Refactor Module X
├── N1 Research
│     ├── Arcanis (OSINT)
│     └── Curator (doc)
├── N2 Architecture
│     ├── Arcanis
│     └── Premortem
├── N3 Code
│     ├── Master-Code
│     └── GitHub-Manager
└── N4 Documentation
      └── Curator
```

Format canonique : `mission_graph.yaml`

```yaml
mission: Refactor Module X
version: 1.0
nodes:
  - id: N1
    role: Research
    agents: [tesla-arcanis-360, tesla-curator-prime]
    depends_on: []
    contract_ref: contracts/N1.yaml
  - id: N2
    role: Architecture
    agents: [tesla-arcanis-360, premortem]
    depends_on: [N1]
  - id: N3
    role: Code
    agents: [tesla-master-code, tesla-github-manager]
    depends_on: [N2]
  - id: N4
    role: Documentation
    agents: [tesla-curator-prime]
    depends_on: [N3]
```

Le Mission Graph est la **Single Source of Truth**. Les agents sont une implémentation.

---

## 4. Capability Scoring – Routage indépendant des vendors

On ne choisit plus "Flash / Sonnet / Opus". On score des capacités.

Axes (0–100) :
- Reasoning
- Code
- Audit
- Memory / RAG
- Cost_efficiency  (100 = le moins cher)
- Latency

**Capability Matrix – v4.0**

| Modèle | Reasoning | Code | Audit | Memory | Cost | Latency | Profil d'usage |
|---|---|---|---|---|---|---|---|
| Gemini Flash | 40 | 55 | 45 | 70 | 100 | 100 | I/O volumétrique, recherche, doc |
| Gemini Pro | 78 | 75 | 70 | 80 | 65 | 70 | Planification, architecture |
| Claude Sonnet | 82 | 94 | 85 | 75 | 55 | 60 | Code, refactor, tests – cheval de bataille |
| Claude Opus | 95 | 92 | 96 | 80 | 15 | 35 | Premortem critique, arbitrage sécurité – RARE |
| GPT-OSS* | 70 | 80 | 60 | 60 | 85 | 55 | Scaffolding massif – *si disponible* |

Sélection : `score = w_reason*Reasoning + w_code*Code + w_audit*Audit - λ*cost_penalty`
avec poids définis par le type de nœud du Mission Graph.

Règles GEMINI.md impératives AVANT montée en gamme :
1. Low-Code First
2. Anti-Lecture Linéaire : `rg`, `jq`, Tree-sitter, search_router
3. Boucle LSP : `lsp_diagnostics` obligatoire

Voir `CAPABILITY_SCORING.md` pour la table complète.

---

## 5. Scheduler

Le Plan inclut un Scheduler explicite.

Modes :
- **Série** : A → B → C
- **Parallèle** : A || B
- **Pipeline** : streaming par lots
- **Fan-out** : 1 → N
- **Fan-in** : N → 1

Exemple :

```
N1 Research
   ↓
N2 Architecture  ⟷  N2b Premortem   (parallèle)
   ↓
N3 Code
   ↓
N4 Tests
   ↓
N5 Doc
```

Chaque nœud déclare : `depends_on`, `can_run_parallel_with`, `fan_out`, `critical_path: true/false`.

---

## 6. Contrats d'agents

Chaque nœud du Mission Graph expose un contrat :

```yaml
id: N3
agent: tesla-master-code
input: [plan_architecture.md, repo_path]
output: [patch.diff, tests_pass.log]
preconditions: [lsp_clean, git_clean]
postconditions: [tests_green, no_lsp_errors]
risks: [regression_api]
time_estimate_min: 25
cost_estimate_tokens: M
model_recommended: claude-sonnet
capability_min: {Code: 85, Reasoning: 70}
```

Team Synergy n'a pas besoin de connaître l'interne de l'agent, seulement son contrat.

---

## 7. Politique Retry / Fallback / Escalade

Pour chaque nœud :

```
Exécution
  ↓ échec ?
Retry x2 – même modèle, prompt resserré
  ↓ toujours KO ?
Fallback – modèle supérieur dans même famille
  ex: Sonnet → Opus, Pro → Opus, Flash → Pro
  ↓ toujours KO ?
Escalade Mahonheim – avec dossier : logs, tentatives, hypothèse blocage
  ↓
Abandon tracé – nœud marqué BLOCKED dans State Machine
```

Retry est loggé dans DB avec `attempt_n`.

Jamais plus de 2 retries automatiques sans changement de modèle.

---

## 8. Budget Manager – Token Economy v4

Chaque chantier ouvre un **budget envelope** :

```
Budget Chantier Refactor X
- Claude : 15 %
- Gemini : 60 %
- GPT-OSS : 25 %
```

Suivi temps réel dans `budget_ledger.md` :

| Nœud | Modèle | Tokens est. | Tokens réel | Quota groupe restant |
|---|---|---|---|---|
| N1 | gemini-flash | S | … | 82% |
| N3 | claude-sonnet | M | … | 71% |

Règles :
- Quotas : groupes Gemini / Claude / GPT-OSS – hebdo + fenêtre 5h glissante
- Circuit-breaker <15% restant → dégradation auto : Opus→Sonnet, Pro→Flash, loggé
- Tâches >25 min segmentées pour contrôler fenêtre 5h
- Appels coûteux en fin de chaîne, après filtrage Flash/Sonnet

---

## 9. State Machine Mission

```
CREATED
  ↓
PLANNED  ← Mission Graph validé
  ↓
RUNNING
  ├→ BLOCKED  → (retry/fallback) → RUNNING
  └→ WAITING   → dépendance externe
  ↓
REVIEW   ← Premortem + Premortem-Économie
  ↓
DONE
  ↓
ARCHIVED
```

Chaque transition est horodatée dans `mission_state.json`, indexée Alexandria.

Permet un futur tableau de bord multi-chantiers.

---

## 10. Protocole d'orchestration SGC

Déclencheur : « J'ouvre un chantier [NOM] pour [objectif]. »

1. **Cadrage** – complexité Low/Med/High, budget envelope initial, mapping rôles
2. **Mission Graph** – générer `mission_graph.yaml` + contrats d'agents
3. **Capability Scoring + Scheduler** – annoter chaque nœud : modèle, coût, dépendances
4. **PLAN.md SGC** – `Gestion-de-Chantiers/[NOM]_v1.0_AAAA-MM-JJ.md`, 11 sections, incluant tableau de routage
5. **Premortem + Premortem-Économie**
   - [ ] Opus remplaçable par Sonnet ?
   - [ ] Recherche en Flash ?
   - [ ] Volumétrie en Flash ?
   - [ ] Quota suffisant ? Plan dégradation ?
   - [ ] Shadow-targeting possible ?
6. **Exécution – AGENTS délègue** selon Scheduler
7. **Retry/Fallback** appliqué par AGENTS si échec nœud
8. **Synchronisation mémoire** – `log_subagent_parser.py` → `alexandria_brain.db`
   - `model_used, complexity, tokens_estimate, attempt_n, node_id`
9. **Rendu Mahonheim** – `MAIN_RENDUE_A_MAHONHEIM=1`, INDEX.md, PROJECT_STATE.md, Alexandria

---

## 11. Shadow-Targeting & Token-Economy

- Research / Doc → injecter Arcanis / Curator dans `self`, **forcé Gemini Flash**
- Log DB : `injection_method='shadow-targeting'`, `model_used`, `complexity`
- Rollback : 1. désactivation sémantique / 2. quarantaine physique / 3. DB `statut='inactive'` / 4. `update_session_history.py`
- Statuts : `active | inactive | expired | failed`

---

## 12. Learning Loop – Alexandria

Après chaque chantier :

```
Mission → Feedback → Performance / Qualité / Temps / Tokens → Leçon → Alexandria
```

Curator-Prime analyse :
- schémas de routage ayant tenu les quotas
- taux succès Sonnet vs Opus
- temps réel vs estimé par type de nœud
- retry rate par agent / modèle

→ Propose ajustements `CAPABILITY_SCORING.md` et `MODEL_ROUTING.md`

Schéma DB étendu :
```sql
ALTER TABLE subagents_skills ADD COLUMN model_used TEXT;
ALTER TABLE subagents_skills ADD COLUMN complexity TEXT CHECK(complexity IN ('Low','Medium','High'));
ALTER TABLE subagents_skills ADD COLUMN tokens_estimate INTEGER;
ALTER TABLE subagents_skills ADD COLUMN node_id TEXT;
ALTER TABLE subagents_skills ADD COLUMN attempt_n INTEGER DEFAULT 1;
ALTER TABLE subagents_skills ADD COLUMN mission_state TEXT;
```

---

## 13. Checklist livraison

- [ ] Mission Graph YAML validé
- [ ] Contrats d'agents complets
- [ ] Capability Scoring + modèle recommandé par nœud
- [ ] Scheduler avec dépendances
- [ ] Budget envelope + ledger
- [ ] Politique Retry documentée
- [ ] Premortem + Premortem-Économie
- [ ] RÈGLE N°4 respectée
- [ ] Boucle LSP / Low-Code / Anti-Lecture vérifiées
- [ ] DB loggée model_used/complexity/tokens/node_id/attempt_n
- [ ] State Machine → DONE
- [ ] INDEX.md / PROJECT_STATE.md / Alexandria
- [ ] `MAIN_RENDUE_A_MAHONHEIM=1`

---

## 14. Références

SOUL.md / ENGINE.md / AGENTS.md / FORCE_TOOLING.md / GEMINI.md / shadow-targeting-method.md / TEAM_ROLES.md / CAPABILITY_SCORING.md / MODEL_ROUTING.md

---

## CHANGELOG

**v4.0 – 2026-07-10 – Tesla Mission Orchestrator**
- Ajout : Mission Graph DAG canonique
- Ajout : Capability Scoring indépendant vendor (Reasoning/Code/Audit/Memory/Cost/Latency)
- Ajout : Scheduler série/parallèle/pipeline/fan-out/fan-in
- Ajout : Contrats d'agents Input/Output/Pré/Post/Risques/Temps/Coût
- Ajout : Politique Retry / Fallback / Escalade Mahonheim
- Ajout : Budget Manager avec envelope par chantier + ledger temps réel
- Ajout : State Machine CREATED→PLANNED→RUNNING→BLOCKED/WAITING→REVIEW→DONE→ARCHIVED
- Ajout : Learning Loop Alexandria post-mission
- Renommage fonctionnel : **Tesla Mission Orchestrator** – nom technique `tesla-team-synergy` conservé
- Conservé : Token-Economy v3, SGC, Règle N°4, Shadow-Targeting, Boucle LSP

**v3.0 – 2026-07-10**
- Token-Economy v2, contrats FORCE_TOOLING, SGC native, DB migration

**v2.0**
- Mission économique token initiale

**v1.0**
- Orchestration multi-agents initiale

---
`MAIN_RENDUE_A_MAHONHEIM=1`
