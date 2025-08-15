"""
Ingestion Engine - Main orchestrator for data ingestion operations.

This module coordinates file tracking, parallel processing, and auto-discovery
to provide a unified interface for ingesting data sources.
"""

from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

from .file_tracker import FileTracker
from .parallel import ParallelProcessor
from .discovery import ProjectDiscovery
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
        
        # Initialize configuration manager
        self.config_manager = ConfigManager(config_path)
        
        # Load sources from configuration
        self.sources = []
        self._load_sources_from_config()
    
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
            # Parse the file (this would call the document parser)
            # For now, we'll create a placeholder
            chunks_created = 1  # Placeholder
            
            # Update file tracker
            self.file_tracker.update_file_tracker(file_path)
            
            return {
                "chunks_created": chunks_created
            }
            
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            return None
    
    def _scan_directory(self, directory_path: Path):
        """Scan directory for files to process."""
        # This would implement the file scanning logic
        # For now, return an empty list
        return []
    
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
