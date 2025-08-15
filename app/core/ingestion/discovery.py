"""
Auto-Discovery - Automatically finds and configures projects from common paths.

This module scans configured directories to discover coding projects and automatically
adds them as data sources for ingestion.
"""

import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class ProjectDiscovery:
    """Automatically discovers coding projects from common paths."""
    
    def __init__(self):
        """Initialize the project discovery system."""
        # Common project indicator files
        self.project_indicators = [
            'README.md', 'README.txt', 'package.json', 'requirements.txt', 
            'setup.py', 'pyproject.toml', 'Cargo.toml', 'go.mod', 'pom.xml',
            'build.gradle', 'Makefile', 'Dockerfile', '.git', '.gitignore',
            'src', 'lib', 'app', 'main.py', 'index.js', 'main.go'
        ]
    
    def discover_projects_from_paths(self, common_paths: List[str]) -> List[Dict[str, Any]]:
        """
        Discover projects from a list of common paths.
        
        Args:
            common_paths: List of path patterns to scan (e.g., ['~/Development'])
            
        Returns:
            List of discovered project configurations
        """
        discovered_projects = []
        
        for path_pattern in common_paths:
            try:
                # Expand user path (e.g., ~/Development -> /Users/username/Development)
                expanded_path = os.path.expanduser(path_pattern)
                
                # Map to container path if it's a user path
                container_path = self._map_to_container_path(path_pattern, expanded_path)
                
                logger.info(f"Scanning auto-discovery path: {path_pattern} -> {container_path}")
                
                if os.path.exists(container_path):
                    # Find projects in this directory
                    projects = self._discover_projects_in_directory(container_path)
                    discovered_projects.extend(projects)
                else:
                    logger.warning(f"Auto-discovery path does not exist: {container_path}")
                    
            except Exception as e:
                logger.error(f"Error scanning auto-discovery path {path_pattern}: {e}")
        
        logger.info(f"Auto-discovery complete. Found {len(discovered_projects)} projects")
        return discovered_projects
    
    def _map_to_container_path(self, path_pattern: str, expanded_path: str) -> str:
        """
        Map a user path to the corresponding container path.
        
        Args:
            path_pattern: Original path pattern (e.g., ~/Development)
            expanded_path: Expanded absolute path
            
        Returns:
            Container path for the directory
        """
        if path_pattern.startswith('~'):
            # For user paths, we need to map to the /host mount
            # Since we're using ..:/host, we need to handle the path mapping correctly
            # The ..:/host maps the parent directory to /host
            # So ~/Development/my_code becomes /host (which contains all projects)
            if 'Development' in expanded_path:
                # For Development paths, map to /host since that's where all projects are
                return "/host"
            else:
                # For other paths, try to map them appropriately
                return f"/host{expanded_path.replace(os.path.expanduser('~'), '')}"
        else:
            return expanded_path
    
    def _discover_projects_in_directory(self, directory_path: str) -> List[Dict[str, Any]]:
        """
        Discover projects in a directory by looking for common project indicators.
        
        Args:
            directory_path: Path to scan for projects
            
        Returns:
            List of discovered project configurations
        """
        projects = []
        
        try:
            if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
                return projects
            
            # List contents of the directory
            for item in os.listdir(directory_path):
                item_path = os.path.join(directory_path, item)
                
                if not os.path.isdir(item_path):
                    continue
                
                # Check if this looks like a project by looking for common project files
                if self._is_project_directory(item_path):
                    project_name = item
                    project_description = self._generate_project_description(item_path)
                    
                    projects.append({
                        "path": item_path,
                        "name": project_name,
                        "description": project_description,
                        "type": "local",
                        "enabled": True
                    })
                    
        except Exception as e:
            logger.error(f"Error discovering projects in {directory_path}: {e}")
        
        return projects
    
    def _is_project_directory(self, directory_path: str) -> bool:
        """
        Check if a directory looks like a project by looking for common project files.
        
        Args:
            directory_path: Path to check
            
        Returns:
            True if directory appears to be a project
        """
        try:
            # Check for any of these indicators
            for indicator in self.project_indicators:
                indicator_path = os.path.join(directory_path, indicator)
                if os.path.exists(indicator_path):
                    return True
            
            # Also check if it's a git repository
            git_path = os.path.join(directory_path, '.git')
            if os.path.exists(git_path) and os.path.isdir(git_path):
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking if {directory_path} is a project: {e}")
            return False
    
    def _generate_project_description(self, project_path: str) -> str:
        """
        Generate a description for a discovered project.
        
        Args:
            project_path: Path to the project
            
        Returns:
            Generated description
        """
        try:
            # Try to read README for description
            readme_files = ['README.md', 'README.txt', 'README']
            for readme in readme_files:
                readme_path = os.path.join(project_path, readme)
                if os.path.exists(readme_path):
                    try:
                        with open(readme_path, 'r', encoding='utf-8') as f:
                            content = f.read(500)  # Read first 500 chars
                            # Extract first meaningful line
                            lines = content.split('\n')
                            for line in lines:
                                line = line.strip()
                                if line and not line.startswith('#') and not line.startswith('<!--'):
                                    return line[:100] + "..." if len(line) > 100 else line
                    except Exception:
                        pass
            
            # Fallback: check for package.json or similar
            package_files = ['package.json', 'pyproject.toml', 'Cargo.toml', 'go.mod']
            for package_file in package_files:
                package_path = os.path.join(project_path, package_file)
                if os.path.exists(package_path):
                    return f"Project with {package_file}"
            
            # Final fallback
            return "Discovered project directory"
            
        except Exception as e:
            logger.error(f"Error generating description for {project_path}: {e}")
            return "Discovered project directory"
    
    def get_project_stats(self, projects: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get statistics about discovered projects.
        
        Args:
            projects: List of discovered projects
            
        Returns:
            Dictionary with project statistics
        """
        if not projects:
            return {"total_projects": 0, "by_type": {}}
        
        # Count by project type indicators
        by_type = {}
        for project in projects:
            project_path = project["path"]
            
            # Determine project type based on indicators
            project_type = self._determine_project_type(project_path)
            by_type[project_type] = by_type.get(project_type, 0) + 1
        
        return {
            "total_projects": len(projects),
            "by_type": by_type
        }
    
    def _determine_project_type(self, project_path: str) -> str:
        """Determine the type of project based on its contents."""
        try:
            if os.path.exists(os.path.join(project_path, 'package.json')):
                return "Node.js"
            elif os.path.exists(os.path.join(project_path, 'requirements.txt')):
                return "Python"
            elif os.path.exists(os.path.join(project_path, 'Cargo.toml')):
                return "Rust"
            elif os.path.exists(os.path.join(project_path, 'go.mod')):
                return "Go"
            elif os.path.exists(os.path.join(project_path, 'pom.xml')):
                return "Java"
            elif os.path.exists(os.path.join(project_path, '.git')):
                return "Git Repository"
            else:
                return "Unknown"
        except Exception:
            return "Unknown"
