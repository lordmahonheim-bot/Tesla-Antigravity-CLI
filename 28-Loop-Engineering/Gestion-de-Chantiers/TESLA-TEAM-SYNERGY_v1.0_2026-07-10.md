---
type: chantier
tags: [chantier/ouvert, cognitif/shadow-targeting, architecture/skill, statut/ouvert]
date_ouverture: 2026-07-10
date_derniere_maj: 2026-07-10
version: 1.1
statut: "Ouvert"
parent: null
enfants: []
remplace: null
---

# 🎯 CHANTIER : TESLA-TEAM-SYNERGY (Shadow-Targeting)
**Ouvert le :** 2026-07-10  
**Dernière mise à jour :** 2026-07-10  
**Statut :** 🟢 Ouvert — Phase de cadrage validée  
**Responsable :** Tesla (sur Antigravity CLI)  
**Autorité de validation :** Lord Mahonheim

---

## 1. Idée Initiale (Genèse du Chantier)

> *« J'ouvre un nouveau chantier: créer l'Agent d'élite (Skill : Shadow-Targeting ): Tesla-Team-Synergy »*
> — Lord Mahonheim

Volonté de créer un nouvel agent d'élite/skill axé sur le "Shadow-Targeting" et la synergie d'équipe ("Team-Synergy"). C'est un orchestrateur silencieux, coordinateur d'élite et non-invasif.

---

## 2. Description du Chantier

### Périmètre
- **Shadow** : `injection_type: shadow-targeted`, `target_subagent: self`. Aucun subagent payant additionnel. Le skill s'injecte silencieusement dans les 3 subagents natifs Antigravity CLI Pro. Pas de modification binaire, pas de contournement CGU – injection contextuelle de prompts + `SKILL.md` légitime.
- **Team-Synergy** : L'Orchestrator ne travaille jamais seul. Il construit un **Mission Graph DAG** canonique pour coordonner plusieurs agents d'élite simultanément (Planner / Challenger / Builder / Tester / Documenter / Auditor).
- **Sans interférer avec l'opérateur** : RÈGLE ABSOLUE N°4 respectée. Le skill **ne délègue pas, n'exécute pas**. Il produit uniquement des artefacts écrits (Mission Graph, contrats, Scheduler, Budget). Seul AGENTS invoque les sous-agents.
- Traçabilité complète dans `subagents_skills` et rollback en 4 étapes en cas de dérive.

### Hors périmètre
- Exécution directe.
- Création de subagents payants.
- Modification du core Antigravity.
- Inférence IA locale ou ajout d'outils binaires.

---

## 3. Objectif Cible (Définition du Succès)

**Scénario type :**
`J'invoque l'Agent d'élite Tesla-Team-Synergy pour [objectif]`

Le Skill produit en <1 passe :
1. `mission_graph.yaml` – DAG avec nœuds, dépendances, contrats
2. `Gestion-de-Chantiers/[NOM]_v1.0_AAAA-MM-JJ.md` – PLAN SGC en 11 sections
3. `capability_routing.md` – Capability Scoring (Reasoning/Code/Audit/Memory/Cost/Latency) + modèle recommandé par nœud
4. `scheduler_plan.md` – Série / parallèle / pipeline / fan-out / fan-in
5. `budget_ledger.md` – Enveloppe tokens Gemini/Claude/GPT-OSS + circuit-breaker 5h
6. `agent_contracts/*.yaml` – Input/Output/Pré/Post/Risques/Temps/Coût par nœud
7. Politique de Retry/Fallback/Escalade

**Livrables concrets à l'invocation :** PLAN SGC validé + Mission Graph + Budget – rien d'autre. L'exécution est ensuite déléguée par AGENTS nœud par nœud, selon le Scheduler.

Cas d'usage canoniques : refactor multi-modules, audit sécurité Premortem, migration stack, chantier doc + code + Git, pipeline OSINT.

---

## 4. Hiérarchie
- **Parent :** Aucun
- **Remplace :** Aucun
- **Enfants :** À définir

---

## 5. Méthodologie & Approche

