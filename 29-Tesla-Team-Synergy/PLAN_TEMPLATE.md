# [NOM-DU-CHANTIER]_v1.0_AAAA-MM-JJ.md
<!-- SGC – AGENTS.md §11 – Tesla Mission Orchestrator v4.0 -->

## 1. Objectif

## 2. Périmètre
In / Out

## 3. Contraintes

## 4. Dépendances

## 5. Mission Graph
Voir `mission_graph.yaml`
Résumé : N1 Research → N2 Architecture → N2b Premortem → N3 Code → N4 Test → N5 Doc

## 6. Risques identifiés (Premortem)

## 7. Tableau de routage – Capability Scoring

| Nœud | Rôle | Sous-agent | Modèle | Reasoning | Code | Audit | Cost | Complexité | Budget |
|---|---|---|---|---|---|---|---|---|---|
| N1 | Research | arcanis/curator | gemini-flash | 40 | 55 | 45 | 100 | Low | S |
| N2 | Archi | arcanis-360 | gemini-pro | 78 | 75 | 70 | 65 | Medium | M |
| N2b | Challenger | premortem | claude-opus | 95 | 92 | 96 | 15 | High | L |
| N3 | Code | master-code | claude-sonnet | 82 | 94 | 85 | 55 | Medium | M |
| N4 | Test | master-code | claude-sonnet | 82 | 94 | 85 | 55 | Medium | M |
| N5 | Doc | curator-prime | gemini-flash | 40 | 55 | 45 | 100 | Low | S |

**Budget envelope :** Gemini 60% / Claude 35% / GPT-OSS 5%

## 8. Scheduler
- Série : N1 → N2 → N2b → N3 → N4 → N5
- Parallèle : –
- Critical path : N1-N5

## 9. Retry / Fallback
- max_retries: 2
- fallback_model: +1 gamme
- escalade: Mahonheim

## 10. Premortem-Économie
- [ ] Opus remplaçable par Sonnet ?
- [ ] Recherche en Flash ?
- [ ] Volumétrie en Flash ?
- [ ] Quota suffisant ? Plan dégradation ?
- [ ] Shadow-targeting possible ?

## 11. Traçabilité
- Session ID :
- Mission State : PLANNED → … → DONE
- DB : model_used / complexity / tokens / node_id / attempt_n
- INDEX.md : oui/non
- PROJECT_STATE.md : oui/non
- Alexandria : oui/non

---
`MAIN_RENDUE_A_MAHONHEIM=1`
