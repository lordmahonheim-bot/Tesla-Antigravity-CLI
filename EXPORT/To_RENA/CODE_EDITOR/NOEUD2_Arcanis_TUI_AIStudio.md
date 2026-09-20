> **ARCHIVE — remplacée pour le parcours sans Chrome (audit du 2026-09-19).**
> Les commandes, modèles, chiffres et certifications ci-dessous ne sont pas
> une procédure validée. Ne pas appliquer les changements système ni les
> exemples d’auto-exécution. Utiliser le [guide corrigé TERMINATOR](LIVRABLE_FINAL_AIStudio_Headless_Terminator.md).

# RAPPORT OSINT : Intégration Terminal/TUI pour Google AI Studio (Gemini)
**NŒUD 2 - Arcanis-360**

## 1. Vue d'ensemble de l'écosystème TUI/CLI pour Gemini
L'utilisation de Google AI Studio en mode purement terminal (zéro Chrome) est parfaitement viable. L'écosystème s'articule autour de trois axes : les outils CLI autonomes, les assistants intégrés (Aider) et les plugins d'éditeurs (Neovim/Helix). 

**Attention** : Depuis fin 2026, l'authentification par clé d'API standard évolue. Privilégier les clés d'autorisation liées aux comptes de service (Service Accounts) pour éviter toute interruption.

---

## 2. Outils CLI Autonomes (Pair Programming Terminal)

### A. Aider (Le standard de facto)
Aider est aujourd'hui la solution CLI la plus robuste pour interagir avec les LLMs directement dans un dépôt Git.
*   **Implémentation** : `python -m pip install aider-chat`
*   **Utilisation** : `export GEMINI_API_KEY=...` suivi de `aider --model gemini/gemini-2.5-flash` (ou modèles expérimentaux via `gemini-exp`).
*   **Avantages** : Indexation native du dépôt Git, application directe des patchs, commande `/add <fichier>` pour un contexte granulaire.
*   **Pertinence** : Excellente. C'est l'outil le plus complet pour rester dans le terminal sans ouvrir d'interface web.

### B. Gemini CLI (Outil Officiel Google)
Client officiel open-source développé par Google, fonctionnant sur Node.js.
*   **Implémentation** : `npm install -g @google/gemini-cli` ou via `npx`.
*   **Fonctionnalités clés** : 
    *   Supporte le protocole MCP (Model Context Protocol).
    *   Boucle ReAct (Reason and Act) intégrée avec accès aux fichiers locaux et commandes shell.
    *   Support PTY (pseudo-terminal) pour exécuter des commandes interactives (`vim`, `git rebase`) depuis le contexte CLI.
*   **Pertinence** : Idéal pour un agent autonome dans le terminal, mais attention aux quotas du "consumer tier" qui poussent vers des clés Vertex/AI Studio dédiées.

---

## 3. Intégrations Éditeurs de Code (Terminal-Native)

### A. Écosystème Neovim
Neovim dispose de l'écosystème le plus riche pour Gemini via des plugins Lua.
1.  **avante.nvim** : Offre une expérience "Cursor-like". Accepte Gemini, gère les attachements de fichiers et propose des vues git-diff pour appliquer les suggestions.
2.  **codecompanion.nvim** : Le couteau suisse. Permet des fenêtres de chat flottantes, des modifications de code inline (`fix this function`), et gère de multiples providers dont Gemini.
3.  **gemini.nvim / askGemini.nvim** : Plugins plus simples dédiés spécifiquement à Google Gemini pour des tâches basiques (explications, tests unitaires).

### B. Écosystème Helix
La philosophie d'Helix (zéro plugin) impose des approches alternatives et plus "Unix-philosophy" :
1.  **LSP-AI** : Un Language Server (LSP) qui sert de pont vers les LLMs. Configuré dans `languages.toml`, il permet d'envoyer les complétions vers l'API Gemini. Peut souffrir de latence selon le modèle.
2.  **Architecture Multi-Pane (Zellij/Tmux)** : La méthode recommandée par la communauté. Exécuter Helix dans un panneau et `Aider` ou `Gemini CLI` dans le panneau adjacent.
3.  **Macros & Pipes** : Utiliser la sélection native d'Helix et l'envoyer via un pipe (`|`) à un script shell/python local qui interroge l'API Gemini et remplace la sélection par la réponse. Léger et redoutablement efficace.

---

## 4. Recommandations Finales (No-Chrome Policy)

1.  **Développeur centré Éditeur (Neovim)** : Installer `avante.nvim` ou `codecompanion.nvim` avec la clé AI Studio. C'est la solution la plus fluide pour éditer sans quitter le contexte visuel du code.
2.  **Développeur Agnostique / Helix** : Utiliser un multiplexeur (Zellij/Tmux) combiné à **Aider-chat**. Cela offre un découplage total entre l'éditeur (Helix) et l'IA (Aider), garantissant des performances maximales sans alourdir l'éditeur.
3.  **DevOps / Sysadmin** : Adopter le **Gemini CLI** officiel pour ses capacités MCP et d'exécution PTY, parfait pour diagnostiquer des systèmes ou écrire des scripts shell en direct.
