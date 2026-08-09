---
type: reference
tags: [securite/premortem, statut/valide]
source: "[[Plan-Obsidian-DataBase-Updated]]"
date: 2026-06-27
version: 1.0
---

# RAPPORT D'AUDIT PREMORTEM : PLAN-OBSIDIAN-DATABASE
**Date de l'audit :** 2026-06-27  
**Analyste :** premortem-analyst (Sous-Agent Tesla)  
**Destinataire :** Mahonheim (Abdellah MOUHTAJ)

---

## 1. Postulat de l'Échec Virtuel (T+3 Mois)

> [!WARNING]
> Nous sommes le **2026-09-27**. 
> Le plan **Plan-Obsidian-DataBase** a été déployé il y a trois mois. C'est aujourd'hui un **échec total et catastrophique**. 
> Les systèmes locaux sont corrompus ou hors-service, les performances sont dégradées, les coûts en tokens ont explosé, et la confiance de l'opérateur dans l'agent est rompue.
> 
> Voici la reconstitution historique objective des causes et mécanismes de ce naufrage technique.

---

## 2. Reconstitution Narrative de la Catastrophe

* **Semaine 1 (Début Juillet 2026) - L'Illusion du Succès :** Les dossiers PARA sont créés et le script `sync_brain.py` indexe correctement les premières notes Markdown dans SQLite FTS5. L'accès rapide par terminal avec `fzf` impressionne par sa rapidité. L'opérateur valide et commence à s'appuyer sur l'index de Tesla.
* **Semaine 3 (Mi-Juillet 2026) - L'Engorgement Multiformat :** Phase 1 activée. L'opérateur dépose des audios de réunions de 2 heures et des PDF de livres entiers dans la file d'ingestion. Le pipeline Whisper local et les scripts d'extraction convertissent le tout en fiches miroirs Markdown massives. `sync_brain.py` tente d'insérer ces blocs de texte de plusieurs centaines de milliers de caractères d'un seul coup dans la table SQLite FTS5.
* **Semaine 5 (Fin Juillet 2026) - Les Premiers Locks Système :** La surveillance temps réel par `inotifywait` déclenche des écritures dans la base SQLite à chaque micro-modification. Parallèlement, l'opérateur travaille activement dans Obsidian et Tesla tente d'effectuer des recherches sémantiques. SQLite lève des erreurs critiques `database is locked` à répétition. La base est temporairement inaccessible, bloquant les routines automatiques de Tesla.
* **Semaine 7 (Août 2026) - L'Invasion des Archives Fantômes :** Phase 3 opérationnelle. Lors des modifications, les anciennes versions de notes stratégiques sont renommées et déplacées dans `04-Archives/`. Cependant, le scan récursif de `sync_brain.py` est naïf : il continue d'indexer le dossier `04-Archives/`. Les requêtes FTS5 de Tesla renvoient désormais des résultats pollués par 5 à 10 doublons obsolètes de la même note. Tesla hallucine en s'appuyant sur des règles ou des comptes-rendus périmés. Les coûts en tokens explosent car Tesla ingère des versions obsolètes en double dans son contexte.
* **Semaine 10 (Fin Août 2026) - La Collision Fatale de l'API REST :** L'opérateur modifie un fichier MOC dans Obsidian au moment précis où Tesla tente de le mettre à jour via le serveur MCP Local REST API (à partir d'un index SQLite qui avait manqué des événements de modification). Obsidian écrase les modifications de Tesla, ou Tesla écrase les ajouts manuels de l'opérateur en raison d'une absence de verrou logique partagé. Des données historiques de projets actifs sont irrémédiablement écrasées.
* **Semaine 12 (Mi-Septembre 2026) - L'Abandon :** Face à un index SQLite désynchronisé à 40%, des erreurs de locks prévisibles et la perte accidentelle de deux notes de gouvernance majeures, l'opérateur désactive le couplage base de données et revient à une recherche textuelle classique et manuelle. Le projet de second cerveau vivant est abandonné.

---

## 3. Analyse Tripartite des Risques (Gary Klein Model)

### A. L'Avocat du Diable (Causes Techniques & Factuelles)
* [ ] **Facteur 1 : Indexation récursive naïve sans filtrage des archives :** L'absence de clause d'exclusion stricte pour `04-Archives/` dans le script `sync_brain.py` a provoqué l'accumulation de doublons obsolètes dans la table FTS5, rendant la recherche sémantique trompeuse pour l'agent.
* [ ] **Facteur 2 : Absence de chunking pour les fiches miroirs de binaires :** Le stockage et l'indexation de transcriptions audio ou d'extraits d'EPUB géants sous forme de blocs de texte monolithiques ont causé des saturations de contexte LLM ("token overflow") et des ralentissements importants du moteur FTS5.
* [ ] **Facteur 3 : Concurrence d'accès SQLite non régulée :** Le mode WAL n'a pas suffi à empêcher les locks d'écriture concurrents entre le daemon `inotifywait` (écritures fréquentes), les pipelines de transcription asynchrones et l'API MCP (requêtes de Tesla), menant à des exceptions d'exécution bloquantes.
* [ ] **Facteur 4 : Remplacement destructif par expressions régulières :** La réécriture de fichiers Markdown complexes ou de MOCs via des regex naïves par l'API REST (au lieu d'un parser d'arbre de syntaxe AST Markdown robuste) a régulièrement corrompu le frontmatter YAML et cassé les liens Obsidian.

### B. L'Inspecteur des Angles Morts (Hypothèses Cachées non Validées)
* **Hypothèse non vérifiée 1 :** Nous avons supposé qu'une synchronisation temps réel par événement (`inotifywait`) était nécessaire et stable, alors qu'une exécution par lot (batch) à des moments précis (fin de session, démarrage de tâche) aurait largement suffi et éliminé 95% des risques de locks concurrents.
* **Hypothèse non vérifiée 2 :** Nous pensions que le Local REST API Obsidian gérait de manière transparente les collisions d'édition en direct avec l'interface graphique de l'opérateur. En réalité, sans protocole de fusion de conflits (diff/merge), l'écrasement mutuel de fichiers était inévitable.
* **Hypothèse non vérifiée 3 :** Nous avons postulé que la règle complexe des 3 occurrences pour la taxonomie des tags serait respectée manuellement, sans mettre en place de barrière technique ou de validation stricte par script.

### C. La Vigie des Signaux Faibles (Indicateurs Précurseurs)
1. **Signal 1 :** Apparition sporadique d'exceptions `sqlite3.OperationalError: database is locked` dans les journaux d'exécution de Tesla en fin de cycle de travail.
2. **Signal 2 :** Présence de fiches miroirs binaires de plus de 50 Ko dans `03-Resources/` sans segmentation sémantique intermédiaire.
3. **Signal 3 :** Citations multiples de la même note (version active et version historique horodatée provenant de `04-Archives/`) dans les réponses sémantiques ou synthèses de Tesla.
4. **Signal 4 :** Logs du script `sync_brain.py` affichant des erreurs silencieuses de parsing YAML dues à des fautes de frappe de l'opérateur sur le frontmatter.

---

## 4. Plan de Résilience & Checklist de Prévention

Pour éviter que ce scénario catastrophe ne se produise dans le monde réel, les contre-mesures obligatoires suivantes doivent être appliquées au plan initial :

| Risque Identifié | Action Préventive Obligatoire | Indicateur de Déclenchement (Seuil) |
| :--- | :--- | :--- |
| **Bruit / Doublons d'indexation** | Modifier `sync_brain.py` pour exclure explicitement les sous-dossiers `04-Archives/` et `_Meta/` du scan de fichiers à indexer dans la table active. | Un seul document issu de `/04-Archives/` détecté dans `avalon_brain.db`. |
| **Locks SQLite concurrents** | Configurer SQLite avec un timeout élevé (`PRAGMA busy_timeout = 10000;`) et abandonner la surveillance continue par inotify au profit d'un déclenchement par lot (batch) en fin de session ou sur commande explicite de Tesla. | Plus de 2 erreurs de verrouillage de base de données par semaine. |
| **Saturation de contexte LLM** | Implémenter un découpage (chunking) logique des fiches miroirs textuelles (par exemple, segments de 2000 mots max avec ID de fragment) avant l'insertion FTS5. | Taille d'une fiche miroir brute insérée dans la base > 30 Ko. |
| **Pertes de données par édition concurrente** | Initialiser un dépôt Git local dans le dossier `/home/lord-mahonheim/bifrost/tesla/Avalon` avec commit automatique périodique ou post-exécution pour assurer la traçabilité et la possibilité de retour arrière immédiat. | Première modification effectuée par Tesla via Local REST API sur un fichier non validé par Git. |

### Checklist de Sûreté Pré-Exécution :
- [ ] **Exclusion des Archives** : Le script `sync_brain.py` contient un test unitaire validant l'exclusion stricte de tout fichier se trouvant dans `04-Archives/` ou comportant le tag `#statut/archive`.
- [ ] **Robustesse SQLite** : Le code d'initialisation de la base SQLite active explicitement `journal_mode=WAL` et configure un timeout d'attente minimal de 10 secondes.
- [ ] **Validation YAML AST** : Avant d'insérer ou d'écrire une note Markdown, Tesla vérifie la validité syntaxique de son frontmatter YAML à l'aide d'une bibliothèque dédiée (ex: `python-frontmatter`) pour éviter les ruptures de formatage.
- [ ] **Mise en place du filet de sécurité (Git)** : Un dépôt Git local est configuré dans le Vault et un script de commit automatique est opérationnel.

---
*Rapport généré et validé localement sur MIDGARD par Tesla (premortem-analyst).*
