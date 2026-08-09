---
type: reference
tags: [securite/premortem, statut/valide]
source: "[[DÉPLOIEMENT DU ROUTEUR DE RECHERCHE HYBRIDE RRF POUR ALEXANDRIA.md]]"
date: 2026-06-27
version: 1.0
---

# RAPPORT D'AUDIT PREMORTEM : ROUTEUR DE RECHERCHE HYBRIDE RRF
**Date de l'audit :** 2026-06-27  
**Analyste :** Tesla (sur Antigravity CLI)  
**Destinataire :** Mahonheim (Abdellah MOUHTAJ)

---

## 1. Postulat de l'Échec Virtuel (T+3 Mois)

> [!WARNING]
> Nous sommes le **2026-09-27**. 
> Le plan **Déploiement du Routeur de Recherche Hybride RRF pour Alexandria** a été exécuté il y a trois mois. C'est aujourd'hui un **échec complet**.
> Les requêtes envoyées au routeur échouent systématiquement en retournant des listes vides ou en provoquant des crashes silencieux de l'interface CLI. Aucun document pertinent n'est récupéré, la table FTS5 est inaccessible et les performances CPU de la machine locale MIDGARD se dégradent en raison d'instances dupliquées du modèle d'embeddings lors de l'exécution concurrente.
> 
> Voici la reconstitution chronologique et l'analyse post-accidentelle de ce naufrage d'ingénierie.

---

## 2. Reconstitution Narrative de la Catastrophe

L'échec s'est propagé selon l'enchaînement d'événements suivant :

1. **La Rupture des Chemins Relatifs (Jour 1) :**
   Le script `search_router.py` a été déployé sous `/home/lord-mahonheim/bifrost/tesla/core/search_router.py`. Le calcul de son répertoire de base s'est fait via `BASE_DIR = os.path.dirname(os.path.abspath(__file__))`, soit `/home/lord-mahonheim/bifrost/tesla/core`. Il a donc cherché SQLite et ChromaDB dans `/home/lord-mahonheim/bifrost/tesla/core/database/`, alors que l'indexeur hybride `indexer_hybrid.py` les avait déployés dans `/home/lord-mahonheim/bifrost/tesla/database/`. Le routeur a créé des répertoires et des bases vides, renvoyant systématiquement 0 résultat à Mahonheim.

2. **Le Blocage Lexical FTS5 sur Caractères Spéciaux (Semaine 2) :**
   Lors de recherches complexes intégrant des opérateurs de code ou des expressions régulières (ex: `*`, `()`, `-`), le moteur FTS5 de SQLite a levé des exceptions de syntaxe de type `sqlite3.OperationalError`. Le script d'origine se contentait de rattraper l'exception en retournant une liste vide. La recherche sémantique ChromaDB fonctionnait encore, mais la recherche hybride est devenue tronquée et instable, masquant les résultats exacts de mots-clés de code.

3. **Le Crash de ChromaDB non Initialisé (Mois 1) :**
   Lors du redémarrage du système ou de l'ajout d'un nouvel utilisateur, la première requête de recherche sémantique a été exécutée avant le premier lancement du script d'indexation. La méthode `chroma_client.get_collection(name="alexandria_vault")` a levé une exception car la collection n'existait pas encore physiquement sur le disque. Sans bloc de gestion d'erreur, le script s'est arrêté brutalement, crashant l'interface CLI d'Antigravity.

---

## 3. Analyse Tripartite des Risques (Gary Klein Model)

### A. L'Avocat du Diable (Causes Techniques & Factuelles)

* [ ] **Facteur 1 : Mauvaise Résolution du Dossier Parent**
  Le script utilise `os.path.dirname(__file__)` pour localiser `database/`. S'il est placé dans `core/`, son parent direct est `core/` et non le dossier racine `/home/lord-mahonheim/bifrost/tesla/`, créant une base de données dupliquée et vide.
