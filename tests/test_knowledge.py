"""
Unit tests for Day 9 Knowledge Engine (RAG 2.0).
Tests DocumentLoader (PDF, DOCX, Markdown, Code, Git Repos), SmartChunker, MetadataExtractor,
Incremental Indexing via SHA256 hashes, HybridRetriever, ChunkReRanker, CitationEngine, and KnowledgeService.
"""

import os
import pytest
from typing import List

from app.models.document import Document, DocumentType
from app.models.chunk import Chunk
from app.adapters.chromadb_knowledge_adapter import ChromaDBKnowledgeAdapter
from app.knowledge.document_loader import DocumentLoader
from app.knowledge.chunker import SmartChunker
from app.knowledge.metadata import MetadataExtractor
from app.knowledge.retriever import HybridRetriever
from app.knowledge.reranker import ChunkReRanker
from app.knowledge.citation import CitationEngine
from app.knowledge.index_manager import IndexManager
from app.knowledge.knowledge_service import KnowledgeService


@pytest.fixture
def tmp_knowledge_adapter(tmp_path):
    chroma_dir = str(tmp_path / "chroma_knowledge_test")
    adapter = ChromaDBKnowledgeAdapter(persist_directory=chroma_dir)
    return adapter


@pytest.fixture
def sample_markdown_file(tmp_path):
    md_file = tmp_path / "FastAPI_Guide.md"
    content = """# FastAPI Authentication Guide
## Section: OAuth2
FastAPI provides easy security using OAuth2 password flow with Bearer tokens.

## Section: Database Setup
Use SQLAlchemy or SQLModel for database interactions in FastAPI applications.
"""
    md_file.write_text(content, encoding="utf-8")
    return str(md_file)


class TestDocumentLoaderAndChunker:
    def test_markdown_document_loading(self, sample_markdown_file):
        loader = DocumentLoader()
        doc, segments = loader.load_document(sample_markdown_file)

        assert doc.doc_type == DocumentType.MARKDOWN
        assert doc.title == "FastAPI_Guide.md"
        assert len(segments) >= 2
        assert segments[0][2] == "Section: OAuth2"

    def test_smart_chunker(self, sample_markdown_file):
        loader = DocumentLoader()
        chunker = SmartChunker(chunk_size=100, chunk_overlap=20)
        doc, segments = loader.load_document(sample_markdown_file)

        chunks = chunker.chunk_document(doc, segments)
        assert len(chunks) >= 2
        assert chunks[0].document_name == "FastAPI_Guide.md"


class TestMetadataAndIncrementalIndexing:
    def test_file_hash_computation(self, sample_markdown_file):
        hash1 = MetadataExtractor.compute_file_hash(sample_markdown_file)
        hash2 = MetadataExtractor.compute_file_hash(sample_markdown_file)
        assert len(hash1) == 64
        assert hash1 == hash2

    def test_incremental_indexing_skips_unchanged_file(self, tmp_knowledge_adapter, sample_markdown_file):
        index_manager = IndexManager(port=tmp_knowledge_adapter)

        # First indexing run
        indexed, count1 = index_manager.index_document(sample_markdown_file, collection="test_docs")
        assert indexed is True
        assert count1 > 0

        # Second indexing run on unchanged file (Hash match)
        indexed2, count2 = index_manager.index_document(sample_markdown_file, collection="test_docs")
        assert indexed2 is False
        assert count2 == 0


class TestRetrieverRerankerAndCitations:
    def test_hybrid_retrieval_and_reranking(self, tmp_knowledge_adapter, sample_markdown_file):
        index_manager = IndexManager(port=tmp_knowledge_adapter)
        index_manager.index_document(sample_markdown_file, collection="test_docs")

        retriever = HybridRetriever(port=tmp_knowledge_adapter)
        candidates = retriever.retrieve_candidates("OAuth2 Bearer tokens authentication", top_k=5, collection="test_docs")
        assert len(candidates) > 0

        reranker = ChunkReRanker()
        top_results = reranker.rerank("OAuth2 Bearer tokens authentication", candidates, top_n=2)
        assert len(top_results) > 0
        assert top_results[0].rerank_score > 0.0

        citation = CitationEngine.format_citation(top_results[0])
        assert "FastAPI_Guide.md" in citation
        assert "Page" in citation or "Section" in citation


class TestKnowledgeServiceFacade:
    def test_knowledge_service_full_flow(self, tmp_path, sample_markdown_file):
        service = KnowledgeService(persist_dir=str(tmp_path / "service_knowledge_db"))

        # Ingest document
        service.ingest_document(sample_markdown_file, collection="test_service_docs")

        # Query Knowledge
        response = service.query_knowledge("SQLAlchemy database setup", collection="test_service_docs")
        assert "results" in response
        assert "formatted_rag_context" in response
        assert "FastAPI_Guide.md" in response["formatted_rag_context"]
