"""
Configuration Package - Configuration management for StackGuide.

This package provides comprehensive configuration management capabilities:
- Data models for sources, settings, and configuration
- Source management with validation and CRUD operations
- Configuration persistence and file management
- Unified configuration manager interface
"""

from .models import SourceConfig, Settings, AutoDiscoveryConfig, IngestionConfig, StorageConfig
from .manager import ConfigManager
from .sources import SourceManager
from .persistence import ConfigPersistence

__all__ = [
    'SourceConfig',
    'Settings',
    'AutoDiscoveryConfig',
    'IngestionConfig',
    'StorageConfig',
    'ConfigManager',
    'SourceManager',
    'ConfigPersistence'
]
