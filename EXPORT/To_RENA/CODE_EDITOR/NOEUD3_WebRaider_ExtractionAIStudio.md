# Rapport d'Extraction Web : Google AI Studio & Antigravity CLI (NŒUD 3)

## 1. Limites Techniques et Quotas (Google AI Studio / Gemini API)
Google AI Studio ne possède pas de limites statiques universelles. Les limites dépendent du modèle utilisé, du tier d'utilisation et du statut de facturation.
*   **Dimensions des limites** :
    *   **RPM (Requests Per Minute)** : Nombre d'appels API en 60 secondes.
    *   **TPM (Tokens Per Minute)** : Nombre total de tokens traités par minute.
    *   **RPD (Requests Per Day)** : Nombre total de requêtes sur 24 heures.
*   **Limites basées sur les dépenses** : Évaluées sur une fenêtre roulante de 10 minutes pour les utilisateurs payants afin d'éviter les pics de dépenses inattendus.
*   **Vérification** : Les limites actives en temps réel doivent être consultées directement dans le tableau de bord de [Google AI Studio](https://aistudio.google.com/). Les erreurs `429 RESOURCE_EXHAUSTED` indiquent un dépassement de ces limites.

## 2. Tarification (Pricing)
*   **Interface Web AI Studio** : L'utilisation de l'interface web pour le prototypage et les tests est **gratuite**.
*   **Gemini API (Free Tier)** : Idéal pour le prototypage et l'utilisation à faible volume. C'est gratuit, mais soumis à des limites de taux, et les données peuvent être utilisées pour améliorer les modèles Google.
*   **Tier Payant / Production** : Facturation à la demande (pay-per-request), généralement par million de tokens (entrée et sortie). Les données de ce tier ne sont pas utilisées pour l'entraînement des modèles, assurant la confidentialité.
*   **Abonnements** : Possibilité de souscrire à des plans (ex. AI Pro ou AI Ultra) pour des limites de prototypage plus élevées dans AI Studio.

## 3. Architecture API
L'architecture de Google AI Studio agit comme une passerelle entre l'expérimentation et le déploiement en production via l'API Gemini.
*   **Architecture Neurale Unifiée** : L'API Gemini traite nativement texte, images, audio, vidéo et code sans nécessiter de modèles séparés, facilitant le raisonnement multimodal complexe.
*   **Interactions API** : Utilise un schéma typé où chaque action (`user_input`, `thought`, `function_call`, `model_output`) est une étape structurée.
*   **Modes d'Interaction** :
    *   *Standard Request/Response* pour les tâches courantes.
    *   *Live API* : Streaming bidirectionnel à faible latence (WebRTC/LiveKit) pour la voix et la vision en temps réel.
    *   *Agentic Workflows* : Support natif pour les appels de fonctions et l'orchestration de sous-agents.
*   **Déploiement (Starter Tier)** : Provisionnement automatique de ressources gérées (Cloud Run, Firestore, Firebase Auth) pour passer d'un prompt à une application web fonctionnelle.

## 4. Intégration avec Antigravity CLI
**Google Antigravity CLI** est une interface terminale légère permettant d'interagir avec des agents de l'écosystème Antigravity.
*   **Relation avec AI Studio** : Bien que Google AI Studio soit la plateforme web de prototypage, les utilisateurs peuvent exporter leur travail de AI Studio vers l'écosystème Antigravity (y compris la CLI) pour poursuivre le développement avec le contexte complet de l'agent.
*   **Caractéristiques CLI** :
    *   *TUI (Terminal User Interface)* optimisée pour la rapidité et les raccourcis clavier, idéale pour les environnements frugaux comme MIDGARD.
    *   *Sous-agents* : Capacité à lancer des agents concurrents pour des tâches parallèles.
    *   *Intégration et Sécurité* : Supporte les plugins, serveurs MCP (Model Context Protocol), et inclut une sandbox pour isoler les exécutions de commandes.
*   **Sources d'installation** : Documenté sur [antigravity.google](https://antigravity.google) (ex: `install.sh`).

---
*Exploration menée par Tesla-Web-Raider dans le respect du Vigilum Codex.*
