# Capability Scoring – Tesla Mission Orchestrator v4.0

Le routage ne choisit plus un nom de modèle. Il choisit la meilleure capacité.

## Axes (0–100)

- **Reasoning** : planification, arbitrage, synthèse complexe
- **Code** : génération / refactor / tests, qualité LSP
- **Audit** : premortem, sécurité, détection contradictions
- **Memory / RAG** : contexte long, recherche documentaire
- **Cost_efficiency** : 100 = le moins cher en tokens/quota
- **Latency** : 100 = le plus rapide

## Matrix v4.0

| Modèle | Reasoning | Code | Audit | Memory | Cost | Latency | $/1M tok out (indicatif) |
|---|---|---|---|---|---|---|---|
| Gemini Flash | 40 | 55 | 45 | 70 | 100 | 100 | ~ |
| Gemini Pro | 78 | 75 | 70 | 80 | 65 | 70 | ~ |
| Claude Sonnet | 82 | 94 | 85 | 75 | 55 | 60 | ~ |
| Claude Opus | 95 | 92 | 96 | 80 | 15 | 35 | ~ |
| GPT-OSS* | 70 | 80 | 60 | 60 | 85 | 55 | ~ |

* GPT-OSS : si disponible dans l'environnement Antigravity, sinon fallback Sonnet.

## Sélection

Pour un nœud N avec exigences `req = {Reasoning, Code, Audit}` :

```
score(model) = w_r*Reasoning + w_c*Code + w_a*Audit + w_m*Memory
               - λ * cost_penalty
```

Poids par rôle :

| Rôle | w_r | w_c | w_a | w_m | λ |
|---|---|---|---|---|---|
| Research | 0.2 | 0.1 | 0.2 | 0.5 | 1.5 |
| Architecture | 0.5 | 0.2 | 0.2 | 0.1 | 0.8 |
| Code | 0.2 | 0.6 | 0.1 | 0.1 | 0.8 |
| Premortem | 0.4 | 0.1 | 0.5 | 0.0 | 0.4 |
| Documentation | 0.3 | 0.0 | 0.1 | 0.6 | 1.5 |

Choisir le modèle avec score maximal qui satisfait `capability_min` du contrat d'agent.

Si quota groupe < 15% : appliquer malus cost x2 → dégradation automatique Opus→Sonnet, Pro→Flash.

## Mapping rapide (compatibilité v3)

- Recherche / OSINT / parsing → Flash  (Cost 100, Memory 70)
- Planification / Archi → Pro  (Reasoning 78)
- Code / Tests → Sonnet  (Code 94)
- Premortem critique → Opus  (Audit 96)
- Doc / README → Flash

Règles GEMINI.md toujours prioritaires : Low-Code First, Anti-Lecture Linéaire, Boucle LSP.

---
`MAIN_RENDUE_A_MAHONHEIM=1`
