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
import asyncio
import concurrent.futures
import pickle

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
        
        # File tracking for incremental indexing
        self.file_tracker_path = Path("/app/data/file_tracker.pkl")
        self.file_tracker = self._load_file_tracker()
        
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
                    name="stackguide_docs",
                    metadata={"description": "StackGuide document chunks"}
                )
                logger.info("Collection ready")
            except Exception as e:
                logger.error(f"Failed to create collection: {e}")
                # Try to get existing collection
                try:
                    self.collection = self.chroma_client.get_collection("stackguide_docs")
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
        
    def _load_file_tracker(self) -> Dict[str, Dict[str, Any]]:
        """Load file tracking data from a pickle file."""
        if self.file_tracker_path.exists():
            try:
                with open(self.file_tracker_path, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                logger.warning(f"Error loading file tracker from {self.file_tracker_path}: {e}")
        return {}
    
    def _save_file_tracker(self):
        """Save file tracking data to a pickle file."""
        try:
            with open(self.file_tracker_path, 'wb') as f:
                pickle.dump(self.file_tracker, f)
        except Exception as e:
            logger.error(f"Error saving file tracker to {self.file_tracker_path}: {e}")
    
    def _add_file_to_tracker(self, file_path: Path, content_hash: str, last_modified: str):
        """Add a file to the file tracking system."""
        self.file_tracker[str(file_path)] = {
            "content_hash": content_hash,
            "last_modified": last_modified
        }
        self._save_file_tracker()
    
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
    
    def _load_sources_from_config(self):
        """Load data sources from configuration."""
        try:
            config = ConfigManager()
            enabled_sources = []
            
            # Collect all enabled sources from all types
            for source_type, source_list in config.sources.items():
                for source in source_list:
                    if source.enabled:
                        enabled_sources.append(source)
            
            logger.info(f"Found {len(enabled_sources)} enabled sources in configuration")
            
            for source in enabled_sources:
                if source.type == "local":
                    # Convert SourceConfig to the dictionary format expected by ingestion
                    self.sources.append({
                        "path": Path(source.path),
                        "type": source.type,
                        "added_at": datetime.now().isoformat(),
                        "config": source
                    })
                    logger.info(f"Loaded configured source: {source.name} ({source.path})")
                else:
                    logger.info(f"Source type {source.type} not yet implemented: {source.name}")
            
            # Add auto-discovered sources
            self._add_auto_discovered_sources(config)
            
            logger.info(f"Loaded {len(self.sources)} sources from configuration")
            
        except Exception as e:
            logger.error(f"Error loading sources from configuration: {e}")
    
    def _add_auto_discovered_sources(self, config: ConfigManager):
        """Auto-discover and add sources from common paths."""
        try:
            settings = config.get_settings()
            if not settings.auto_discovery or not settings.auto_discovery.get('enabled', False):
                logger.info("Auto-discovery is disabled")
                return
            
            logger.info("Starting auto-discovery of projects...")
            
            # Get common paths to scan
            common_paths = settings.auto_discovery.get('common_paths', [])
            
            for path_pattern in common_paths:
                try:
                    # Expand user path (e.g., ~/Development -> /Users/username/Development)
                    expanded_path = os.path.expanduser(path_pattern)
                    
                    # Map to container path if it's a user path
                    if path_pattern.startswith('~'):
                        # For user paths, we need to map to the /host mount
                        # Since we're using ..:/host, we need to handle the path mapping correctly
                        # The ..:/host maps the parent directory to /host
                        # So ~/Development/my_code becomes /host (which contains all projects)
                        # We need to map the full path correctly
                        if 'Development' in expanded_path:
                            # For Development paths, map to /host since that's where all projects are
                            container_path = "/host"
                        else:
                            # For other paths, try to map them appropriately
                            container_path = f"/host{expanded_path.replace(os.path.expanduser('~'), '')}"
                    else:
                        container_path = expanded_path
                    
                    logger.info(f"Scanning auto-discovery path: {path_pattern} -> {container_path}")
                    
                    if os.path.exists(container_path):
                        # Find projects in this directory
                        discovered_projects = self._discover_projects_in_directory(container_path)
                        
                        for project_path, project_info in discovered_projects.items():
                            # Check if this project is already in our sources
                            if not self._is_project_already_configured(project_path):
                                # Add as auto-discovered source
                                self.sources.append({
                                    "path": Path(project_path),
                                    "type": "local",
                                    "added_at": datetime.now().isoformat(),
                                    "config": {
                                        "id": f"auto-{project_info['name']}",
                                        "name": project_info['name'],
                                        "description": f"Auto-discovered project: {project_info['description']}",
                                        "enabled": True
                                    }
                                })
                                logger.info(f"Auto-discovered project: {project_info['name']} at {project_path}")
                            else:
                                logger.debug(f"Project already configured: {project_path}")
                    else:
                        logger.warning(f"Auto-discovery path does not exist: {container_path}")
                        
                except Exception as e:
                    logger.error(f"Error scanning auto-discovery path {path_pattern}: {e}")
            
            logger.info(f"Auto-discovery complete. Total sources: {len(self.sources)}")
            
        except Exception as e:
            logger.error(f"Error during auto-discovery: {e}")
    
    def _discover_projects_in_directory(self, directory_path: str) -> Dict[str, Dict[str, str]]:
        """Discover projects in a directory by looking for common project indicators."""
        projects = {}
        
        try:
            if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
                return projects
            
            # List contents of the directory
            for item in os.listdir(directory_path):
                item_path = os.path.join(directory_path, item)
                
                if not os.path.isdir(item_path):
                    continue
                
                # Check if this looks like a project by looking for common project files
                if self._is_project_directory(item_path):
                    project_name = item
                    project_description = self._generate_project_description(item_path)
                    
                    projects[item_path] = {
                        "name": project_name,
                        "description": project_description
                    }
                    
        except Exception as e:
            logger.error(f"Error discovering projects in {directory_path}: {e}")
        
        return projects
    
    def _is_project_directory(self, directory_path: str) -> bool:
        """Check if a directory looks like a project by looking for common project files."""
        try:
            # Common project indicator files
            project_indicators = [
                'README.md', 'README.txt', 'package.json', 'requirements.txt', 
                'setup.py', 'pyproject.toml', 'Cargo.toml', 'go.mod', 'pom.xml',
                'build.gradle', 'Makefile', 'Dockerfile', '.git', '.gitignore',
                'src', 'lib', 'app', 'main.py', 'index.js', 'main.go'
            ]
            
            # Check for any of these indicators
            for indicator in project_indicators:
                indicator_path = os.path.join(directory_path, indicator)
                if os.path.exists(indicator_path):
                    return True
            
            # Also check if it's a git repository
            git_path = os.path.join(directory_path, '.git')
            if os.path.exists(git_path) and os.path.isdir(git_path):
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking if {directory_path} is a project: {e}")
            return False
    
    def _generate_project_description(self, project_path: str) -> str:
        """Generate a description for a discovered project."""
        try:
            # Try to read README for description
            readme_files = ['README.md', 'README.txt', 'README']
            for readme in readme_files:
                readme_path = os.path.join(project_path, readme)
                if os.path.exists(readme_path):
                    try:
                        with open(readme_path, 'r', encoding='utf-8') as f:
                            content = f.read(500)  # Read first 500 chars
                            # Extract first meaningful line
                            lines = content.split('\n')
                            for line in lines:
                                line = line.strip()
                                if line and not line.startswith('#') and not line.startswith('<!--'):
                                    return line[:100] + "..." if len(line) > 100 else line
                    except Exception:
                        pass
            
            # Fallback: check for package.json or similar
            package_files = ['package.json', 'pyproject.toml', 'Cargo.toml', 'go.mod']
            for package_file in package_files:
                package_path = os.path.join(project_path, package_file)
                if os.path.exists(package_path):
                    return f"Project with {package_file}"
            
            # Final fallback
            return "Discovered project directory"
            
        except Exception as e:
            logger.error(f"Error generating description for {project_path}: {e}")
            return "Discovered project directory"
    
    def _is_project_already_configured(self, project_path: str) -> bool:
        """Check if a project path is already in our configured sources."""
        for source in self.sources:
            if str(source["path"]) == project_path:
                return True
        return False
    
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
        total_files_processed = 0
        total_chunks_created = 0
        
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
                        total_files_processed += result["files_processed"]
                        total_chunks_created += result["chunks_created"]
                else:
                    logger.warning(f"Source type {source_type} not yet implemented")
                    
            except Exception as e:
                error_msg = f"Error processing source {source['path']}: {e}"
                logger.error(error_msg)
                errors.append(error_msg)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        result = IngestionResult(
            files_processed=total_files_processed,
            chunks_created=total_chunks_created,
            errors=errors,
            processing_time=processing_time,
            sources_updated=sources_updated
        )
        
        logger.info(f"Ingestion complete: {result.files_processed} files, {result.chunks_created} chunks in {processing_time:.2f}s")
        return result
    
    def ingest_url(self, url: str, source_name: str = None) -> IngestionResult:
        """Ingest a specific document from a URL."""
        try:
            logger.info(f"Starting URL ingestion: {url}")
            
            # Parse URL to determine source type
            if 'confluence' in url.lower():
                return self._ingest_confluence_page(url, source_name)
            elif 'notion' in url.lower():
                return self._ingest_notion_page(url, source_name)
            elif 'github' in url.lower():
                return self._ingest_github_content(url, source_name)
            elif 'google.com/docs' in url.lower():
                return self._ingest_google_docs(url, source_name)
            else:
                return self._ingest_generic_url(url, source_name)
                
        except Exception as e:
            logger.error(f"Error ingesting URL {url}: {e}")
            return IngestionResult(
                files_processed=0,
                chunks_created=0,
                sources_processed=0,
                errors=[f"Failed to ingest {url}: {str(e)}"]
            )
    
    def _ingest_confluence_page(self, url: str, source_name: str = None) -> IngestionResult:
        """Ingest a specific Confluence page."""
        try:
            # Extract page ID from URL
            page_id = self._extract_confluence_page_id(url)
            if not page_id:
                raise ValueError("Could not extract page ID from Confluence URL")
            
            # Get page content via Confluence API
            page_content = self._fetch_confluence_page(page_id)
            
            # Process the content
            chunks = self._process_content(page_content, f"confluence_page_{page_id}")
            
            # Store in vector database
            self._store_chunks(chunks, {
                'source_type': 'confluence',
                'source_url': url,
                'page_id': page_id,
                'source_name': source_name or f"Confluence Page {page_id}",
                'ingested_at': datetime.now().isoformat()
            })
            
            logger.info(f"Successfully ingested Confluence page {page_id}")
            return IngestionResult(
                files_processed=1,
                chunks_created=len(chunks),
                sources_processed=1,
                errors=[]
            )
            
        except Exception as e:
            logger.error(f"Error ingesting Confluence page: {e}")
            raise
    
    def _ingest_notion_page(self, url: str, source_name: str = None) -> IngestionResult:
        """Ingest a specific Notion page."""
        try:
            # Extract page ID from URL
            page_id = self._extract_notion_page_id(url)
            if not page_id:
                raise ValueError("Could not extract page ID from Notion URL")
            
            # Get page content via Notion API
            page_content = self._fetch_notion_page(page_id)
            
            # Process the content
            chunks = self._process_content(page_content, f"notion_page_{page_id}")
            
            # Store in vector database
            self._store_chunks(chunks, {
                'source_type': 'notion',
                'source_url': url,
                'page_id': page_id,
                'source_name': source_name or f"Notion Page {page_id}",
                'ingested_at': datetime.now().isoformat()
            })
            
            logger.info(f"Successfully ingested Notion page {page_id}")
            return IngestionResult(
                files_processed=1,
                chunks_created=len(chunks),
                sources_processed=1,
                errors=[]
            )
            
        except Exception as e:
            logger.error(f"Error ingesting Notion page: {e}")
            raise
    
    def _ingest_github_content(self, url: str, source_name: str = None) -> IngestionResult:
        """Ingest specific GitHub content (file, README, etc.)."""
        try:
            # Parse GitHub URL to get repo, path, etc.
            repo_info = self._parse_github_url(url)
            if not repo_info:
                raise ValueError("Could not parse GitHub URL")
            
            # Fetch content via GitHub API
            content = self._fetch_github_content(repo_info)
            
            # Process the content
            chunks = self._process_content(content, f"github_{repo_info['path']}")
            
            # Store in vector database
            self._store_chunks(chunks, {
                'source_type': 'github',
                'source_url': url,
                'repo': repo_info['repo'],
                'path': repo_info['path'],
                'source_name': source_name or f"GitHub {repo_info['repo']}/{repo_info['path']}",
                'ingested_at': datetime.now().isoformat()
            })
            
            logger.info(f"Successfully ingested GitHub content: {repo_info['path']}")
            return IngestionResult(
                files_processed=1,
                chunks_created=len(chunks),
                sources_processed=1,
                errors=[]
            )
            
        except Exception as e:
            logger.error(f"Error ingesting GitHub content: {e}")
            raise
    
    def _ingest_generic_url(self, url: str, source_name: str = None) -> IngestionResult:
        """Ingest generic web content."""
        try:
            # Fetch web page content
            content = self._fetch_web_content(url)
            
            # Process the content
            chunks = self._process_content(content, f"web_page_{hash(url)}")
            
            # Store in vector database
            self._store_chunks(chunks, {
                'source_type': 'web',
                'source_url': url,
                'source_name': source_name or f"Web Page {urlparse(url).netloc}",
                'ingested_at': datetime.now().isoformat()
            })
            
            logger.info(f"Successfully ingested web content: {url}")
            return IngestionResult(
                files_processed=1,
                chunks_created=len(chunks),
                sources_processed=1,
                errors=[]
            )
            
        except Exception as e:
            logger.error(f"Error ingesting web content: {e}")
            raise
    
    def _ingest_local_directory(self, source_path: str, force_reindex: bool = False) -> Dict[str, Any]:
        """
        Ingest all files from a local directory.
        
        Args:
            source_path: Path to the source directory
            force_reindex: If True, reindex all files even if unchanged
            
        Returns:
            Dictionary with processing statistics
        """
        source_path = Path(source_path)
        if not source_path.exists() or not source_path.is_dir():
            logger.warning(f"Source path does not exist or is not a directory: {source_path}")
            return {"files_processed": 0, "chunks_created": 0}
        
        logger.info(f"Processing local directory: {source_path}")
        
        # Collect all files that need processing
        files_to_process = []
        for file_path in self._scan_directory(source_path):
            if self._should_reindex_file(file_path, force_reindex):
                files_to_process.append(file_path)
        
        if not files_to_process:
            logger.info(f"No files need processing in {source_path}")
            return {"files_processed": 0, "chunks_created": 0}
        
        logger.info(f"Found {len(files_to_process)} files to process in {source_path}")
        
        # Process files in parallel
        return self._process_files_parallel(files_to_process, source_path)
    
    def _process_files_parallel(self, files: List[Path], source_path: Path) -> Dict[str, Any]:
        """Process multiple files in parallel for better performance."""
        try:
            # Use ThreadPoolExecutor for I/O-bound operations
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                # Submit all file processing tasks
                future_to_file = {
                    executor.submit(self._process_single_file, file_path, source_path): file_path 
                    for file_path in files
                }
                
                # Collect results as they complete
                processed_files = 0
                total_chunks = 0
                
                for future in concurrent.futures.as_completed(future_to_file):
                    file_path = future_to_file[future]
                    try:
                        result = future.result()
                        if result:
                            processed_files += 1
                            total_chunks += result.get("chunks_created", 0)
                            logger.debug(f"Processed file: {file_path}")
                    except Exception as e:
                        logger.error(f"Error processing file {file_path}: {e}")
                
                return {
                    "files_processed": processed_files,
                    "chunks_created": total_chunks
                }
                
        except Exception as e:
            logger.error(f"Error in parallel file processing: {e}")
            # Fallback to sequential processing
            return self._process_files_sequential(files, source_path)
    
    def _process_files_sequential(self, files: List[Path], source_path: Path) -> Dict[str, Any]:
        """Fallback sequential processing if parallel processing fails."""
        processed_files = 0
        total_chunks = 0
        
        for file_path in files:
            try:
                result = self._process_single_file(file_path, source_path)
                if result:
                    processed_files += 1
                    total_chunks += result.get("chunks_created", 0)
            except Exception as e:
                logger.error(f"Error processing file {file_path}: {e}")
        
        return {
            "files_processed": processed_files,
            "chunks_created": total_chunks
        }
    
    def _process_single_file(self, file_path: Path, source_path: Path) -> Optional[Dict[str, Any]]:
        """Process a single file and return processing results."""
        try:
            # Parse the file
            chunks = self.parser.parse_file(file_path, source_path)
            if not chunks:
                return None
            
            # Store chunks in Chroma DB
            self._store_chunks(chunks)
            
            # Update file tracker
            self._update_file_tracker(file_path)
            
            return {
                "chunks_created": len(chunks)
            }
            
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            return None
    
    def _scan_directory(self, directory_path: Path) -> Generator[Path, None, None]:
        """Scan directory for files to process."""
        for item in directory_path.rglob('*'):
            if item.is_file():
                yield item
    
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

    def _should_reindex_file(self, file_path: Path, force_reindex: bool = False) -> bool:
        """
        Determine if a file should be re-indexed.
        
        Args:
            file_path: Path to the file
            force_reindex: If True, always reindex
            
        Returns:
            True if file should be reindexed
        """
        if force_reindex:
            return True
            
        try:
            # Get current file stats
            stat = file_path.stat()
            current_modified = str(stat.st_mtime)
            current_size = stat.st_size
            
            # Check if file exists in tracker
            file_key = str(file_path)
            if file_key not in self.file_tracker:
                logger.debug(f"File not in tracker, will index: {file_path}")
                return True
            
            tracked_info = self.file_tracker[file_key]
            
            # Check if modification time changed
            if tracked_info.get("last_modified") != current_modified:
                logger.debug(f"File modified, will reindex: {file_path}")
                return True
            
            # Check if file size changed significantly (indicates content change)
            tracked_size = tracked_info.get("file_size", 0)
            if abs(current_size - tracked_size) > 100:  # 100 byte threshold
                logger.debug(f"File size changed, will reindex: {file_path}")
                return True
            
            # Check if file is already indexed in Chroma
            if not self._is_file_indexed(file_path):
                logger.debug(f"File not indexed in Chroma, will index: {file_path}")
                return True
            
            logger.debug(f"File unchanged, skipping: {file_path}")
            return False
            
        except Exception as e:
            logger.warning(f"Error checking file status, will index: {file_path} - {e}")
            return True
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate a hash of the file content for change detection."""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                return hashlib.md5(content).hexdigest()
        except Exception as e:
            logger.warning(f"Error calculating file hash for {file_path}: {e}")
            return ""
    
    def _update_file_tracker(self, file_path: Path):
        """Update the file tracker with current file information."""
        try:
            stat = file_path.stat()
            content_hash = self._calculate_file_hash(file_path)
            
            self._add_file_to_tracker(
                file_path,
                content_hash,
                str(stat.st_mtime)
            )
            
        except Exception as e:
            logger.warning(f"Error updating file tracker for {file_path}: {e}")
