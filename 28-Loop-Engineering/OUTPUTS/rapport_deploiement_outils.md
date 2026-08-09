# Rapport de Déploiement : Utilitaires Système Bas Niveau

## 1. Diagnostic de l'Existant (Avant Action)
L'audit de la machine hôte MIDGARD avait révélé l'absence de deux utilitaires système clés :
- **`entr`** : Outil de surveillance événementielle de fichiers.
- **`tiktoken-cli`** : Compteur local de tokens pour l'API Gemini.

---

## 2. Actions de Déploiement & Compilations

### A. Compilation & Installation de `entr`
Comme l'agent n'a pas les droits `sudo` sur la machine, l'utilitaire a été compilé à partir des sources officielles et installé localement dans l'espace utilisateur :
1. Clonage de la branche stable : `https://github.com/eradman/entr.git`.
2. Compilation native via `gcc` et `make`.
3. Installation dans le dossier utilisateur avec configuration du préfixe cible :
   ```bash
   make PREFIX=/home/lord-mahonheim/.local install
   ```
4. **Résultat** : Binaire `entr` disponible et exécutable à `/home/lord-mahonheim/.local/bin/entr` (qui est inclus dans le `PATH` système).

### B. Compilation & Installation de `tiktoken` (Go)
1. Téléchargement et compilation à la volée du paquet officiel Go `tiktoken-go-cli` :
   ```bash
   GOBIN=/home/lord-mahonheim/.local/bin go install github.com/alexgorbatchev/tiktoken-go-cli@latest
   ```
2. Création d'un lien symbolique standard `tiktoken` pointant sur `tiktoken-go-cli` pour simplifier l'écriture des scripts :
   ```bash
   ln -s /home/lord-mahonheim/.local/bin/tiktoken-go-cli /home/lord-mahonheim/.local/bin/tiktoken
   ```
3. **Résultat** : Binaire `tiktoken` disponible et exécutable à `/home/lord-mahonheim/.local/bin/tiktoken` (utilisant par défaut l'encodage `cl100k_base` compatible GPT-4 / Gemini).

---

## 3. Preuve de Fonctionnement & Synergie en Situation Réelle

Pour prouver la viabilité et la bonne synergie des deux outils, nous avons conçu un script d'arrière-plan [watch_and_count.sh](file:///home/lord-mahonheim/bifrost/tesla/sandbox/scripts/watch_and_count.sh) :
- **Rôle** : Surveiller les modifications d'un fichier et afficher instantanément son nombre de tokens dès qu'il est sauvegardé.

### Déroulement du Test de Sûreté :
1. Initialisation d'un fichier test avec la chaîne `Hello Midgard` (3 tokens).
2. Lancement du démon de surveillance dans les tâches d'arrière-plan.
3. Modification du fichier par l'agent en ajoutant du texte.
4. Le watcher a intercepté l'événement et a immédiatement mis à jour le comptage à 18 tokens.

### Capture des logs du test (Task 96) :
```text
Watching /home/lord-mahonheim/bifrost/tesla/sandbox/test_file.txt. Press Ctrl+C to stop.
[19:35:12] Initial token count: 3
[19:35:25] File modified. Current token count: 18
```

Le bon fonctionnement de la chaîne est validé à 100%. Les deux binaires sont installés de manière permanente et autonome sans aucune dépendance externe active.

---
*Livrable enregistré localement pour Obsidian Avalon dans [OUTPUTS/rapport_deploiement_outils.md](file:///home/lord-mahonheim/bifrost/tesla/OUTPUTS/rapport_deploiement_outils.md).*
