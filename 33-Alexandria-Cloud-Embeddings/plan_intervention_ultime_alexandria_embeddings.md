![Status](https://img.shields.io/badge/Status-MVP-blue) ![Ecosystem](https://img.shields.io/badge/Ecosystem-TESLA%20ANTIGRAVITY-purple) ![Security](https://img.shields.io/badge/Security-ID%20LOCKED-red) ![Python](https://img.shields.io/badge/Python-3.12+-blue)

---
type: reference
tags: [curation/certified, curator/prime, status/valid]
coterie: tesla
date: 2026-07-11
author: tesla-curator-prime
confidence_score: 99%
sources: ["[[plan_intervention_alexandria_embeddings.md]]", "[[Plan_d_Intervention_By_RENA.md]]", "[[Plan_d_Intervention_By_Apodex.md]]", "[[Plan_d_Intervention_By_ChatGPT.txt]]"]
---

# CERTIFIED REPORT: ULTIMATE INTERVENTION PLAN ALEXANDRIA EMBEDDINGS

## 1. Diagnostic Summary

The current semantic architecture of Alexandria ([indexer_hybrid.py](file:///home/lord-mahonheim/bifrost/tesla/DataBase/Files/indexer_hybrid.py)) poses critical hardware and financial risks on MIDGARD (8 GB RAM, pure CPU). Its coupling with `PyTorch`, `sentence-transformers`, and `ChromaDB` (including `onnxruntime`) consumes over 1.2 GB of RAM at rest and peaks at over 5.2 GB when indexing large batches. This technical debt weakens the language server (`pyright` via `karellen-lsp-mcp`), causing repeated crashes and blocking the Self-Healing loop. Furthermore, the absence of a local deduplication cache and a strict privacy policy (PII/confidential data) exposes the system to sensitive data leaks and network quota waste during re-indexations.

The transition to a **cloud-local architecture** relying on the Gemini API for embeddings generation and on a single SQLite database configured in WAL mode (`alexandria_brain.db`) completely eliminates the local memory footprint at rest while preserving the sovereignty and speed of local searches.

This document constitutes the **Ultimate Intervention Plan** validated under the principles of the Vigilum Codex. It merges the strengths of the intervention plans of **RENA (V2.1)**, **Apodex**, **ChatGPT**, and **Tesla (initial)** to offer the most robust, secure, and economical compromise for MIDGARD.

---

## 2. Verified Facts & Evidence Pack

### 2.1 Objective Confrontation Grid of the Plans

| Evaluation Criterion | Initial Tesla Plan | RENA Plan (V2.1) | Apodex Plan | ChatGPT Plan | **Ultimate Consolidated Plan (Merger)** |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Infrared Vision** | Validated. | Validated and hardened. | Validated. | Validated (90-95%). | **Absolute consensus on Cloud-Local migration.** |
| **llama.cpp Doctrine** | Temporary packaging. | Ephemeral, subprocess, trap EXIT, ban `llama-cpp-python`. | Same as RENA + `LLAMA_CPP_DOCTRINE.md` doc. | Packaging only, no inference daemon. | **RENA + Apodex**: Ephemeral subprocess CLI under `/tmp`, trap EXIT, dedicated doctrine doc. |
| **Embedding model** | `text-embedding-004` (obsolete/maintenance). | `models/gemini-embedding-001` (768 dimension). | `models/gemini-embedding-001:768`. | Abstract / Modular (versionable). | **Gemini-embedding-001 (768d)** configured via `EmbeddingProvider` abstraction with possible fallback. |
| **Format & Storage** | SQLite BLOB. | L2 Little-Endian normalized Float32 BLOB in SQLite WAL. | Normalized BLOB. | FLOAT32 BLOB or sqlite-vec. | **RENA**: L2 normalized Float32 BLOB stored in SQLite WAL (no JSON, avoids duplicates). |
| **Search & Similarity** | Pure Python / Local NumPy. | FTS5 top 100 BM25 candidates + NumPy dot product (cosine). | FTS5 top 100 + NumPy. | sqlite-vec (C extension). | **Dual Speed**: Local NumPy by default (Low-Code), sqlite-vec as an option via abstraction. |
| **Hybrid RRF k=60** | Kept as invariant. | Kept (FTS5 BM25 + NumPy Cosine). | Kept as invariant. | Kept. | **Invariant kept**: RRF fusion (k=60) between BM25 and NumPy semantic score. |
| **Deduplication Cache** | SHA-256 cache requested. | SHA256(text + model_version) implemented (60-80% savings). | Cache validated. | SHA-256 recommended. | **RENA**: Mandatory cache based on `sha256(text + model_version)` to eliminate redundant calls. |
| **Privacy & GDPR** | Vague. | `confidential:true` Gate + PII Scrubber regex + FTS5-only. | Gate validated. | Absent. | **RENA**: Privacy Gate (YAML frontmatter) + PII Scrubber (regex) to exclude sensitive data from the cloud. |
| **Offline robustness** | Vague rate limiting. | Batches of 96, 3x exponential retry, circuit breaker, SQLite queue. | Queue + degraded FTS5-only. | Absent. | **RENA + ChatGPT**: SQLite `pending_embeddings` queue, network circuit breaker, degraded FTS5 search. |
| **Database Structure** | Denormalized (text duplication). | Normalized (4 tables: docs, chunks, registry, pending). | Same as RENA. | Over-engineered (6 tables, metadata, sync_queue). | **RENA**: 4 minimal normalized tables under SQLite WAL. |
| **Governance & QMS** | Mentioned. | QMS integration + `tesla-master-code` delegation. | QMS, FORCE_TOOLING, MVP-GITHUB dual-copy. | Formal benchmarks before/after. | **Synthesis**: 6-phase QMS, Phase 0 benchmark, MVP dual-copy, LSP validation by `code-auditor`. |

### 2.2 Critical Analysis of Flaws and Blind Spots

1. **Tesla's Initial Plan**:
   - *Strengths*: Correctly states the overall strategic direction and preserves the RRF k=60 invariant.
   - *Flaws*: Presents a denormalized relational schema where raw text is duplicated between the chunk tables and the vector registry, wasting disk space on MIDGARD. Lacks rigor on offline mode management and task organization.
2. **RENA's Plan**:
   - *Strengths*: It is the most solid plan in terms of software implementation (batching, exponential backoff, circuit-breaker, normalized SQL structure). The Privacy Gate and the PII Scrubber make it the only plan compliant with the security requirements of the Vigilum Codex.
   - *Flaws*: Categorically rejects the `sqlite-vec` extension without providing an extension structure (abstraction) in case the corpus exceeds a critical volume threshold (e.g., >100k chunks), forcing a linear NumPy scan.
3. **Apodex's Plan**:
   - *Strengths*: Excellent document structuring and focus on governance (QMS, LSP validation, dual-commit on MVP-GITHUB). Proposes the formal creation of the `LLAMA_CPP_DOCTRINE.md` doctrine.
   - *Flaws*: Lacks proprietary technical depth; it is a textual repetition of RENA's choices with no algorithmic added value.
4. **ChatGPT's Plan**:
   - *Strengths*: Brings an excellent architectural contribution by proposing the `EmbeddingProvider` interface to isolate SQLite from Google's API, as well as a clean separation of the indexing and search pipelines to simplify unit testing.
   - *Flaws*: Initially proposes the binary extension `sqlite-vec` which requires a C compilation on the host, violating MIDGARD's simplicity doctrine. Also presents an over-engineered 6-table SQL schema that is hard to maintain.

---

## 3. Comparative Reasoning & Hypotheses

### 3.1 Technological Arbitration: sqlite-vec vs Local NumPy
The use of `sqlite-vec` (proposed by ChatGPT) allows HNSW similarity queries in C in less than 2 ms, but requires a specific C compilation and the loading of a shared binary (`.so`) within SQLite, which weakens portability and contradicts the Low-Code doctrine.
Conversely, the RENA/Apodex approach performs lexical pre-filtering via FTS5 to surface the top 100 most relevant candidates (BM25), then performs a NumPy matrix calculation on these 100 normalized vectors in less than 0.3 ms. The O(N) algorithmic cost on the entire database is eliminated by the preliminary lexical selection.

**Validated Decision (Dual-Speed)**:
- **V3.0 (Current)**: Use of **FTS5 + Local NumPy** (Low-Code, 0 binary dependencies, stable and fast).
- **V3.1 (Future/Optional)**: Isolation of the vector calculation in a `VectorSearchProvider` class. If the corpus exceeds 100k chunks and a purely vector search is required, a `SqliteVecProvider` implementation can be activated via the `ENABLE_SQLITE_VEC=1` environment variable without altering the semantic indexer.

### 3.2 Modularity of the EmbeddingProvider
To avoid Vendor Lock-in linked to the Gemini API, the network call code must be encapsulated behind an abstract `EmbeddingProvider` interface:
- `GeminiEmbeddingProvider` (Active by default, uses the official `google-genai` SDK).
- `MockEmbeddingProvider` (Used for unit testing and offline mode).
- `VoyageEmbeddingProvider` (Possible future extension).

---

## 4. Contradictions & System Limits (FMEA Shield)

| Potential Failure | Severity (S) | Probability (P) | Detection (D) | RPN | Prevention Actions & Mitigations |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Gemini API Unavailable / Offline** | 4 | 3 | 1 | **12** | Storage in `pending_embeddings`. Automatic failover to degraded mode (local FTS5 BM25 only). Automatic recovery via cron/just script. |
| **API Quota Exceeded (Rate Limits)** | 3 | 3 | 2 | **18** | Processing indexing requests in batches of 96, exponential backoff (3x retries), and circuit-breaker. |
| **API Keys / Credentials / PII Leak** | 5 | 2 | 2 | **20** | Mandatory PII Scrubber analyzing text by regex before sending. Exclusion of files marked `confidential: true` from any Cloud processing. |
| **Dimension Incompatibility (Drift)** | 4 | 2 | 1 | **8** | Metadata stored in `vector_registry` (`model_version` and `dim`). Automatic dimension validation prior to insertion. |
| **Excessive NumPy RAM consumption** | 2 | 2 | 2 | **8** | Strict limitation of the cosine calculation to the top 100 candidates from the FTS5 pre-filter (limits matrix load). |

---

## 5. Architectural Recommendations & Detailed Action Plan

### 5.1 Final Unified SQLite Schema (SQLite WAL)

The relational schema below (normalized, 4 tables) is configured in WAL mode to guarantee secure concurrent writes and atomic transactions.

```sql
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

-- Imported documents table
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY,
    path TEXT UNIQUE NOT NULL,
    mtime REAL NOT NULL,
    hash_doc TEXT NOT NULL,
    confidential INTEGER DEFAULT 0 -- 1 = Sensitive data isolated locally
);

-- Text fragments table (Chunks)
CREATE TABLE IF NOT EXISTS chunks (
    id INTEGER PRIMARY KEY,
    doc_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    text TEXT NOT NULL,
    hash_chunk TEXT UNIQUE NOT NULL, -- SHA-256 du texte du fragment
    token_count INTEGER,
    created_at REAL NOT NULL
    id INTEGER PRIMARY KEY,
    doc_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    text TEXT NOT NULL,
    hash_chunk TEXT UNIQUE NOT NULL, -- SHA-256 of the fragment's text
    token_count INTEGER,
    created_at REAL NOT NULL
);

-- Normalized semantic vectors registry
CREATE TABLE IF NOT EXISTS vector_registry (
    chunk_id INTEGER PRIMARY KEY REFERENCES chunks(id) ON DELETE CASCADE,
    embedding BLOB NOT NULL, -- L2 normalized FLOAT32 BLOB (Little-Endian, dimension 768)
    dim INTEGER NOT NULL DEFAULT 768,
    model_version TEXT NOT NULL DEFAULT 'gemini-embedding-001:768',
    hash_chunk TEXT NOT NULL,
    created_at REAL NOT NULL
);

-- Queue for asynchronous API call failures management
CREATE TABLE IF NOT EXISTS pending_embeddings (
    chunk_id INTEGER PRIMARY KEY REFERENCES chunks(id) ON DELETE CASCADE,
    attempts INTEGER DEFAULT 0,
    last_error TEXT,
    next_retry_at REAL NOT NULL
);

-- Indexes to accelerate search and cleanup
CREATE INDEX IF NOT EXISTS idx_chunks_hash ON chunks(hash_chunk);
CREATE INDEX IF NOT EXISTS idx_vector_model ON vector_registry(model_version);
CREATE INDEX IF NOT EXISTS idx_docs_conf ON documents(confidential);
```

---

### 5.2 Software Components Specification

#### A. The PII Scrubber (Gatekeeper)
Before each transmission of a text fragment to the Gemini API, the `PIIScrubber` module must run a regex-based filter to obscure sensitive information:
```python
import re

class PIIScrubber:
    PATTERNS = {
        "google_api_key": r"AIzaSy[a-zA-Z0-9\-_]{33}",
        "openai_api_key": r"sk-[a-zA-Z0-9]{48}",
        "github_token": r"gh[oprs]_[a-zA-Z0-9]{36,255}",
        "generic_secret": r"(?i)(password|secret|passwd|private_key)\s*[:=]\s*['\"][a-zA-Z0-9_\-\.\!\@\#\$]{8,}['\"]",
        "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        "jwt_token": r"eyJ[a-zA-Z0-9-_]+\.eyJ[a-zA-Z0-9-_]+\.[a-zA-Z0-9-_]+"
    }

    @classmethod
    def scrub(cls, text: str) -> str:
        scrubbed = text
        for name, pattern in cls.PATTERNS.items():
            scrubbed = re.sub(pattern, f"[REDACTED_{name.upper()}]", scrubbed)
        return scrubbed
```

#### B. The Privacy Gate
When parsing a Markdown file:
1. Analyze the document's YAML frontmatter.
2. If the document contains the `confidential: true` or `private: true` tag, or if its file path belongs to the protected `/02-Areas/Confidentiel/` folder:
   - Assign the value `1` to the `confidential` column of the `documents` table.
   - Index the fragment's text solely in the local FTS5 index.
   - **Strictly prohibit** any call to the Gemini API for this file (no insertion into `vector_registry` or `pending_embeddings`).

#### C. Local Deduplication Cache
To optimize performance and the "Token Economy":
1. Calculate `hash_chunk = sha256(text + model_version)`.
2. Query the local database: `SELECT embedding FROM vector_registry WHERE hash_chunk = ? AND model_version = ?`.
3. If the vector exists, insert it directly into the destination table linked to the new document, without calling the Cloud service.

#### D. EmbeddingProvider Abstraction
```python
from abc import ABC, abstractmethod
import numpy as np

class EmbeddingProvider(ABC):
    @abstractmethod
    def generate_embeddings(self, texts: list[str]) -> list[np.ndarray]:
        """Generates a list of L2-normalized embeddings vectors for a list of texts."""
        pass
```

---

### 5.3 Execution Pipelines

```
========================================================================================
                                INDEXATION PIPELINE
========================================================================================
 Markdown File (*.md)
        │
        ▼
 Light Chunker   ──► [If frontmatter confidential: true] ──► FTS5 Indexation Only
        │ (1000 chars / 200 overlap)                              (Marked confidential=1)
        ▼
  SHA256 Chunk + Model Version
        │
        ├──► [HIT] Local SQLite Cache ──► Retrieve vector from DB (Zero API Calls)
        │
        └──► [MISS] PII Scrubber ──► Gemini API (models/gemini-embedding-001, dim 768)
                                        │
                                        ▼
                                 SQLite Storage
                          (vector_registry table: BLOB)
                                        │
                                        ▼
                                 FTS5 Indexation
                          (fts_vault_index table)

========================================================================================
                                SEARCH PIPELINE
========================================================================================
  User Query
        │
        ├──► Gemini API (Query embedding generation into temporary cache)
        │
        ├──► Step 1: SQLite FTS5 Pre-filter (BM25) ──► Top 100 Lexical Candidates
        │                                                     │
        ▼                                                     ▼
  Step 2: Local NumPy Dot Product Calculation (cosine) on the 100 BLOB Candidates
        │
        ▼
  Step 3: RRF Fusion (Reciprocal Rank Fusion, k=60)
        │
        ▼
   Hybrid Results (Lexical + Semantic)
========================================================================================
```

---

### 5.4 The llama.cpp Doctrine (Ephemeral Usage)

To protect MIDGARD from any memory overload linked to the execution of resident inference daemons, the `llama.cpp` toolchain must obey the strict hardware doctrine formalized in the [LLAMA_CPP_DOCTRINE.md](file:///home/lord-mahonheim/bifrost/tesla/DataBase/Files/LLAMA.CPP/LLAMA_CPP_DOCTRINE.md) file:

1. **Prohibition of Resident Inference**: Absolute prohibition to run `llama-server`, `llama-cli` in interactive mode, or to import `llama-cpp-python` in production scripts.
2. **Single Use / Tooling**: llama.cpp is only allowed for model conversion (HF to GGUF) and quantization (Q4_K_M, Q8_0).
3. **Isolated Ephemeral Workspace**:
   - Each quantization operation must create a unique temporary folder under `/tmp/llama-pack-XXXX`.
   - Systematic use of the `subprocess.run` command to call the locally compiled native binary `llama-quantize`.
   - Implementation of an exception handler or a `trap EXIT` in bash to fully purge the `/tmp/llama-pack-*` temporary folder after execution, even in case of error or interruption.
   - Validation of the quantized artifact's integrity by checking for the GGUF magic header (`0x46554747` or `GGUF` in ASCII).

---

### 5.5 Operational Roadmap (6 Phases - 7 Days)

#### Phase 0: Reference Benchmark & Diagnostics (Day 1)
*   **Objectives**: Capture the physical performance and memory of the old hybrid indexer (ChromaDB/Torch/sentence-transformers) to document the migration's gains.
*   **Actions**:
    1. Measure the indexer's resident RAM in idle state and during the indexation of a control batch of 100 documents.
    2. Record the average semantic search latency.
    3. Document these metrics in `/home/lord-mahonheim/bifrost/tesla/OUTPUTS/benchmark_midgard_before.md`.
*   **Validation Recipe (Phase 0)**: 
    - The benchmark file is created and contains real encrypted hardware data (RAM, CPU, time).

#### Phase I: Indexer Refactoring (Days 2 - 3)
*   **Objectives**: Eliminate heavy dependencies and develop the cloud indexer call logic.
*   **Actions**:
    1. Remove `torch`, `sentence-transformers`, `chromadb`, and `onnxruntime` from the `requirements.txt` file and uninstall the dependencies from the `.venv`.
    2. Implement the `EmbeddingProvider` interface and its `GeminiEmbeddingProvider` implementation via the `google-genai` SDK.
    3. Integrate the `PIIScrubber` and the cryptographic deduplication cache (SHA-256).
*   **Validation Recipe (Phase I)**:
    - Successful execution of `pyright` via `karellen-lsp-mcp` demonstrating 0 import errors.
    - Unit test validating the SHA-256 hashing and proper secret masking by the `PIIScrubber`.

#### Phase II: SQLite Migration & Hybrid RRF Search (Days 4 - 5)
*   **Objectives**: Configure the relational database and set up the RRF fusion.
*   **Actions**:
    1. Write and execute the `migrate_to_v2.py` migration script to create the normalized tables (`documents`, `chunks`, `vector_registry`, `pending_embeddings`).
    2. Update `search_router.py` to pre-filter via FTS5 (top 100), load the corresponding vector BLOBs, calculate cosine similarity with NumPy, and merge with RRF (k=60).
*   **Validation Recipe (Phase II)**:
    - Execution of a test hybrid search in less than 50 ms for a corpus of at least 1,000 test files.
    - Verification of the consistency of the dimensions (768) inserted into SQLite.

#### Phase III: llama.cpp Formalization & Ephemeral Tooling (Day 6 Morning)
*   **Objectives**: Deploy the secure quantization wrapper and enact the doctrine.
*   **Actions**:
    1. Write the `tools/quantize_model.py` script using `subprocess` on the local `llama-quantize` binary.
    2. Implement the temporary folder creation under `/tmp/` and the automatic cleanup via `trap EXIT` or Python `try...finally` block.
    3. Write the doctrine file `/home/lord-mahonheim/bifrost/tesla/DataBase/Files/LLAMA.CPP/LLAMA_CPP_DOCTRINE.md`.
*   **Validation Recipe (Phase III)**:
    - Successful quantization test of a minimal model (e.g., TinyLLaMA 110M).
    - Verification after execution that the `/tmp/llama-pack-*` temporary folder was fully destroyed.

#### Phase IV: Resilience, Security & Degraded Mode Tests (Day 6 Afternoon)
*   **Objectives**: Validate the security locks and operation in offline degraded mode.
*   **Actions**:
    1. Inject a test document containing the `confidential: true` tag and verify that no network call is issued.
    2. Simulate a network outage (or API key deactivation) and verify the redirection of chunks to `pending_embeddings` with an immediate switch to pure FTS5 search (degraded mode without crashing).
    3. Execute a full code audit with `tesla-code-auditor` (Semgrep and LSP diagnostics).
*   **Validation Recipe (Phase IV)**:
    - Validation by the Curator of the audit logs showing that 0 IP packets leaked for confidential documents.
    - Error-free execution of the search engine in degraded mode (without internet connection).

#### Phase V: Certification, Memory Alignment & Closure (Day 7)
*   **Objectives**: Finalize the overhaul, document the architecture, and sync repositories.
*   **Actions**:
    1. Write the final technical documentation `ALEXANDRIA_V2_ARCHITECTURE.md` in `Avalon/03-Resources/`.
    2. Update Universal Memory files: `memory/PROJECT_STATE.md`, `memory/SESSION_LOG.md`, and `memory/liste_projets_antigravity_BASE.md`.
    3. Copy the new code and documentation files to the public Git repository `MVP-GITHUB/32-ALEXANDRIA-CLOUD-EMBEDDINGS/`.
    4. Execute the dual commit and dual push (with Lord Mahonheim's express authorization).
*   **Validation Recipe (Phase V)**:
    - Full harmonization of the `/memory/` folder verified.
    - Clean local Git commits and `clean` Git status on the main repository and MVP-GITHUB.

---
*Certified and signed on MIDGARD by Tesla Curator Prime.*
---
