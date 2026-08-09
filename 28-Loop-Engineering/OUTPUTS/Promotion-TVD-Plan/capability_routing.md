# Capability Scoring & Routing

| Nœud | Modèle Recommandé | Raison (Scoring) |
|---|---|---|
| **N1** | Gemini Flash | I/O volumétrique (7 fichiers sources lourds à ingérer). Cost: 100, Memory: 70. |
| **N1b** | Gemini Flash | Extraction web et navigation rapide. Latency: 100. |
| **N2** | Claude Sonnet | Analyse comparative et raisonnement poussé pour la sélection d'outils (Reasoning: 82, Cost: 55). |
| **N3** | Claude Sonnet | Conception d'architecture et de logique algorithmique logicielle (Code: 94). |
| **N4** | Claude Opus | Évaluation des risques critiques et AMDEC (Audit: 96). |

## Politique Retry / Fallback
- **Retry (x2)** : Si l'agent échoue (timeout ou mauvaise qualité), relance sur le même modèle avec instruction d'auto-correction.
- **Fallback** : 
  - Si N1/N1b échouent → Escalade vers Gemini Pro ou Claude Sonnet.
  - Si N2/N3 échouent → Escalade vers Claude Opus.
- **Escalade Finale** : Suspension de la State Machine (BLOCKED) et restitution du rapport d'erreur à Lord Mahonheim.
