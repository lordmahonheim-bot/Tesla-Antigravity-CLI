# MODEL_ROUTING – Cheatsheet v4.0
# Tesla Mission Orchestrator

**Capability Selection FORCE_TOOLING : Pertinence > Sécurité > Fiabilité > Coût > Simplicité > Reproductibilité > Économie cognitive**

Utiliser **Capability Scoring** – voir `CAPABILITY_SCORING.md`

Résumé rapide :

| Besoin | Modèle | Score Code | Cost |
|---|---|---|---|
| Recherche / OSINT / parsing / doc | Gemini Flash | 55 | 100 |
| Planification / Archi | Gemini Pro | 75 | 65 |
| Code / Refactor / Tests | Claude Sonnet | 94 | 55 |
| Premortem critique / Sécurité | Claude Opus | 92 | 15 |
| Scaffolding massif | GPT-OSS* / Sonnet | 80 | 85 |

*si disponible

**Avant montée en gamme – OBLIGATOIRE :**
1. Low-Code First
2. Anti-Lecture Linéaire : `rg` / `jq` / Tree-sitter / search_router
3. Boucle LSP : `lsp_diagnostics`

Escalade : Flash → Pro/Sonnet → Opus – documenter raison.

Quotas : Gemini | Claude | GPT-OSS – hebdo + 5h glissant.
Circuit-breaker <15% → Opus→Sonnet, Pro→Flash.

Shadow-Targeting éco : Arcanis/Curator dans `self`, forcé Flash.

---
`MAIN_RENDUE_A_MAHONHEIM=1`
