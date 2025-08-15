"""
Ingestion Engine - Main orchestrator for data ingestion operations.

This module coordinates file tracking, parallel processing, and auto-discovery
to provide a unified interface for ingesting data sources.
"""

from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
import requests
from urllib.parse import urlparse
import re

from .file_tracker import FileTracker
from .parallel import ParallelProcessor
from .discovery import ProjectDiscovery
from .chroma_storage import ChromaStorage
from .document_parser import DocumentParser
from core.config import ConfigManager, SourceConfig

logger = logging.getLogger(__name__)


class IngestionEngine:
    """Main ingestion engine that coordinates all ingestion operations."""
    
    def __init__(self, config_path: str = None):
        """
        Initialize the ingestion engine.
        
        Args:
            config_path: Path to configuration file
        """
        # Initialize components
        self.file_tracker = FileTracker()
        self.parallel_processor = ParallelProcessor(max_workers=4)
        self.project_discovery = ProjectDiscovery()
        self.chroma_storage = ChromaStorage()
        self.document_parser = DocumentParser()
        
        # Initialize configuration manager
        self.config_manager = ConfigManager(config_path)
        
        # Load sources from configuration
        self.sources = []
        self._load_sources_from_config()
    
    def ingest_url(self, url: str, source_name: str = None) -> Dict[str, Any]:
        """
        Ingest content from a specific URL (Confluence, Notion, GitHub, etc.).
        
        Args:
            url: URL to ingest
            source_name: Optional name for the source
            
        Returns:
            Dictionary with ingestion results
        """
        try:
            logger.info(f"Starting URL ingestion: {url}")
            
            # Parse URL to determine type
            url_type = self._detect_url_type(url)
            
            if url_type == "confluence":
                return self._ingest_confluence_page(url, source_name)
            elif url_type == "notion":
                return self._ingest_notion_page(url, source_name)
            elif url_type == "github":
                return self._ingest_github_content(url, source_name)
            elif url_type == "generic":
                return self._ingest_generic_url(url, source_name)
            else:
                return {
                    "success": False,
                    "errors": [f"Unsupported URL type: {url_type}"],
                    "chunks_created": 0
                }
                
        except Exception as e:
            logger.error(f"Error during URL ingestion: {e}")
            return {
                "success": False,
                "errors": [str(e)],
                "chunks_created": 0
            }
    
    def _detect_url_type(self, url: str) -> str:
        """
        Detect the type of URL for appropriate processing.
        
        Args:
            url: URL to analyze
            
        Returns:
            URL type string
        """
        url_lower = url.lower()
        
        if any(domain in url_lower for domain in ['atlassian.net', 'confluence', 'jira']):
            return "confluence"
        elif any(domain in url_lower for domain in ['notion.so', 'notion.site']):
            return "notion"
        elif any(domain in url_lower for domain in ['github.com', 'githubusercontent.com']):
            return "github"
        else:
            return "generic"
    
    def _ingest_confluence_page(self, url: str, source_name: str = None) -> Dict[str, Any]:
        """
        Ingest content from a Confluence page.
        
        Args:
            url: Confluence page URL
            source_name: Optional name for the source
            
        Returns:
            Dictionary with ingestion results
        """
        try:
            logger.info(f"Ingesting Confluence page: {url}")
            
            # For now, we'll do a basic HTTP request
            # In production, you'd want to use the Confluence API with proper authentication
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Extract content from HTML
            content = self._extract_confluence_content(response.text)
            
            if not content:
                return {
                    "success": False,
                    "errors": ["Could not extract content from Confluence page"],
                    "chunks_created": 0
                }
            
            # Create chunks from content
            chunks = self._create_chunks_from_text(content, url)
            
            # Store in Chroma DB (placeholder for now)
            # In production, you'd integrate with the storage system
            
            logger.info(f"Successfully ingested Confluence page: {len(chunks)} chunks created")
            
            return {
                "success": True,
                "chunks_created": len(chunks),
                "source": source_name or "Confluence Page",
                "url": url,
                "content_length": len(content)
            }
            
        except requests.RequestException as e:
            logger.error(f"HTTP error ingesting Confluence page: {e}")
            return {
                "success": False,
                "errors": [f"HTTP error: {str(e)}"],
                "chunks_created": 0
            }
        except Exception as e:
            logger.error(f"Error ingesting Confluence page: {e}")
            return {
                "success": False,
                "errors": [str(e)],
                "chunks_created": 0
            }
    
    def _ingest_notion_page(self, url: str, source_name: str = None) -> Dict[str, Any]:
        """
        Ingest content from a Notion page.
        
        Args:
            url: Notion page URL
            source_name: Optional name for the source
            
        Returns:
            Dictionary with ingestion results
        """
        try:
            logger.info(f"Ingesting Notion page: {url}")
            
            # For now, we'll do a basic HTTP request
            # In production, you'd want to use the Notion API with proper authentication
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Extract content from HTML
            content = self._extract_notion_content(response.text)
            
            if not content:
                return {
                    "success": False,
                    "errors": ["Could not extract content from Notion page"],
                    "chunks_created": 0
                }
            
            # Create chunks from content
            chunks = self._create_chunks_from_text(content, url)
            
            logger.info(f"Successfully ingested Notion page: {len(chunks)} chunks created")
            
            return {
                "success": True,
                "chunks_created": len(chunks),
                "source": source_name or "Notion Page",
                "url": url,
                "content_length": len(content)
            }
            
        except Exception as e:
            logger.error(f"Error ingesting Notion page: {e}")
            return {
                "success": False,
                "errors": [str(e)],
                "chunks_created": 0
            }
    
    def _ingest_github_content(self, url: str, source_name: str = None) -> Dict[str, Any]:
        """
        Ingest content from GitHub (README, documentation, etc.).
        
        Args:
            url: GitHub content URL
            source_name: Optional name for the source
            
        Returns:
            Dictionary with ingestion results
        """
        try:
            logger.info(f"Ingesting GitHub content: {url}")
            
            # Convert GitHub web URL to raw content URL
            raw_url = self._convert_github_to_raw_url(url)
            
            if not raw_url:
                return {
                    "success": False,
                    "errors": ["Could not convert GitHub URL to raw content"],
                    "chunks_created": 0
                }
            
            # Fetch raw content
            response = requests.get(raw_url, timeout=30)
            response.raise_for_status()
            
            content = response.text
            
            # Create chunks from content
            chunks = self._create_chunks_from_text(content, url)
            
            logger.info(f"Successfully ingested GitHub content: {len(chunks)} chunks created")
            
            return {
                "success": True,
                "chunks_created": len(chunks),
                "source": source_name or "GitHub Content",
                "url": url,
                "content_length": len(content)
            }
            
        except Exception as e:
            logger.error(f"Error ingesting GitHub content: {e}")
            return {
                "success": False,
                "errors": [str(e)],
                "chunks_created": 0
            }
    
    def _ingest_generic_url(self, url: str, source_name: str = None) -> Dict[str, Any]:
        """
        Ingest content from a generic URL.
        
        Args:
            url: Generic URL
            source_name: Optional name for the source
            
        Returns:
            Dictionary with ingestion results
        """
        try:
            logger.info(f"Ingesting generic URL: {url}")
            
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Extract text content from HTML
            content = self._extract_text_from_html(response.text)
            
            if not content:
                return {
                    "success": False,
                    "errors": ["Could not extract content from URL"],
                    "chunks_created": 0
                }
            
            # Create chunks from content
            chunks = self._create_chunks_from_text(content, url)
            
            logger.info(f"Successfully ingested generic URL: {len(chunks)} chunks created")
            
            return {
                "success": True,
                "chunks_created": len(chunks),
                "source": source_name or "Web Page",
                "url": url,
                "content_length": len(content)
            }
            
        except Exception as e:
            logger.error(f"Error ingesting generic URL: {e}")
            return {
                "success": False,
                "errors": [str(e)],
                "chunks_created": 0
            }
    
    def _extract_confluence_content(self, html_content: str) -> str:
        """Extract main content from Confluence HTML."""
        # Basic content extraction - in production, use proper HTML parsing
        # Look for main content areas
        content_patterns = [
            r'<div[^>]*class="[^"]*content[^"]*"[^>]*>(.*?)</div>',
            r'<div[^>]*id="main-content"[^>]*>(.*?)</div>',
            r'<article[^>]*>(.*?)</article>'
        ]
        
        for pattern in content_patterns:
            match = re.search(pattern, html_content, re.DOTALL | re.IGNORECASE)
            if match:
                return self._clean_html_content(match.group(1))
        
        # Fallback: extract text from body
        return self._extract_text_from_html(html_content)
    
    def _extract_notion_content(self, html_content: str) -> str:
        """Extract main content from Notion HTML."""
        # Basic content extraction for Notion
        content_patterns = [
            r'<div[^>]*class="[^"]*notion-page-content[^"]*"[^>]*>(.*?)</div>',
            r'<main[^>]*>(.*?)</main>'
        ]
        
        for pattern in content_patterns:
            match = re.search(pattern, html_content, re.DOTALL | re.IGNORECASE)
            if match:
                return self._clean_html_content(match.group(1))
        
        # Fallback: extract text from body
        return self._extract_text_from_html(html_content)
    
    def _extract_text_from_html(self, html_content: str) -> str:
        """Extract clean text content from HTML."""
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', html_content)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove common HTML entities
        text = text.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
        
        return text.strip()
    
    def _clean_html_content(self, html_content: str) -> str:
        """Clean and extract text from HTML content."""
        # Remove script and style tags
        html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        
        # Extract text
        return self._extract_text_from_html(html_content)
    
    def _convert_github_to_raw_url(self, url: str) -> str:
        """Convert GitHub web URL to raw content URL."""
        # Convert URLs like:
        # https://github.com/user/repo/blob/main/README.md
        # to:
        # https://raw.githubusercontent.com/user/repo/main/README.md
        
        if 'github.com' in url and '/blob/' in url:
            url = url.replace('github.com', 'raw.githubusercontent.com')
            url = url.replace('/blob/', '/')
            return url
        
        return None
    
    def _create_chunks_from_text(self, text: str, source_url: str, chunk_size: int = 1000) -> List[str]:
        """
        Create text chunks from content.
        
        Args:
            text: Text content to chunk
            source_url: Source URL for the content
            chunk_size: Size of each chunk
            
        Returns:
            List of text chunks
        """
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Try to break at sentence boundaries
            if end < len(text):
                # Look for sentence endings
                sentence_end = text.rfind('.', start, end)
                if sentence_end > start and sentence_end > start + chunk_size * 0.7:
                    end = sentence_end + 1
                else:
                    # Look for word boundaries
                    word_end = text.rfind(' ', start, end)
                    if word_end > start + chunk_size * 0.7:
                        end = word_end
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end
        
        return chunks
    
    def _load_sources_from_config(self):
        """Load data sources from configuration and auto-discovery."""
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
            
            logger.info(f"Loaded {len(self.sources)} total sources")
            
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
            logger.debug(f"Auto-discovery common_paths from config: {common_paths}")
            logger.debug(f"Auto-discovery settings: {settings.auto_discovery}")
            
            # Discover projects
            discovered_projects = self.project_discovery.discover_projects_from_paths(common_paths)
            
            # Add discovered projects as sources
            for project in discovered_projects:
                # Check if this project is already in our sources
                if not self._is_project_already_configured(project["path"]):
                    # Add as auto-discovered source
                    self.sources.append({
                        "path": Path(project["path"]),
                        "type": "local",
                        "added_at": datetime.now().isoformat(),
                        "config": {
                            "id": f"auto-{project['name']}",
                            "name": project['name'],
                            "description": f"Auto-discovered project: {project['description']}",
                            "enabled": True
                        }
                    })
                    logger.info(f"Auto-discovered project: {project['name']} at {project['path']}")
                else:
                    logger.debug(f"Project already configured: {project['path']}")
            
            # Log discovery statistics
            stats = self.project_discovery.get_project_stats(discovered_projects)
            logger.info(f"Auto-discovery complete. Project stats: {stats}")
            
        except Exception as e:
            logger.error(f"Error during auto-discovery: {e}")
    
    def _is_project_already_configured(self, project_path: str) -> bool:
        """Check if a project path is already in our configured sources."""
        for source in self.sources:
            if str(source["path"]) == project_path:
                return True
        return False
    
    def ingest_all(self, force_reindex: bool = False) -> Dict[str, Any]:
        """
        Run the complete ingestion process.
        
        Args:
            force_reindex: If True, reindex all files even if unchanged
            
        Returns:
            Dictionary with processing statistics
        """
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
        
        result = {
            "files_processed": total_files_processed,
            "chunks_created": total_chunks_created,
            "errors": errors,
            "processing_time": processing_time,
            "sources_updated": sources_updated
        }
        
        logger.info(f"Ingestion complete: {result['files_processed']} files, {result['chunks_created']} chunks in {processing_time:.2f}s")
        return result
    
    def _ingest_local_directory(self, source_path: Path, force_reindex: bool = False) -> Dict[str, Any]:
        """
        Ingest all files from a local directory.
        
        Args:
            source_path: Path to the source directory
            force_reindex: If True, reindex all files even if unchanged
            
        Returns:
            Dictionary with processing statistics
        """
        if not source_path.exists() or not source_path.is_dir():
            logger.warning(f"Source path does not exist or is not a directory: {source_path}")
            return {"files_processed": 0, "chunks_created": 0}
        
        logger.info(f"Processing local directory: {source_path}")
        
        # Collect all files that need processing
        files_to_process = []
        for file_path in self._scan_directory(source_path):
            if self.file_tracker.should_reindex_file(file_path, force_reindex):
                files_to_process.append(file_path)
        
        if not files_to_process:
            logger.info(f"No files need processing in {source_path}")
            return {"files_processed": 0, "chunks_created": 0}
        
        logger.info(f"Found {len(files_to_process)} files to process in {source_path}")
        
        # Process files in parallel
        return self.parallel_processor.process_files_parallel(
            files_to_process, 
            self._process_single_file, 
            source_path
        )
    
    def _process_single_file(self, file_path: Path, source_path: Path) -> Optional[Dict[str, Any]]:
        """Process a single file and return processing results."""
        try:
            # Parse the file using the document parser
            chunks = self.document_parser.parse_file(file_path)
            
            if not chunks:
                logger.warning(f"No chunks created for file: {file_path}")
                return {"chunks_created": 0}
            
            # Store chunks in Chroma DB
            source_name = self._get_source_name_for_path(source_path)
            chunks_stored = self.chroma_storage.store_chunks(chunks, source_name)
            
            if chunks_stored != len(chunks):
                logger.warning(f"Only stored {chunks_stored}/{len(chunks)} chunks for {file_path}")
            
            # Update file tracker
            self.file_tracker.update_file_tracker(file_path)
            
            return {
                "chunks_created": len(chunks),
                "chunks_stored": chunks_stored,
                "file_path": str(file_path)
            }
            
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            return None
    
    def _scan_directory(self, directory_path: Path):
        """Scan directory for files to process."""
        files = []
        
        try:
            # Get the source configuration to know what patterns to look for
            source_config = None
            logger.debug(f"Looking for source config for directory: {directory_path}")
            logger.debug(f"Available sources: {[s.get('path', '') for s in self.sources]}")
            
            for source in self.sources:
                source_path = str(source.get('path', ''))
                logger.debug(f"Comparing source path '{source_path}' with directory '{directory_path}'")
                if source_path == str(directory_path):
                    source_config = source
                    logger.debug(f"Found matching source config: {source_config}")
                    break
            
            if not source_config:
                # Default patterns if no specific config found
                patterns = ["*.md", "*.txt", "*.json", "*.yaml", "*.yml", "*.xml", "*.ini", "*.sql", "*.csv"]
                exclude_patterns = ["__pycache__", "*.pyc", ".git", "node_modules", ".env*"]
                logger.warning(f"No source config found for {directory_path}, using default patterns")
            else:
                patterns = source_config.get('patterns', ["*.md", "*.txt"])
                exclude_patterns = source_config.get('exclude_patterns', ["__pycache__", "*.pyc", ".git"])
                logger.debug(f"Using patterns from config: {patterns}")
            
            # Scan directory recursively
            for file_path in directory_path.rglob("*"):
                if file_path.is_file():
                    # Check if file matches any pattern
                    file_matches = False
                    for pattern in patterns:
                        if file_path.match(pattern):
                            file_matches = True
                            logger.debug(f"File {file_path} matches pattern {pattern}")
                            break
                    
                    # Check if file should be excluded
                    file_excluded = False
                    for exclude_pattern in exclude_patterns:
                        if exclude_pattern.startswith("*."):
                            # File extension pattern
                            if file_path.suffix == exclude_pattern[1:]:
                                file_excluded = True
                                logger.debug(f"File {file_path} excluded by pattern {exclude_pattern}")
                                break
                        elif exclude_pattern in str(file_path):
                            # Path contains pattern
                            file_excluded = True
                            logger.debug(f"File {file_path} excluded by pattern {exclude_pattern}")
                            break
                    
                    if file_matches and not file_excluded:
                        files.append(file_path)
                        logger.debug(f"Added file {file_path} to processing list")
            
            logger.info(f"Found {len(files)} files matching patterns in {directory_path}")
            
        except Exception as e:
            logger.error(f"Error scanning directory {directory_path}: {e}")
        
        return files
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the ingestion engine."""
        file_tracker_stats = self.file_tracker.get_stats()
        
        return {
            "total_sources": len(self.sources),
            "file_tracking": file_tracker_stats,
            "parallel_workers": self.parallel_processor.max_workers
        }
    
    def clear_file_tracker(self):
        """Clear all file tracking data."""
        self.file_tracker.clear_tracker()
        logger.info("File tracker cleared")
    
    def _get_source_name_for_path(self, source_path: Path) -> str:
        """
        Get the source name for a given path.
        
        Args:
            source_path: Path to the source
            
        Returns:
            Source name string
        """
        # Try to find the source in configuration
        for source in self.sources:
            if str(source.get('path', '')) == str(source_path):
                return source.get('name', str(source_path))
        
        # If not found in config, use the path name
        return source_path.name if source_path.name else str(source_path)
