> **ARCHIVE — remplacée pour le parcours sans Chrome (audit du 2026-09-19).**
> Les commandes, modèles, chiffres et certifications ci-dessous ne sont pas
> une procédure validée. Ne pas appliquer les changements système ni les
> exemples d’auto-exécution. Utiliser le [guide corrigé TERMINATOR](LIVRABLE_FINAL_AIStudio_Headless_Terminator.md).

# ÉTUDE DE FAISABILITÉ & PLANS D'INTERVENTION : INTÉGRATION IDE x ANTIGRAVITY CLI (MIDGARD)

## RÉSULTAT FINAL ATTENDU
Le déploiement d'un environnement de développement hybride et ultra-résilient pour la machine MIDGARD (Intel i7, 8 Go RAM, HDD 1 To). Cet environnement doit permettre une synergie parfaite entre Google AI Studio (prototypage cloud), Antigravity CLI (orchestration locale, v1.2.7), et un éditeur de code ultra-léger garantissant zéro utilisation de swap sur le disque mécanique (ce qui provoquerait un gel du système).

---

## PARTIE 1 : SYNTHÈSE COMPARATIVE (SCORING)

Basé sur le croisement des rapports d'analyse Arcanis-360 et Web-Raider, voici la matrice de corrélation pour le profil matériel MIDGARD.

| Éditeur | RAM Estimée | Charge HDD (I/O) | Compatibilité AGY | Extensibilité IA | Verdict Faisabilité |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Neovim / Helix** | ~50-80 Mo | Nulle (après boot) | Excellente (TUI) | Haute (MCP) | **Validé (Recommandé N°1)** |
| **Lite XL** | ~20-50 Mo | Faible | Bonne | Faible | Validé (Alternative GUI) |
| **Zed Editor** | ~150-300 Mo | Moyenne | Excellente (Alacritty) | Haute | **Validé (Recommandé N°2)** |
| **VS Code / VSCodium** | > 1 Go | Critique | Moyenne | Haute | **Rejeté (Risque de SWAP)** |
| **JetBrains (Recommandé par Google)** | > 1.5 Go | Critique | Haute (Officiel) | Haute | **Rejeté (Crash HDD garanti)** |

---

## PARTIE 2 : FOCUS GOOGLE AI STUDIO & FIREBASE SUNSET

### Étude de faisabilité détaillée
Le sunset de Firebase Studio (22 mars 2027) impose une transition. Google oriente les développeurs vers **Google AI Studio** (cloud/navigateur) pour l'expérimentation, et **Antigravity CLI** pour l'exécution locale.
Sur MIDGARD, l'utilisation de Google AI Studio consommera les ressources de Google Chrome (~2 Go de RAM). L'avantage est la décharge du CPU local pour l'inférence. L'inconvénient est la charge RAM. Il est donc critique que le reste de l'écosystème local (AGY + Éditeur) ne dépasse pas 1 Go de RAM cumulé.

### Plan d'intervention (Migration & Synchronisation)
1. **Évaluer les dépendances Firebase Studio** : Identifier immédiatement les projets s'appuyant sur l'UI de Firebase Studio et planifier leur transition avant le 22 mars 2027.
2. **Provisionner Google AI Studio** : Créer les espaces de travail nécessaires directement depuis Chrome pour déporter la charge de prototypage IA dans le cloud.
3. **Mettre à niveau Antigravity** : Vérifier que le CLI local est bien en v1.2.7 pour garantir le support des standards de communication (MCP et hooks).
4. **Établir le pipeline de rapatriement** : Définir un flux de travail clair pour copier/importer le code généré dans AI Studio vers le dépôt local de MIDGARD (`~/bifrost/tesla`).

---

## PARTIE 3 : SOLUTION RECOMMANDÉE N°1 - NEOVIM (Approche Terminal-First)

Cette solution est la seule qui garantisse une sécurité absolue contre les crashs matériels. En utilisant Neovim combiné à Tmux, les I/O du disque mécanique sont quasi-nuls et la consommation RAM reste sous la barre des 100 Mo.

