"""
Chroma Storage Manager - Handles storing document chunks in Chroma DB.

This module manages the storage of parsed document chunks in Chroma DB,
including embedding generation and metadata storage.
"""

import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import chromadb
from chromadb.config import Settings

logger = logging.getLogger(__name__)


class ChromaStorage:
    """Manages storage of document chunks in Chroma DB."""
    
    def __init__(self, host: str = "chroma", port: int = 8000, collection_name: str = "stackguide_docs"):
        """
        Initialize the Chroma storage manager.
        
        Args:
            host: Chroma DB host
            port: Chroma DB port
            collection_name: Name of the collection to use
        """
        self.host = host
        self.port = port
        self.collection_name = collection_name
        self.client = None
        self.collection = None
        self._connect()
    
    def _connect(self):
        """Connect to Chroma DB."""
        try:
            # Connect to Chroma DB
            self.client = chromadb.HttpClient(
                host=self.host,
                port=self.port,
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Get or create collection
            try:
                self.collection = self.client.get_collection(name=self.collection_name)
                logger.info(f"Connected to existing collection: {self.collection_name}")
            except Exception:
                # Collection doesn't exist, create it
                self.collection = self.client.create_collection(
                    name=self.collection_name,
                    metadata={"description": "StackGuide document chunks"}
                )
                logger.info(f"Created new collection: {self.collection_name}")
                
        except Exception as e:
            logger.error(f"Failed to connect to Chroma DB: {e}")
            raise
    
    def store_chunks(self, chunks: List[Dict[str, Any]], source_name: str = None) -> int:
        """
        Store document chunks in Chroma DB.
        
        Args:
            chunks: List of chunks to store
            source_name: Name of the source these chunks came from
            
        Returns:
            Number of chunks successfully stored
        """
        if not chunks:
            return 0
        
        try:
            # Prepare data for Chroma DB
            documents = []
            metadatas = []
            ids = []
            
            for i, chunk in enumerate(chunks):
                # Generate unique ID for this chunk
                chunk_id = f"{chunk['metadata']['file_path']}_{i}_{hash(chunk['content']) % 1000000}"
                
                # Prepare metadata
                metadata = chunk['metadata'].copy()
                if source_name:
                    metadata['source_name'] = source_name
                metadata['chunk_index'] = i
                
                # Add to lists
                documents.append(chunk['content'])
                metadatas.append(metadata)
                ids.append(chunk_id)
            
            # Store in Chroma DB
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Stored {len(chunks)} chunks in Chroma DB")
            return len(chunks)
            
        except Exception as e:
            logger.error(f"Error storing chunks in Chroma DB: {e}")
            return 0
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection."""
        try:
            if not self.collection:
                return {"error": "Not connected to collection"}
            
            count = self.collection.count()
            
            return {
                "collection_name": self.collection_name,
                "total_documents": count,
                "status": "Connected"
            }
            
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {"error": str(e)}
    
    def search(self, query: str, n_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search for documents in the collection.
        
        Args:
            query: Search query
            n_results: Number of results to return
            
        Returns:
            List of search results
        """
        try:
            if not self.collection:
                return []
            
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            # Format results
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    formatted_results.append({
                        "content": doc,
                        "metadata": results['metadatas'][0][i] if results['metadatas'] and results['metadatas'][0] else {},
                        "distance": results['distances'][0][i] if results['distances'] and results['distances'][0] else 0.0,
                        "id": results['ids'][0][i] if results['ids'] and results['ids'][0] else ""
                    })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching collection: {e}")
            return []
    
    def delete_source(self, source_path: str) -> int:
        """
        Delete all chunks from a specific source.
        
        Args:
            source_path: Path of the source to delete
            
        Returns:
            Number of chunks deleted
        """
        try:
            if not self.collection:
                return 0
            
            # Get all documents with this source path
            results = self.collection.get(
                where={"file_path": source_path}
            )
            
            if not results['ids']:
                return 0
            
            # Delete the documents
            self.collection.delete(ids=results['ids'])
            
            deleted_count = len(results['ids'])
            logger.info(f"Deleted {deleted_count} chunks from source: {source_path}")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error deleting source {source_path}: {e}")
            return 0
    
    def clear_collection(self) -> bool:
        """Clear all documents from the collection."""
        try:
            if not self.collection:
                return False
            
            # Delete the collection and recreate it
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "StackGuide document chunks"}
            )
            
            logger.info(f"Cleared collection: {self.collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing collection: {e}")
            return False
    
    def get_source_stats(self, source_path: str) -> Dict[str, Any]:
        """
        Get statistics about a specific source.
        
        Args:
            source_path: Path of the source
            
        Returns:
            Dictionary with source statistics
        """
        try:
            if not self.collection:
                return {"error": "Not connected to collection"}
            
            # Get all documents with this source path
            results = self.collection.get(
                where={"file_path": source_path}
            )
            
            if not results['ids']:
                return {
                    "source_path": source_path,
                    "chunk_count": 0,
                    "file_types": [],
                    "total_content_length": 0
                }
            
            # Calculate statistics
            file_types = set()
            total_length = 0
            
            for metadata in results['metadatas']:
                if metadata and 'file_type' in metadata:
                    file_types.add(metadata['file_type'])
                if metadata and 'total_length' in metadata:
                    total_length += metadata.get('total_length', 0)
            
            return {
                "source_path": source_path,
                "chunk_count": len(results['ids']),
                "file_types": list(file_types),
                "total_content_length": total_length
            }
            
        except Exception as e:
            logger.error(f"Error getting source stats for {source_path}: {e}")
            return {"error": str(e)}
