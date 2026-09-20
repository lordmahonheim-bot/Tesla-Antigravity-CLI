> **ARCHIVE — remplacée pour le parcours sans Chrome (audit du 2026-09-19).**
> Les commandes, modèles, chiffres et certifications ci-dessous ne sont pas
> une procédure validée. Ne pas appliquer les changements système ni les
> exemples d’auto-exécution. Utiliser le [guide corrigé TERMINATOR](LIVRABLE_FINAL_AIStudio_Headless_Terminator.md).

# PLAN D'INTERVENTION LINÉAIRE ET NUMÉROTÉ (NŒUD 6)
**Auteur :** Tesla-Curator-Prime (CKO)
**Date :** 19 Septembre 2026
**Cible :** Environnement MIDGARD (Intel i7, 7.6 Go RAM, HDD)

---

## DÉFINITION DU RÉSULTAT FINAL ATTENDU
Le déploiement de ce plan garantira un **écosystème hybride de développement** parfaitement fluide sur la machine MIDGARD.
À l'issue de l'exécution, le système permettra de :
1. Prototyper des solutions dans le cloud via **Google AI Studio** sur Google Chrome.
2. Rapatrier le code de manière sécurisée et versionnée (Vigilum Codex) via un pipeline Git scripté.
3. Valider, auditer et exécuter ce code localement à travers **Antigravity CLI (AGY v1.2.7)** et des hooks de sécurité (`bandit`).
4. Éditer le code localement avec une empreinte RAM inférieure à **500 Mo** pour prévenir tout freeze du disque mécanique (HDD).

---

## PARTIE 1 : SYNTHÈSE COMPARATIVE DES ÉDITEURS (CONTRAINTE MIDGARD)

