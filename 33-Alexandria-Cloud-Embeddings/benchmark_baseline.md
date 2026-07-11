# BENCHMARK BASELINE - ALEXANDRIA EMBEDDINGS V1.0 (BASELINE)
Date: 2026-07-11 19:49:44
Machine: MIDGARD (Ubuntu, CPU-only, 8 Go RAM)

## Moteur de Reference (Actuel)
- Moteur sémantique local : `ChromaDB` (In-Process)
- Modèle d'embeddings local : `SentenceTransformer` (`all-MiniLM-L6-v2` - 384 dimensions)
- Dépendances : `torch`, `sentence-transformers`, `chromadb`

## Metriques Physiques Mesurees

| Metrique | Valeur Baseline | Description |
| :--- | :--- | :--- |
| **RAM au repos (Idle)** | 452.56 Mo | Empreinte mémoire résidente (RSS) avec ChromaDB et le modèle chargé en mémoire |
| **RAM Max Indexation** | 609.68 Mo | Pic de mémoire résidente (RSS) lors de l'indexation de 100 documents |
| **Temps d'indexation (100 docs)** | 371.81 s | Temps total de traitement et génération locale d'embeddings |
| **Vitesse d'indexation** | 0.27 doc/s | Nombre de documents traités par seconde |
| **Latence moyenne de recherche** | 310.19 ms | Temps de calcul de l'embedding de requête + query ChromaDB + SQLite FTS5 + RRF |
| **RAM Max Recherche** | 26.51 Mo | Pic de mémoire résidente lors de l'exécution de la recherche |
| **CPU Moyen Indexation** | 26.9% | Utilisation CPU moyenne cumulée sur tous les cœurs |

## Observations & Diagnostic
1. **Empreinte memoire excessive** : Le chargement au repos de sentence-transformers + ChromaDB nécessite plus de 452.6 Mo de RAM, limitant les ressources de MIDGARD.
2. **Pic memoire a l'indexation** : Durant le traitement de seulement 100 fichiers, la RAM monte à 609.7 Mo, ce qui risque d'entraîner des crashs sur des corpus plus importants ou lors d'indexations concurrentes.
3. **Dependances systeme** : La présence de `torch` et `sentence-transformers` alourdit inutilement le virtualenv de production et ralentit le serveur de langage (LSP).