* [ ] **Facteur 2 : Erreur de Syntaxe FTS5 non Tolérante**
  L'algorithme de nettoyage de requête se limite à remplacer le guillemet simple par un espace. La présence d'autres caractères syntaxiques de FTS5 (ex: `*`, `NEAR`, `OR`) continue de lever des exceptions d'analyse (`sqlite3.OperationalError`), renvoyant un tableau de résultats vides.
* [ ] **Facteur 3 : Absence de Gestion de Collection Inexistante**
  L'appel à `get_collection` part du principe que l'index sémantique existe toujours. Si la base est corrompue, purgée ou vierge, le script crash immédiatement au lieu de proposer un fallback gracieux ou de rediriger vers l'indexation.

### B. L'Inspecteur des Angles Morts (Hypothèses Cachées non Validées)

* **Hypothèse non vérifiée 1 :** *Les listes de sortie de ChromaDB sont toujours synchrones.* Le code suppose que `ids`, `documents` et `metadatas` de la recherche sémantique ont exactement la même taille et les mêmes indices. En cas de corruption partielle de l'index de ChromaDB, cela peut générer un `IndexError: list index out of range` lors de l'accès à `metadatas[rank - 1]`.
* **Hypothèse non vérifiée 2 :** *ChromaDB retourne toujours un dictionnaire valide.* Si la recherche ne retourne aucun résultat, `results["ids"]` peut contenir une liste vide `[[]]`, ce qui passe le test initial `semantic_results["ids"]` mais peut faire crasher le code si on accède de manière non sécurisée à ses indices.

### C. La Vigie des Signaux Faibles (Indicateurs Précurseurs)

1. **Signal 1 :** Retour systématique de résultats sémantiques purs (0 résultat lexical FTS5) pour des termes contenant des caractères spéciaux ou de la syntaxe SQL/Python.
2. **Signal 2 :** Temps de démarrage excessifs du routeur de recherche hybride causés par le chargement du modèle HuggingFace à chaque nouvelle requête isolée.
3. **Signal 3 :** Création d'un dossier parasite `core/database/` en plus du répertoire `database/` officiel à la racine du projet.

---

## 4. Plan de Résilience & Checklist de Prévention

Pour optimiser et corriger le plan du routeur, les actions préventives obligatoires suivantes doivent être intégrées au plan initial :

| Risque Identifié | Action Préventive Obligatoire | Indicateur de Déclenchement (Seuil) |
| :--- | :--- | :--- |
| **Désalignement des Chemins** | Ajuster `DB_PATH` et `CHROMA_DIR` pour pointer sur le répertoire parent de `core/` (la racine). | Immédiat (Dès l'écriture du code) |
| **Crash de Collection Manquante** | Encapsuler l'accès à la collection Chroma dans un bloc `try/except` retournant un avertissement clair et un fallback lexical pur. | Immédiat (Dans le script `search_router.py`) |
| **Erreurs de syntaxe FTS5** | Ajouter un filtre de nettoyage robuste (Regex alphanumérique) en fallback automatique si le MATCH initial échoue. | Immédiat (Dans le script `search_router.py`) |
| **Accès Index Chroma Hors-Limites** | Valider la taille des tableaux de ChromaDB (`ids`, `documents`, `metadatas`) avant tout accès par index dans la boucle RRF. | Immédiat (Dans la fonction `compute_rrf`) |

### Checklist de Sûreté Pré-Exécution :
- [ ] **Alignement des Chemins Physiques :** S'assurer que le script résout `/home/lord-mahonheim/bifrost/tesla/database/alexandria_brain.db` et non `/home/lord-mahonheim/bifrost/tesla/core/database/`.
- [ ] **Fallback de Collection :** Tester le comportement de la recherche hybride lorsque le répertoire Chroma est absent (doit s'exécuter en mode lexical pur sans crasher).
- [ ] **Audit Statique Pyright :** Le code révisé de `search_router.py` doit passer sous Pyright avec 0 erreur.

---
*Rapport généré et validé localement sur MIDGARD par Tesla.*

Signé / Fait par : Tesla sur Antigravity CLI  
Main rendue à Mahonheim
