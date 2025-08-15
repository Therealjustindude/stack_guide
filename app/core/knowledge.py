"""
Core knowledge engine for StackGuide RAG pipeline.
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import chromadb
from chromadb.config import Settings

logger = logging.getLogger(__name__)


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


class KnowledgeEngine:
    """Core knowledge engine for querying and retrieving information."""
    
    def __init__(self, chroma_host: str = "chroma", chroma_port: int = 8000):
        """Initialize the knowledge engine."""
        self.chroma_client = chromadb.HttpClient(
            host=chroma_host,
            port=chroma_port,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create the main collection
        try:
            self.collection = self.chroma_client.get_collection("stackguide_docs")
            logger.info("Connected to existing Chroma collection")
        except Exception:
            self.collection = self.chroma_client.create_collection("stackguide_docs")
            logger.info("Created new Chroma collection")
    
    def query(self, question: str, max_results: int = 5) -> QueryResponse:
        """
        Process a user query and return an answer with sources.
        
        Args:
            question: User's question
            max_results: Maximum number of source documents to retrieve
            
        Returns:
            QueryResponse with answer and sources
        """
        try:
            # Step 1: Retrieve relevant documents
            search_results = self._retrieve_documents(question, max_results)
            
            if not search_results:
                return QueryResponse(
                    answer="I couldn't find any relevant information to answer your question. Try rephrasing or adding more data sources.",
                    sources=[],
                    confidence=0.0
                )
            
            # Step 2: Generate answer using LLM (placeholder for now)
            answer = self._generate_answer(question, search_results)
            
            # Step 3: Return response with sources
            return QueryResponse(
                answer=answer,
                sources=search_results,
                confidence=self._calculate_confidence(search_results)
            )
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return QueryResponse(
                answer=f"Sorry, I encountered an error while processing your question: {str(e)}",
                sources=[],
                confidence=0.0
            )
    
    def _retrieve_documents(self, question: str, max_results: int) -> List[SearchResult]:
        """Retrieve relevant documents using vector similarity search."""
        try:
            # Use the question as the query vector
            results = self.collection.query(
                query_texts=[question],
                n_results=max_results,
                include=["documents", "metadatas", "distances"]
            )
            
            search_results = []
            if results["documents"] and results["documents"][0]:
                for i, (doc, metadata, distance) in enumerate(zip(
                    results["documents"][0],
                    results["metadatas"][0],
                    results["distances"][0]
                )):
                    # Convert distance to similarity score (0-1, higher is better)
                    score = 1.0 - (distance / 2.0)  # Normalize distance to score
                    
                    search_results.append(SearchResult(
                        content=doc,
                        metadata=metadata or {},
                        score=score,
                        source=metadata.get("source_file", "Unknown") if metadata else "Unknown"
                    ))
            
            # Sort by relevance score
            search_results.sort(key=lambda x: x.score, reverse=True)
            
            logger.info(f"Retrieved {len(search_results)} documents for query: {question}")
            return search_results
            
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            return []
    
    def _generate_answer(self, question: str, search_results: List[SearchResult]) -> str:
        """Generate a helpful answer using the retrieved documents."""
        if not search_results:
            return "I couldn't find any relevant information to answer your question. Try rephrasing or adding more data sources."
        
        # Get the top result for primary answer
        top_result = search_results[0]
        
        # Extract meaningful source information
        source_file = top_result.metadata.get('source_file', 'Unknown file')
        file_name = source_file.split('/')[-1] if source_file != 'Unknown file' else 'Unknown'
        section = top_result.metadata.get('section', '')
        
        # Build a helpful answer
        answer = f"Based on the documentation, here's what I found:\n\n"
        
        # Add the most relevant content (truncate if too long)
        content = top_result.content.strip()
        if len(content) > 800:
            # Try to find a good break point
            truncated = content[:800]
            last_period = truncated.rfind('.')
            if last_period > 600:  # Only truncate if we can find a good break
                content = truncated[:last_period + 1]
            else:
                content = truncated + "..."
        
        answer += f"{content}\n\n"
        
        # Add source attribution
        answer += f"**Source**: {file_name}"
        if section:
            answer += f" (Section: {section})"
        answer += f"\n**File path**: {source_file}\n"
        
        # Add relevance score
        answer += f"**Relevance**: {top_result.score:.1%}\n\n"
        
        # If we have multiple results, mention them
        if len(search_results) > 1:
            answer += f"I found {len(search_results)} relevant documents. "
            answer += f"Here are the other sources that might help:\n\n"
            
            for i, result in enumerate(search_results[1:4], 2):  # Show top 3 additional sources
                other_file = result.metadata.get('source_file', 'Unknown').split('/')[-1]
                other_section = result.metadata.get('section', '')
                answer += f"{i}. **{other_file}**"
                if other_section:
                    answer += f" - {other_section}"
                answer += f" (Relevance: {result.score:.1%})\n"
        
        return answer
    
    def _calculate_confidence(self, search_results: List[SearchResult]) -> float:
        """Calculate confidence score based on search results."""
        if not search_results:
            return 0.0
        
        # Average the top 3 scores, weighted by position
        top_scores = search_results[:3]
        weights = [1.0, 0.7, 0.4]  # Top result gets full weight
        
        weighted_sum = sum(score.score * weight for score, weight in zip(top_scores, weights))
        total_weight = sum(weights[:len(top_scores)])
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the document collection."""
        try:
            count = self.collection.count()
            return {
                "total_documents": count,
                "collection_name": "stackguide_docs",
                "status": "connected"
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {
                "total_documents": 0,
                "collection_name": "stackguide_docs",
                "status": "error",
                "error": str(e)
            }
