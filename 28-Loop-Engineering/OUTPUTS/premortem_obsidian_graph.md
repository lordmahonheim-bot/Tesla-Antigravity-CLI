# Rapport Premortem : Graphe Obsidian et Pipeline d'Ingestion

## 1. Analyse des Risques

### 1.1 Surcharge Sémantique (Semantic Bloat)
- **Symptôme :** Génération de nœuds trop granulaires, redondants ou triviaux lors du parsing par Gemini (ex: création de notes distinctes pour "API Gemini", "Gemini API", "Intégration Gemini").
- **Impact :** Le graphe devient un "bruit" illisible, perd son utilité décisionnelle et la pertinence du RAG (Retrieval-Augmented Generation) chute drastiquement.
- **Contrainte :** Mettre en place un mécanisme de déduplication strict et un dictionnaire d'alias canoniques (via la clé `aliases` du YAML). Imposer un seuil de pertinence minimum à l'LLM avant de justifier la création d'un nouveau nœud conceptuel.

### 1.2 Boucles Infinies de Wikilinks
- **Symptôme :** Références circulaires incontrôlées générées organiquement par le LLM (ex: `Nœud A` pointe vers `Nœud B` qui pointe vers `Nœud A`).
- **Impact :** Plantage des moteurs de recherche du RAG ou du graphe lors de la résolution du contexte (traversée de nœuds infinie), provoquant des crashs ou une consommation CPU/mémoire critique.
- **Contrainte :** Le RAG et le script d'extraction doivent limiter la profondeur de résolution des liens. La contrainte **Depth=2** doit être imposée en dur lors de la collecte du contexte. Interdire les résolutions récursives non bornées.

### 1.3 Out Of Memory (OOM) et Instabilité ETL
- **Symptôme :** Le chargement de l'ensemble du corpus de transcripts dans le contexte de Gemini pour l'extraction provoque un OOM, ou dépasse la limite de tokens du modèle.
- **Impact :** Échec silencieux ou brutal du script `session_to_graph.py`, entraînant une corruption de la mise à jour des notes et une désynchronisation de l'état du graphe.
- **Contrainte :** Traitement incrémental obligatoire (delta-parsing). Le script d'ingestion ne doit traiter que les nouvelles entrées (par batchs ou chunks) depuis la dernière exécution réussie, plutôt que de re-parser l'historique entier.

## 2. Contraintes Strictes pour le Développement

1. **Limite de Profondeur (Depth Limit) :** Toute traversée du graphe pour générer du contexte RAG est formellement bridée à **Depth=2**.
2. **Création Stricte des Nœuds :** Interdiction absolue de créer des notes vides (placeholders) ou des nœuds spéculatifs. Une note `_MOC/Graph_Nodes` n'est générée que si une entité est clairement définie et possède du contenu substantiel.
3. **Validation Frontmatter :** Le script d'ingestion doit valider rigoureusement le format YAML avant écriture. Tout lien `[[...]]` dans l'en-tête YAML doit être systématiquement encadré de guillemets doubles (`"[[Nom_du_noeud]]"`) sous peine de corrompre le parseur d'Obsidian.
4. **Gestion de l'État ETL :** L'ingestion des transcripts doit reposer sur des pointeurs (timestamps ou hash) pour garantir un traitement différentiel à l'empreinte mémoire maîtrisée, écartant tout risque d'OOM sur les exécutions futures.

## 3. Nœud 4 : Stress-Test Final sur le Code ETL Généré

Après analyse de `session_to_graph.py` et `generate_daily_log.py`, plusieurs risques résiduels critiques ont été identifiés sur l'architecture implémentée :

### 3.1 `session_to_graph.py`
- **Risque d'OOM et de Dépassement de Tokens (Chunking manquant) :** La ligne `text = f.read()` lit tout le fichier en mémoire puis l'envoie en un seul bloc à Gemini. Si un transcript dépasse la fenêtre de contexte de Gemini (ou consomme trop de RAM locale), cela provoquera un crash. *Action requise :* Implémenter un découpage (chunking) du texte avant l'appel à l'API.
- **Absence de Gestion de Rate-Limiting :** Le script itère sur tous les nouveaux fichiers et appelle l'API Gemini sans aucun délai (sleep). Cela va très probablement déclencher une erreur `429 Too Many Requests`. *Action requise :* Ajouter un `time.sleep` ou une gestion des exceptions pour le backoff exponentiel.
- **Collisions de Fichiers (Déduplication basique) :** L'extraction des nœuds nomme simplement le fichier `f"{title}.md"`. Si différents transcripts parlent du même `title`, le fichier sera écrasé avec de nouvelles informations au lieu d'être fusionné, entraînant une perte de données. *Action requise :* Mettre en place une logique de fusion de contenu (append) si le fichier existe déjà.

### 3.2 `generate_daily_log.py`
- **Écrasement du Journal Journalier :** Le script ouvre le fichier en mode écriture `'w'`, écrasant ainsi tout historique si l'ETL est exécuté plusieurs fois dans la même journée. *Action requise :* Passer en mode ajout (`'a'`) ou faire une mise à jour intelligente du fichier.
- **Comptage Erroné des Ingestions :** Le script affiche `len(tracker)` comme nombre de *Transcripts tracked* aujourd'hui. Il s'agit en réalité du nombre total historique de fichiers, pas du delta du jour. *Action requise :* Modifier l'ETL pour retourner le nombre exact de nouveaux fichiers traités aujourd'hui et les passer au script de log.

**Conclusion du Nœud 4 :** L'architecture actuelle n'est pas robuste pour une mise en production (Scale). Les scripts doivent être patchés pour inclure le chunking, la fusion des nœuds existants, et la gestion du rate-limit.
