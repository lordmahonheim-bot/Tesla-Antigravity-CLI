# TEAM_ROLES – Tesla Team Synergy v3.0

| Rôle | Sous-agent | Mission principale | Modèle par défaut | Déclencheur |
|---|---|---|---|---|
| Orchestrator | Tesla principal (AGENTS) | Gouvernance, arbitrage, séquence | – | Toujours |
| Planner | tesla-arcanis-360 | Analyse, décomposition, PLAN.md SGC | Gemini Pro | Chantier ouvert |
| Challenger | premortem | Stress-test, AMDEC, angles morts | Claude Opus | Après PLAN |
| Architect | tesla-arcanis-360 | Conception technique, choix d'archi | Gemini Pro | Si design requis |
| Builder | tesla-master-code | Implémentation, refactor, LSP Self-Healing | Claude Sonnet | Phase build |
| Tester | tesla-master-code | Tests unitaires/intégration | Claude Sonnet | Post-build |
| Documenter | tesla-curator-prime | Synthèses, README, Alexandria | Gemini Flash | Livraison |
| Auditor | tesla-github-manager | Git, Conventional Commits, CODEOWNERS | Gemini Flash | Pre-commit |
| OSINT / Web | tesla-arcanis-360 | Web Raiding, OSINT, Agent-Reach | Gemini Flash | Recherche |
| Vidéo | tesla-video-director | Pipelines vidéo | Gemini Flash / Pro | Chantier AV |

**Notes :**
- Orchestrator = toujours Tesla principal. Jamais délégué.
- Builder = Tester = même skill `tesla-master-code`, postures différentes.
- OSINT utilise le wrapper `agent_reach_wrapper.py` – anti-SSRF obligatoire.
- Toute injection Shadow-Targeting → log `subagents_skills` avec `model_used`, `complexity`.

Voir SKILL.md §5 pour le routage modèle détaillé.
