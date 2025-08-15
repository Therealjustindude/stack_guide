"""
Ingestion Package - Handles data collection and processing for StackGuide.

This package provides comprehensive data ingestion capabilities including:
- File change tracking for incremental indexing
- Parallel processing for better performance
- Auto-discovery of coding projects
- Document parsing and chunking
"""

from .file_tracker import FileTracker
from .parallel import ParallelProcessor
from .discovery import ProjectDiscovery
from .engine import IngestionEngine

__all__ = [
    'FileTracker',
    'ParallelProcessor', 
    'ProjectDiscovery',
    'IngestionEngine'
]