- Conforme strict au **GEMINI.md** : Low-Code First, Anti-Lecture Linéaire (`rg`/`jq`/Tree-sitter), Boucle LSP obligatoire.
- Séparation stricte Planification vs Exécution (AGENTS gère l'exécution).
- Validation par contrats stricts entre les nœuds (`agent_contracts`).

---

## 6. Architecture Technique Cible

**Zéro nouvel outil binaire. Stack 100% existante (Vigilum Codex) :**
- `tesla-arcanis-360` – Planner / Architect / OSINT
- `tesla-master-code` – Builder / Tester – Boucle LSP Self-Healing + Loop Engineering
- `premortem` – Challenger / AMDEC
- `tesla-curator-prime` – Documentation / Alexandria
- `tesla-github-manager` – Auditor / Conventional Commits
- `tesla-video-director` – si chantier AV
- Alexandria / `alexandria_brain.db` – RAG FTS5 + ChromaDB
- `log_subagent_parser.py` – traçabilité
- MCP : Filesystem, GitHub, Obsidian, Browser/Playwright

**Seule dépendance technique :** 1 migration SQL idempotente sur `alexandria_brain.db` avec les champs : `model_used`, `complexity`, `tokens_estimate`, `node_id`, `attempt_n`, `mission_state`.

---

## 7. Phases & Calendrier

| Phase | Description | Livrable | Statut |
|---|---|---|---|
| **Phase 1** | Cadrage et spécifications | Document de spécifications (ce fichier) | ✅ Validée |
| **Phase 2** | Réception du dossier-projet | Fichiers sources | 🟢 En cours |
| **Phase 3** | Développement & Migration | Fichier `SKILL.md` + Migration SQL | ⚪ En attente |
| **Phase 4** | Recette et Validation | Rapport de validation | ⚪ En attente |

---

## 8. TODO List

- [x] Créer le cahier des charges initial
- [x] Mettre à jour `INDEX.md`
- [x] Mettre à jour `PROJECT_STATE.md`
- [x] Poser les questions de cadrage et intégrer les réponses
- [ ] Réceptionner le dossier-projet (déploiement de Tesla-Team-Synergy)
- [ ] Exécuter la migration SQL idempotente sur `alexandria_brain.db`
- [ ] Rédiger/Déployer le `SKILL.md` de `tesla-team-synergy`

---

## 9. Ressources & Fichiers Liés

| Ressource | Lien | Type |
|---|---|---|
| Cadrage validé | Intégré au cahier des charges | Spécifications |

---

## 10. Journal de Bord

| Date | Événement | Décision |
|---|---|---|
| 2026-07-10 | Mahonheim ouvre le chantier | Cahier des charges créé. Questions de cadrage posées. |
| 2026-07-10 | Validation du cadrage | Périmètre verrouillé (Shadow-Targeting / Mission Graph DAG). 7 livrables définis. Migration SQL requise. |

---

## 11. Risques & Blocages

| Risque | Niveau | Mitigation (Contre-mesure) |
|---|---|---|
| Non-respect Règle N°4 (Exécution au lieu de planifier) | 🔴 Élevé | Définition stricte des limites dans le `SKILL.md`. Rollback en 4 étapes. |
| Altération base `alexandria_brain.db` | 🟡 Moyen | Script de migration strictement idempotent et audité avant exécution. |

---

## 12. Critères de Clôture (Definition of Done)

- [ ] L'agent/skill `tesla-team-synergy` est défini et déployé.
- [ ] La migration SQL est appliquée à `alexandria_brain.db` de manière idempotente.
- [ ] Le Skill produit avec succès les 7 livrables contractuels en <1 passe sans exécuter d'actions tierces.
- [ ] La documentation respecte les standards Master.

---

## 13. Signature & Horodatage de Clôture
*(Section à compléter lors de l'archivage)*

- **Date de clôture :** —
- **Résultat final :** —
- **Signé :** Tesla sur Antigravity CLI
- **Main rendue à :** Lord Mahonheim

---
*Chantier géré par Tesla sous la doctrine du Vigilum Codex.*
