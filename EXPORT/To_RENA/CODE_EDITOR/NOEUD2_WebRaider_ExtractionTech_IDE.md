# Rapport d'Extraction : Intégration Éditeurs et Écosystème Antigravity

**Cible** : Profil MIDGARD (Intel i7, 8 Go RAM totale, HDD 1 To, Ubuntu, Antigravity CLI v1.2.7)
**Date d'extraction** : Septembre 2026

---

## 1. Écosystème Google : AI Studio & Sunset Firebase Studio
* **Sunset Firebase Studio** : Google a officialisé la fermeture de Firebase Studio pour le **22 mars 2027**. Les nouvelles créations de workspace sont déjà désactivées. Les services d'infrastructure (Firestore, Auth, Functions) ne sont pas impactés.
* **Chemins de migration** :
  * **Prototypage rapide / Web** : Migration vers **Google AI Studio** (gratuit pour le prototypage, facturation à l'API pour la production).
  * **Développement Local & Agentique (Code-First)** : Google oriente les développeurs vers **Google Antigravity** et son CLI, positionné comme l'IDE/environnement de nouvelle génération pour le développement autonome.

*Sources : Documentation Google AI Studio / Guides de migration Firebase 2026.*

## 2. Architecture des Plugins Antigravity CLI
Antigravity CLI (v1.2.7) utilise une architecture modulaire et décentralisée, conçue pour limiter l'empreinte de base du terminal :
* **Manifeste** : Les plugins sont définis par un fichier `plugin.json` strict.
* **Localisation** : Ils sont chargés dynamiquement depuis `~/.gemini/antigravity-cli/plugins/`.
* **Standardisation MCP** : Antigravity intègre la prise en charge du **Model Context Protocol (MCP)**, ce qui permet à l'agent de se connecter à des serveurs contextuels externes et à l'éditeur de code de dialoguer avec l'agent.
* **Philosophie "Minimal Host"** : Le CLI reste très léger. Les fonctionnalités "IDE" sont déportées via des hooks (`hooks.json`) et des slash commands accessibles directement dans le terminal.

## 3. Comparatif des Éditeurs Légers (Profil 8 Go RAM + HDD)

Sur une machine restreinte à 8 Go de RAM (~3 Go disponibles en charge) et surtout **limitée par un disque dur mécanique (HDD)**, le choix de l'éditeur est critique pour éviter le *swap* qui gèlera le système.

| Éditeur | Empreinte RAM (Projet Moyen) | Startup (HDD) | Architecture | Recommandation MIDGARD |
| :--- | :--- | :--- | :--- | :--- |
| **Neovim / Vim** | Très faible (~80 MB + LSP) | Instantané | Terminal, C/Lua | **Excellente**. Zéro overhead graphique. |
| **Helix** | Très faible (~80 MB + LSP) | Instantané | Terminal, Rust | **Excellente**. "Batteries incluses", très rapide. |
| **Lite XL** | Ultra faible (~20-50 MB) | Très rapide | GUI, C/Lua | **Excellente**. La meilleure alternative GUI. |
| **Sublime Text / Geany** | Faible (~100-200 MB) | Rapide | GUI, C++ / C | **Bonne**. Rapide et robuste. |
| **Zed** | Moyenne (~100-300 MB) | Moyenne | GUI, Rust/GPU | **Moyenne**. Efficace, mais plus lent à charger sur HDD. |
| **VS Code / Codium** | Élevée (500 MB - 1.5 GB+) | Lente | GUI, Electron | **À proscrire**. L'indexation saturera le HDD. |

*Note sur VS Code vs VSCodium* : Contrairement à certains mythes, VSCodium a **exactement la même empreinte RAM** que VS Code. La seule différence réside dans l'absence de télémétrie, ce qui ne sauve pas le système des lourdeurs liées à Electron et aux extensions.

## 4. Retours Communautaires & Tribal Knowledge (Reddit, Hacker News)
L'exploration des communautés techniques (Reddit, HN) pour un setup "8 Go RAM + Linux + HDD" met en évidence un consensus clair :
1. **Le HDD est le véritable goulot d'étranglement** : Le manque de RAM n'est pas fatal tant qu'on ne *swap* pas. Dès que la mémoire est pleine, le swap sur HDD rend le système inutilisable.
2. **Fuite des applications Electron** : Il est impératif de fuir VS Code, Discord, ou tout éditeur basé sur Chromium.
3. **Optimisations recommandées** :
   * **`zram` / `zswap`** : Activer ZRAM sous Ubuntu. Cela permet de compresser la RAM avant d'écrire sur le disque, repoussant drastiquement le moment où le système ralentit.
   * **Exclusion d'indexation** : Dans n'importe quel éditeur, configurer strictement l'exclusion des dossiers lourds (`node_modules`, `target`, `build`) pour éviter que le disque mécanique ne passe son temps à indexer au lieu de lire les fichiers utiles.
   * Si possible, n'activer que les serveurs LSP (Language Server Protocol) strictement nécessaires, car ils sont très gourmands en mémoire.

## 5. Synthèse Stratégique pour Lord Mahonheim
Pour combler les 30% de fonctionnalités IDE manquantes tout en respectant l'écosystème Antigravity CLI et les contraintes matérielles de MIDGARD :

1. **Option Terminal Native (Le Choix Puriste)** : Adopter **Helix** ou **Neovim**. Ces outils partagent le même espace de travail (le terminal) que l'Antigravity CLI. Ils exploitent la légèreté de la machine et ne sont pas ralentis par le HDD au démarrage.
2. **Option GUI Ultra-Légère** : Si une interface graphique est indispensable, **Lite XL** est la meilleure option. Avec un cœur en C et des plugins en Lua, il offre des fonctionnalités IDE basiques pour moins de 50 Mo de RAM.
3. **Paramétrage Système Obligatoire** : 
   * Activer et configurer **`zram`** sur Ubuntu.
   * Restreindre les plugins et l'indexation de fichiers.
   * Utiliser le CLI Antigravity pour l'orchestration, et l'éditeur de texte *exclusivement* pour la frappe et la navigation du code.
