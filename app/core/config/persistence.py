"""
Configuration Persistence - Handles loading and saving configuration files.

This module manages the persistence of configuration data including
JSON file operations, default configuration creation, and validation.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

from .models import SourceConfig, Settings

logger = logging.getLogger(__name__)


class ConfigPersistence:
    """Handles configuration file persistence and management."""
    
    def __init__(self, config_path: Path = None):
        """
        Initialize the configuration persistence manager.
        
        Args:
            config_path: Path to configuration file
        """
        if config_path is None:
            config_path = Path("./config/sources.json")
        
        self.config_path = Path(config_path)
        self.config_data = {}
    
    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file.
        
        Returns:
            Loaded configuration data
        """
        try:
            if not self.config_path.exists():
                logger.warning(f"Configuration file not found: {self.config_path}")
                self.config_data = self._create_default_config()
                return self.config_data
            
            with open(self.config_path, 'r') as f:
                self.config_data = json.load(f)
            
            logger.info(f"Configuration loaded from {self.config_path}")
            return self.config_data
            
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            self.config_data = self._create_default_config()
            return self.config_data
    
    def save_config(self, config_data: Dict[str, Any]) -> bool:
        """
        Save configuration to file.
        
        Args:
            config_data: Configuration data to save
            
        Returns:
            True if saved successfully
        """
        try:
            # Ensure config directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_path, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            logger.info(f"Configuration saved to {self.config_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            return False
    
    def _create_default_config(self) -> Dict[str, Any]:
        """
        Create default configuration if none exists.
        
        Returns:
            Default configuration data
        """
        logger.info("Creating default configuration")
        
        default_config = {
            "sources": {
                "local": [
                    {
                        "id": "current-project",
                        "name": "Current Project",
                        "path": "./",
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
                    "common_paths": [],
                    "scan_interval_hours": 24,
                    "max_projects_per_path": 50
                }
            }
        }
        
        # Save default config
        self.save_config(default_config)
        return default_config
    
    def parse_sources(self, config_data: Dict[str, Any]) -> Dict[str, List[SourceConfig]]:
        """
        Parse sources from configuration data.
        
        Args:
            config_data: Configuration data dictionary
            
        Returns:
            Dictionary of parsed sources by type
        """
        sources = {}
        
        for source_type, source_list in config_data.get("sources", {}).items():
            sources[source_type] = []
            
            for source_data in source_list:
                try:
                    # Handle different source types
                    if source_type == "local":
                        # Local sources require a path
                        if "path" not in source_data:
                            logger.error(f"Local source missing path: {source_data.get('id', 'unknown')}")
                            continue
                        path = source_data["path"]
                    elif source_type == "git":
                        # Git sources use URL instead of path
                        path = source_data.get("url", "")
                    elif source_type == "cloud":
                        # Cloud sources don't have a path
                        path = ""
                    else:
                        path = source_data.get("path", "")
                    
                    source = SourceConfig(
                        id=source_data["id"],
                        name=source_data["name"],
                        path=path,
                        type=source_data["type"],
                        enabled=source_data["enabled"],
                        description=source_data.get("description", ""),
                        patterns=source_data.get("patterns", []),
                        exclude_patterns=source_data.get("exclude_patterns", []),
                        config=source_data.get("config", {})
                    )
                    sources[source_type].append(source)
                    
                except KeyError as e:
                    logger.error(f"Invalid source configuration: missing {e}")
                except Exception as e:
                    logger.error(f"Error parsing source configuration: {e}")
        
        return sources
    
    def parse_settings(self, config_data: Dict[str, Any]) -> Settings:
        """
        Parse global settings from configuration data.
        
        Args:
            config_data: Configuration data dictionary
            
        Returns:
            Parsed settings object
        """
        settings_data = config_data.get("settings", {})
        
        return Settings(
            default_chunk_size=settings_data.get("default_chunk_size", 1000),
            default_chunk_overlap=settings_data.get("default_chunk_overlap", 200),
            max_file_size_mb=settings_data.get("max_file_size_mb", 10),
            scan_interval_minutes=settings_data.get("scan_interval_minutes", 60),
            auto_discovery=settings_data.get("auto_discovery", {})
        )
    
    def export_config(self, sources: Dict[str, List[SourceConfig]], settings: Settings) -> Dict[str, Any]:
        """
        Export configuration to dictionary format for saving.
        
        Args:
            sources: Source configurations by type
            settings: Global settings
            
        Returns:
            Dictionary representation of configuration
        """
        config_to_save = {
            "sources": {},
            "settings": {
                "default_chunk_size": settings.default_chunk_size,
                "default_chunk_overlap": settings.default_chunk_overlap,
                "max_file_size_mb": settings.max_file_size_mb,
                "scan_interval_minutes": settings.scan_interval_minutes,
                "auto_discovery": settings.auto_discovery
            }
        }
        
        for source_type, sources_list in sources.items():
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
        
        return config_to_save
    
    def backup_config(self, backup_path: Path = None) -> bool:
        """
        Create a backup of the current configuration.
        
        Args:
            backup_path: Path for backup file
            
        Returns:
            True if backup created successfully
        """
        try:
            if backup_path is None:
                backup_dir = self.config_path.parent / "backups"
                backup_dir.mkdir(exist_ok=True)
                backup_path = backup_dir / f"sources_backup_{int(time.time())}.json"
            
            if self.config_path.exists():
                import shutil
                shutil.copy2(self.config_path, backup_path)
                logger.info(f"Configuration backed up to {backup_path}")
                return True
            else:
                logger.warning("No configuration file to backup")
                return False
                
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return False
    
    def validate_config_file(self) -> bool:
        """
        Validate the configuration file structure.
        
        Returns:
            True if configuration is valid
        """
        try:
            if not self.config_path.exists():
                return False
            
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            # Check required top-level keys
            required_keys = ["sources", "settings"]
            for key in required_keys:
                if key not in config:
                    logger.error(f"Configuration missing required key: {key}")
                    return False
            
            # Validate sources structure
            sources = config.get("sources", {})
            if not isinstance(sources, dict):
                logger.error("Sources must be a dictionary")
                return False
            
            # Validate settings structure
            settings = config.get("settings", {})
            if not isinstance(settings, dict):
                logger.error("Settings must be a dictionary")
                return False
            
            logger.debug("Configuration file validation passed")
            return True
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in configuration file: {e}")
            return False
        except Exception as e:
            logger.error(f"Error validating configuration: {e}")
            return False
