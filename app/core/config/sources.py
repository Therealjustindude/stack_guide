"""
Source Management - Handles data source configuration and operations.

This module manages the creation, updating, and removal of data sources
including local directories, git repositories, and cloud services.
"""

import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

from .models import SourceConfig

logger = logging.getLogger(__name__)


class SourceManager:
    """Manages data source configurations and operations."""
    
    def __init__(self):
        """Initialize the source manager."""
        self.sources: Dict[str, List[SourceConfig]] = {}
    
    def add_source(self, source: SourceConfig) -> bool:
        """
        Add a new source to configuration.
        
        Args:
            source: Source configuration to add
            
        Returns:
            True if added successfully
        """
        try:
            if source.type not in self.sources:
                self.sources[source.type] = []
            
            # Check for duplicate ID
            if self.get_source_by_id(source.id):
                logger.error(f"Source with ID '{source.id}' already exists")
                return False
            
            self.sources[source.type].append(source)
            
            logger.info(f"Added source: {source.name} ({source.type})")
            return True
            
        except Exception as e:
            logger.error(f"Error adding source: {e}")
            return False
    
    def update_source(self, source_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update an existing source configuration.
        
        Args:
            source_id: Source identifier
            updates: Dictionary of fields to update
            
        Returns:
            True if updated successfully
        """
        source = self.get_source_by_id(source_id)
        if not source:
            logger.error(f"Source not found: {source_id}")
            return False
        
        try:
            for key, value in updates.items():
                if hasattr(source, key):
                    setattr(source, key, value)
            
            logger.info(f"Updated source: {source_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating source: {e}")
            return False
    
    def remove_source(self, source_id: str) -> bool:
        """
        Remove a source from configuration.
        
        Args:
            source_id: Source identifier
            
        Returns:
            True if removed successfully
        """
        try:
            for source_type, sources_list in self.sources.items():
                for i, source in enumerate(sources_list):
                    if source.id == source_id:
                        removed_source = sources_list.pop(i)
                        logger.info(f"Removed source: {removed_source.name}")
                        return True
            
            logger.error(f"Source not found: {source_id}")
            return False
            
        except Exception as e:
            logger.error(f"Error removing source: {e}")
            return False
    
    def get_source_by_id(self, source_id: str) -> Optional[SourceConfig]:
        """
        Get a specific source by ID.
        
        Args:
            source_id: Source identifier
            
        Returns:
            Source configuration or None if not found
        """
        for sources_list in self.sources.values():
            for source in sources_list:
                if source.id == source_id:
                    return source
        return None
    
    def get_enabled_sources(self, source_type: str = None) -> List[SourceConfig]:
        """
        Get all enabled sources, optionally filtered by type.
        
        Args:
            source_type: Optional source type filter (local, git, cloud)
            
        Returns:
            List of enabled source configurations
        """
        if source_type:
            return [s for s in self.sources.get(source_type, []) if s.enabled]
        
        all_sources = []
        for sources_list in self.sources.values():
            all_sources.extend([s for s in sources_list if s.enabled])
        
        return all_sources
    
    def get_sources_by_type(self, source_type: str) -> List[SourceConfig]:
        """
        Get all sources of a specific type.
        
        Args:
            source_type: Type of sources to retrieve
            
        Returns:
            List of source configurations
        """
        return self.sources.get(source_type, [])
    
    def validate_source(self, source: SourceConfig) -> bool:
        """
        Validate a source configuration.
        
        Args:
            source: Source configuration to validate
            
        Returns:
            True if valid
        """
        try:
            # Check required fields
            if not source.id or not source.name or not source.type:
                logger.error("Source missing required fields: id, name, or type")
                return False
            
            # Validate source type
            if source.type not in ["local", "git", "cloud"]:
                logger.error(f"Invalid source type: {source.type}")
                return False
            
            # Validate local sources
            if source.type == "local":
                if not source.path:
                    logger.error("Local source must have a path")
                    return False
                
                # Check if path exists (optional validation)
                try:
                    path = Path(source.path)
                    if not path.exists():
                        logger.warning(f"Local source path does not exist: {source.path}")
                except Exception:
                    logger.warning(f"Could not validate path: {source.path}")
            
            # Validate git sources
            elif source.type == "git":
                if not source.config or "url" not in source.config:
                    logger.error("Git source must have a URL in config")
                    return False
            
            logger.debug(f"Source validation passed: {source.id}")
            return True
            
        except Exception as e:
            logger.error(f"Error validating source: {e}")
            return False
    
    def get_source_stats(self) -> Dict[str, Any]:
        """
        Get statistics about configured sources.
        
        Returns:
            Dictionary with source statistics
        """
        stats = {
            "total_sources": 0,
            "by_type": {},
            "enabled_count": 0,
            "disabled_count": 0
        }
        
        for source_type, sources_list in self.sources.items():
            stats["by_type"][source_type] = len(sources_list)
            stats["total_sources"] += len(sources_list)
            
            for source in sources_list:
                if source.enabled:
                    stats["enabled_count"] += 1
                else:
                    stats["disabled_count"] += 1
        
        return stats
    
    def clear_sources(self):
        """Clear all configured sources."""
        self.sources = {}
        logger.info("All sources cleared")
    
    def export_sources(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Export sources to dictionary format for saving.
        
        Returns:
            Dictionary representation of sources
        """
        export_data = {}
        
        for source_type, sources_list in self.sources.items():
            export_data[source_type] = []
            for source in sources_list:
                source_dict = {
                    "id": source.id,
                    "name": source.name,
                    "path": source.path,
                    "type": source.type,
                    "enabled": source.enabled,
                    "description": source.description,
                    "patterns": source.patterns or [],
                    "exclude_patterns": source.exclude_patterns or []
                }
                if source.config:
                    source_dict["config"] = source.config
                export_data[source_type].append(source_dict)
        
        return export_data
