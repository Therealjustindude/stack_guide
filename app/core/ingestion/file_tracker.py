"""
File Tracker - Handles file change detection for incremental indexing.

This module tracks file modification times, content hashes, and indexing status
to avoid re-processing unchanged files during ingestion.
"""

import os
import hashlib
import pickle
import threading
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class FileTracker:
    """Tracks file changes to enable incremental indexing."""
    
    def __init__(self, tracker_path: Path = None):
        """
        Initialize the file tracker.
        
        Args:
            tracker_path: Path to store the tracker data
        """
        if tracker_path is None:
            tracker_path = Path("/app/config/file_tracker.pkl")
        
        self.tracker_path = tracker_path
        self.file_data = self._load_tracker()
        self._lock = threading.Lock()  # Thread safety lock
    
    def _load_tracker(self) -> Dict[str, Dict[str, Any]]:
        """Load file tracking data from pickle file."""
        if self.tracker_path.exists():
            try:
                with open(self.tracker_path, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                logger.warning(f"Error loading file tracker from {self.tracker_path}: {e}")
        return {}
    
    def _save_tracker(self):
        """Save file tracking data to pickle file."""
        try:
            # Ensure directory exists
            self.tracker_path.parent.mkdir(parents=True, exist_ok=True)
            
            with self._lock:  # Thread-safe read
                data_to_save = self.file_data.copy()  # Copy to avoid modification during save
            
            with open(self.tracker_path, 'wb') as f:
                pickle.dump(data_to_save, f)
        except Exception as e:
            logger.error(f"Error saving file tracker to {self.tracker_path}: {e}")
    
    def should_reindex_file(self, file_path: Path, force_reindex: bool = False) -> bool:
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
            
            # Check if file exists in tracker (thread-safe read)
            file_key = str(file_path)
            with self._lock:
                if file_key not in self.file_data:
                    logger.debug(f"File not in tracker, will index: {file_path}")
                    return True
                
                tracked_info = self.file_data[file_key]
            
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
            if not tracked_info.get("indexed_in_chroma", False):
                logger.debug(f"File not indexed in Chroma, will index: {file_path}")
                return True
            
            logger.debug(f"File unchanged, skipping: {file_path}")
            return False
            
        except Exception as e:
            logger.warning(f"Error checking file status, will index: {file_path} - {e}")
            return True
    
    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate a hash of the file content for change detection."""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                return hashlib.md5(content).hexdigest()
        except Exception as e:
            logger.warning(f"Error calculating file hash for {file_path}: {e}")
            return ""
    
    def update_file_tracker(self, file_path: Path, indexed_in_chroma: bool = True):
        """Update the file tracker with current file information."""
        try:
            stat = file_path.stat()
            content_hash = self.calculate_file_hash(file_path)
            
            with self._lock:  # Thread-safe update
                self.file_data[str(file_path)] = {
                    "content_hash": content_hash,
                    "last_modified": str(stat.st_mtime),
                    "file_size": stat.st_size,
                    "indexed_in_chroma": indexed_in_chroma
                }
            
            self._save_tracker()
            
        except Exception as e:
            logger.warning(f"Error updating file tracker for {file_path}: {e}")
    
    def mark_file_indexed(self, file_path: Path):
        """Mark a file as successfully indexed in Chroma DB."""
        file_key = str(file_path)
        with self._lock:  # Thread-safe update
            if file_key in self.file_data:
                self.file_data[file_key]["indexed_in_chroma"] = True
        self._save_tracker()
    
    def get_file_info(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Get tracking information for a specific file."""
        with self._lock:  # Thread-safe read
            return self.file_data.get(str(file_path))
    
    def clear_tracker(self):
        """Clear all file tracking data."""
        with self._lock:  # Thread-safe update
            self.file_data = {}
        self._save_tracker()
        logger.info("File tracker cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about tracked files."""
        with self._lock:  # Thread-safe read
            total_files = len(self.file_data)
            indexed_files = sum(1 for info in self.file_data.values() if info.get("indexed_in_chroma", False))
        
        return {
            "total_tracked_files": total_files,
            "indexed_files": indexed_files,
            "pending_files": total_files - indexed_files
        }
