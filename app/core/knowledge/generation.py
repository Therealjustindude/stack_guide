"""
Answer Generation - Handles LLM integration and response creation.

This module generates answers to user queries using retrieved documents and
creates actionable steps based on the question type and content.
"""

import logging
from typing import List, Dict, Any
import re

from .models import SearchResult

logger = logging.getLogger(__name__)


class AnswerGenerator:
    """Generates answers to user queries using retrieved documents."""
    
    def __init__(self):
        """Initialize the answer generator."""
        pass
    
    def generate_answer(self, question: str, search_results: List[SearchResult]) -> str:
        """
        Generate a comprehensive answer to a user query.
        
        Args:
            question: User's question
            search_results: Retrieved relevant documents
            
        Returns:
            Generated answer with actionable steps
        """
        if not search_results:
            return "I couldn't find any relevant information to answer your question."
        
        try:
            # Analyze question type to determine response structure
            question_type = self._analyze_question_type(question)
            
            # Generate main answer content
            main_content = self._generate_main_content(question, search_results)
            
            # Generate actionable steps based on question type
            actionable_steps = self._generate_actionable_steps(question, search_results, question_type)
            
            # Combine content
            answer = self._combine_answer_parts(main_content, actionable_steps, search_results)
            
            logger.debug(f"Generated answer for '{question[:50]}...' with {len(search_results)} sources")
            return answer
            
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return f"Sorry, I encountered an error while generating an answer: {str(e)}"
    
    def _analyze_question_type(self, question: str) -> str:
        """
        Analyze the question to determine its type and response structure.
        
        Args:
            question: User's question
            
        Returns:
            Question type for response generation
        """
        question_lower = question.lower()
        
        if any(word in question_lower for word in ['how', 'install', 'setup', 'run', 'start']):
            return "how_to"
        elif any(word in question_lower for word in ['what', 'is', 'are', 'does', 'do']):
            return "what_is"
        elif any(word in question_lower for word in ['where', 'find', 'locate']):
            return "where"
        elif any(word in question_lower for word in ['config', 'environment', 'env', 'settings']):
            return "config"
        elif any(word in question_lower for word in ['command', 'script', 'bash', 'terminal']):
            return "command"
        else:
            return "general"
    
    def _generate_main_content(self, question: str, search_results: List[SearchResult]) -> str:
        """
        Generate the main content of the answer.
        
        Args:
            question: User's question
            search_results: Retrieved documents
            
        Returns:
            Main answer content
        """
        # Combine content from top results
        combined_content = ""
        max_content_length = 3000
        
        for i, result in enumerate(search_results[:3]):  # Top 3 results
            content = result.content.strip()
            
            # Truncate content if needed
            if len(content) > 1000:
                content = self._smart_truncate(content, 1000)
            
            # Add content with separator
            if combined_content:
                combined_content += "\n\n---\n\n"
            
            combined_content += f"**Source {i+1}:** {content}"
            
            # Check if we're approaching the limit
            if len(combined_content) > max_content_length:
                break
        
        return combined_content
    
    def _smart_truncate(self, content: str, max_length: int) -> str:
        """
        Intelligently truncate content while preserving structure.
        
        Args:
            content: Content to truncate
            max_length: Maximum length
            
        Returns:
            Truncated content
        """
        if len(content) <= max_length:
            return content
        
        # Try to break at code blocks first
        if '```' in content:
            parts = content.split('```')
            truncated = ""
            for i, part in enumerate(parts):
                if i % 2 == 0:  # Non-code parts
                    if len(truncated + part) > max_length:
                        break
                    truncated += part
                else:  # Code parts
                    if len(truncated + '```' + part + '```') > max_length:
                        break
                    truncated += '```' + part + '```'
            
            if truncated:
                return truncated + "..."
        
        # Try to break at sentences
        sentences = re.split(r'[.!?]+', content)
        truncated = ""
        for sentence in sentences:
            if len(truncated + sentence + '.') > max_length:
                break
            truncated += sentence + '.'
        
        if truncated:
            return truncated + "..."
        
        # Fallback to simple truncation
        return content[:max_length-3] + "..."
    
    def _generate_actionable_steps(self, question: str, search_results: List[SearchResult], question_type: str) -> str:
        """
        Generate actionable steps based on question type.
        
        Args:
            question: User's question
            search_results: Retrieved documents
            question_type: Type of question
            
        Returns:
            Actionable steps section
        """
        if question_type == "how_to":
            return self._generate_how_to_steps(question, search_results)
        elif question_type == "config":
            return self._generate_configuration_steps(question, search_results)
        elif question_type == "command":
            return self._generate_command_steps(question, search_results)
        else:
            return self._generate_general_steps(question, search_results)
    
    def _generate_how_to_steps(self, question: str, search_results: List[SearchResult]) -> str:
        """Generate step-by-step instructions for how-to questions."""
        steps = []
        
        # Look for setup/installation content
        for result in search_results:
            content = result.content.lower()
            if any(term in content for term in ['install', 'setup', 'run', 'start']):
                # Extract numbered or bulleted steps
                lines = result.content.split('\n')
                for line in lines:
                    line = line.strip()
                    if re.match(r'^[\d\-*]+\.?\s+', line) and len(line) > 10:
                        steps.append(line)
        
        if steps:
            return "\n\n## 🚀 Setup Instructions\n\n" + "\n".join(steps[:5])
        else:
            return "\n\n## 🚀 Setup Instructions\n\nBased on the available documentation, here are the general steps:\n\n1. Review the project structure and requirements\n2. Install dependencies as specified\n3. Configure environment variables\n4. Run the application"
    
    def _generate_configuration_steps(self, question: str, search_results: List[SearchResult]) -> str:
        """Generate configuration and environment setup steps."""
        config_info = []
        
        for result in search_results:
            content = result.content
            # Look for environment variables, config files, etc.
            env_vars = re.findall(r'[A-Z_]+=[^\s]+', content)
            config_files = re.findall(r'config\.(?:json|yaml|yml|ini|toml)', content, re.IGNORECASE)
            
            if env_vars:
                config_info.extend([f"`{var}`" for var in env_vars[:5]])
            if config_files:
                config_info.append(f"Configuration file: `{config_files[0]}`")
        
        if config_info:
            return "\n\n## ⚙️ Configuration\n\n" + "\n".join(config_info)
        else:
            return "\n\n## ⚙️ Configuration\n\nCheck the project documentation for configuration requirements and environment variables."
    
    def _generate_command_steps(self, question: str, search_results: List[SearchResult]) -> str:
        """Generate command-line instructions."""
        commands = []
        
        for result in search_results:
            content = result.content
            # Look for command patterns
            cmd_patterns = re.findall(r'`([^`]+)`', content)
            for cmd in cmd_patterns:
                if any(term in cmd.lower() for term in ['git', 'npm', 'pip', 'docker', 'make', 'python', 'node']):
                    commands.append(f"```bash\n{cmd}\n```")
        
        if commands:
            return "\n\n## 💻 Commands\n\n" + "\n".join(commands[:3])
        else:
            return "\n\n## 💻 Commands\n\nCheck the project README or documentation for specific commands."
    
    def _generate_general_steps(self, question: str, search_results: List[SearchResult]) -> str:
        """Generate general guidance steps."""
        return "\n\n## 📋 Next Steps\n\n1. Review the retrieved documentation\n2. Check source files for additional context\n3. Consult project-specific documentation if available"
    
    def _combine_answer_parts(self, main_content: str, actionable_steps: str, search_results: List[SearchResult]) -> str:
        """
        Combine all answer parts into a final response.
        
        Args:
            main_content: Main answer content
            actionable_steps: Actionable steps section
            search_results: Source documents
            
        Returns:
            Complete formatted answer
        """
        # Create source attribution
        source_attribution = self._create_source_attribution(search_results)
        
        # Combine all parts
        answer_parts = [
            main_content,
            actionable_steps,
            source_attribution
        ]
        
        return "\n".join(filter(None, answer_parts))
    
    def _create_source_attribution(self, search_results: List[SearchResult]) -> str:
        """
        Create source attribution section.
        
        Args:
            search_results: Source documents
            
        Returns:
            Formatted source attribution
        """
        if not search_results:
            return ""
        
        sources = []
        for i, result in enumerate(search_results[:3]):  # Top 3 sources
            source_name = result.source
            score = result.score
            
            # Clean up source name
            if source_name.startswith('/host/'):
                source_name = source_name[6:]  # Remove /host/ prefix
            
            sources.append(f"{i+1}. **{source_name}** (Relevance: {score:.2f})")
        
        return f"\n\n## 📚 Sources\n\n" + "\n".join(sources)
    
    def get_answer_summary(self, answer: str) -> Dict[str, Any]:
        """
        Get a summary of the generated answer.
        
        Args:
            answer: Generated answer
            
        Returns:
            Summary statistics
        """
        return {
            "length": len(answer),
            "has_steps": "Setup Instructions" in answer or "Configuration" in answer,
            "has_commands": "Commands" in answer,
            "has_sources": "Sources" in answer,
            "sections": len([part for part in answer.split('\n\n') if part.strip()])
        }
