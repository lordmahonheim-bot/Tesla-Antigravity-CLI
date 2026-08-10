![Status](https://img.shields.io/badge/Status-MVP-blue) ![Ecosystem](https://img.shields.io/badge/Ecosystem-TESLA%20ANTIGRAVITY-purple) ![Security](https://img.shields.io/badge/Security-ID%20LOCKED-red) ![Python](https://img.shields.io/badge/Python-3.12+-blue)

# BASELINE BENCHMARK - ALEXANDRIA EMBEDDINGS V1.0 (BASELINE)
Date: 2026-07-11 19:49:44
Machine: MIDGARD (Ubuntu, CPU-only, 8 GB RAM)

## Reference Engine (Current)
- Local semantic engine: `ChromaDB` (In-Process)
- Local embeddings model: `SentenceTransformer` (`all-MiniLM-L6-v2` - 384 dimensions)
- Dependencies: `torch`, `sentence-transformers`, `chromadb`

## Measured Physical Metrics

| Metric | Baseline Value | Description |
| :--- | :--- | :--- |
| **Idle RAM** | 452.56 MB | Resident memory footprint (RSS) with ChromaDB and the model loaded in memory |
| **Max Indexation RAM** | 609.68 MB | Peak resident memory (RSS) when indexing 100 documents |
| **Indexation Time (100 docs)** | 371.81 s | Total processing time and local embeddings generation |
| **Indexation Speed** | 0.27 doc/s | Number of documents processed per second |
| **Avg Search Latency** | 310.19 ms | Query embedding compute time + ChromaDB query + SQLite FTS5 + RRF |
| **Max Search RAM** | 26.51 MB | Peak resident memory during search execution |
| **Avg Indexation CPU** | 26.9% | Cumulative average CPU utilization across all cores |

## Observations & Diagnostics
1. **Excessive memory footprint**: Loading sentence-transformers + ChromaDB at rest requires more than 452.6 MB of RAM, limiting MIDGARD's resources.
2. **Indexation memory peak**: During the processing of only 100 files, RAM spikes to 609.7 MB, which risks causing crashes on larger corpora or during concurrent indexations.
3. **System dependencies**: The presence of `torch` and `sentence-transformers` unnecessarily bloats the production virtualenv and slows down the Language Server (LSP).
