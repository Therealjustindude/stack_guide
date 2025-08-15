"""
Configuration Models - Data structures for StackGuide configuration.

This module defines the dataclasses and types used for configuration management
including data sources, settings, and application parameters.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional


@dataclass
class SourceConfig:
    """Configuration for a single data source."""
    id: str
    name: str
    type: str
    enabled: bool
    description: str
    path: str = None  # Optional for git and cloud sources
    patterns: List[str] = field(default_factory=list)
    exclude_patterns: List[str] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Settings:
    """Global settings for StackGuide."""
    default_chunk_size: int = 1000
    default_chunk_overlap: int = 200
    max_file_size_mb: int = 10
    scan_interval_minutes: int = 60
    auto_discovery: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AutoDiscoveryConfig:
    """Configuration for automatic project discovery."""
    enabled: bool = False
    common_paths: List[str] = field(default_factory=lambda: ["~/Development", "~/Projects"])
    scan_interval_hours: int = 24
    max_projects_per_path: int = 50
    project_indicators: List[str] = field(default_factory=lambda: [
        "README.md", "package.json", "requirements.txt", ".git"
    ])


@dataclass
class IngestionConfig:
    """Configuration for data ingestion settings."""
    chunk_size: int = 1000
    chunk_overlap: int = 200
    max_file_size_mb: int = 10
    supported_extensions: List[str] = field(default_factory=lambda: [
        ".md", ".txt", ".py", ".js", ".ts", ".java", ".go", ".rs", ".yaml", ".yml", ".json"
    ])
    exclude_patterns: List[str] = field(default_factory=lambda: [
        "__pycache__", "*.pyc", ".git", "node_modules", ".env*", "*.log"
    ])


@dataclass
class StorageConfig:
    """Configuration for data storage and persistence."""
    data_directory: str = "/app/data"
    file_tracker_path: str = "/app/data/file_tracker.pkl"
    backup_enabled: bool = True
    backup_interval_hours: int = 24
    max_backup_files: int = 10
