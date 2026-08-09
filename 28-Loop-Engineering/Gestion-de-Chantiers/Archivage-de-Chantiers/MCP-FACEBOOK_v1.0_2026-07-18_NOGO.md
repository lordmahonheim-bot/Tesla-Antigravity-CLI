# Cahier des Charges : MCP Facebook (Chantier 018)

## 1. Contexte
Afin de centraliser et d'optimiser sa présence sur les réseaux sociaux souverains, Lord Mahonheim requiert l'intégration d'un serveur MCP (Model Context Protocol) dédié à Facebook. Cet outil liera directement le cerveau d'Antigravity CLI (MIDGARD) aux plateformes Meta.

## 2. Objectif Principal
Développer, sécuriser et déployer un "MCP Facebook" permettant une gestion intégrale (lecture, publication, modération) du profil "Lord Mahonheim" et, avec une priorité absolue, de la page "Vigilum Codex".

## 3. Périmètre
- **Lecture :** Récupération asynchrone des métriques, commentaires et messages de la page.
- **Écriture :** Publication de contenus (textes, images, liens) depuis MIDGARD.
- **Cibles :** Le compte personnel "Lord Mahonheim" (administration) et la Page "Vigilum Codex" (exploitation).

## 4. Dépendances & Outils
- **Architecture :** L'API officielle Facebook Graph. (Le web-scraping ou l'automatisation de navigateur étant trop fragiles et risqués pour le compte principal, l'API officielle est la seule solution garantissant la performance, l'opérationalité et la sécurité exigées).
- **Prérequis :** Création d'une application dans le portail "Meta for Developers", obtention des Page Access Tokens longue durée.
- **Langage MCP :** Python ou TypeScript (standard MCP).

## 5. Livrables Attendus
1. Le code source du serveur `mcp-facebook`.
2. Le guide de configuration (Vigilum Codex) pour l'intégration sécurisée des tokens API.
3. L'intégration dans le fichier `settings.json` d'Antigravity CLI.

## 6. Budget Cognitif (Tokens)
Élevé. L'API Facebook Graph est complexe et nécessite une gestion pointue des permissions (Scopes) et des renouvellements de tokens.

## 7. Critères d'Acceptation
- Un agent Tesla doit être capable, sur commande de l'opérateur, de lire les derniers commentaires de la page Vigilum Codex et d'y répondre via l'API, sans ouvrir de navigateur.
- Aucun dépassement de quota (Rate Limiting) ou blocage de compte.

## 8. Phases d'Exécution
1. **Renseignement & Configuration (Action Humaine Requise) :** Inscription sur Meta Developers, création de l'App, et génération du "Page Access Token" pour la page Vigilum Codex.
2. **Développement du MCP :** Codage du serveur avec les outils natifs MCP (lecture de flux, publication).
3. **Sandbox & Test :** Exécution en mode Dry-Run ou sur des posts privés.
4. **Déploiement Opérationnel :** Raccordement définitif à Antigravity CLI.

## 9. Analyse des Risques et Mitigation
- **Risque :** Bannissement du compte principal "Lord Mahonheim" pour comportement bot non autorisé.
- **Mitigation :** Utilisation exclusive de l'API Graph officielle en mode "App vérifiée". Implémentation du "Human Verification Gate" (validation de l'Orchestrateur requise avant tout `POST` destructif ou public).

## 10. Journal de Bord
- **2026-07-18 :** Réponses au cadrage par Lord Mahonheim. Décision stratégique d'utiliser l'API officielle pour assurer la sécurité de l'identité principale. Déclaration officielle de l'ouverture du Chantier 018.

## 11. Clôture
- Statut actuel : 🟢 Ouvert
- Date de clôture : N/A
