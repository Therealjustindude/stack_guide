"""
Document Parser - Handles parsing of different file types into searchable chunks.

This module parses various document formats and creates semantic chunks
that can be stored in the vector database for retrieval.
"""

import re
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class DocumentParser:
    """Parses documents into searchable text chunks."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize the document parser.
        
        Args:
            chunk_size: Maximum size of each chunk in characters
            chunk_overlap: Overlap between chunks in characters
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def parse_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Parse a file and return chunks with metadata.
        
        Args:
            file_path: Path to the file to parse
            
        Returns:
            List of chunks with content and metadata
        """
        try:
            # Determine file type and parse accordingly
            file_extension = file_path.suffix.lower()
            
            if file_extension in ['.md', '.markdown']:
                return self._parse_markdown(file_path)
            elif file_extension in ['.txt', '.log']:
                return self._parse_text(file_path)
            elif file_extension in ['.json']:
                return self._parse_json(file_path)
            elif file_extension in ['.yaml', '.yml']:
                return self._parse_yaml(file_path)
            elif file_extension in ['.xml']:
                return self._parse_xml(file_path)
            elif file_extension in ['.ini', '.cfg', '.conf']:
                return self._parse_ini(file_path)
            elif file_extension in ['.sql']:
                return self._parse_sql(file_path)
            elif file_extension in ['.csv']:
                return self._parse_csv(file_path)
            elif file_extension in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.h']:
                return self._parse_code(file_path)
            else:
                # Try to parse as text for unknown types
                return self._parse_text(file_path)
                
        except Exception as e:
            logger.error(f"Error parsing file {file_path}: {e}")
            return []
    
    def _parse_markdown(self, file_path: Path) -> List[Dict[str, Any]]:
        """Parse Markdown files with section awareness."""
        try:
            content = file_path.read_text(encoding='utf-8')
            chunks = []
            
            # Split by headers to maintain semantic structure
            sections = re.split(r'^(#{1,6}\s+.+)$', content, flags=re.MULTILINE)
            
            current_section = ""
            current_header = "Document"
            
            for section in sections:
                if section.strip():
                    if section.startswith('#'):
                        # This is a header
                        current_header = section.strip()
                        current_section = ""
                    else:
                        # This is content
                        current_section = section.strip()
                        if current_section:
                            # Create chunks from this section
                            section_chunks = self._create_chunks(
                                current_section, 
                                file_path, 
                                current_header
                            )
                            chunks.extend(section_chunks)
            
            return chunks
            
        except Exception as e:
            logger.error(f"Error parsing Markdown file {file_path}: {e}")
            return []
    
    def _parse_text(self, file_path: Path) -> List[Dict[str, Any]]:
        """Parse plain text files."""
        try:
            content = file_path.read_text(encoding='utf-8')
            return self._create_chunks(content, file_path, "Text Document")
        except Exception as e:
            logger.error(f"Error parsing text file {file_path}: {e}")
            return []
    
    def _parse_json(self, file_path: Path) -> List[Dict[str, Any]]:
        """Parse JSON files."""
        try:
            import json
            content = file_path.read_text(encoding='utf-8')
            data = json.loads(content)
            
            # Convert JSON to readable text
            json_text = json.dumps(data, indent=2)
            return self._create_chunks(json_text, file_path, "JSON Document")
            
        except Exception as e:
            logger.error(f"Error parsing JSON file {file_path}: {e}")
            return []
    
    def _parse_yaml(self, file_path: Path) -> List[Dict[str, Any]]:
        """Parse YAML files."""
        try:
            import yaml
            content = file_path.read_text(encoding='utf-8')
            data = yaml.safe_load(content)
            
            # Convert YAML to readable text
            yaml_text = yaml.dump(data, default_flow_style=False)
            return self._create_chunks(yaml_text, file_path, "YAML Document")
            
        except Exception as e:
            logger.error(f"Error parsing YAML file {file_path}: {e}")
            return []
    
    def _parse_xml(self, file_path: Path) -> List[Dict[str, Any]]:
        """Parse XML files."""
        try:
            from xml.etree import ElementTree
            tree = ElementTree.parse(file_path)
            root = tree.getroot()
            
            # Convert XML to readable text
            xml_text = ElementTree.tostring(root, encoding='unicode', method='xml')
            return self._create_chunks(xml_text, file_path, "XML Document")
            
        except Exception as e:
            logger.error(f"Error parsing XML file {file_path}: {e}")
            return []
    
    def _parse_ini(self, file_path: Path) -> List[Dict[str, Any]]:
        """Parse INI configuration files."""
        try:
            import configparser
            config = configparser.ConfigParser()
            config.read(file_path)
            
            # Convert INI to readable text
            ini_text = ""
            for section in config.sections():
                ini_text += f"[{section}]\n"
                for key, value in config.items(section):
                    ini_text += f"{key} = {value}\n"
                ini_text += "\n"
            
            return self._create_chunks(ini_text, file_path, "Configuration File")
            
        except Exception as e:
            logger.error(f"Error parsing INI file {file_path}: {e}")
            return []
    
    def _parse_sql(self, file_path: Path) -> List[Dict[str, Any]]:
        """Parse SQL files."""
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Split by semicolons to separate statements
            statements = [stmt.strip() for stmt in content.split(';') if stmt.strip()]
            
            chunks = []
            for i, statement in enumerate(statements):
                if statement:
                    chunk = {
                        "content": statement,
                        "metadata": {
                            "file_path": str(file_path),
                            "file_name": file_path.name,
                            "file_type": "sql",
                            "chunk_type": "sql_statement",
                            "statement_index": i,
                            "total_statements": len(statements)
                        }
                    }
                    chunks.append(chunk)
            
            return chunks
            
        except Exception as e:
            logger.error(f"Error parsing SQL file {file_path}: {e}")
            return []
    
    def _parse_csv(self, file_path: Path) -> List[Dict[str, Any]]:
        """Parse CSV files."""
        try:
            import csv
            content = file_path.read_text(encoding='utf-8')
            
            # Parse CSV and convert to readable text
            csv_text = ""
            reader = csv.reader(content.splitlines())
            
            for i, row in enumerate(reader):
                if i == 0:  # Header row
                    csv_text += " | ".join(row) + "\n"
                    csv_text += "-" * (len(" | ".join(row))) + "\n"
                else:
                    csv_text += " | ".join(row) + "\n"
            
            return self._create_chunks(csv_text, file_path, "CSV Document")
            
        except Exception as e:
            logger.error(f"Error parsing CSV file {file_path}: {e}")
            return []
    
    def _parse_code(self, file_path: Path) -> List[Dict[str, Any]]:
        """Parse code files with function/class awareness."""
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # For code files, try to maintain function/class boundaries
            # This is a simplified approach - could be enhanced with AST parsing
            lines = content.split('\n')
            chunks = []
            current_chunk = []
            
            for line in lines:
                current_chunk.append(line)
                
                # Check if we've reached a natural boundary
                if (line.strip().startswith(('def ', 'class ', 'function ', 'public ', 'private ')) or
                    line.strip().startswith('}') or
                    line.strip().startswith('end')):
                    
                    if current_chunk:
                        chunk_text = '\n'.join(current_chunk)
                        if len(chunk_text.strip()) > 50:  # Only add substantial chunks
                            chunk = {
                                "content": chunk_text,
                                "metadata": {
                                    "file_path": str(file_path),
                                    "file_name": file_path.name,
                                    "file_type": "code",
                                    "chunk_type": "code_block",
                                    "language": file_path.suffix[1:] if file_path.suffix else "unknown"
                                }
                            }
                            chunks.append(chunk)
                        current_chunk = []
            
            # Add any remaining content
            if current_chunk:
                chunk_text = '\n'.join(current_chunk)
                if len(chunk_text.strip()) > 50:
                    chunk = {
                        "content": chunk_text,
                        "metadata": {
                            "file_path": str(file_path),
                            "file_name": file_path.name,
                            "file_type": "code",
                            "chunk_type": "code_block",
                            "language": file_path.suffix[1:] if file_path.suffix else "unknown"
                        }
                    }
                    chunks.append(chunk)
            
            return chunks
            
        except Exception as e:
            logger.error(f"Error parsing code file {file_path}: {e}")
            return []
    
    def _create_chunks(self, text: str, file_path: Path, doc_type: str) -> List[Dict[str, Any]]:
        """
        Create chunks from text with proper overlap.
        
        Args:
            text: Text content to chunk
            file_path: Path to the source file
            doc_type: Type of document
            
        Returns:
            List of chunks with content and metadata
        """
        if not text.strip():
            return []
        
        chunks = []
        start = 0
        
        while start < len(text):
            # Determine chunk end
            end = start + self.chunk_size
            
            # Try to find a good break point (sentence or paragraph boundary)
            if end < len(text):
                # Look for sentence endings
                for i in range(end, max(start + self.chunk_size - 100, start), -1):
                    if text[i] in '.!?':
                        end = i + 1
                        break
                
                # If no sentence boundary found, look for paragraph breaks
                if end == start + self.chunk_size:
                    for i in range(end, max(start + self.chunk_size - 50, start), -1):
                        if text[i] == '\n' and (i + 1 >= len(text) or text[i + 1] == '\n'):
                            end = i + 1
                            break
            
            # Extract chunk content
            chunk_content = text[start:end].strip()
            
            if chunk_content:
                chunk = {
                    "content": chunk_content,
                    "metadata": {
                        "file_path": str(file_path),
                        "file_name": file_path.name,
                        "file_type": file_path.suffix[1:] if file_path.suffix else "unknown",
                        "chunk_type": doc_type,
                        "chunk_start": start,
                        "chunk_end": end,
                        "total_length": len(text)
                    }
                }
                chunks.append(chunk)
            
            # Move to next chunk with overlap
            start = end - self.chunk_overlap
            if start >= len(text):
                break
        
        return chunks
