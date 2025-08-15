"""
Parallel Processing - Handles concurrent file processing for better performance.

This module provides parallel file processing capabilities using ThreadPoolExecutor
to speed up the ingestion process by processing multiple files simultaneously.
"""

import concurrent.futures
from pathlib import Path
from typing import List, Dict, Any, Callable, Optional
import logging

logger = logging.getLogger(__name__)


class ParallelProcessor:
    """Handles parallel processing of files during ingestion."""
    
    def __init__(self, max_workers: int = 4):
        """
        Initialize the parallel processor.
        
        Args:
            max_workers: Maximum number of concurrent workers
        """
        self.max_workers = max_workers
    
    def process_files_parallel(
        self, 
        files: List[Path], 
        process_func: Callable[[Path, Any], Optional[Dict[str, Any]]],
        source_path: Path,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Process multiple files in parallel for better performance.
        
        Args:
            files: List of file paths to process
            process_func: Function to process each file
            source_path: Source directory path
            **kwargs: Additional arguments to pass to process_func
            
        Returns:
            Dictionary with processing statistics
        """
        if not files:
            return {"files_processed": 0, "chunks_created": 0}
        
        try:
            logger.info(f"Processing {len(files)} files with {self.max_workers} workers")
            
            # Use ThreadPoolExecutor for I/O-bound operations
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit all file processing tasks
                future_to_file = {
                    executor.submit(process_func, file_path, source_path, **kwargs): file_path 
                    for file_path in files
                }
                
                # Collect results as they complete
                processed_files = 0
                total_chunks = 0
                errors = []
                
                for future in concurrent.futures.as_completed(future_to_file):
                    file_path = future_to_file[future]
                    try:
                        result = future.result()
                        if result:
                            processed_files += 1
                            total_chunks += result.get("chunks_created", 0)
                            logger.debug(f"Processed file: {file_path}")
                        else:
                            logger.debug(f"No result from processing: {file_path}")
                    except Exception as e:
                        error_msg = f"Error processing file {file_path}: {e}"
                        logger.error(error_msg)
                        errors.append(error_msg)
                
                # Log summary
                if errors:
                    logger.warning(f"Completed with {len(errors)} errors")
                else:
                    logger.info(f"Successfully processed {processed_files} files")
                
                return {
                    "files_processed": processed_files,
                    "chunks_created": total_chunks,
                    "errors": errors
                }
                
        except Exception as e:
            logger.error(f"Error in parallel file processing: {e}")
            # Fallback to sequential processing
            return self._process_files_sequential(files, process_func, source_path, **kwargs)
    
    def _process_files_sequential(
        self, 
        files: List[Path], 
        process_func: Callable[[Path, Any], Optional[Dict[str, Any]]],
        source_path: Path,
        **kwargs
    ) -> Dict[str, Any]:
        """Fallback sequential processing if parallel processing fails."""
        logger.info("Falling back to sequential processing")
        
        processed_files = 0
        total_chunks = 0
        errors = []
        
        for file_path in files:
            try:
                result = process_func(file_path, source_path, **kwargs)
                if result:
                    processed_files += 1
                    total_chunks += result.get("chunks_created", 0)
            except Exception as e:
                error_msg = f"Error processing file {file_path}: {e}"
                logger.error(error_msg)
                errors.append(error_msg)
        
        return {
            "files_processed": processed_files,
            "chunks_created": total_chunks,
            "errors": errors
        }
    
    def get_optimal_worker_count(self, file_count: int) -> int:
        """
        Determine optimal number of workers based on file count.
        
        Args:
            file_count: Number of files to process
            
        Returns:
            Optimal number of workers
        """
        if file_count <= 4:
            return max(1, file_count)
        elif file_count <= 20:
            return min(self.max_workers, 4)
        else:
            return min(self.max_workers, 8)
    
    def estimate_processing_time(self, file_count: int, avg_time_per_file: float) -> float:
        """
        Estimate total processing time for parallel execution.
        
        Args:
            file_count: Number of files to process
            avg_time_per_file: Average time per file in seconds
            
        Returns:
            Estimated total time in seconds
        """
        optimal_workers = self.get_optimal_worker_count(file_count)
        parallel_time = (file_count * avg_time_per_file) / optimal_workers
        return parallel_time
