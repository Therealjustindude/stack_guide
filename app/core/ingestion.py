"""
Data Ingestion Engine - Handles data collection and processing for StackGuide

This module provides comprehensive data ingestion capabilities including:
- Local file system scanning
- Document parsing and chunking
- Metadata extraction
- Chroma DB integration
- Incremental re-indexing
"""

import os
import hashlib
import mimetypes
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Generator
from dataclasses import dataclass
import logging

# Document processing imports
import markdown
from bs4 import BeautifulSoup
import ast
import re

# Chroma DB integration
import chromadb
from chromadb.config import Settings

# Configuration management
from core.config import ConfigManager, SourceConfig

logger = logging.getLogger(__name__)


@dataclass
class DocumentChunk:
    """Represents a chunk of document content."""
    content: str
    metadata: Dict[str, Any]
    chunk_id: str
    source_file: str
    chunk_index: int
    total_chunks: int


@dataclass
class IngestionResult:
    """Result of an ingestion operation."""
    files_processed: int
    chunks_created: int
    errors: List[str]
    processing_time: float
    sources_updated: List[str]


class DocumentParser:
    """Handles parsing of different document types."""
    
    # File extensions we can process
    SUPPORTED_EXTENSIONS = {
        '.md': 'markdown',
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.java': 'java',
        '.cpp': 'cpp',
        '.c': 'c',
        '.h': 'header',
        '.txt': 'text',
        '.rst': 'restructuredtext',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.json': 'json',
        '.xml': 'xml',
        '.html': 'html',
        '.css': 'css',
        '.sql': 'sql',
        '.sh': 'shell',
        '.dockerfile': 'dockerfile',
        '.gitignore': 'gitignore',
        '.env.example': 'env',
        'requirements.txt': 'requirements',
        'README': 'readme',
        'Makefile': 'makefile'
    }
    
    # Files to exclude from processing
    EXCLUDED_FILES = {
        '.git', '.gitignore', '.env', '.DS_Store', '__pycache__',
        'node_modules', '.venv', 'venv', 'env', '.pytest_cache',
        '.coverage', '*.pyc', '*.pyo', '*.pyd', '*.so', '*.dll',
        '*.exe', '*.bin', '*.log', '*.tmp', '*.temp'
    }
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize the document parser.
        
        Args:
            chunk_size: Maximum tokens per chunk
            chunk_overlap: Overlap between chunks for context
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def can_parse_file(self, file_path: Path) -> bool:
        """Check if a file can be parsed."""
        # Check if file is in excluded list
        if any(excluded in str(file_path) for excluded in self.EXCLUDED_FILES):
            return False
        
        # Check file extension
        if file_path.suffix in self.SUPPORTED_EXTENSIONS:
            return True
        
        # Check special filenames
        if file_path.name in self.SUPPORTED_EXTENSIONS:
            return True
        
        return False
    
    def parse_file(self, file_path: Path) -> List[DocumentChunk]:
        """
        Parse a file and return chunks.
        
        Args:
            file_path: Path to the file to parse
            
        Returns:
            List of document chunks
        """
        try:
            file_type = self._get_file_type(file_path)
            
            if file_type == 'markdown':
                return self._parse_markdown(file_path)
            elif file_type == 'python':
                return self._parse_python(file_path)
            elif file_type == 'text':
                return self._parse_text(file_path)
            elif file_type == 'yaml':
                return self._parse_yaml(file_path)
            elif file_type == 'json':
                return self._parse_json(file_path)
            else:
                return self._parse_generic(file_path)
                
        except Exception as e:
            logger.error(f"Error parsing file {file_path}: {e}")
            return []
    
    def _get_file_type(self, file_path: Path) -> str:
        """Determine the file type for parsing."""
        if file_path.suffix in self.SUPPORTED_EXTENSIONS:
            return self.SUPPORTED_EXTENSIONS[file_path.suffix]
        
        if file_path.name in self.SUPPORTED_EXTENSIONS:
            return self.SUPPORTED_EXTENSIONS[file_path.name]
        
        return 'text'
    
    def _parse_markdown(self, file_path: Path) -> List[DocumentChunk]:
        """Parse Markdown files with structure preservation."""
        content = file_path.read_text(encoding='utf-8')
        
        # Split by headers for semantic chunking
        lines = content.split('\n')
        chunks = []
        current_chunk = []
        current_header = "Introduction"
        
        for line in lines:
            if line.startswith('#'):
                # Save previous chunk if it exists
                if current_chunk:
                    chunks.append(self._create_chunk(
                        '\n'.join(current_chunk),
                        file_path,
                        len(chunks),
                        current_header
                    ))
                
                # Start new chunk
                current_header = line.strip('#').strip()
                current_chunk = [line]
            else:
                current_chunk.append(line)
        
        # Add final chunk
        if current_chunk:
            chunks.append(self._create_chunk(
                '\n'.join(current_chunk),
                file_path,
                len(chunks),
                current_header
            ))
        
        return chunks
    
    def _parse_python(self, file_path: Path) -> List[DocumentChunk]:
        """Parse Python files with function/class context."""
        content = file_path.read_text(encoding='utf-8')
        
        try:
            tree = ast.parse(content)
            chunks = []
            
            # Extract imports
            imports = [node for node in tree.body if isinstance(node, (ast.Import, ast.ImportFrom))]
            if imports:
                import_text = '\n'.join(ast.unparse(node) for node in imports)
                chunks.append(self._create_chunk(
                    import_text,
                    file_path,
                    len(chunks),
                    "Imports"
                ))
            
            # Extract classes and functions
            for node in tree.body:
                if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                    node_text = ast.unparse(node)
                    chunks.append(self._create_chunk(
                        node_text,
                        file_path,
                        len(chunks),
                        f"{type(node).__name__}: {node.name}"
                    ))
            
            # If no structured content, fall back to generic parsing
            if not chunks:
                return self._parse_generic(file_path)
            
            return chunks
            
        except SyntaxError:
            # Fall back to generic parsing for files with syntax errors
            return self._parse_generic(file_path)
    
    def _parse_text(self, file_path: Path) -> List[DocumentChunk]:
        """Parse plain text files."""
        content = file_path.read_text(encoding='utf-8')
        return self._parse_generic(file_path)
    
    def _parse_yaml(self, file_path: Path) -> List[DocumentChunk]:
        """Parse YAML files."""
        content = file_path.read_text(encoding='utf-8')
        return self._parse_generic(file_path)
    
    def _parse_json(self, file_path: Path) -> List[DocumentChunk]:
        """Parse JSON files."""
        content = file_path.read_text(encoding='utf-8')
        return self._parse_generic(file_path)
    
    def _parse_generic(self, file_path: Path) -> List[DocumentChunk]:
        """Generic parsing for any file type."""
        content = file_path.read_text(encoding='utf-8')
        
        # Simple chunking by lines
        lines = content.split('\n')
        chunks = []
        current_chunk = []
        current_size = 0
        
        for line in lines:
            line_size = len(line)
            
            if current_size + line_size > self.chunk_size and current_chunk:
                # Save current chunk
                chunks.append(self._create_chunk(
                    '\n'.join(current_chunk),
                    file_path,
                    len(chunks),
                    f"Section {len(chunks) + 1}"
                ))
                
                # Start new chunk with overlap
                overlap_lines = current_chunk[-self.chunk_overlap//50:]  # Rough estimate
                current_chunk = overlap_lines + [line]
                current_size = sum(len(l) for l in current_chunk)
            else:
                current_chunk.append(line)
                current_size += line_size
        
        # Add final chunk
        if current_chunk:
            chunks.append(self._create_chunk(
                '\n'.join(current_chunk),
                file_path,
                len(chunks),
                f"Section {len(chunks) + 1}"
            ))
        
        return chunks
    
    def _create_chunk(self, content: str, file_path: Path, chunk_index: int, section: str) -> DocumentChunk:
        """Create a document chunk with metadata."""
        chunk_id = f"{file_path.stem}_{chunk_index}_{hashlib.md5(content.encode()).hexdigest()[:8]}"
        
        metadata = {
            "source_file": str(file_path),
            "file_type": self._get_file_type(file_path),
            "section": section,
            "chunk_index": chunk_index,
            "file_size": file_path.stat().st_size,
            "last_modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
            "created_at": datetime.now().isoformat()
        }
        
        return DocumentChunk(
            content=content.strip(),
            metadata=metadata,
            chunk_id=chunk_id,
            source_file=str(file_path),
            chunk_index=chunk_index,
            total_chunks=0  # Will be updated later
        )


class DataIngestionEngine:
    """Engine for ingesting data from various sources."""
    
    def __init__(self, chroma_host: str = None, chroma_port: int = None, config_path: str = None):
        """
        Initialize the ingestion engine.
        
        Args:
            chroma_host: Chroma DB host (defaults to environment variable)
            chroma_port: Chroma DB port (defaults to environment variable)
            config_path: Path to configuration file
        """
        self.sources = []
        self.processed_files = 0
        self.total_chunks = 0
        
        # Initialize configuration manager
        self.config_manager = ConfigManager(config_path)
        settings = self.config_manager.get_settings()
        
        # Initialize parser with configured settings
        self.parser = DocumentParser(
            chunk_size=settings.default_chunk_size,
            chunk_overlap=settings.default_chunk_overlap
        )
        
        # Get Chroma DB connection details from environment variables
        import os
        self.chroma_host = chroma_host or os.getenv("CHROMA_HOST", "localhost")
        self.chroma_port = chroma_port or int(os.getenv("CHROMA_PORT", "8000"))
        
        # Initialize Chroma DB connection
        try:
            # Create HTTP client with explicit settings
            self.chroma_client = chromadb.HttpClient(
                host=self.chroma_host,
                port=self.chroma_port
            )
            logger.info(f"Created Chroma DB client for {self.chroma_host}:{self.chroma_port}")
            
            # Test the connection
            self.chroma_client.heartbeat()
            logger.info("Chroma DB heartbeat successful")
            
            # Get or create collection
            try:
                self.collection = self.chroma_client.get_or_create_collection(
                    name="stackguide_documents",
                    metadata={"description": "StackGuide document chunks"}
                )
                logger.info("Collection ready")
            except Exception as e:
                logger.error(f"Failed to create collection: {e}")
                # Try to get existing collection
                try:
                    self.collection = self.chroma_client.get_collection("stackguide_documents")
                    logger.info("Got existing collection")
                except Exception as e2:
                    logger.error(f"Failed to get collection: {e2}")
                    self.collection = None
            
        except Exception as e:
            logger.error(f"Failed to connect to Chroma DB: {e}")
            self.chroma_client = None
            self.collection = None
        
        # Load sources from configuration
        self._load_sources_from_config()
        
    def _load_sources_from_config(self):
        """Load enabled sources from configuration."""
        try:
            enabled_sources = self.config_manager.get_enabled_sources()
            for source in enabled_sources:
                if source.type == "local":
                    # For local sources, add the path to our sources list
                    self.sources.append({
                        "path": Path(source.path),
                        "type": source.type,
                        "added_at": datetime.now().isoformat(),
                        "config": source
                    })
                    logger.info(f"Loaded configured source: {source.name} ({source.path})")
                else:
                    logger.info(f"Source type {source.type} not yet implemented: {source.name}")
            
            logger.info(f"Loaded {len(self.sources)} sources from configuration")
            
        except Exception as e:
            logger.error(f"Error loading sources from configuration: {e}")
    
    def add_source(self, source_path: str, source_type: str = "local") -> bool:
        """
        Add a data source for ingestion.
        
        Args:
            source_path: Path to the source
            source_type: Type of source (local, git, cloud)
            
        Returns:
            True if source was added successfully
        """
        path = Path(source_path)
        
        if not path.exists():
            logger.error(f"Source path does not exist: {source_path}")
            return False
        
        self.sources.append({
            "path": path,
            "type": source_type,
            "added_at": datetime.now().isoformat()
        })
        
        logger.info(f"Added source: {source_path} ({source_type})")
        return True
    
    def ingest_all(self, force_reindex: bool = False) -> IngestionResult:
        """
        Run the complete ingestion process.
        
        Args:
            force_reindex: If True, reindex all files even if unchanged
            
        Returns:
            IngestionResult with processing statistics
        """
        if not self.chroma_client:
            return IngestionResult(
                files_processed=0,
                chunks_created=0,
                errors=["Chroma DB not connected"],
                processing_time=0.0,
                sources_updated=[]
            )
        
        start_time = datetime.now()
        errors = []
        sources_updated = []
        
        logger.info(f"Starting ingestion process for {len(self.sources)} sources")
        
        for source in self.sources:
            try:
                source_path = source["path"]
                source_type = source["type"]
                
                logger.info(f"Processing source: {source_path}")
                
                if source_type == "local":
                    result = self._ingest_local_directory(source_path, force_reindex)
                    if result["files_processed"] > 0:
                        sources_updated.append(str(source_path))
                else:
                    logger.warning(f"Source type {source_type} not yet implemented")
                    
            except Exception as e:
                error_msg = f"Error processing source {source['path']}: {e}"
                logger.error(error_msg)
                errors.append(error_msg)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        result = IngestionResult(
            files_processed=self.processed_files,
            chunks_created=self.total_chunks,
            errors=errors,
            processing_time=processing_time,
            sources_updated=sources_updated
        )
        
        logger.info(f"Ingestion complete: {result.files_processed} files, {result.chunks_created} chunks")
        return result
    
    def _ingest_local_directory(self, directory_path: Path, force_reindex: bool) -> Dict[str, Any]:
        """Ingest documents from a local directory."""
        files_processed = 0
        chunks_created = 0
        
        # Walk through directory
        for file_path in self._scan_directory(directory_path):
            if not self.parser.can_parse_file(file_path):
                continue
            
            try:
                # Check if file needs reindexing
                if not force_reindex and self._is_file_indexed(file_path):
                    logger.debug(f"File already indexed: {file_path}")
                    continue
                
                # Parse and chunk the file
                chunks = self.parser.parse_file(file_path)
                
                if chunks:
                    # Update total chunks count
                    for chunk in chunks:
                        chunk.total_chunks = len(chunks)
                    
                    # Store chunks in Chroma DB
                    self._store_chunks(chunks)
                    
                    files_processed += 1
                    chunks_created += len(chunks)
                    
                    # Update instance counters
                    self.processed_files += 1
                    self.total_chunks += len(chunks)
                    
                    logger.info(f"Processed {file_path}: {len(chunks)} chunks")
                
            except Exception as e:
                logger.error(f"Error processing file {file_path}: {e}")
        
        return {
            "files_processed": files_processed,
            "chunks_created": chunks_created
        }
    
    def _scan_directory(self, directory_path: Path) -> Generator[Path, None, None]:
        """Scan directory for files to process."""
        for item in directory_path.rglob('*'):
            if item.is_file():
                yield item
    
    def _is_file_indexed(self, file_path: Path) -> bool:
        """Check if a file is already indexed in Chroma DB."""
        try:
            # Query for existing chunks from this file
            results = self.collection.query(
                query_texts=[""],
                n_results=1,
                where={"source_file": str(file_path)}
            )
            
            return len(results["ids"][0]) > 0
            
        except Exception as e:
            logger.warning(f"Error checking if file is indexed: {e}")
            return False
    
    def _store_chunks(self, chunks: List[DocumentChunk]):
        """Store document chunks in Chroma DB."""
        if not chunks:
            return
        
        try:
            # Prepare data for Chroma DB
            ids = [chunk.chunk_id for chunk in chunks]
            documents = [chunk.content for chunk in chunks]
            metadatas = [chunk.metadata for chunk in chunks]
            
            # Add chunks to collection
            self.collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
            
            logger.debug(f"Stored {len(chunks)} chunks in Chroma DB")
            
        except Exception as e:
            logger.error(f"Error storing chunks in Chroma DB: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current ingestion status."""
        return {
            "sources": len(self.sources),
            "files_processed": self.processed_files,
            "total_chunks": self.total_chunks,
            "chroma_connected": self.chroma_client is not None,
            "ready": self.chroma_client is not None
        }
    
    def search_chunks(self, query: str, n_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search for relevant document chunks.
        
        Args:
            query: Search query
            n_results: Number of results to return
            
        Returns:
            List of relevant chunks with metadata
        """
        if not self.collection:
            return []
        
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            # Format results
            formatted_results = []
            for i in range(len(results["ids"][0])):
                formatted_results.append({
                    "chunk_id": results["ids"][0][i],
                    "content": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i] if "distances" in results else None
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching chunks: {e}")
            return []
    
    def clear_index(self) -> bool:
        """Clear all indexed documents."""
        try:
            if self.collection:
                self.collection.delete(where={})
                self.processed_files = 0
                self.total_chunks = 0
                logger.info("Cleared document index")
                return True
        except Exception as e:
            logger.error(f"Error clearing index: {e}")
        
        return False
