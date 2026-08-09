# Budget Ledger - Test-Refactor-Auth

**Envelope globale :**
- Claude : 40%
- Gemini : 60%
- GPT-OSS : 0%

**Estimations par Nœud :**
| Nœud | Modèle | Tokens est. | Tokens réel | Quota groupe restant estimé | Circuit Breaker |
|---|---|---|---|---|---|
| N1 | gemini-pro | S (15k) | - | 95% | OK |
| N2 | claude-sonnet | L (50k) | - | 80% | OK |
| N3 | claude-opus | M (20k) | - | 75% | OK |

**Politique de dégradation :** Si Quota Claude < 15% restant, N3 bascule d'Opus vers Sonnet.
