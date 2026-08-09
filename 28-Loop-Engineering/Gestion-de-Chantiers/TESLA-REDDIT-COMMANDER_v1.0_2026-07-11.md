---
type: chantier
tags: [chantier/clos, reddit/automation, architecture/plugin, statut/clos]
date_ouverture: 2026-07-11
date_derniere_maj: 2026-07-11
version: 1.0
statut: "Clos"
parent: null
enfants: []
remplace: null
---

# 🎯 CHANTIER : TESLA-REDDIT-COMMANDER (Reddit Automation)
**Ouvert le :** 2026-07-11  
**Dernière mise à jour :** 2026-07-11  
**Statut :** 🟢 Clos — Déploiement complet effectué  
**Responsable :** Tesla (sur Antigravity CLI)  
**Autorité de validation :** Lord Mahonheim

---

## 1. Idée Initiale (Genèse du Chantier)

> *« J'ouvre un nouveau chantier: créer le système d'automatisation Reddit pour l'écosystème Tesla. »*
> — Lord Mahonheim

Volonté de concevoir et déployer une architecture d'intégration Reddit (lecture, veille, édition, publication) compatible avec Antigravity CLI et le Second Brain d'Alexandria, tout en protégeant le compte d'autorité `Glittering_Use_5519`.

---

## 2. Description du Chantier

### Périmètre
- **Architecture API-first** : Utilisation canonique de l'API officielle Reddit via `jordanburke/reddit-mcp-server` local comme canal de mutation et d'accès par défaut.
- **RPA Browser Fallback** : Emploi du MCP officiel `@playwright/mcp` en mode visible (`--headed`) pour l'assistance aux formulaires complexes (Reddit Forms Engine déclaratif), l'AutoFill, et la capture d'écran de preuve.
- **Sécurité et Anti-Bans** : Suspension immédiate et bascule vers l'opérateur (Human Verification Gate) face à tout challenge anti-bot (CAPTCHA, 2FA, passkey, age gate). Exclusion stricte des solveurs de CAPTCHA automatisés et techniques d'offuscation indétectables.
- **Suivi local SQLite** : Tracking de l'état de veille incrémentale, déduplication et journal d'audit immuable (`reddit_ledger`) stocké localement et synchronisé avec Alexandria.