### Plan d'intervention linéaire
1. **Installer les paquets de base** : Ouvrir un terminal et exécuter `sudo apt update && sudo apt install neovim tmux ripgrep fd-find`.
2. **Initialiser le multiplexeur** : Créer le fichier `~/.tmux.conf` et configurer des raccourcis pour scinder l'écran en deux (un panneau pour l'éditeur, un panneau pour AGY).
3. **Installer un gestionnaire de plugins** : Déployer `lazy.nvim` pour Neovim afin d'assurer un chargement asynchrone des extensions, minimisant ainsi le temps d'accès au HDD au démarrage.
4. **Protéger le disque dur (Exclusions)** : Configurer les plugins de recherche (Telescope) pour exclure strictement les répertoires d'indexation lourds (`node_modules`, `.git`, `build`).
5. **Connecter Antigravity via MCP** : Configurer Neovim (via LSP ou plugins dédiés) pour lire les manifestes et communiquer avec les plugins situés dans `~/.gemini/antigravity-cli/plugins/`.
6. **Démarrer le Workspace** : Taper `tmux new -s tesla`. Dans la fenêtre de gauche, lancer `nvim`. Dans la fenêtre de droite, lancer l'interface utilisateur terminal d'AGY (`agy`).

---

## PARTIE 4 : SOLUTION ALTERNATIVE N°2 - ZED EDITOR (Approche GUI Moderne)

Si une interface graphique est indispensable, Zed Editor est le meilleur compromis. Écrit en Rust et accéléré par le GPU (MX130/Intel UHD), il soulage le CPU de l'i7, même si son premier démarrage sera légèrement ralenti par le HDD mécanique par rapport à Neovim.

### Plan d'intervention linéaire
1. **Installer Zed** : Exécuter le script officiel via `curl -f https://zed.dev/install.sh | sh`.
2. **Valider l'accélération matérielle** : Lancer l'éditeur et s'assurer qu'il s'appuie sur le GPU pour le rendu de son interface utilisateur, économisant ainsi les cycles du processeur central.
3. **Restreindre l'indexation (Crucial)** : Ouvrir `settings.json` dans Zed et ajouter une liste stricte d'exclusions de fichiers (File Excludes) pour empêcher le HDD de mouliner continuellement.
4. **Désactiver la télémétrie** : Dans ce même fichier `settings.json`, couper toutes les remontées d'informations automatiques pour préserver la bande passante et l'I/O disque.
5. **Lier Antigravity CLI** : Ouvrir le panneau de terminal intégré (propulsé par Alacritty, extrêmement léger) en bas de la fenêtre Zed.
6. **Lancer la session** : Exécuter `agy` dans ce terminal intégré tout en utilisant l'arborescence latérale de Zed pour manipuler les fichiers visuellement.

---

## PARTIE 5 : OPTIMISATIONS SYSTÈME MIDGARD (Transversales)

Ces étapes sont **OBLIGATOIRES**, quelle que soit la solution d'éditeur choisie. Elles visent à transformer la RAM en disque virtuel compressé (ZRAM) et à empêcher Linux de solliciter le disque mécanique pour pallier le manque de mémoire.

### Plan d'intervention linéaire
1. **Installer l'outil ZRAM** : Exécuter `sudo apt install zram-tools`.
2. **Configurer la taille de la ZRAM** : Éditer le fichier `/etc/default/zramswap` en root. Fixer l'allocation (PERCENT) à 50, ce qui dédiera environ 4 Go à la compression mémoire.
3. **Choisir l'algorithme de compression** : Toujours dans `/etc/default/zramswap`, forcer l'utilisation de l'algorithme `zstd` (excellent ratio vitesse/compression pour un i7 de 10ème génération).
4. **Désengorger le HDD (Swappiness)** : Éditer le fichier `/etc/sysctl.conf`. Ajouter la ligne `vm.swappiness=10` à la fin du fichier. Cela interdit à Linux d'utiliser le SWAP disque tant qu'il reste au moins 10% de RAM disponible.
5. **Appliquer les politiques système** : Exécuter `sudo sysctl -p` pour valider la règle de swappiness, puis `sudo systemctl restart zramswap` pour activer la partition compressée.
6. **Vérifier l'état de survie** : Ouvrir Google Chrome, lancer l'éditeur choisi et AGY. Taper `zramctl` dans un autre terminal pour s'assurer que la mémoire compressée est activement utilisée, et `htop` pour vérifier que le SWAP disque reste à zéro.
