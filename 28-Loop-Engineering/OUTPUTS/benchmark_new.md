# BENCHMARK POST-MIGRATION - ALEXANDRIA EMBEDDINGS V2.0
Date: 2026-07-11 20:48:07
Machine: MIDGARD (Ubuntu, CPU-only, 8 Go RAM)

## Moteur Optimise
- Moteur sémantique : `Gemini Cloud API` (`models/gemini-embedding-001` - 768 dimensions)
- Base de données : `SQLite WAL` normalisée à 4 tables
- Similarité : `NumPy Dot Product` local (cosinus sur Top 100 FTS5)
- RRF : `Reciprocal Rank Fusion` ($k=60$)
- Dépendances : Élimination de `torch`, `sentence-transformers`, `chromadb`

## Metriques Physiques Mesurees

| Metrique | Valeur Moteur V2 | Description |
| :--- | :--- | :--- |
| **RAM au repos (Idle)** | 127.11 Mo | Empreinte mémoire résidente (RSS) du nouveau chargeur |
| **RAM Max Indexation** | 137.48 Mo | Pic de mémoire résidente (RSS) lors de l'indexation de 100 documents |
| **Temps d'indexation (100 docs)** | 597.59 s | Temps total de traitement (indexation lexicale + file d'attente sémantique) |
| **Vitesse d'indexation** | 0.17 doc/s | Nombre de documents traités par seconde |
| **Latence moyenne de recherche** | 200.53 ms | Temps de calcul FTS5 + similarité cosinus NumPy + fusion RRF |
| **RAM Max Recherche** | 28.56 Mo | Pic de mémoire résidente lors de l'exécution de la recherche |
| **CPU Moyen Indexation** | 3.3% | Utilisation CPU moyenne cumulée sur tous les cœurs |
