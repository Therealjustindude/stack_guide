"""
Configuration Manager - Main orchestrator for configuration operations.

This module coordinates source management, persistence, and settings
to provide a unified interface for configuration management.
"""

import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

from .models import SourceConfig, Settings
from .sources import SourceManager
from .persistence import ConfigPersistence

logger = logging.getLogger(__name__)


class ConfigManager:
    """Main configuration manager that coordinates all configuration operations."""
    
    def __init__(self, config_path: str = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_path: Path to configuration file (defaults to config/sources.json)
        """
        # Initialize components
        self.persistence = ConfigPersistence(config_path)
        self.source_manager = SourceManager()
        
        # Load configuration
        self.config_data = {}
        self.sources: Dict[str, List[SourceConfig]] = {}
        self.settings: Settings = Settings()
        
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file and parse into components."""
        try:
            # Load raw configuration data
            self.config_data = self.persistence.load_config()
            
            # Parse sources and settings
            self.sources = self.persistence.parse_sources(self.config_data)
            self.settings = self.persistence.parse_settings(self.config_data)
            
            # Update source manager with loaded sources
            self.source_manager.sources = self.sources
            
            logger.info(f"Configuration loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            self._create_default_config()
    
    def _create_default_config(self):
        """Create and load default configuration."""
        try:
            logger.info("Creating default configuration")
            
            # Create default config data
            self.config_data = self.persistence._create_default_config()
            
            # Parse the default configuration
            self.sources = self.persistence.parse_sources(self.config_data)
            self.settings = self.persistence.parse_settings(self.config_data)
            
            # Update source manager
            self.source_manager.sources = self.sources
            
            logger.info("Default configuration created and loaded")
            
        except Exception as e:
            logger.error(f"Error creating default configuration: {e}")
    
    def add_source(self, source: SourceConfig) -> bool:
        """
        Add a new source to configuration.
        
        Args:
            source: Source configuration to add
            
        Returns:
            True if added successfully
        """
        try:
            # Validate source before adding
            if not self.source_manager.validate_source(source):
                return False
            
            # Add to source manager
            if self.source_manager.add_source(source):
                # Update internal sources
                self.sources = self.source_manager.sources
                
                # Save to file
                self._save_config()
                return True
            
            return False
            
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
        try:
            if self.source_manager.update_source(source_id, updates):
                # Update internal sources
                self.sources = self.source_manager.sources
                
                # Save to file
                self._save_config()
                return True
            
            return False
            
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
            if self.source_manager.remove_source(source_id):
                # Update internal sources
                self.sources = self.source_manager.sources
                
                # Save to file
                self._save_config()
                return True
            
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
        return self.source_manager.get_source_by_id(source_id)
    
    def get_enabled_sources(self, source_type: str = None) -> List[SourceConfig]:
        """
        Get all enabled sources, optionally filtered by type.
        
        Args:
            source_type: Optional source type filter (local, git, cloud)
            
        Returns:
            List of enabled source configurations
        """
        return self.source_manager.get_enabled_sources(source_type)
    
    def get_sources_by_type(self, source_type: str) -> List[SourceConfig]:
        """
        Get all sources of a specific type.
        
        Args:
            source_type: Type of sources to retrieve
            
        Returns:
            List of source configurations
        """
        return self.source_manager.get_sources_by_type(source_type)
    
    def get_source_stats(self) -> Dict[str, Any]:
        """
        Get statistics about configured sources.
        
        Returns:
            Dictionary with source statistics
        """
        return self.source_manager.get_source_stats()
    
    def get_settings(self) -> Settings:
        """Get current settings."""
        return self.settings
    
    def update_settings(self, updates: Dict[str, Any]) -> bool:
        """
        Update global settings.
        
        Args:
            updates: Dictionary of settings to update
            
        Returns:
            True if updated successfully
        """
        try:
            for key, value in updates.items():
                if hasattr(self.settings, key):
                    setattr(self.settings, key, value)
            
            # Save to file
            self._save_config()
            logger.info("Settings updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error updating settings: {e}")
            return False
    
    def _save_config(self):
        """Save current configuration to file."""
        try:
            # Export configuration data
            config_data = self.persistence.export_config(self.sources, self.settings)
            
            # Save to file
            if self.persistence.save_config(config_data):
                logger.info("Configuration saved successfully")
            else:
                logger.error("Failed to save configuration")
                
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
    
    def reload(self):
        """Reload configuration from file."""
        self._load_config()
        logger.info("Configuration reloaded")
    
    def backup_config(self, backup_path: Path = None) -> bool:
        """
        Create a backup of the current configuration.
        
        Args:
            backup_path: Path for backup file
            
        Returns:
            True if backup created successfully
        """
        return self.persistence.backup_config(backup_path)
    
    def validate_config(self) -> bool:
        """
        Validate the current configuration.
        
        Returns:
            True if configuration is valid
        """
        try:
            # Validate file structure
            if not self.persistence.validate_config_file():
                return False
            
            # Validate all sources
            for source_type, sources_list in self.sources.items():
                for source in sources_list:
                    if not self.source_manager.validate_source(source):
                        logger.error(f"Invalid source configuration: {source.id}")
                        return False
            
            logger.info("Configuration validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Error validating configuration: {e}")
            return False
    
    def get_config_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current configuration.
        
        Returns:
            Dictionary with configuration summary
        """
        source_stats = self.get_source_stats()
        
        return {
            "config_file": str(self.persistence.config_path),
            "sources": source_stats,
            "settings": {
                "chunk_size": self.settings.default_chunk_size,
                "chunk_overlap": self.settings.default_chunk_overlap,
                "max_file_size_mb": self.settings.max_file_size_mb,
                "scan_interval_minutes": self.settings.scan_interval_minutes,
                "auto_discovery_enabled": self.settings.auto_discovery.get('enabled', False)
            },
            "validation": self.validate_config()
        }
