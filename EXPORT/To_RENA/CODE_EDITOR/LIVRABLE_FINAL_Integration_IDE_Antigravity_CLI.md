# LIVRABLE FINAL : INTÉGRATION ÉDITEUR DE CODE × ANTIGRAVITY CLI (MIDGARD)

![Status](https://img.shields.io/badge/Status-MVP-blue) ![Ecosystem](https://img.shields.io/badge/Ecosystem-TESLA%20ANTIGRAVITY-purple) ![Security](https://img.shields.io/badge/Security-ID%20LOCKED-red) ![Python](https://img.shields.io/badge/Python-3.12+-blue)

**Date** : 19 Septembre 2026
**Classification** : Étude de faisabilité certifiée PREMORTEM
**Certification** : `WARNING_ISSUED` → Corrections intégrées → **RECOMMENDED**
**Score de résilience** : 0.7 → **0.85** (post-corrections)
**Agents mobilisés** : Tesla-Arcanis-360, Tesla-Web-Raider, Tesla-Curator-Prime, Tesla-PREMORTEM

---

## TABLE DES MATIÈRES

1. [Contexte et Résultat Final Attendu](#1-contexte-et-résultat-final-attendu)
2. [Profil Matériel MIDGARD](#2-profil-matériel-midgard)
3. [Synthèse Comparative — Scoring Consolidé](#3-synthèse-comparative--scoring-consolidé)
4. [PLAN A — Google AI Studio (Prototypage Cloud)](#4-plan-a--google-ai-studio-prototypage-cloud)
5. [PLAN B — Neovim + Tmux (Solution Recommandée N°1 — Terminal-First)](#5-plan-b--neovim--tmux-solution-recommandée-n1--terminal-first)
6. [PLAN C — Zed Editor (Solution Alternative N°2 — GUI Moderne)](#6-plan-c--zed-editor-solution-alternative-n2--gui-moderne)
7. [PLAN D — Optimisations Système MIDGARD (Transversal Obligatoire)](#7-plan-d--optimisations-système-midgard-transversal-obligatoire)
8. [Registre des Risques (PREMORTEM)](#8-registre-des-risques-premortem)
9. [Architecture Cible Finale](#9-architecture-cible-finale)
10. [Annexes — Rapports Sources](#10-annexes--rapports-sources)

---

## 1. CONTEXTE ET RÉSULTAT FINAL ATTENDU

**Problématique** : Lord Mahonheim utilise Antigravity CLI v1.2.7 avec un écosystème Tesla complètement personnalisé sur MIDGARD (Ubuntu Linux). AGY couvre ~70% des besoins IDE (génération, exécution, orchestration IA). Il reste **30% non couverts** : édition visuelle de code, navigation d'arborescence, debugging graphique, refactoring multi-fichiers.

**Contrainte stratégique** : Google a annoncé le sunset de Firebase Studio au **22 mars 2027** avec orientation vers Google AI Studio et les environnements compatibles Antigravity.

**Résultat final** : Un environnement de développement hybride composé de :
- **Google AI Studio** (cloud, via Chrome) → prototypage IA et expérimentation
- **Un éditeur de code ultra-léger** (local) → édition, navigation, debugging
- **Antigravity CLI v1.2.7** (terminal) → orchestration agentique, MCP, automation
- Le tout fonctionnant **simultanément** sur MIDGARD sans saturer la RAM ni provoquer de swap sur le HDD mécanique.

---

## 2. PROFIL MATÉRIEL MIDGARD

| Composant | Spécification | Contrainte |
|-----------|---------------|------------|
| **CPU** | Intel Core i7-10510U (4C/8T, boost 4.9GHz) | Suffisant pour la compilation et les LSP |
| **RAM** | 7.6 Go total | **~3 Go disponibles** en usage (Chrome + AGY + GNOME) |
| **Stockage** | WD 1 To HDD mécanique (ext4) | **PAS DE SSD** — le swap sur HDD = freeze système |
| **GPU** | NVIDIA MX130 (2 Go) + Intel UHD | Utilisable pour le rendu GPU (Zed) |
| **OS** | Ubuntu Linux, GNOME Shell | Standard |
| **Réseau** | WiFi 192.168.11.110 | Requis pour AI Studio |
| **AGY** | Antigravity CLI v1.2.7 | Installé à `~/.local/bin/agy` |

> **⚠️ Règle de survie MIDGARD** : Budget RAM pour l'éditeur = **maximum 500 Mo**. Au-delà, la machine swap sur le HDD et devient inutilisable. Toute solution Electron (VS Code, Atom, etc.) est **formellement proscrite**.

---

## 3. SYNTHÈSE COMPARATIVE — SCORING CONSOLIDÉ

| Éditeur | RAM | I/O HDD | Compat. AGY | IA Native | Verdict MIDGARD |
|:---|:---|:---|:---|:---|:---|
| **Neovim + Tmux** | ~50-80 Mo | Nulle | ★★★★★ (TUI native) | Haute (plugins) | ✅ **Recommandé N°1** |
| **Helix** | ~50-80 Mo | Nulle | ★★★★★ (TUI native) | Moyenne | ✅ Alternative Terminal |
| **Zed Editor** | ~150-300 Mo | Moyenne | ★★★★☆ (Alacritty) | Haute (native) | ✅ **Recommandé N°2** |
| **Lite XL** | ~20-50 Mo | Faible | ★★★☆☆ | Faible | ✅ Ultra-léger GUI |
| **Sublime Text 4** | ~100-200 Mo | Faible | ★★★☆☆ (Terminus) | Faible | ⚠️ Acceptable |
| **VS Code / VSCodium** | 500 Mo - 1.5 Go+ | **Critique** | ★★★★☆ | Haute | ❌ **Rejeté** |
| **JetBrains IDEs** | > 1.5 Go | **Critique** | ★★★★★ (officiel) | Haute | ❌ **Rejeté** |

> **Fait** : JetBrains est officiellement recommandé par Google pour l'intégration Antigravity, mais il est **physiquement impossible** de l'exécuter correctement sur MIDGARD (HDD + 8 Go RAM). Ce n'est pas un choix, c'est une contrainte matérielle.

---

## 4. PLAN A — GOOGLE AI STUDIO (Prototypage Cloud)

### Étude de faisabilité

| Critère | Évaluation |
|---------|------------|
| **Impact RAM locale** | Nul (exécution cloud). Seul Chrome consomme (~2 Go, déjà en charge) |
| **Compatibilité AGY** | Stratégique — Google oriente la migration Firebase vers AGY + AI Studio |
| **Vendor lock-in** | Moyen — dépendance cloud Google, mais le code reste exportable |
| **Pérennité** | Haute — Google investit massivement dans cette direction post-Firebase |

### Plan d'intervention linéaire

1. **Accéder à Google AI Studio** : Ouvrir Chrome et naviguer vers `https://aistudio.google.com`. Se connecter avec le compte Google associé à l'écosystème Tesla.

2. **Inventorier les projets Firebase Studio** : Lister tous les projets actifs dans Firebase Studio avant le gel. Exporter le code source de chaque projet vers le dépôt local MIDGARD (`~/bifrost/tesla/`).

3. **Créer les espaces de travail AI Studio** : Pour chaque projet identifié à l'étape 2, créer un espace équivalent dans Google AI Studio. Configurer les clés API Gemini nécessaires.

4. **Établir le pipeline de rapatriement** : Définir un flux de travail standardisé :
   - Prototyper dans AI Studio (cloud)
   - Exporter le code généré (copier/coller ou téléchargement)
   - Intégrer dans le dépôt local via `git add` + `git commit`
   - Utiliser AGY en local pour l'itération et l'orchestration agentique

5. **Valider la boucle complète** : Tester le cycle complet (AI Studio → export → local → AGY) sur un mini-projet de test avant la date limite du 22 mars 2027.

6. **Planifier le retrait de Firebase Studio** : Programmer un rappel pour le 1er mars 2027 afin de vérifier que tous les projets ont été migrés et que le pipeline fonctionne.

---

## 5. PLAN B — NEOVIM + TMUX (Solution Recommandée N°1 — Terminal-First)

### Pourquoi Neovim

- **RAM** : ~50-80 Mo (100x moins que VS Code)
- **I/O HDD** : Quasi-nulles après le démarrage initial
- **Synergie AGY** : Les deux sont des TUI — ils partagent le même espace de travail (le terminal). Aucune friction d'intégration.
- **Extensibilité** : Écosystème de plugins mature (Telescope, nvim-tree, LSP natif, treesitter)

### Plan d'intervention linéaire

> **Résultat final de ce plan** : Un workspace Tmux scindé en deux : Neovim à gauche (édition, navigation, LSP), AGY à droite (orchestration, MCP, génération). Les deux communiquent via le système de fichiers partagé.

1. **Installer les paquets fondamentaux** :
   ```bash
   sudo apt update && sudo apt install -y neovim tmux ripgrep fd-find git curl
   ```

2. **Installer le gestionnaire de plugins `lazy.nvim`** :
   ```bash
   git clone --filter=blob:none https://github.com/folke/lazy.nvim.git \
     --branch=stable ~/.local/share/nvim/lazy/lazy.nvim
   ```

3. **Créer la configuration Neovim de base** :
   ```bash
   mkdir -p ~/.config/nvim && nvim ~/.config/nvim/init.lua
   ```
   Contenu minimal : charger `lazy.nvim`, activer les numéros de ligne, définir l'indentation à 2 espaces, activer la coloration syntaxique treesitter.

4. **Installer les plugins essentiels (via lazy.nvim)** :
   - `nvim-treesitter` — coloration syntaxique avancée
   - `telescope.nvim` — recherche fuzzy de fichiers et de texte (utilise `ripgrep` et `fd`)
   - `nvim-tree.lua` — explorateur de fichiers latéral
   - `nvim-lspconfig` — configuration des Language Servers (Python, JS, etc.)
   - `mason.nvim` — installation automatique des LSP servers

5. **Configurer les exclusions d'indexation (Protection HDD)** :
   Dans la configuration Telescope, ajouter les exclusions strictes :
   ```lua
   file_ignore_patterns = { "node_modules", ".git", "build", "dist", "target", "__pycache__", ".venv" }
   ```

6. **⚠️ Synergie AGY — Délégation MCP (Correction PREMORTEM)** :
   > **NE PAS tenter de configurer MCP directement dans Neovim.** Il n'existe pas de client MCP natif stable pour Neovim.
   
   La synergie se fait via **Tmux** :
   - Neovim gère l'**édition textuelle pure** (écriture, navigation, LSP, refactoring)
   - AGY CLI (dans le panneau Tmux adjacent) gère **exclusivement** le MCP, l'orchestration et la génération
   - Les deux partagent le même système de fichiers — quand AGY génère un fichier, Neovim le voit instantanément

7. **Configurer Tmux** :
   ```bash
   cat > ~/.tmux.conf << 'EOF'
   # Préfixe : Ctrl+a (plus ergonomique que Ctrl+b)
   unbind C-b
   set -g prefix C-a
   bind C-a send-prefix
   
   # Scission horizontale : Ctrl+a puis |
   bind | split-window -h
   # Scission verticale : Ctrl+a puis -
   bind - split-window -v
   
   # Navigation entre panneaux : Alt + flèches
   bind -n M-Left select-pane -L
   bind -n M-Right select-pane -R
   bind -n M-Up select-pane -U
   bind -n M-Down select-pane -D
   
   # Historique étendu
   set -g history-limit 10000
   
   # Support 256 couleurs
   set -g default-terminal "tmux-256color"
   EOF
   ```

8. **Démarrer le Workspace Tesla** :
   ```bash
   tmux new -s tesla
   ```
   Puis scinder l'écran (`Ctrl+a` puis `|`). Dans le panneau de gauche : `nvim .` Dans le panneau de droite : `agy`.

9. **Valider le fonctionnement** :
   - Dans AGY (panneau droit), demander la génération d'un fichier de test
   - Dans Neovim (panneau gauche), vérifier que le fichier apparaît dans nvim-tree
   - Ouvrir le fichier, vérifier la coloration syntaxique et le LSP
   - Confirmer que la RAM totale (Chrome + GNOME + Neovim + AGY) reste sous 6 Go via `htop`

---

## 6. PLAN C — ZED EDITOR (Solution Alternative N°2 — GUI Moderne)

### Pourquoi Zed

- **RAM** : ~150-300 Mo (3-4x moins que VS Code)
- **Architecture** : Écrit en Rust, rendu GPU (soulage le CPU)
- **Terminal intégré** : Propulsé par Alacritty (ultra-rapide) — permet de lancer AGY directement dans l'éditeur
- **IA native** : Intégration IA intégrée (OpenAI, Anthropic, etc.) avec faible empreinte

### Plan d'intervention linéaire

> **Résultat final de ce plan** : Zed Editor avec AGY dans le terminal intégré, arborescence latérale pour la navigation visuelle, et accélération GPU activée.

1. **Installer Zed Editor** :
   ```bash
   curl -f https://zed.dev/install.sh | sh
   ```

2. **⚠️ Vérifier l'accélération matérielle Vulkan (Correction PREMORTEM)** :
   L'architecture hybride Intel UHD + NVIDIA MX130 peut poser problème. Vérifier AVANT de lancer Zed :
   ```bash
   sudo apt install -y vulkan-tools mesa-vulkan-drivers
   vulkaninfo --summary
   ```
   Si Vulkan n'est pas détecté sur le GPU dédié, forcer le GPU Intel :
   ```bash
   # Ajouter dans ~/.bashrc ou lancer avant Zed :
   export __NV_PRIME_RENDER_OFFLOAD=0
   ```

3. **Lancer Zed et configurer les exclusions (Protection HDD)** :
   Ouvrir Zed, accéder aux paramètres (`Ctrl+,`) et ajouter dans `settings.json` :
   ```json
   {
     "file_scan_exclusions": [
       "node_modules", ".git", "build", "dist", "target",
       "__pycache__", ".venv", "*.pyc"
     ],
     "telemetry": {
       "diagnostics": false,
       "metrics": false
     }
   }
   ```

4. **Désactiver la télémétrie** : Déjà inclus dans le `settings.json` ci-dessus. Cela préserve la bande passante et réduit les I/O disque.

5. **Lier Antigravity CLI** :
   Ouvrir le terminal intégré de Zed (`Ctrl+`` ` ou via le menu). Exécuter `agy` dans ce terminal. L'arborescence latérale de Zed permet la navigation visuelle pendant qu'AGY opère dans le terminal en bas.

6. **Configurer le thème et la police** :
   Choisir un thème sombre économe en rendu GPU. Configurer la police monospace préférée (ex: `JetBrains Mono`, `Fira Code`).

7. **Valider le fonctionnement** :
   - Ouvrir un projet (`zed ~/bifrost/tesla/`)
   - Vérifier que l'arborescence se charge rapidement
   - Lancer AGY dans le terminal intégré
   - Tester la génération d'un fichier et sa visibilité dans l'arborescence
   - Contrôler la RAM via `htop` : Chrome + GNOME + Zed + AGY doit rester sous 6.5 Go

---

## 7. PLAN D — OPTIMISATIONS SYSTÈME MIDGARD (Transversal Obligatoire)

> **⚠️ Ce plan est OBLIGATOIRE quelle que soit la solution choisie (Plan B ou Plan C).** Il transforme la gestion mémoire de MIDGARD pour compenser l'absence de SSD.

### Plan d'intervention linéaire

1. **Installer l'outil ZRAM** :
   ```bash
   sudo apt install -y zram-tools
   ```

2. **Configurer la taille et l'algorithme ZRAM** :
   ```bash
   sudo nano /etc/default/zramswap
   ```
   Modifier les lignes suivantes :
   ```
   PERCENT=50
   ALGO=zstd
   ```
   Cela dédie environ 4 Go de RAM compressée comme swap ultra-rapide. L'algorithme `zstd` offre le meilleur ratio vitesse/compression pour un i7 de 10ème génération.

3. **⚠️ Configurer la Swappiness (Correction PREMORTEM CRITIQUE)** :
   ```bash
   sudo nano /etc/sysctl.conf
   ```
   Ajouter à la fin du fichier :
   ```
   vm.swappiness=100
   ```
   > **ATTENTION** : Avec ZRAM, la swappiness **DOIT** être à `100` (et non `10`). Une valeur basse comme `10` force le kernel à éviter le swap ZRAM et à évincer le cache fichier vers le HDD mécanique, ce qui provoque exactement le thrashing qu'on cherche à éviter. Une swappiness à `100` indique au kernel de privilégier la compression ZRAM (ultra-rapide) plutôt que les I/O sur le disque mécanique.

4. **Appliquer les modifications** :
   ```bash
   sudo sysctl -p
   sudo systemctl restart zramswap
   ```

5. **Désactiver le swap fichier HDD** (optionnel mais recommandé si ZRAM est actif) :
   ```bash
   sudo swapoff /swap.img
   # Pour rendre permanent, commenter la ligne swap dans /etc/fstab :
   sudo nano /etc/fstab
   # Commenter la ligne contenant /swap.img
   ```

6. **Vérifier l'état** :
   ```bash
   # Vérifier que ZRAM est actif :
   zramctl
   # Vérifier que le swap HDD est désactivé :
   swapon --show
   # Vérifier la swappiness :
   cat /proc/sys/vm/swappiness
   # Doit afficher : 100
   ```

7. **Test de charge** :
   Ouvrir simultanément Chrome (quelques onglets), l'éditeur choisi et AGY. Observer avec `htop` que :
   - Le swap ZRAM est utilisé (normal et souhaité)
   - Le swap HDD (`/swap.img`) reste à **0**
   - Le système reste fluide

---

## 8. REGISTRE DES RISQUES (PREMORTEM)

| # | Risque | RPN | Catégorie | Mitigation | Statut |
|---|--------|-----|-----------|------------|--------|
| 1 | Contresens swappiness avec ZRAM (valeur `10` au lieu de `100`) | **90** | Régression système | Corrigé dans Plan D étape 3 — swappiness fixée à `100` | ✅ Corrigé |
| 2 | Implémentation MCP fantôme dans Neovim | **64** | Complétude | Corrigé dans Plan B étape 6 — MCP délégué à AGY via Tmux | ✅ Corrigé |
| 3 | Échec accélération GPU Vulkan pour Zed | **45** | Faisabilité matérielle | Corrigé dans Plan C étape 2 — vérification `vulkaninfo` obligatoire | ✅ Corrigé |
| 4 | Vendor lock-in Google AI Studio | **20** | Stratégique | Mitigation : pipeline de rapatriement local (Plan A étape 4) | ⚠️ Accepté |
| 5 | Courbe d'apprentissage Neovim | **15** | Adoption | Mitigation : Zed comme Plan C alternatif si Neovim trop abrupt | ⚠️ Accepté |

**Score de résilience post-corrections** : **0.85 / 1.0**
**Verdict final** : **RECOMMENDED** ✅

---

## 9. ARCHITECTURE CIBLE FINALE

```
┌─────────────────────────────────────────────────────────────────┐
│                    MIDGARD — ARCHITECTURE IDE                    │
│               (Budget RAM total : < 6.5 Go)                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────────────────────────────────┐ │
│  │  Chrome       │  │  Terminal (Tmux ou Zed intégré)          │ │
│  │  (~2 Go RAM)  │  │                                          │ │
│  │              │  │  ┌─────────────┐  ┌──────────────────┐  │ │
│  │  Google AI   │  │  │  Neovim     │  │  Antigravity CLI │  │ │
│  │  Studio      │  │  │  ou Zed     │  │  (agy v1.2.7)    │  │ │
│  │  (Cloud)     │  │  │  (~80-300Mo)│  │  (~330 Mo)       │  │ │
│  │              │  │  │             │  │                  │  │ │
│  │  Prototypage │  │  │  Édition    │  │  MCP / Agents    │  │ │
│  │  IA          │  │  │  Navigation │  │  Orchestration   │  │ │
│  │  Expérim.    │  │  │  LSP/Debug  │  │  Génération      │  │ │
│  └──────┬───────┘  │  └──────┬──────┘  └────────┬─────────┘  │ │
│         │          │         │                   │            │ │
│         │          │         └───────┬───────────┘            │ │
│         │          │                 │                        │ │
│         │          │    Système de fichiers partagé           │ │
│         │          │    ~/bifrost/tesla/                      │ │
│         │          └──────────────────────────────────────────┘ │
│         │                                                       │
│         └──── Export/Import code ──── Pipeline rapatriement     │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│  ZRAM (4 Go compressés, zstd, swappiness=100)                   │
│  HDD Swap : DÉSACTIVÉ                                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 10. ANNEXES — RAPPORTS SOURCES

| Nœud | Agent | Rapport |
|------|-------|---------|
| 0 | Audit Système | Profil MIDGARD (inline dans cette session) |
| 1 | Tesla-Arcanis-360 | [NOEUD1_Arcanis360_DeepResearch_IDE.md](file:///home/lord-mahonheim/bifrost/tesla/OUTPUTS/NOEUD1_Arcanis360_DeepResearch_IDE.md) |
| 2 | Tesla-Web-Raider | [NOEUD2_WebRaider_ExtractionTech_IDE.md](file:///home/lord-mahonheim/bifrost/tesla/OUTPUTS/NOEUD2_WebRaider_ExtractionTech_IDE.md) |
| 3 | Tesla-Curator-Prime | [NOEUD3_CuratorPrime_EtudeFaisabilite_IDE.md](file:///home/lord-mahonheim/bifrost/tesla/OUTPUTS/NOEUD3_CuratorPrime_EtudeFaisabilite_IDE.md) |
| 4 | Tesla-PREMORTEM | [NOEUD4_PREMORTEM_Certification_IDE.md](file:///home/lord-mahonheim/bifrost/tesla/OUTPUTS/NOEUD4_PREMORTEM_Certification_IDE.md) |

---

> *Ce document est le livrable final certifié de la mission « Intégration Éditeur de Code × Antigravity CLI ». Il consolide les travaux de 4 agents d'élite Tesla et intègre les 3 corrections critiques identifiées par l'audit PREMORTEM. Tous les plans d'intervention sont exécutables séquentiellement sur MIDGARD sans risque de régression système.*
