# SGC PLAN : Contrôle Absolu Deluge sur MIDGARD

## 1. Nom du Chantier et Objectifs
**Chantier :** Contrôle Absolu Deluge sur MIDGARD
**Objectif :** Maîtrise totale, sans friction, en ligne de commande et Web du client BitTorrent Deluge (installation de `deluge-console`, `deluged`, `deluge-web`, configuration `systemd` pour automatisation Zéro-Touch).

## 2. Contexte et Enjeux
- **Contexte :** Optimisation et automatisation des téléchargements BitTorrent sur l'environnement MIDGARD.
- **Enjeux :** Fiabilité du daemon (`deluged`), accessibilité CLI/Web, résilience (redémarrage auto via `systemd`), sécurité et isolation (user dédié).

## 3. Périmètre (Scope)
- **In-Scope :** Installation des paquets Deluge, configuration de `deluged` et `deluge-web`, création et activation des services `systemd`, configuration des accès utilisateurs (CLI/Web), définition des arborescences de téléchargement.
- **Out-of-Scope :** Configuration de reverse proxy complexe, configuration de VPN.

## 4. Mission Graph (DAG)
Orchestration complète de la Team-Synergy (cf. `mission_graph.yaml` pour le détail d'exécution) :
1. **Tesla-Arcanis-360** (Acquisition & Concept)
2. **Tesla-Web-Raider** (OSINT & Veille Technique sur Deluge 2.x)
3. **Tesla-Curator-Prime** (Harmonie & Architecture : Permissions, Systemd)
4. **Tesla-Master-Code** (Ingénierie & Code : Scripting Zéro-Touch)
5. **Tesla-Writing-Skills** (Documentation & Exploitation)
6. **Tesla-PREMORTEM** (Stress-Test & AMDEC)

## 5. Capability Scoring & Budget Ledger
- **Arcanis-360 :** 15% (Cadrage conceptuel et arborescence)
- **Web-Raider :** 10% (Recherche des bonnes pratiques sécurité et API Deluge)
- **Curator-Prime :** 20% (Conception de l'architecture systemd et gestion des droits)
- **Master-Code :** 25% (Implémentation du script bash Zéro-Touch)
- **Writing-Skills :** 10% (Création du manuel opératoire et des mémos CLI)
- **PREMORTEM :** 20% (Audit de résilience, analyse des failles et GO/NO-GO)
- **Budget temps d'exécution estimé :** 2.5 cycles d'agent.

## 6. Architecture & Spécifications
- **Composants :** `deluged` (Daemon backend), `deluge-web` (Interface Web UI), `deluge-console` (Interface CLI).
- **Services `systemd` :** 
  - `deluged.service` (Type: simple, User: deluge, Group: deluge)
  - `deluge-web.service` (Type: simple, User: deluge, Group: deluge)
- **Stockage :** Arborescence standardisée (En cours, Terminés, Watch, Torrents, Logs).

## 7. Phases de Déploiement
- **Phase 1 :** Cadrage & Renseignement (Arcanis & Web-Raider)
- **Phase 2 :** Architecture logicielle et Système (Curator-Prime)
- **Phase 3 :** Programmation de l'automatisation (Master-Code)
- **Phase 4 :** Documentation (Writing-Skills)
- **Phase 5 :** Évaluation PREMORTEM et Décision Finale (Premortem)

## 8. State Machine & Politique de Retry
- **État Initial :** INIT
- **Transitions :** INIT -> DESIGN -> SCRIPTING -> TESTING -> DOC -> PREMORTEM -> DONE
- **Politique de Retry :** 
  - Erreur d'accès/recherche (Web-Raider) : Retry 3 fois, backoff exponentiel.
  - Échec de validation du script shell (Master-Code) : Retour à Curator-Prime pour ajustement.
  - NO-GO Premortem : Re-routage automatique vers Master-Code ou Curator-Prime en fonction du type d'échec (OOM, fail systemd, etc.).

## 9. Critères de Succès
- Daemon `deluged` exécuté en tâche de fond sous un utilisateur dédié.
- Interface `deluge-web` accessible via le port défini.
- `deluge-console` pleinement fonctionnelle localement sans demande de mot de passe interactif (utilisation de `auth`).
- Les services survivent de façon autonome à un redémarrage système (enabled).

## 10. Livrables attendus (En fin de cycle complet)
- Script Bash d'installation Zéro-Touch (`deploy_deluge.sh`).
- Modèles de fichiers unitaires `systemd`.
- Structure du fichier `auth` et `core.conf`.
- Documentation d'exploitation (`DELUGE_RUNBOOK.md`).
- Rapport PREMORTEM et certification GO/NO-GO.

## 11. Validation & Sign-off (Blocage de Phase - Règle 13/19)
- **Statut Actuel :** 🛑 WAITING FOR OPERATOR VALIDATION
- L'orchestration des agents d'élite est actuellement bloquée.
- En attente explicite du GO de l'opérateur (Lord Mahonheim) pour invoquer le DAG et déclencher la production des livrables.
