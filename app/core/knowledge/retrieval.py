"""
Document Retrieval - Handles vector search and document fetching.

This module manages the retrieval of relevant documents using vector similarity
search and provides filtering and ranking capabilities.
"""

import logging
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings

from .models import SearchResult, SearchQuery

logger = logging.getLogger(__name__)


class DocumentRetriever:
    """Handles document retrieval using vector similarity search."""
    
    def __init__(self, chroma_host: str = "chroma", chroma_port: int = 8000):
        """
        Initialize the document retriever.
        
        Args:
            chroma_host: Chroma DB host
            chroma_port: Chroma DB port
        """
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
    
    def retrieve_documents(self, query: SearchQuery) -> List[SearchResult]:
        """
        Retrieve relevant documents using vector similarity search.
        
        Args:
            query: Search query with parameters
            
        Returns:
            List of relevant search results
        """
        try:
            # Use the question as the query vector
            results = self.collection.query(
                query_texts=[query.text],
                n_results=query.max_results,
                include=["documents", "metadatas", "distances"]
            )
            
            search_results = []
            
            if results["documents"] and results["documents"][0]:
                documents = results["documents"][0]
                metadatas = results["metadatas"][0]
                distances = results["distances"][0]
                
                for i, (doc, metadata, distance) in enumerate(zip(documents, metadatas, distances)):
                    # Convert distance to similarity score (0-1, higher is better)
                    score = 1.0 - (distance / max(distances)) if distances else 0.5
                    
                    # Apply minimum score filter
                    if score < query.min_score:
                        continue
                    
                    # Create search result
                    search_result = SearchResult(
                        content=doc,
                        metadata=metadata or {},
                        score=score,
                        source=metadata.get('source_file', f'result_{i}') if metadata else f'result_{i}'
                    )
                    
                    search_results.append(search_result)
                    
                    logger.debug(f"Retrieved document {i+1}: score={score:.3f}, source={search_result.source}")
            
            logger.info(f"Retrieved {len(search_results)} documents for query: '{query.text[:50]}...'")
            return search_results
            
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            return []
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the Chroma collection."""
        try:
            count = self.collection.count()
            return {
                "status": "Connected",
                "total_documents": count,
                "collection_name": "stackguide_docs"
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {
                "status": "Error",
                "total_documents": 0,
                "collection_name": "stackguide_docs"
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
        try:
            results = self.collection.query(
                query_texts=[""],  # Empty query, just filter by metadata
                n_results=max_results,
                where=filters,
                include=["documents", "metadatas"]
            )
            
            search_results = []
            if results["documents"] and results["documents"][0]:
                documents = results["documents"][0]
                metadatas = results["metadatas"][0]
                
                for i, (doc, metadata) in enumerate(zip(documents, metadatas)):
                    search_result = SearchResult(
                        content=doc,
                        metadata=metadata or {},
                        score=1.0,  # No distance score for metadata-only queries
                        source=metadata.get('source_file', f'filtered_result_{i}') if metadata else f'filtered_result_{i}'
                    )
                    search_results.append(search_result)
            
            logger.info(f"Found {len(search_results)} documents matching metadata filters")
            return search_results
            
        except Exception as e:
            logger.error(f"Error searching by metadata: {e}")
            return []
    
    def get_document_by_id(self, document_id: str) -> Optional[SearchResult]:
        """
        Retrieve a specific document by its ID.
        
        Args:
            document_id: ID of the document to retrieve
            
        Returns:
            SearchResult if found, None otherwise
        """
        try:
            results = self.collection.get(
                ids=[document_id],
                include=["documents", "metadatas"]
            )
            
            if results["documents"] and results["documents"][0]:
                doc = results["documents"][0]
                metadata = results["metadatas"][0] if results["metadatas"] else {}
                
                return SearchResult(
                    content=doc,
                    metadata=metadata,
                    score=1.0,
                    source=metadata.get('source_file', document_id)
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving document {document_id}: {e}")
            return None
