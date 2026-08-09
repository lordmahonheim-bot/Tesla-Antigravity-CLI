---
type: reference
tags: [securite/premortem, statut/valide]
source: "[[ARCHITECTURE HYBRIDE POUR ALEXANDRIA.txt]]"
date: 2026-06-27
version: 1.0
---

# RAPPORT D'AUDIT PREMORTEM : ARCHITECTURE HYBRIDE POUR ALEXANDRIA
**Date de l'audit :** 2026-06-27  
**Analyste :** Tesla (sur Antigravity CLI)  
**Destinataire :** Mahonheim (Abdellah MOUHTAJ)

---

## 1. Postulat de l'Échec Virtuel (T+3 Mois)

> [!WARNING]
> Nous sommes le **2026-09-27**. 
> Le plan **Architecture Hybride pour Alexandria** a été déployé il y a trois mois. C'est aujourd'hui un **échec total et catastrophique**. 
> Les systèmes locaux sont corrompus ou hors-service. Obsidian subit des freezes permanents dus à des conflits d'indexation géants, l'espace de stockage de la machine MIDGARD s'est dégradé en raison de fichiers d'embeddings résiduels non purgés, les requêtes sémantiques renvoient des résultats totalement désalignés par rapport aux fichiers physiques réels, et la recherche hybride est devenue inutilisable à cause de l'incohérence absolue des bases de données.
> 
> Voici la reconstitution historique objective des causes et mécanismes de ce naufrage technique.

---

## 2. Reconstitution Narrative de la Catastrophe

L'effondrement s'est produit en trois phases distinctes suite au déploiement initial :

1. **La Phase d'Incohérence Initiale (Semaine 1) :**
   Le déploiement a été initié en supposant l'existence d'une base nommée `alexandria_master.db` dans un répertoire inexistant `alexandria/database/`. Le script a donc créé une base SQLite vide à cet endroit. Pendant ce temps, le système Obsidian et le dashboard Dataview de Mahonheim continuaient de lire la véritable base `/home/lord-mahonheim/bifrost/tesla/Avalon/03-Resources/alexandria_brain.db`. La double indexation n'a jamais ciblé la base réelle, créant un désalignement total des outils dès le premier jour.

2. **La Dérive de l'Indexation et Pollution Sémantique (Semaines 2 à 4) :**
   En raison de la génération d'un `UUIDv4` aléatoire à chaque passage de l'indexeur sur les fichiers Markdown, chaque modification d'une fiche (correction d'une simple coquille, mise à jour d'un statut) a généré de nouveaux UUID. ChromaDB a accumulé les anciens vecteurs des anciennes versions des documents comme s'il s'agissait de documents distincts. Sans mécanisme de réconciliation sémantique ni de purge des vecteurs orphelins, la base ChromaDB a gonflé de manière exponentielle, polluant les résultats avec des fragments obsolètes.

3. **L'Asphyxie Matérielle et Effondrement Mathématique (Mois 2 et 3) :**
   À mesure que le volume de fiches et de codes augmentait, l'inférence CPU non incrémentale (réindexation complète de tous les fichiers à chaque exécution de `indexer_hybrid.py`) est devenue si lente qu'elle monopolisait 100% du CPU de MIDGARD pendant de longues minutes. Le calcul naïf de la fusion des scores par somme linéaire ($Score_{hybride} = 0.5 \cdot BM25 + 0.5 \cdot Cosine$) s'est effondré : le score BM25 (non borné, pouvant atteindre plus de 20 ou 30) a complètement écrasé le score de distance Cosinus (limité entre 0 et 2). La recherche est devenue purement lexicale, rendant ChromaDB totalement inutile malgré la consommation de ressources.

---

## 3. Analyse Tripartite des Risques (Gary Klein Model)

### A. L'Avocat du Diable (Causes Techniques & Factuelles)

