# tesla-team-synergy – Tesla Mission Orchestrator v4.0

Pack complet – Antigravity CLI

```
tesla-team-synergy-pack/
├── .agents/skills/tesla-team-synergy/   # à copier dans votre projet
│   ├── SKILL.md                        # skill canonique v4.0
│   ├── CAPABILITY_SCORING.md
│   ├── MODEL_ROUTING.md
│   ├── TEAM_ROLES.md
│   ├── PLAN_TEMPLATE.md
│   ├── README.md                       # FR
│   ├── README_EN.md
│   ├── AGENTS_PATCH.md
│   ├── migration_db_subagents_skills_v4.sql
│   ├── contracts/contract_template.yaml
│   └── examples/mission_graph.yaml
│
└── MVP-GITHUB/tesla-team-synergy/       # copie prête pour dépôt public
    └── (mêmes fichiers)
```

## Install

```bash
# 1. Skill
cp -r .agents/skills/tesla-team-synergy /votre-projet-tesla/.agents/skills/

# 2. DB Alexandria (1x)
sqlite3 ~/bifrost/tesla/Avalon/03-Resources/alexandria_brain.db < migration_db_subagents_skills_v4.sql

# 3. AGENTS.md
# Appliquer AGENTS_PATCH.md §4
```

## Quoi de neuf v4.0

- Mission Graph DAG
- Capability Scoring indépendant vendor
- Scheduler série/parallèle/pipeline/fan-out/fan-in
- Contrats d'agents
- Retry / Fallback / Escalade
- Budget Manager + ledger
- State Machine mission
- Learning Loop Alexandria

Conforme SOUL 3.0 / ENGINE 1.0 / AGENTS 4.0 / FORCE_TOOLING 1.0 / GEMINI.md 2.0

`MAIN_RENDUE_A_MAHONHEIM=1`
