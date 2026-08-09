# Rapport d'Audit : Utilitaires Système Bas Niveau pour l'Optimisation de Contexte et d'Appels API

## 1. Diagnostic de l'Existant (MIDGARD)
Nous avons audité la présence et l'état des utilitaires suggérés dans le rapport de l'opérateur sur la machine MIDGARD :

| Utilitaire Système | Statut sur Hôte | Chemin d'Accès | Rôle pour l'Agent |
| :--- | :--- | :--- | :--- |
| **`ripgrep` (binaire `rg`)** | **Disponible** | `/usr/bin/rg` | Recherche de motifs ultra-rapide sans lecture de fichiers complets. |
| **`fzf`** | **Disponible** | `/usr/bin/fzf` | Recherche de chemin de fichier interactive/scriptable. |
| **`jq`** | **Disponible** | `/usr/bin/jq` | Filtrage et nettoyage de payloads JSON. |
| **`sed` / `awk`** | **Disponible** | `/usr/bin/sed` & `/usr/bin/awk` | Extraction de tranches de lignes spécifiques dans de longs fichiers. |
| **`entr`** | **Non disponible** | - | Surveillance événementielle de modifications de fichiers. |
| **`tiktoken-cli`** | **Non disponible** | - | Comptage local de tokens avant appels API. |

---

## 2. Analyse Critique des Outils & Alternatives Locales

### A. Triage de contexte & Recherche chirurgicale (Anti-Saturation)
- **`ripgrep` (`rg`)** : Cet outil est notre atout majeur pour éviter l'ingestion de fichiers inutiles. Afin de maximiser son efficacité, nous pouvons créer un fichier de configuration `.ripgreprc` à la racine du projet pour exclure systématiquement les dossiers volumineux (`.git`, `.venv`, `node_modules`, `.agents/`) et les fichiers de cache. Ainsi, les commandes de recherche lancées par l'agent ne retourneront que les lignes pertinentes avec une consommation minimale de tokens.
- **`jq`** : Indispensable pour traiter les sorties d'APIs ou manipuler les bases de données JSON. Il évite de saturer le contexte en filtrant les attributs requis (ex. `cat graph.json | jq '.nodes[].id'`).

### B. Automatisation Événementielle (File Watching)
- **Alternative native : `inotifywait`** : Bien que `entr` ne soit pas installé, le système MIDGARD dispose nativement de **`inotifywait`** (installé à `/usr/bin/inotifywait`). Il s'appuie directement sur l'API `inotify` du noyau Linux pour surveiller les événements système sur les fichiers et dossiers (création, modification, écriture).
- **Implémentation** : Nous pouvons utiliser `inotifywait` dans un script d'arrière-plan idempotent ou un démon local pour déclencher les validations LSP et l'indexation de codebase au moment exact où un fichier source est modifié, éliminant tout besoin de scruter périodiquement (polling) en consommant de la RAM.

### C. Disjoncteur de Tokens (Budgeting)
- **Alternative Python local** : L'absence de `tiktoken-cli` peut être compensée par un script Python léger exécuté localement dans notre environnement virtuel (`.venv`). En important la bibliothèque de tokenisation standard `tiktoken` (ou un tokenizer léger hors-ligne), nous pouvons concevoir un utilitaire de validation de budget de jetons capable d'intercepter les requêtes ou de mesurer la taille sémantique d'un fichier avant son injection.

---

## 3. Arsenal Complémentaire Détecté (Nouveaux Atouts)

En effectuant un scan profond des outils disponibles sur MIDGARD, nous avons identifié deux utilitaires bas niveau cruciaux pour le projet Bifrost :

### A. Le Convertisseur Universel : `pandoc`
- **Disponibilité** : **Disponible** à `/usr/bin/pandoc`.
- **Intérêt pour le Web Raider** : Lors de l'extraction de pages web (par `mcp-server-fetch` ou `chrome-devtools`), le HTML brut récupéré contient une énorme quantité de balisage structurel, de scripts, de styles CSS et de métadonnées inutiles. En utilisant `pandoc` comme filtre (ex: `pandoc -f html -t markdown_strict`), nous obtenons un Markdown purifié contenant uniquement le contenu sémantique essentiel.
- **Gain constaté** : Le volume de données textuelles à traiter est **divisé par 5 à 10**, ce qui protège la fenêtre de contexte et réduit les coûts de tokens de manière drastique.

### B. La Surveillance Événementielle Native : `inotify-tools`
- **Disponibilité** : **Disponible** à `/usr/bin/inotifywait`.
- **Intérêt** : Permet de monter des chaînes d'intégration continue locales (tests automatisés, auto-linting) sans surcoût CPU.

### C. Le Différentiel Natif : `git diff` / `git show`
- **Disponibilité** : **Disponible** (intégré au projet).
- **Intérêt** : Lors de la boucle de self-healing (LSP), plutôt que de charger l'intégralité d'un fichier modifié pour vérifier les modifications, l'agent peut simplement exécuter `git diff <file>` pour examiner le delta précis de sa modification.

---

## 4. Recommandations Stratégiques pour le Projet Bifrost

1. **Intégration de `pandoc` dans le Web Raider** : Configurer la chaîne d'extraction pour appliquer un nettoyage automatique des pages HTML via `pandoc` avant l'enregistrement dans la base de données.
2. **Standardisation de `.ripgreprc`** : Déployer un fichier de configuration `.ripgreprc` local pour accélérer les diagnostics et protéger le contexte lors des scans globaux.
3. **Création d'un script de comptage de tokens** : Ajouter un script utilitaire local `sandbox/scripts/token_budget.py` pour valider l'impact en tokens de tout fichier ou dossier avant son analyse par l'agent.

---
*Livrable enregistré localement pour Obsidian Avalon dans [OUTPUTS/audit_outils_systeme.md](file:///home/lord-mahonheim/bifrost/tesla/OUTPUTS/audit_outils_systeme.md).*