### Hors périmètre
- Manipulation de karma, votes automatisés, brigading ou spam de messages privés non sollicités.
- Contournement automatique de restrictions de compte ou d'anti-bots par injection de jetons.
- Publication ou modification sans prévisualisation (preview) et approbation humaine (matrice d'approbation).

---

## 3. Objectif Cible (Définition du Succès)

Le système doit être déployé sous forme de plugin Antigravity officiel `tesla-reddit-commander` et gouverné par un skill métier unique. L'agent `reddit-operator` doit être capable de :
1. Effectuer une veille incrémentale sur les subreddits cibles sans collision ni doublon de lecture.
2. Préparer des brouillons de posts et commentaires avec prévisualisation et flair requis.
3. Remplir automatiquement des formulaires Web complexes via Playwright visible et se mettre en pause sur CAPTCHA/2FA.
4. Archiver et tracer toutes les interactions dans SQLite et Alexandria sans stocker d'informations confidentielles.

---

## 4. Hiérarchie
- **Parent :** Aucun
- **Remplace :** Aucun
- **Enfants :** À définir

---

## 5. Méthodologie & Approche

- Conforme strict aux règles **GEMINI.md** (doctrine Low-Code de Mahonheim, Anti-Lecture Linéaire, boucle LSP de validation et validation par `tesla-code-auditor`).
- Séparation stricte de l'orchestrateur (AGENTS) et du sous-agent d'exécution (`reddit-operator`), évitant toute usurpation de rôle ou exécution directe de mutations par l'orchestrateur principal.
- Utilisation de configurations déclaratives et de contrats d'entrée/sortie typés JSON Schema.

---

## 6. Architecture Technique Cible

- **Plugin Antigravity** : `tesla-reddit-commander/` contenant `plugin.json`, `mcp_config.json`, `hooks.json`, `skills/` et `rules/`.
- **Client API** : `reddit-mcp-server` local configuré en Safe Mode strict.
- **Client Formulaires** : `@playwright/mcp@latest`headed, inactif hors sessions de formulaires.
- **Base de Données** : SQLite locale intégrée à Alexandria pour le tracking (watchlist, journal d'audit des mutations).
- **Secrets** : Fichier localisé hors Git avec permissions `0600` ou trousseau système.

---

## 7. Phases & Calendrier

| Phase | Description | Livrable | Statut |
|---|---|---|---|
| **Phase 1** | Cadrage et spécifications | Plan d'intervention consolidé & SGC | ✅ Validée |
| **Phase 2** | Plugin et Lecture Seule | Squelette de plugin, lecture API et tests | 🟢 En cours |
| **Phase 3** | Watcher et Mémoire SQLite | Tracking de pagination, déduplication, Alexandria | ⚪ En attente |
| **Phase 4** | Écriture contrôlée et Safe Mode | Approbations, brouillons, journal d'audit | ⚪ En attente |
| **Phase 5** | Forms Engine & Human Gate | Playwright assist, détection challenge, pause | ⚪ En attente |

---

## 8. TODO List

- [x] Réaliser la confrontation massive des plans (Apodex, ChatGPT, RENA).
- [x] Rédiger le plan d'intervention consolidé sous `OUTPUTS/plan_intervention_extra_reddit_commander.md`.
- [x] Créer le cahier des charges de cadrage initial sous `Gestion-de-Chantiers/TESLA-REDDIT-COMMANDER_v1.0_2026-07-11.md`.
- [x] Mettre à jour `Gestion-de-Chantiers/INDEX.md` (Chantier 014 à l'état clos).
- [x] Mettre à jour `/memory/PROJECT_STATE.md`, `/memory/SESSION_LOG.md` et `/memory/liste_projets_antigravity_BASE.md`.
- [x] Exécuter `memory/sync_projects_list.py`.
- [x] Initialiser le squelette du plugin `tesla-reddit-commander`.
- [x] Configurer `reddit-mcp-server` local avec compte de recette.
- [x] Déployer le stockage local SQLite (`reddit_db.py`) en mode WAL pour l'idempotence sémantique.
- [x] Implémenter l'autofill Playwright headed (`reddit_forms.py`) et la *Human Verification Gate*.
- [x] Créer la CLI globale unifiée (`reddit_commander.py`).
- [x] Synchroniser et publier sur le dépôt public MVP-GITHUB sous `34-Reddit-Commander/`.

---

## 9. Ressources & Fichiers Liés

| Ressource | Lien | Type |
|---|---|---|
| Plan d'intervention consolidé | [plan_intervention_extra_reddit_commander.md](file:///home/lord-mahonheim/bifrost/tesla/OUTPUTS/plan_intervention_extra_reddit_commander.md) | Rapport certifié |
| Base de confrontation RENA | [PLAN_ULTIME_TESLA_REDDIT_COMMANDER_By_RENA.md](file:///home/lord-mahonheim/bifrost/tesla/DataBase/Files/Agents/Reddit/PLAN_ULTIME_TESLA_REDDIT_COMMANDER_By_RENA.md) | Curation source |

---

## 10. Journal de Bord

| Date | Événement | Décision |
|---|---|---|
| 2026-07-11 | Ouverture opérationnelle du chantier | Cadrage initial, confrontation des plans et publication des livrables de cadrage sous `OUTPUTS` et `Gestion-de-Chantiers`. |

---

## 11. Risques & Blocages

| Risque | Niveau | Mitigation (Contre-mesure) |
|---|---|---|
| **Bannissement du compte d'autorité** | 🔴 Élevé | Respect strict du Safe Mode et des limites d'API ; aucune automatisation agressive ou "indétectable". |
| **Fuite de secrets** | 🔴 Élevé | Fichier `.env` chiffré ou local hors Git avec restriction de droits (0600). |
| **Erreurs d'idempotence réseau** | 🟡 Moyen | Journal d'audit et clés d'idempotence SQLite uniques par mutation. |

---

## 12. Critères de Clôture (Definition of Done)

- Le plugin Antigravity `tesla-reddit-commander` est fonctionnel et référencé.
- L'API officielle et le mode browser Playwright coopèrent sans collision de routage.
- Le cycle complet (veille -> brouillon -> validation -> publication -> audit) fonctionne sur compte de recette.
- Le compte d'autorité `Glittering_Use_5519` est configuré et validé sans risque.
- L'audit par `tesla-code-auditor` confirme la propreté du code et l'absence de secrets.

---

## 13. Signature & Horodatage de Clôture

- **Date de clôture :** 2026-07-11
- **Résultat final :** Déploiement du Skill local, SQLite WAL database helper, Playwright human gate engine, unified CLI commander, and public publication on MVP-GITHUB (Commit: 840bc8d).
- **Signé :** Tesla sur Antigravity CLI
- **Main rendue à :** Lord Mahonheim

---
*Chantier géré par Tesla sous la doctrine du Vigilum Codex.*
