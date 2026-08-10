![Status](https://img.shields.io/badge/Status-MVP-blue) ![Ecosystem](https://img.shields.io/badge/Ecosystem-TESLA%20ANTIGRAVITY-purple) ![Security](https://img.shields.io/badge/Security-ID%20LOCKED-red) ![Python](https://img.shields.io/badge/Python-3.12+-blue)

# POST-MIGRATION BENCHMARK - ALEXANDRIA EMBEDDINGS V2.0
Date: 2026-07-11 20:48:07
Machine: MIDGARD (Ubuntu, CPU-only, 8 GB RAM)

## Optimized Engine
- Semantic engine: `Gemini Cloud API` (`models/gemini-embedding-001` - 768 dimensions)
- Database: `SQLite WAL` normalized to 4 tables
- Similarity: Local `NumPy Dot Product` (cosine on Top 100 FTS5)
- RRF: `Reciprocal Rank Fusion` ($k=60$)
- Dependencies: Elimination of `torch`, `sentence-transformers`, `chromadb`

## Measured Physical Metrics

| Metric | V2 Engine Value | Description |
| :--- | :--- | :--- |
| **Idle RAM** | 127.11 MB | Resident memory footprint (RSS) of the new loader |
| **Max Indexation RAM** | 137.48 MB | Peak resident memory (RSS) when indexing 100 documents |
| **Indexation Time (100 docs)** | 597.59 s | Total processing time (lexical indexation + semantic queue) |
| **Indexation Speed** | 0.17 doc/s | Number of documents processed per second |
| **Avg Search Latency** | 200.53 ms | FTS5 + NumPy cosine similarity + RRF fusion compute time |
| **Max Search RAM** | 28.56 MB | Peak resident memory during search execution |
| **Avg Indexation CPU** | 3.3% | Cumulative average CPU utilization across all cores |
