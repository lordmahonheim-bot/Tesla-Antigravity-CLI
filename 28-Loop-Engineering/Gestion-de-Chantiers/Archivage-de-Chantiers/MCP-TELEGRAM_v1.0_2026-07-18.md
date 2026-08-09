# Cahier des Charges : MCP Telegram (Chantier 019)

## 1. Contexte
Lord Mahonheim souhaite désenclaver l'écosystème MIDGARD de son terminal physique. L'objectif est de créer un "Mobile Command Center" via Telegram, plateforme réputée pour la flexibilité et l'ouverture de son API, pour piloter l'architecture Antigravity CLI à distance.

## 2. Objectif Principal
Développer, sécuriser et déployer un serveur MCP Telegram bidirectionnel en Python. Ce serveur permettra à l'opérateur d'envoyer des commandes depuis son smartphone et de recevoir des alertes ou des rapports asynchrones générés par les agents locaux.

## 3. Périmètre
- **Bidirectionnel :** Capacité d'envoi de commandes (ex: lancer une recherche, exécuter un script) et de réception de notifications (ex: fin de tâche, rapports de veille).
- **Format :** Textes, Markdown, et potentiellement fichiers (rapports).

## 4. Dépendances & Outils
- **API :** Telegram Bot API (officielle, via BotFather).
- **Langage & Framework :** Python (sélectionné par l'Orchestrateur pour sa robustesse en OSINT et gestion de données). Librairie recommandée : `python-telegram-bot`.
- **Intégration MCP :** SDK Python officiel pour Model Context Protocol.

## 5. Livrables Attendus
1. Code source du serveur MCP Telegram (`mcp-telegram.py`).
2. Script de lancement et configuration `.env` (Token + Chat ID).
3. Service `systemd` pour garantir que le bot écoute en permanence en tâche de fond (Zero-Touch Background Ops).
4. Enregistrement dans `settings.json` d'Antigravity CLI.

## 6. Budget Cognitif (Tokens)
Modéré. L'API Telegram est simple, l'effort principal réside dans la structure MCP (prompts et tools exposés) et le filtrage de sécurité.

## 7. Critères d'Acceptation & Clôture
- Le bot doit ignorer catégoriquement (silence total) tout message provenant d'un ID Telegram autre que celui de Lord Mahonheim.
- Le bot doit pouvoir transmettre un message (alerte) de l'agent vers le téléphone.
- Le bot doit pouvoir recevoir une consigne du téléphone et la transmettre à MIDGARD pour exécution.

## 8. Phases d'Exécution
1. **Création BotFather (Action Humaine) :** Obtention du Token Bot et récupération de l'ID personnel de l'opérateur.
2. **Développement Python :** Codage de l'interface MCP (lecture/écriture Telegram) avec le verrou de sécurité (ID Lock).
3. **Déploiement `systemd` :** Mise en place du démon pour une écoute H24.
4. **Test de boucle :** Envoi d'une commande test depuis mobile -> exécution MIDGARD -> réponse mobile.

## 9. Analyse des Risques et Mitigation
- **Risque d'Intrusion :** Un tiers trouve le bot et tente de l'utiliser pour exécuter du code sur MIDGARD.
  - **Mitigation :** Hardcoding ou variable d'environnement stricte de l'ID Telegram de l'opérateur (`ALLOWED_USER_ID`). Tout autre ID est bloqué au niveau du socket, sans même être traité par l'IA.

## 10. Journal de Bord
- **2026-07-18 :** Ouverture du Chantier 019. Validation du périmètre bidirectionnel et du verrouillage par ID. Choix de Python acté par l'Orchestrateur.

## 11. Clôture
- Statut actuel : 🟢 Ouvert
- Date de clôture : N/A
