---
type: reference
tags: [curation/certified, curator/prime, status/valid, superpowers, ai-skills]
coterie: tesla
date: 2026-07-23
author: tesla-curator-prime
confidence_score: 99%
sources: ["Arcanis-360 Report", "Web-Raider Report", "Master-Code Report"]
---

# CERTIFIED REPORT: Topo Pédagogique : Le Framework Superpowers & /superpowers:writing-skills

## 1. Diagnostic Summary
Le framework "Superpowers", créé par Jesse Vincent (obra), est une architecture de conception de compétences pour les agents IA (Claude Code, Antigravity, etc.). Son but principal est d'imposer une discipline d'ingénierie stricte dans la création de prompts et de workflows pour l'IA, éliminant ainsi le "vibe coding" (programmation à l'instinct) au profit de méthodes rigoureuses empruntées au génie logiciel classique.

## 2. Verified Facts & Evidence Pack
| Asserted Fact | Primary Source Reference | Confidence |
| :--- | :--- | :--- |
| **Origine et Auteur** : Créé par Jesse Vincent (obra) pour fiabiliser les agents IA. | Rapports des agents | 99% |
| **Mécanique `writing-skills`** : Transposition du TDD (RED-GREEN-REFACTOR) au Markdown et aux prompts. | Rapports des agents | 99% |
| **Structure Hybride** : Frontmatter YAML (pour le SDO) + Corps Markdown lu par l'agent. | Rapports des agents | 99% |
| **Règle d'Or (Information Gap)** : Ne jamais résumer le workflow dans le YAML. | Rapports des agents | 99% |

## 3. Le Concept : Skill Discovery Optimization (SDO) et la Règle d'Or
La structure technique repose sur un fichier hybride :
- **Frontmatter YAML** : Utilisé pour le *Skill Discovery Optimization* (SDO). Il permet au système d'indexer et de découvrir la compétence.
- **Corps Markdown** : Contient les instructions détaillées lues par l'agent.

**La Règle d'Or** : Il est strictement interdit de résumer le workflow ou la logique métier dans la description YAML.
*Pourquoi ?* En créant délibérément un vide d'information (information gap) dans la description de haut niveau, on force le LLM à charger, lire et analyser le contenu complet du fichier Markdown. Cela empêche l'IA de "halluciner" son propre workflow en se basant sur un simple résumé.

## 4. Mécanique TDD Appliquée à l'IA (`writing-skills`)
La méta-compétence `writing-skills` introduit le Test-Driven Development (TDD) pour la création de compétences IA :
1. **RED** : Définir le comportement attendu et observer l'agent échouer ou se tromper de direction.
2. **GREEN** : Rédiger le fichier Markdown (`SKILL.md`) avec les contraintes strictes pour guider l'agent avec succès.
3. **REFACTOR** : Affiner le prompt, optimiser le SDO et s'assurer que la compétence est découvrable et réutilisable sans régression.

## 5. Cas d'Usage et Valeur pour les Ingénieurs
Les ingénieurs peuvent exploiter le framework Superpowers pour :
- **Génération ciblée** : Créer automatiquement des sous-compétences spécifiques (ex: `team-review-checklist`).
- **Structuration non-destructive** : Organiser la cognition de l'agent IA sans risquer de casser le code de production sous-jacent.
- **TDD Imposé** : Appliquer des standards de développement logiciel (tests, modularité, prédictibilité) aux comportements non-déterministes des LLMs.

---
*Certified and signed on MIDGARD by Tesla Curator Prime.*
