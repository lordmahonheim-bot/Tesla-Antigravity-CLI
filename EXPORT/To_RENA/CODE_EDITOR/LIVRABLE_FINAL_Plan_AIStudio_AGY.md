> **ARCHIVE — remplacée pour le parcours sans Chrome (audit du 2026-09-19).**
> Les commandes, modèles, chiffres et certifications ci-dessous ne sont pas
> une procédure validée. Ne pas appliquer les changements système ni les
> exemples d’auto-exécution. Utiliser le [guide corrigé TERMINATOR](LIVRABLE_FINAL_AIStudio_Headless_Terminator.md).

# LIVRABLE FINAL : PLAN D'INTERVENTION LINÉAIRE (GOOGLE AI STUDIO × ANTIGRAVITY CLI)

![Status](https://img.shields.io/badge/Status-MVP-blue) ![Ecosystem](https://img.shields.io/badge/Ecosystem-TESLA%20ANTIGRAVITY-purple) ![Security](https://img.shields.io/badge/Security-ID%20LOCKED-red) ![Python](https://img.shields.io/badge/Python-3.12+-blue)

**Auteur :** Tesla-Team-Synergy (Arcanis-360, Web-Raider, Master-Code, Github-Manager, Curator-Prime, PREMORTEM)
**Date :** 19 Septembre 2026
**Cible :** Environnement MIDGARD (Intel i7, 7.6 Go RAM, HDD)
**Certification :** `RECOMMENDED` (Score: 0.85/1.00 — Corrections PREMORTEM intégrées)

---

## DÉFINITION DU RÉSULTAT FINAL ATTENDU
Le déploiement de ce plan garantira un **écosystème hybride de développement** parfaitement fluide sur la machine MIDGARD pour combler l'arrêt de Firebase Studio (22 mars 2027). 

À l'issue de l'exécution, le système permettra de :
1. Prototyper des solutions dans le cloud via **Google AI Studio** sur Google Chrome (délégant la charge de calcul).
2. Rapatrier le code de manière sécurisée et versionnée (Vigilum Codex) via un pipeline Git scripté.
3. Valider, auditer et exécuter ce code localement à travers **Antigravity CLI (AGY v1.2.7)** et des hooks de sécurité (`bandit`).
4. Éditer le code localement avec **Neovim ou Helix**, garantissant une empreinte RAM inférieure à 100 Mo pour prévenir tout freeze du disque mécanique (HDD). L'utilisation de Docker (I/O intensif) est expressément proscrite au profit d'environnements virtuels (`venv`).

---

## ÉTAPE 1 : OPTIMISATIONS SYSTÈME MIDGARD (Pré-requis matériel)

Pour sécuriser l'absence de swap sur le HDD et allouer un maximum de ressources à Chrome et AGY :

1. **Activation de ZRAM (Compression en RAM pour éviter le disque mécanique)** :
   Ouvrir un terminal local et exécuter :
   ```bash
   sudo apt update && sudo apt install -y zram-tools
   ```
   Éditer `/etc/default/zramswap` en sudo, puis ajouter/modifier ces lignes :
   ```
   ALGO=zstd
   PERCENT=30
   ```
2. **Réglage de la Swappiness (Spécifique ZRAM)** :
   Pour éviter que le kernel n'écrive sur le HDD, la swappiness avec ZRAM doit être haute :
   ```bash
   sudo nano /etc/sysctl.conf
   # Ajouter la ligne suivante à la fin du fichier :
   vm.swappiness=100
   vm.vfs_cache_pressure=50
   ```
3. **Appliquer les paramètres** :
   ```bash
   sudo sysctl -p
   sudo systemctl restart zramswap
   ```
4. **Limitation de l'empreinte Chrome** :
   - Dans Google Chrome, aller dans **Paramètres > Performances**.
   - Activer le mode **Économiseur de mémoire** (libère la RAM des onglets inactifs).
   - Fermer strictement tous les onglets hors `aistudio.google.com` lors des sessions de prototypage.

---

## ÉTAPE 2 : PRÉPARATION DU WORKSPACE LOCAL ET AGY CLI

L'exécution locale du code cloud doit être ultra-légère (pas de Docker sur le HDD MIDGARD).

1. **Installer Neovim/Helix, Python 3.10 et les outils de sécurité (sans Docker)** :
   ```bash
   sudo apt install -y neovim python3.10 python3.10-venv python3-pip git
   pip3 install bandit requests
   ```
2. **Initialiser la structure de projet dans le dépôt local** :
   ```bash
   mkdir -p ~/bifrost/tesla/scripts ~/bifrost/tesla/src
   ```
3. **Créer la configuration Antigravity (Isolation légère via venv)** :
   Créer le fichier `~/bifrost/tesla/agy-workspace.yaml` :
   ```yaml
   version: "1.2.7"
   workspace: "midgard-ai-sandbox"
   execution:
     runtime: "python3.10"
     isolation: "venv"    # ⚠️ Correction PREMORTEM : Venv au lieu de Docker pour préserver le HDD
     entrypoint: "src/generated_main.py"
   hooks:
     pre_flight: "./scripts/validate-and-deps.sh"
     post_flight: "./scripts/cleanup.sh"
   ```
4. **Créer le Hook de validation sécurité (Vigilum Codex)** :
   Créer le fichier `~/bifrost/tesla/scripts/validate-and-deps.sh` :
   ```bash
   #!/bin/bash
   echo "[MIDGARD] Validation statique par Bandit..."
   bandit -r ./src/ || { echo "[MIDGARD] Code rejeté par sécurité (Fail-Closed)"; exit 1; }
   if [ -f "requirements.txt" ]; then 
       pip install -r requirements.txt
   fi
   ```
5. **Rendre le script exécutable** : 
   ```bash
   chmod +x ~/bifrost/tesla/scripts/validate-and-deps.sh
   ```

---

## ÉTAPE 3 : INITIALISATION CLOUD (GOOGLE AI STUDIO)

1. Ouvrir Google Chrome et naviguer vers `https://aistudio.google.com`.
2. Se connecter avec le compte de l'écosystème Tesla.
3. Générer et copier la clé API Gemini de production.
4. Exporter la clé API dans l'environnement MIDGARD pour que AGY puisse l'exploiter :
   ```bash
   echo 'export GEMINI_API_KEY="VOTRE_CLÉ_API"' >> ~/.bashrc
   source ~/.bashrc
   ```

---

## ÉTAPE 4 : PIPELINE DE RAPATRIEMENT GIT ET EXÉCUTION

Ceci est le flux de travail régulier pour migrer le code d'AI Studio vers MIDGARD, validé par Tesla-Github-Manager.

1. **Sécurisation du Working Tree (Correction PREMORTEM)** :
   Avant de rapatrier du code, s'assurer que l'environnement local est synchronisé sans écraser le travail en cours.
   ```bash
   cd ~/bifrost/tesla
   git stash
   git checkout develop
   git pull origin develop
   ```
2. **Création de la branche éphémère** :
   ```bash
   git checkout -b feature/ai-studio-integration
   ```
3. **Rapatriement Manuel du Code (Zéro Ambiguïté)** :
   - Depuis Google AI Studio (dans Chrome), copier le code du prototype validé.
   - Ouvrir Neovim ou Helix dans le terminal : `nvim src/generated_main.py`.
   - Coller le code copié, sauvegarder et quitter l'éditeur.
4. **Orchestration et Scan Sécurité via AGY** :
   Lancer AGY pour exécuter les hooks (`validate-and-deps.sh`) et déclencher l'environnement virtuel.
   ```bash
   agy run
   ```
   *(Si `bandit` détecte une faille, AGY bloquera l'exécution (Fail-Closed). Le code devra être corrigé dans Neovim).*
5. **Validation et Commit (Vigilum Codex)** :
   Une fois l'exécution réussie, certifier l'intégration dans Git.
   ```bash
   git add src/generated_main.py
   git commit -m "feat(cloud-sync): rapatriement logique IA depuis AI Studio"
   git push origin feature/ai-studio-integration
   ```

---
*Fin du plan d'intervention. La boucle est sécurisée, déterministe et validée selon la doctrine PREMORTEM contre tout effondrement matériel (I/O Thrashing) de la machine MIDGARD.*
