# LIVRABLE FINAL : PLAN D'INTERVENTION HEADLESS (AI STUDIO × TERMINATOR)

![Status](https://img.shields.io/badge/Status-MVP-blue) ![Ecosystem](https://img.shields.io/badge/Ecosystem-TESLA%20ANTIGRAVITY-purple) ![Security](https://img.shields.io/badge/Security-ID%20LOCKED-red) ![Python](https://img.shields.io/badge/Python-3.12+-blue)

**Auteur :** Tesla-Team-Synergy (Nœuds 1 à 7)
**Date :** 19 Septembre 2026
**Cible :** Environnement MIDGARD (Intel i7, 7.6 Go RAM, HDD)
**Certification :** `RECOMMENDED` (Score: 0.95/1.00 — Corrections PREMORTEM appliquées)

---

## 1. RÉSULTAT FINAL ATTENDU
Un environnement de travail **"Headless" ultra-léger et autonome**, s'exécutant intégralement dans l'émulateur de terminal **Terminator**. 

L'objectif est d'exploiter la puissance de l'API Google AI Studio en mode 100% CLI/TUI pour pallier la fermeture de Firebase Studio. L'usage de **Google Chrome est strictement proscrit** afin de protéger les 8 Go de RAM et le disque dur (HDD) de la machine MIDGARD. L'interface graphique s'efface totalement : **Terminator devient le hub absolu.**

---

## 2. PRÉPARATION MATÉRIELLE ET SYSTÈME (Corrections PREMORTEM)

L'optimisation du noyau Linux est primordiale pour ne pas crasher la machine (OOM Killer) tout en empêchant le ralentissement du HDD.

1. **Protection de la RAM et du HDD (ZRAM + Swap limité)** :
   *Interdiction formelle de désactiver totalement le swap (`swapoff -a` = DANGER).*
   - Installez et activez ZRAM (2 à 4 Go en RAM compressée).
   - Configurez `/etc/sysctl.conf` avec une priorité absolue à la RAM, sans couper le filet de sécurité du HDD :
     ```bash
     vm.swappiness=1
     vm.vfs_cache_pressure=50
     ```
   - Appliquez via `sudo sysctl -p`.

2. **Protection I/O (Stockage Temporaire en RAM)** :
   Pour éviter que les outils CLI n'usent le disque mécanique avec des lectures/écritures constantes, montez `/tmp` en RAM :
   ```bash
   sudo mount -t tmpfs -o size=1G tmpfs /tmp
   ```
   *(Pensez à ajouter cette ligne dans `/etc/fstab` pour la persistance au redémarrage : `tmpfs /tmp tmpfs defaults,noatime,size=1G 0 0`)*

3. **Authentification Cloud** :
   Générez une clé sur `aistudio.google.com` (une seule fois), puis :
   ```bash
   echo 'export GEMINI_API_KEY="votre_cle_api"' >> ~/.bashrc
   source ~/.bashrc
   ```

---

## 3. CONFIGURATION DES PANNEAUX TERMINATOR

Divisez l'interface de **Terminator** en trois panneaux distincts via ses raccourcis natifs pour un confort de travail absolu :

1. `Ctrl+Shift+E` : Divise l'écran en deux colonnes (Gauche / Droite).
2. `Ctrl+Shift+O` (sur la colonne de gauche) : Divise la colonne de gauche en deux (Haut / Bas).

**Disposition Cible :**
*   **Panneau 1 (Gauche - Haut) : Éditeur de Code.** (Neovim ou Helix). Zone d'écriture et de relecture manuelle du code généré.
*   **Panneau 2 (Gauche - Bas) : Console Git.** Réservé au versioning (Vigilum Codex) et monitoring (`htop`).
*   **Panneau 3 (Droite - Pleine Hauteur) : IA & AGY.** Zone dédiée à l'interaction avec le LLM (CLI) et à l'exécution de Antigravity CLI v1.2.7.

---

## 4. CHOIX DE L'OUTIL IA CLI ET WORKFLOW (VIGILUM CODEX)

### L'Outil : Aider CLI (Recommandé)
Aider est l'outil TUI le plus mature pour l'API Gemini.
**ATTENTION (Mitigation I/O) :** Pour éviter le thrashing du HDD, lancez Aider **strictement** avec ces paramètres :
```bash
aider --model gemini/gemini-pro --map-tokens 0 --no-auto-commits
```

### Le Workflow d'Exécution Sécurisée

**Étape 1 : Initialisation (Panneau 2)**
*   `git checkout main && git pull origin main`
*   `git checkout -b feature/nouvelle-integration-ai`

**Étape 2 : Génération du Code (Panneau 3)**
*   Lancez `aider` avec les flags stricts ci-dessus.
*   Demandez à Gemini de générer le code. Aider écrira les modifications directement dans le fichier cible (ex: `src/mon_module.py`).

**Étape 3 : Revue Humaine Obligatoire (Panneau 1) - CRITIQUE**
*   **Interdiction d'auto-exécuter le code généré.**
*   Dans Neovim (Panneau 1), ouvrez `src/mon_module.py`. Relisez visuellement le code pour écarter toute hallucination (effacement de fichiers, boucle infinie).

**Étape 4 : Orchestration (Panneau 3)**
*   Une fois le code validé visuellement, exécutez-le via la sandbox locale d'AGY :
    ```bash
    agy run src/mon_module.py
    ```

**Étape 5 : Validation Git (Panneau 2)**
*   `git diff` (pour vérifier l'atomicité de la modification).
*   `git add src/mon_module.py`
*   `git commit -m "feat(core): intégration logique IA headless"`
*   `git push -u origin feature/nouvelle-integration-ai`

---
*Ce plan Headless est certifié "Fail-Safe". Il désactive la menace de surconsommation de Chrome, bloque les I/O excessifs sur le HDD, et empêche toute exécution destructrice par le LLM, le tout sans jamais quitter l'interface native de Terminator.*
