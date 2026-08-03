# ADR 004: Knowledge Engine (RAG 2.0) Architecture

## Status
**Accepted** — 2026-07-31

## Context
As Project Astra transitions to Phase 3 (Knowledge Intelligence), Astra requires a dedicated Knowledge Engine distinct from Long-Term Memory (Day 6). 

Memory handles user preferences, experiences, and conversation logs. Knowledge Engine handles external documents (PDFs, DOCX, Markdown, HTML, TXT), source code repositories, API documentation, and ADRs.

## Decision
We have designed and implemented **Knowledge Engine (RAG 2.0)** following Hexagonal Architecture:

1. **Separation of Knowledge from Memory**:
   - `KnowledgePort` and `ChromaDBKnowledgeAdapter` manage isolated collections (`project_docs`, `code_repos`, `research_papers`, `personal_notes`, `api_docs`).
   - Long-Term Memory remains isolated in `astra_memory.db` and `astra_semantic_memory`.

2. **Multi-Format Document Parsing & Smart Chunking**:
   - `DocumentLoader` parses PDF (`pypdf`), DOCX (`python-docx`), Markdown, TXT, HTML, Python source code, and full Git Repositories.
   - `SmartChunker` applies overlapping character windows (500 chars, 100 overlap) while preserving paragraph boundaries and section headers.

3. **Incremental Indexing via SHA256 File Hashes**:
   - `IndexManager` computes SHA256 file hashes before parsing. If file hash exists in collection, indexing is skipped, eliminating redundant vector computations.

4. **Hybrid Retrieval & Two-Stage Re-Ranking**:
   - `HybridRetriever` combines dense semantic vector search with sparse BM25 keyword matching for candidate retrieval.
   - `ChunkReRanker` re-scores top 20 candidate chunks down to top 5 most relevant chunks based on query term density, exact phrase matches, and section header alignment.

5. **Inline Source Citations**:
   - `CitationEngine` formats precise inline citations (e.g. `[FastAPI.pdf, Page 14, Section: Authentication]`) for LLM prompt context injection.

## Consequences
- Astra can index entire local Git repositories (`c:/Users/rudra/OneDrive/Desktop/astra`) and answer code/architecture queries with exact source citations.
- Performance scales efficiently due to SHA256 incremental indexing and two-stage re-ranking.
