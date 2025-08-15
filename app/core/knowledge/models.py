"""
Data Models - Core data structures for the knowledge engine.

This module defines the dataclasses and types used throughout the knowledge
engine for search results, query responses, and other data structures.
"""

from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class SearchResult:
    """Result from a document search."""
    content: str
    metadata: Dict[str, Any]
    score: float
    source: str


@dataclass
class QueryResponse:
    """Response to a user query."""
    answer: str
    sources: List[SearchResult]
    confidence: float


@dataclass
class DocumentChunk:
    """A chunk of document content with metadata."""
    content: str
    metadata: Dict[str, Any]
    chunk_id: str
    source_file: str
    chunk_index: int
    total_chunks: int


@dataclass
class SearchQuery:
    """A search query with parameters."""
    text: str
    max_results: int = 5
    min_score: float = 0.0
    filters: Dict[str, Any] = None


@dataclass
class ConfidenceMetrics:
    """Metrics used to calculate confidence scores."""
    top_scores: List[float]
    score_variance: float
    result_count: int
    content_quality: float
    metadata_completeness: float
