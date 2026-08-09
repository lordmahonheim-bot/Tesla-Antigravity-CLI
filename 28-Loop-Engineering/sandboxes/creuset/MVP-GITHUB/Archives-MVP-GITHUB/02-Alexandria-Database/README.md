# Alexandria Universal Library

## Hybrid Architecture (SQL + Vectors)
Alexandria represents the universal library and cognitive indexing layer of the Vigilum Codex ecosystem. It operates on a hybrid storage and retrieval architecture combining:
1. **Lexical Retrieval (SQLite FTS5)**: For exact matching of keywords, paths, tags, and titles.
2. **Semantic Retrieval (ChromaDB)**: For concept-based searches using dense embeddings, ensuring high-recall query matching even when precise vocabulary differs.

These two retrieval methods are combined via a Reciprocal Rank Fusion (RRF) algorithm to deliver unified, high-accuracy context.

## SQLite Schema & FTS5 Virtual Table
The indexing database `alexandria_brain.db` implements the following schema:

```sql
-- File tracking registry
CREATE TABLE IF NOT EXISTS file_registry (
    filepath TEXT PRIMARY KEY,
    last_modified REAL NOT NULL
);

-- Lexical Full-Text Search (FTS5) table
CREATE VIRTUAL TABLE fts_vault_index USING fts5(
    chunk_id,
    filepath,
    content
);
```

## Semantic Incremental Indexer
The script `indexer_hybrid.py` scans a localized documentation folder (the `Vault`), splits modified documents into overlapping chunks, computes dense vector representations using a local SentenceTransformer model (default: `all-MiniLM-L6-v2`), and inserts them into ChromaDB and the SQLite FTS5 index. It tracks modification times in the `file_registry` to execute in a strictly incremental, token-efficient manner.

## Running the RRF Search Router
The hybrid search router fuses lexical and semantic scores using RRF to return the top results without any LLM hallucination.
To query the database:
```bash
python 02-Alexandria-Database/search_router.py "your search query"
```
*Note: Make sure `chromadb` and `sentence-transformers` are installed in your environment before running.*
