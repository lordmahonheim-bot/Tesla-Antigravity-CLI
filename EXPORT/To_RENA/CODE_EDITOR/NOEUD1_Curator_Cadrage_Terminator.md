> **ARCHIVE — remplacée pour le parcours sans Chrome (audit du 2026-09-19).**
> Les commandes, modèles, chiffres et certifications ci-dessous ne sont pas
> une procédure validée. Ne pas appliquer les changements système ni les
> exemples d’auto-exécution. Utiliser le [guide corrigé TERMINATOR](LIVRABLE_FINAL_AIStudio_Headless_Terminator.md).

# NOEUD 1 : CADRAGE ABSOLU - WORKFLOW HEADLESS GOOGLE AI STUDIO

## 1. RÉSULTAT FINAL ATTENDU
Un environnement de travail "Headless" ultra-léger, s'exécutant intégralement et exclusivement au sein de l'émulateur de terminal **Terminator** sous Linux. Cet environnement doit permettre l'exploitation totale de **Google AI Studio** (via API et CLI) pour anticiper et pallier la fermeture de Firebase Studio (prévue le 22 mars 2027), sans jamais nécessiter le lancement d'un navigateur lourd (Chrome proscrit) afin de préserver les ressources limitées de MIDGARD (8 Go RAM, HDD mécanique).

## 2. CONTRAINTES SYSTÈME (PROFIL MIDGARD)
- **Interface** : Exécution 100% CLI/TUI dans Terminator. Navigateurs web lourds strictement proscrits.
- **Mémoire (RAM)** : 8 Go (dont ~3 Go disponibles). La solution doit minimiser l'empreinte mémoire (empreinte cible du workflow < 150 Mo).
- **Stockage (HDD)** : Disque dur mécanique. Interdiction stricte de générer des écritures/lectures intensives ou du swap sur disque (afin d'éviter les goulots d'étranglement I/O).

## 3. PLAN D'INTERVENTION LINÉAIRE ET NUMÉROTÉ

### Phase 1 : Préparation de l'environnement Système (MIDGARD)
1. **Désactiver le swap sur disque** : Exécuter `sudo swapoff -a` (et commenter l'entrée swap dans `/etc/fstab`) pour empêcher le système de swapper sur le HDD.
2. **Activer ZRAM** : Configurer le module `zram` pour créer un espace d'échange en RAM compressée (allocation d'environ 2 à 4 Go). Cela compensera la désactivation du swap HDD tout en évitant les I/O bloquantes.
3. **Configurer Terminator** : Créer un profil de fenêtrage optimisé (split-screen) dédié au workflow (un panneau pour l'éditeur, un pour l'exécution/CLI, un pour le monitoring).

### Phase 2 : Configuration Headless de Google AI Studio
1. **Acquisition de la clé API** : (Action préalable unique) Générer une clé API Google AI Studio.
2. **Sécurisation des secrets** : Stocker la clé API dans le profil bash/zsh (`~/.bashrc` ou fichier dédié sourcé) via une variable d'environnement `export GEMINI_API_KEY="x"`. Restreindre les droits du fichier avec `chmod 600`.
3. **Validation réseau** : Tester la connectivité à l'API via une requête `curl` simple pour s'assurer du bon fonctionnement sans navigateur.

### Phase 3 : Déploiement des Outils TUI/CLI
1. **Déploiement d'Antigravity CLI (AGY)** : Vérifier la présence et la configuration du binaire `agy` (v1.2.7) dans le PATH système.
2. **Installation de l'éditeur léger** : Installer Neovim (ou Micro) comme éditeur principal pour remplacer les IDE lourds basés sur Electron (comme VS Code).
3. **Installation des utilitaires de traitement** : Installer `jq` pour le parsing rapide du JSON renvoyé par l'API AI Studio en ligne de commande.

### Phase 4 : Scénario d'Exécution Quotidien
1. **Ouverture du Workspace** : Lancer Terminator avec le layout sauvegardé.
2. **Édition du Code/Prompt** : Utiliser Neovim dans le panneau de gauche pour formuler les instructions ou le code source.
3. **Interaction IA** : Lancer la commande CLI (ex: `agy chat` ou script maison `curl` + `jq`) dans le panneau de droite pour interroger Google AI Studio.
4. **Monitoring (Optionnel)** : Garder `htop` (filtré sur l'usage mémoire) dans un petit panneau inférieur pour garantir que l'usage de la RAM reste sous les 3 Go disponibles.
