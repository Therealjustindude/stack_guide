"""
Knowledge Engine - Main orchestrator for RAG operations.

This module coordinates document retrieval, answer generation, and confidence
scoring to provide a unified interface for querying the knowledge base.
"""

import logging
from typing import List, Dict, Any, Optional

from .models import SearchResult, QueryResponse, SearchQuery
from .retrieval import DocumentRetriever
from .generation import AnswerGenerator
from .confidence import ConfidenceScorer

logger = logging.getLogger(__name__)


class KnowledgeEngine:
    """Main knowledge engine for querying and retrieving information."""
    
    def __init__(self, chroma_host: str = "chroma", chroma_port: int = 8000):
        """
        Initialize the knowledge engine.
        
        Args:
            chroma_host: Chroma DB host
            chroma_port: Chroma DB port
        """
        # Initialize components
        self.retriever = DocumentRetriever(chroma_host, chroma_port)
        self.generator = AnswerGenerator()
        self.scorer = ConfidenceScorer()
        
        logger.info("Knowledge engine initialized")
    
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
            # Step 1: Create search query
            search_query = SearchQuery(
                text=question,
                max_results=max_results
            )
            
            # Step 2: Retrieve relevant documents
            search_results = self.retriever.retrieve_documents(search_query)
            
            if not search_results:
                return QueryResponse(
                    answer="I couldn't find any relevant information to answer your question. Try rephrasing or adding more data sources.",
                    sources=[],
                    confidence=0.0
                )
            
            # Step 3: Generate answer using retrieved documents
            answer = self.generator.generate_answer(question, search_results)
            
            # Step 4: Calculate confidence score
            confidence = self.scorer.calculate_confidence(search_results, question)
            
            # Step 5: Return response with sources
            return QueryResponse(
                answer=answer,
                sources=search_results,
                confidence=confidence
            )
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return QueryResponse(
                answer=f"Sorry, I encountered an error while processing your question: {str(e)}",
                sources=[],
                confidence=0.0
            )
    
    def get_detailed_response(self, question: str, max_results: int = 5) -> Dict[str, Any]:
        """
        Get a detailed response with confidence breakdown and analysis.
        
        Args:
            question: User's question
            max_results: Maximum number of source documents to retrieve
            
        Returns:
            Dictionary with detailed response information
        """
        try:
            # Get basic query response
            response = self.query(question, max_results)
            
            # Get confidence breakdown
            confidence_breakdown = self.scorer.get_confidence_breakdown(
                response.sources, question
            )
            
            # Get answer summary
            answer_summary = self.generator.get_answer_summary(response.answer)
            
            # Get collection stats
            collection_stats = self.retriever.get_collection_stats()
            
            return {
                "response": response,
                "confidence_breakdown": confidence_breakdown,
                "answer_summary": answer_summary,
                "collection_stats": collection_stats,
                "query_info": {
                    "question": question,
                    "max_results": max_results,
                    "results_retrieved": len(response.sources)
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting detailed response: {e}")
            return {
                "error": str(e),
                "response": None
            }
    
    def search_by_metadata(self, filters: Dict[str, Any], max_results: int = 10) -> List[SearchResult]:
        """
        Search documents by metadata filters.
        
        Args:
            filters: Metadata filters to apply
            max_results: Maximum number of results
            
        Returns:
            List of matching search results
        """
        return self.retriever.search_by_metadata(filters, max_results)
    
    def get_document_by_id(self, document_id: str) -> Optional[SearchResult]:
        """
        Retrieve a specific document by its ID.
        
        Args:
            document_id: ID of the document to retrieve
            
        Returns:
            SearchResult if found, None otherwise
        """
        return self.retriever.get_document_by_id(document_id)
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the Chroma collection."""
        return self.retriever.get_collection_stats()
    
    def get_engine_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge engine."""
        collection_stats = self.retriever.get_collection_stats()
        
        return {
            "status": "Active",
            "components": {
                "retriever": "DocumentRetriever",
                "generator": "AnswerGenerator", 
                "scorer": "ConfidenceScorer"
            },
            "collection": collection_stats,
            "capabilities": [
                "Vector similarity search",
                "Answer generation with actionable steps",
                "Confidence scoring and analysis",
                "Metadata-based filtering",
                "Detailed response breakdowns"
            ]
        }
    
    def test_connection(self) -> Dict[str, Any]:
        """Test the connection to Chroma DB and return status."""
        try:
            stats = self.retriever.get_collection_stats()
            return {
                "status": "Connected",
                "collection": stats,
                "message": "Knowledge engine is ready"
            }
        except Exception as e:
            return {
                "status": "Error",
                "error": str(e),
                "message": "Failed to connect to knowledge base"
            }
