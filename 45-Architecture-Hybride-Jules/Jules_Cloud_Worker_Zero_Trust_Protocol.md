---
tags: [architecture, agent, zero-trust, midgard]
date: 2026-08-11
---

# Jules Cloud Worker - Zero-Trust Protocol

Le sous-agent **Jules** est un *Cloud Execution Worker* asynchrone dédié à la génération lourde (UI/HTML/CSS).

## Doctrine de Souveraineté
Jules n'a **aucune autorité** sur la station MIDGARD. Il n'a aucun accès aux fichiers locaux en dehors du strict périmètre de sa mission asynchrone.

## Protocole Matériel d'Invocation
Toute communication avec Jules doit s'effectuer via le wrapper natif de Tesla : `tools/tesla-jules`.

### Flux d'Exécution :
1. **Verrou de Sécurité** : `git status` (doit être clean, blocage sinon).
2. **Déploiement** : `./tools/tesla-jules mission "[PROMPT]"`
   - Le script injecte les balises de traçabilité (`JULES_RESPONSE_TO_TESLA`, `MAIN_RENDUE_A_MAHONHEIM`).
3. **Surveillance** : `./tools/tesla-jules sessions`
4. **Rapatriement Isolé** : `./tools/tesla-jules pull <session_id>`
   - Le script isole le travail de Jules dans une branche sécurisée (`staging/jules_<session_id>`).
   - Le rapport de Jules est extrait et affiché.
5. **Auditeur Indépendant (Code-Auditor)** : Passage des diagnostics LSP avant toute fusion sur `master`.

> *Ce protocole est assimilé dans l'architecture canonique Tesla Antigravity CLI.*

## Règle Anti-Hallucination Cognitive
Pour prévenir l'effondrement de contexte (Context Collapse) et les blocages liés aux contrôles de périmètre du LLM distant, **il est formellement interdit de fournir des chemins système absolus (ex: `/home/lord-mahonheim/...`) dans les requêtes adressées à Jules.**
L'Agent Orchestrateur doit obligatoirement désigner les fichiers cibles par leur chemin **relatif** au dépôt (ex: `Gestionnaire-de-Projets/Cluedo/...`). Le wrapper `tesla-jules` gérera la réconciliation des chemins au rapatriement.
