"""
Knowledge Package - Core RAG pipeline for StackGuide.

This package provides comprehensive knowledge retrieval and generation capabilities:
- Document retrieval using vector similarity search
- Answer generation with actionable steps
- Confidence scoring and result analysis
- Metadata-based filtering and search
"""

from .models import SearchResult, QueryResponse, SearchQuery, DocumentChunk, ConfidenceMetrics
from .engine import KnowledgeEngine
from .retrieval import DocumentRetriever
from .generation import AnswerGenerator
from .confidence import ConfidenceScorer

__all__ = [
    'SearchResult',
    'QueryResponse', 
    'SearchQuery',
    'DocumentChunk',
    'ConfidenceMetrics',
    'KnowledgeEngine',
    'DocumentRetriever',
    'AnswerGenerator',
    'ConfidenceScorer'
]
