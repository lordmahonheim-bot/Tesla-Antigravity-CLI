---
type: chantier_sgc
chantier_id: "021"
title: "Obsidian Graph Relationnel"
status: "⚪ Clos"
date_creation: "2026-07-20"
date_cloture: "2026-07-20"
tags: [chantier, actif, obsidian, RAG, second-cerveau]
version: "1.0"
---

# Cahier des Charges — Chantier 021 : Obsidian Graph Relationnel

> [!NOTE]
> **Contexte** : Ce chantier fait suite à l'analyse de la vidéo "Obsidian Graph" et au plan d'intervention stratégique produit par la Team-Synergy. L'objectif est de remplacer le fichier monolithique `knowledge_graph.json` par un réseau neuronal dynamique de fichiers Markdown reliés par des wikilinks, avec une colorimétrie stratégique stricte.

---

## 1. Description du Projet
- **Périmètre** : Conversion de l'extraction des logs de sessions en un format `_MOC/Graph_Nodes/*.md` interconnecté.
- **Bénéficiaire** : Lord Mahonheim / Écosystème Tesla
- **Priorité** : Haute (Élévation de l'architecture cognitive TASLB).

## 2. Objectifs Cibles (DoD - Definition of Done)
- [ ] Le script `session_to_graph.py` (ou équivalent) est capable de parser un transcript et de créer/mettre à jour des notes individuelles.
- [ ] Les connexions s'effectuent via des wikilinks automatiques (`[[Entité]]`).
- [ ] L'architecture `Daily_Log_YYYY-MM-DD.md` est en place pour le concept "Build in Public".
- [ ] La colorimétrie "Vigilum Codex" est prête à être configurée via les tags.

## 3. Ressources & Dépendances
- **Entrées** : `OUTPUTS/plan_intervention_obsidian_graph.md`, `SESSION_TRANSCRIPTS.md`.
- **Agents Assignés** : `tesla-master-code` (Dev), `tesla-premortem` (Audit RAG), `tesla-web-raider`, `tesla-curator-prime`, `tesla-arcanis-360`.

## 4. Livrables Attendus
- Script ETL Python pour la sémantique de graphe.
- Nouveaux dossiers `_MOC/Graph_Nodes/` et `_MOC/Daily_Logs/` provisionnés.
- Rapport de tests sur la profondeur du RAG (Eviter le Semantic Bloat).

## 5. Budget Token (Gouvernance)
- **Modèle Primaire** : Gemini 2.5 Flash (Vélocité, parsing sémantique des transcripts).
- **Modèle Secondaire** : Claude 3.5 Sonnet (Génération et refactoring du script).
- **Audit Critique** : Claude 3.5 Opus (Uniquement si nécessaire pour verrouillage final).

## 6. Historique des Actions
- **2026-07-20** : Ouverture du chantier, création du cahier des charges d'après le plan Team-Synergy.

## 7. Gestion des Risques (Premortem)
- **Risque** : Explosion du contexte RAG (Semantic Bloat) due à la transitivité infinie des wikilinks.
- **Mitigation** : Le routeur de recherche doit limiter l'exploration à une profondeur stricte (Depth = 2).

## 8. Synchronisation GitHub (Règle 12)
- [ ] Scripts poussés sur `bifrost/tesla`.
- [ ] Documentation MVP poussée sur `MVP-GITHUB/` une fois complétée.

## 9. Next Steps
1. Développer le pipeline ETL de création des nœuds (`tesla-master-code`).
2. Paramétrer les tags pour la colorimétrie dans Obsidian.

## 10. Validations (Checkpoints)
- [x] Phase 1 : Cadrage et Architecture validés (Plan Team-Synergy).
- [x] Phase 2 : Développement du script ETL avec Master-Code.
- [x] Phase 3 : Recette, Self-Healing, et audit RAG (certification Curator-Prime).

## 11. Signature & Horodatage de Clôture
- Date : 2026-07-20
- Approbation : Certifié conforme sous la doctrine Vigilum Codex (Sceau Curator-Prime v1.0).