* [ ] **Facteur 1 : Incohérence des Chemins et de la Taxonomie**
  Le plan cible `alexandria/database/alexandria_master.db` alors que la base de données de production active, sanctuarisée par le Vigilum Codex, est [alexandria_brain.db](file:///home/lord-mahonheim/bifrost/tesla/Avalon/03-Resources/alexandria_brain.db).
* [ ] **Facteur 2 : Le Faux Alignement Pivot UUIDv4**
  L'utilisation d'un `UUIDv4` purement dynamique/aléatoire interdit tout alignement persistant lors de modifications. Le système ne dispose d'aucun index unique stable (ex: chemin relatif du fichier + index du chunk) permettant de faire des `upsert` sémantiques ou de purger les chunks supprimés.
* [ ] **Facteur 3 : Normalisation Naïve et Rupture Mathématique**
  Les scores BM25 de SQLite FTS5 ne sont pas bornés et dépendent de la fréquence du terme dans le document. Les sommer directement avec des distances cosinus (bornées) sans normalisation min-max dynamique ou algorithme de fusion de rangs (RRF) fausse complètement le classement hybride.
* [ ] **Facteur 4 : Conflits de Synchronisation Obsidian**
  Placer le répertoire `.chroma_vectors/` directement sous un dossier synchronisé par Obsidian ou Git sans règle d'exclusion stricte entraîne l'indexation de milliers de fichiers de base de données binaires de Chroma, provoquant des conflits d'accès et des ralentissements système.

### B. L'Inspecteur des Angles Morts (Hypothèses Cachées non Validées)

* **Hypothèse non vérifiée 1 :** *L'indexation complète est toujours viable.* Le plan suppose que la réindexation de tous les fichiers du second cerveau peut se faire à la volée. En réalité, sans indexation incrémentale (basée sur le hash du fichier ou la date `last_modified`), le temps d'inférence CPU bloque le système dès que le vault dépasse quelques centaines de fiches.
* **Hypothèse non vérifiée 2 :** *ChromaDB libère proprement la mémoire en in-process.* Bien que ChromaDB soit initialisé avec un `PersistentClient` en Python, les objets PyTorch et le modèle d'embeddings `all-MiniLM-L6-v2` restent chargés en mémoire tant que le processus Python hôte n'est pas détruit. Si l'indexation est appelée au sein d'un wrapper à longue durée de vie, la RAM de 8 Go de MIDGARD sera saturée.
* **Hypothèse non vérifiée 3 :** *L'environnement Python global supporte l'installation.* Le plan propose `pip install chromadb sentence-transformers --no-cache-dir` sans cibler explicitement l'environnement virtuel (`.venv`) local du projet, ce qui risque de casser des dépendances système de MIDGARD.

### C. La Vigie des Signaux Faibles (Indicateurs Précurseurs)

1. **Signal 1 :** Augmentation continue de la taille du répertoire `.chroma_vectors/` disproportionnée par rapport au nombre réel de fiches Obsidian (signe d'accumulation de résidus orphelins).
2. **Signal 3 :** Écrasement systématique des résultats sémantiques par les résultats textuels lors de requêtes contenant des mots-clés spécifiques (signe d'un déséquilibre de l'échelle des scores BM25).
3. **Signal 4 :** Apparition d'alertes LSP (Pyright) dans le script `search_router.py` en raison de l'utilisation de types non déclarés ou d'API obsolètes de ChromaDB.

---

## 4. Plan de Résilience & Checklist de Prévention

Pour optimiser et corriger le plan d'architecture initial, les modifications et contre-mesures obligatoires suivantes doivent être intégrées :

| Risque Identifié | Action Préventive Obligatoire | Indicateur de Déclenchement (Seuil) |
| :--- | :--- | :--- |
| **Incohérence de Base SQLite** | Rediriger les scripts vers [alexandria_brain.db](file:///home/lord-mahonheim/bifrost/tesla/Avalon/03-Resources/alexandria_brain.db) et la table virtuelle `fts_vault_index`. | Immédiat (Dès l'écriture du code) |
| **Doublons/Orphelins de Vecteurs** | Générer un identifiant de fragment déterministe sous la forme `hash(filepath + chunk_index)` ou `UUIDv5` basé sur le chemin relatif, permettant l'Upsert automatique dans ChromaDB. | Immédiat (Dans le script `indexer_hybrid.py`) |
| **Saturation CPU/Temps d'Indexation** | Implémenter une indexation incrémentale en comparant le timestamp de dernière modification (`last_modified`) de chaque fichier avec la base SQLite avant de réindexer. | Dès que le volume de fichiers > 100 fiches |
| **Déséquilibre de Fusion des Scores** | Remplacer la somme linéaire naïve par l'algorithme **Reciprocal Rank Fusion (RRF)** ou par une normalisation Min-Max dynamique sur le top-K des résultats. | Immédiat (Dans le script `search_router.py`) |
| **Pollution et conflits Git/Obsidian** | Placer le répertoire de cache Chroma (ex: `.chroma_vectors/`) dans les dossiers exclus par Obsidian et listés dans `.gitignore`. | Immédiat (Configuration du projet) |

### Checklist de Sûreté Pré-Exécution :
- [ ] **Alignement des Emplacements :** Vérifier que le chemin de la base SQLite pointe sur `Avalon/03-Resources/alexandria_brain.db`.
- [ ] **Sanité des Dépendances :** Installer les paquets Python exclusivement dans l'environnement virtuel du projet via `.venv/bin/pip install chromadb sentence-transformers`.
- [ ] **Validation LSP :** Le code de `indexer_hybrid.py` et `search_router.py` doit être vérifié par `pyright-lsp` avec 0 erreur avant tout stress-test.
- [ ] **Vérification de la Purge :** Développer un mécanisme de détection des fichiers supprimés physiquement pour purger de manière équivalente les entrées dans SQLite FTS5 et dans ChromaDB.

---

## 5. Spécifications du Code Corrigé et Amélioré

### A. Algorithme de Recherche Hybride avec Fusion par Rangs (RRF)
Pour fusionner de manière optimale les résultats lexicaux de FTS5 et sémantiques de ChromaDB, nous utilisons la formule RRF suivante pour chaque document $d$ apparaissant dans les résultats :

$$RRF\_Score(d) = \sum_{m \in M} \frac{1}{k + rank_m(d)}$$

Où $M = \{lexical, semantique\}$, $rank_m(d)$ est le rang du document $d$ dans le moteur $m$ (1-indexed), et $k$ est une constante de lissage standardisée (généralement $k = 60$). Cette méthode garantit un classement stable sans subir l'échelle arbitraire des scores BM25 ou Cosine.

### B. Indexation Incrémentale et Clef Pivot Déterministe
- **ID Unique :** `f"{rel_path}#chunk_{chunk_index}"` ou son hachage MD5/SHA256.
- **Processus :**
  1. Lire `last_modified` du fichier Markdown sur le disque.
  2. Comparer avec le champ `last_modified` stocké dans `fts_vault_index` pour ce fichier.
  3. Si inchangé, ignorer.
  4. Si modifié ou nouveau, segmenter en chunks, supprimer l'ancien index du fichier sémantique/lexical (par requête d'effacement sur `filepath`), et insérer les nouveaux chunks.
  5. Si un fichier n'existe plus sur le disque, exécuter une suppression en cascade sur SQLite et ChromaDB.

---
*Rapport généré et validé localement sur MIDGARD par Tesla.*

Signé / Fait par : Tesla sur Antigravity CLI  
Main rendue à Mahonheim
