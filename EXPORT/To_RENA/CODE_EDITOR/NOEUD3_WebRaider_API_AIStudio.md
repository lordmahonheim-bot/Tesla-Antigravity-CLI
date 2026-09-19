# Rapport d'Exploration : SDK google-genai en Ligne de Commande

## 1. Interactions Terminal (CLI)
Le SDK Python `google-genai` est principalement une bibliothèque de développement et ne fournit pas d'interface en ligne de commande (CLI) native intégrée pour un usage direct dans le terminal.
Pour interagir via le terminal, il existe deux approches principales :
- **Utiliser l'outil officiel Gemini CLI** : Google propose `@google/gemini-cli` via npm, conçu pour les workflows dans le terminal. (Installation : `npm install -g @google/gemini-cli`).
- **Créer un wrapper CLI personnalisé** : On peut facilement créer un script Python qui prend des arguments via `sys.argv` et appelle le client `google-genai`.

## 2. Limites de requêtes (Rate Limits)
Les limites de l'API dépendent du niveau d'utilisation du projet (Free, Tier 1, 2, 3), du modèle spécifique (les modèles expérimentaux étant plus limités) et du statut de facturation.
- **Les 3 dimensions de limites** :
  - **RPM** (Requests Per Minute) : Requêtes par minute.
  - **TPM** (Tokens Per Minute) : Volume total de tokens par minute.
  - **RPD** (Requests Per Day) : Requêtes par jour.
- En cas de dépassement, l'API renvoie une erreur HTTP `429 RESOURCE_EXHAUSTED`. Il est recommandé d'implémenter un mécanisme d'**exponential backoff with jitter** dans le script CLI. L'API Batch de Gemini est suggérée pour le traitement asynchrone sans impact sur les limites temps réel.

## 3. Authentification et Variables d'Environnement
Le SDK détecte automatiquement certaines variables d'environnement pour l'authentification lors de l'initialisation du client (`genai.Client()`) :
- **Clé API (Google AI Studio)** :
  - `GEMINI_API_KEY` (Recommandé)
  - `GOOGLE_API_KEY` (Prend la priorité si les deux sont définies).
- **Vertex AI (Enterprise)** : Utilisation des Application Default Credentials (ADC) avec les variables :
  - `GOOGLE_CLOUD_PROJECT`
  - `GOOGLE_CLOUD_LOCATION`
  - `GOOGLE_GENAI_USE_ENTERPRISE=true`
  
*Pour la configuration sous Linux : Ajouter `export GEMINI_API_KEY='votre_cle'` dans `~/.bashrc`.*

**Sources consultées :**
- Google GenAI SDK GitHub (https://github.com/google/google-genai-sdk)
- Gemini CLI Tool (https://github.com/google/gemini-cli)
- Google AI Dev Rate Limits (https://ai.google.dev/pricing)
- Authentication Guide (https://ai.google.dev/docs/authentication)
