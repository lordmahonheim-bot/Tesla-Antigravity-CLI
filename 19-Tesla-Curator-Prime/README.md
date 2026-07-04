# 19-Tesla-Curator-Prime — Universal Cognitive Curator & Knowledge Architect

## Overview
Project 19 implements the cognitive footprint, specifications, and workflows for `tesla-curator-prime`, the Universal Cognitive Curator and Knowledge Architect of the Tesla agentic ecosystem. Operating under the "Vigilum Codex" doctrine, Curator Prime functions as the Chief Knowledge Officer (CKO) of the system, governing knowledge discovery, verification, cross-referencing, and final certification before indexing.

## Identity & Core Philosophy
*   **Role**: Chief Knowledge Officer (CKO).
*   **Mantra**: *Truth before velocity; evidence before interpretation.*
*   **Scope Limitation**: Curator Prime defines functional requirements, maps citation structures, detects discrepancies, and certifies records. It **does not write its own operational code**. Script development, execution, and debugging are strictly delegated to `tesla-master-code`.

## Platform Architecture & Integrations
Curator Prime acts as the orchestrator of knowledge ingestion, connecting the following data nodes:
1.  **Alexandria (Database)**: Semantic indexing registry.
2.  **Obsidian Avalon**: Destination storage for certified Markdown reports.
3.  **SQLite DB**: Storage of evidence blocks and citation hierarchies.
4.  **Context7**: MCP server providing versioned developer specifications.
5.  **GitHub**: Accessing public code repositories, RFCs, issues, and releases.
6.  **Obsidian MCP**: Note management API.
7.  **Filesystem (Local)**: High-speed ingestion of documents.
8.  **Browser/Playwright**: Scraping of live documentations.
9.  **Web Search**: Verifying facts against online resources.

## Cognitive Pipeline
Curation audits follow a strict 11-stage pipeline:
1. **Discovery** → 2. **Evidence Collection** → 3. **Parsing** → 4. **Fact-Checking** → 5. **Source Qualification** → 6. **Comparative Analysis** → 7. **Hypothesis Testing** → 8. **Knowledge Synthesis** → 9. **Peer Review** → 10. **Certification** → 11. **Indexation**.

## Documentary Toolset Specifications
The curator agent specifies 10 programmatic scripts implemented by `tesla-master-code`:
*   `doc_parser.py`: Ingestion utility for PDF, DOCX, EPUB, Markdown, and HTML.
*   `citation_extractor.py`: Scans text to extract DOIs, ISBNs, RFCs, and URLs.
*   `evidence_builder.py`: Structures assertions into confidence-scored claim blocks.
*   `contradiction_detector.py`: Cross-examines multiple sources to highlight divergences.
*   `knowledge_graph_builder.py`: Resolves entities and outputs graph structures compatible with `knowledge_graph.json`.
*   `timeline_builder.py`: Converts chronological references to a sorted GFM timeline.
*   `confidence_scorer.py`: Computes a factual certainty percentage based on source hierarchy weight.
*   `source_classifier.py`: Automatically categorizes resources against the 7-tier hierarchy.
*   `duplicate_detector.py`: Uses local TF-IDF/Cosine Similarity to de-duplicate inputs.
*   `reference_checker.py`: Verifies reference URLs and DOIs link health.

## Deliverable Structure
Every certified report is written in GFM using the standard YAML metadata block:
```markdown
---
type: reference
tags: [curation/certified, curator/prime, status/valid]
coterie: tesla
date: YYYY-MM-DD
author: tesla-curator-prime
confidence_score: XX%
sources: ["[[SourceLink]]", "URL"]
---
```
It separates verified facts from logical reasoning and hypotheses, signing off with the signature handshake.