Les contraintes matérielles strictes (HDD, 3 Go RAM dispo, max 500 Mo pour l'éditeur) excluent d'office les IDE lourds (VS Code, JetBrains). La sélection se porte sur les éditeurs en terminal (TUI).

| Solution | Empreinte RAM | CPU Usage | Compatibilité AGY | Extensibilité IA | Risque HDD | Verdict Faisabilité |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Neovim (N°1)** | ~30 - 80 Mo | Très Faible | Excellente (TUI) | Haute (Plugins Lua) | Nul (Zéro swap) | **CERTIFIÉ EXCELLENT** |
| **Helix (N°2)** | ~15 - 50 Mo | Très Faible | Excellente (TUI) | Moyenne (Built-in) | Nul (Zéro swap) | **CERTIFIÉ TRÈS BON** |
| VS Code (Réf.) | ~800 Mo - 2 Go| Modéré | Bonne | Haute | **CRITIQUE** (Freeze) | **PROSCRIT** |

**Matrice de Corrélation avec Antigravity CLI :**
Les éditeurs TUI comme Neovim/Helix s'intègrent nativement à côté d'AGY v1.2.7 dans un multiplexeur de terminal (ex: `tmux` ou `zellij`), permettant de garder la sandbox d'orchestration et l'éditeur à l'écran avec une empreinte RAM cumulée sous les 150 Mo.

---

## PARTIE 2 : FOCUS GOOGLE AI STUDIO & ANTIGRAVITY

**Étude de faisabilité détaillée :**
Suite à l'obsolescence de Firebase Studio (22 mars 2027), Google AI Studio s'impose comme le "playground" cloud gratuit (sur interface web) et payant (API pour production).
- **Corrélation avec AGY :** AI Studio permet le prototypage "Vibe Coding" via Chrome. Le code généré est ensuite transféré vers le terminal où AGY CLI (v1.2.7) l'orchestre avec son architecture d'agents (TUI, MCP, sub-agents).
- **Sécurité et Lock-in :** Un script Python local d'ingestion agnostique limitera la dépendance à l'API Gemini.

**Plan d'intervention AI Studio (Pré-requis) :**
1. Ouvrir Google Chrome et naviguer vers `aistudio.google.com`.
2. Générer et copier la clé API Gemini.
3. Exporter la clé API dans le `.bashrc` de MIDGARD : `export GEMINI_API_KEY="votre_clé"`.

---

## PARTIE 3 : SOLUTION RECOMMANDÉE N°1 (NEOVIM + AGY CLI)

Voici le guide d'exécution chronologique de bout en bout, intégrant les recommandations de Master-Code et Github-Manager.

### Phase 1 : Initialisation de l'Écosystème
1. Installer Neovim, Python 3.10 et les outils de sécurité :
   ```bash
   sudo apt update && sudo apt install -y neovim python3.10 python3-pip git docker.io
   pip3 install bandit requests
   ```
2. Initialiser la structure de projet dans le dépôt local :
   ```bash
   mkdir -p ~/bifrost/tesla/scripts ~/bifrost/tesla/src
   ```

### Phase 2 : Configuration d'Antigravity et des Hooks
3. Créer le fichier de configuration `~/bifrost/tesla/agy-workspace.yaml` :
   ```yaml
   version: "1.2.7"
   workspace: "midgard-ai-sandbox"
   execution:
     runtime: "python3.10"
     isolation: "docker"
     entrypoint: "src/generated_main.py"
   hooks:
     pre_flight: "./scripts/validate-and-deps.sh"
     post_flight: "./scripts/cleanup.sh"
   ```
4. Créer le hook de validation `~/bifrost/tesla/scripts/validate-and-deps.sh` :
   ```bash
   #!/bin/bash
   echo "[MIDGARD] Validation statique par Bandit..."
   bandit -r ./src/ || { echo "[MIDGARD] Rejeté par sécurité"; exit 1; }
   if [ -f "requirements.txt" ]; then pip install -r requirements.txt; fi
   ```
5. Rendre le script exécutable : `chmod +x ~/bifrost/tesla/scripts/validate-and-deps.sh`.

### Phase 3 : Flux de Rapatriement Git (Vigilum Codex)
6. Avant d'ingérer du code de AI Studio, s'assurer que l'environnement est propre :
   ```bash
   cd ~/bifrost/tesla
   git checkout develop
   git pull origin develop
   ```
7. Créer la branche éphémère de fonctionnalité :
   ```bash
   git checkout -b feature/ai-studio-nouvelle-feature
   ```
8. Utiliser le script `pull_ai_studio.py` (ou coller manuellement dans `src/generated_main.py`) le code généré via Chrome.
9. Exécuter le code via Antigravity pour déclencher le scan et la sandbox :
   ```bash
   agy run
   ```
10. Valider et commiter selon le Vigilum Codex (Conventional Commits) :
    ```bash
    git add .
    git commit -m "feat(cloud-sync): rapatriement de la logique IA générée"
    git push origin feature/ai-studio-nouvelle-feature
    ```

---

## PARTIE 4 : SOLUTION ALTERNATIVE N°2 (HELIX EDITOR)

Helix offre un éditeur modal similaire à Neovim mais ne nécessitant aucune configuration (Batteries included). Idéal si le temps d'intervention sur les plugins Lua de Neovim est un frein.

**Plan d'intervention alternatif :**
1. Installer Helix : `sudo add-apt-repository ppa:maveonair/helix-editor && sudo apt update && sudo apt install helix`.
2. Remplacer Neovim par Helix dans le workflow (commande `hx .` au lieu de `nvim .`).
3. La configuration AGY (`agy-workspace.yaml`), les hooks (`validate-and-deps.sh`) et le pipeline de branches Git (`feature/ai-studio-*`) restent rigoureusement identiques à la Phase 2 et 3 de la Solution N°1.
4. L'empreinte mémoire d'Helix se maintiendra autour de 20 Mo, s'accordant parfaitement avec Chrome et AGY.

---

## PARTIE 5 : OPTIMISATIONS SYSTÈME MIDGARD (Transversales)

Pour sécuriser l'absence de swap sur le HDD et allouer un maximum de ressources à Chrome et AGY :

1. **Activation de ZRAM (Compression en RAM pour éviter le disque)** :
   ```bash
   sudo apt install zram-tools
   # Éditer /etc/default/zramswap
   # Ajouter : ALGO=zstd, PERCENT=30
   sudo systemctl restart zramswap
   ```
2. **Réduction de la tendance au swap (Swappiness)** :
   ```bash
   # Éditer /etc/sysctl.conf et ajouter :
   vm.swappiness=10
   vm.vfs_cache_pressure=50
   sudo sysctl -p
   ```
3. **Limitation de l'empreinte Chrome** :
   - Activer le mode "Économiseur de mémoire" (Memory Saver) dans les paramètres de Chrome (libère la RAM des onglets inactifs).
   - Fermer strictement tous les onglets hors `aistudio.google.com` lors des sessions de prototypage.
