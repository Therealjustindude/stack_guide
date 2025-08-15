"""
Configuration management for StackGuide data sources and settings.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class SourceConfig:
    """Configuration for a single data source."""
    id: str
    name: str
    path: str
    type: str
    enabled: bool
    description: str
    patterns: List[str] = None
    exclude_patterns: List[str] = None
    config: Dict[str, Any] = None


@dataclass
class Settings:
    """Global settings for StackGuide."""
    default_chunk_size: int = 1000
    default_chunk_overlap: int = 200
    max_file_size_mb: int = 10
    scan_interval_minutes: int = 60
    auto_discovery: Dict[str, Any] = None


class ConfigManager:
    """Manages StackGuide configuration and data sources."""
    
    def __init__(self, config_path: str = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_path: Path to configuration file (defaults to config/sources.json)
        """
        if config_path is None:
            # Default to config/sources.json relative to project root
            project_root = Path(__file__).parent.parent.parent
            config_path = project_root / "config" / "sources.json"
        
        self.config_path = Path(config_path)
        self.config_data = {}
        self.sources: Dict[str, List[SourceConfig]] = {}
        self.settings: Settings = Settings()
        
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file."""
        try:
            if not self.config_path.exists():
                logger.warning(f"Configuration file not found: {self.config_path}")
                self._create_default_config()
                return
            
            with open(self.config_path, 'r') as f:
                self.config_data = json.load(f)
            
            self._parse_sources()
            self._parse_settings()
            
            logger.info(f"Configuration loaded from {self.config_path}")
            
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            self._create_default_config()
    
    def _create_default_config(self):
        """Create default configuration if none exists."""
        logger.info("Creating default configuration")
        
        default_config = {
            "sources": {
                "local": [
                    {
                        "id": "current-project",
                        "name": "Current Project",
                        "path": "/workspace",
                        "type": "local",
                        "enabled": True,
                        "description": "Current project directory",
                        "patterns": ["*.py", "*.md", "*.txt", "*.yaml", "*.yml", "*.json"],
                        "exclude_patterns": ["__pycache__", "*.pyc", ".git", "node_modules", ".env*"]
                    }
                ],
                "git": [],
                "cloud": []
            },
            "settings": {
                "default_chunk_size": 1000,
                "default_chunk_overlap": 200,
                "max_file_size_mb": 10,
                "scan_interval_minutes": 60,
                "auto_discovery": {
                    "enabled": True,
                    "git_repos": True,
                    "common_paths": ["~/Development", "~/Documents", "~/Projects"]
                }
            }
        }
        
        # Ensure config directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write default config
        with open(self.config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        self.config_data = default_config
        self._parse_sources()
        self._parse_settings()
    
    def _parse_sources(self):
        """Parse sources from configuration."""
        self.sources = {}
        
        for source_type, source_list in self.config_data.get("sources", {}).items():
            self.sources[source_type] = []
            
            for source_data in source_list:
                try:
                    source = SourceConfig(
                        id=source_data["id"],
                        name=source_data["name"],
                        path=source_data["path"],
                        type=source_data["type"],
                        enabled=source_data["enabled"],
                        description=source_data.get("description", ""),
                        patterns=source_data.get("patterns", []),
                        exclude_patterns=source_data.get("exclude_patterns", []),
                        config=source_data.get("config", {})
                    )
                    self.sources[source_type].append(source)
                    
                except KeyError as e:
                    logger.error(f"Invalid source configuration: missing {e}")
                except Exception as e:
                    logger.error(f"Error parsing source configuration: {e}")
    
    def _parse_settings(self):
        """Parse global settings from configuration."""
        settings_data = self.config_data.get("settings", {})
        
        self.settings = Settings(
            default_chunk_size=settings_data.get("default_chunk_size", 1000),
            default_chunk_overlap=settings_data.get("default_chunk_overlap", 200),
            max_file_size_mb=settings_data.get("max_file_size_mb", 10),
            scan_interval_minutes=settings_data.get("scan_interval_minutes", 60),
            auto_discovery=settings_data.get("auto_discovery", {})
        )
    
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
            self._save_config()
            
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
            
            self._save_config()
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
                        self._save_config()
                        logger.info(f"Removed source: {removed_source.name}")
                        return True
            
            logger.error(f"Source not found: {source_id}")
            return False
            
        except Exception as e:
            logger.error(f"Error removing source: {e}")
            return False
    
    def _save_config(self):
        """Save current configuration to file."""
        try:
            # Convert sources back to dictionary format
            config_to_save = {
                "sources": {},
                "settings": {
                    "default_chunk_size": self.settings.default_chunk_size,
                    "default_chunk_overlap": self.settings.default_chunk_overlap,
                    "max_file_size_mb": self.settings.max_file_size_mb,
                    "scan_interval_minutes": self.settings.scan_interval_minutes,
                    "auto_discovery": self.settings.auto_discovery
                }
            }
            
            for source_type, sources_list in self.sources.items():
                config_to_save["sources"][source_type] = []
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
                    config_to_save["sources"][source_type].append(source_dict)
            
            # Ensure config directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_path, 'w') as f:
                json.dump(config_to_save, f, indent=2)
            
            logger.info(f"Configuration saved to {self.config_path}")
            
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
    
    def reload(self):
        """Reload configuration from file."""
        self._load_config()
    
    def get_settings(self) -> Settings:
        """Get current settings."""
        return self.settings
