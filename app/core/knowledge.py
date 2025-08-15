"""
Core knowledge engine for StackGuide RAG pipeline.
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import chromadb
from chromadb.config import Settings

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Result from a document search."""
    content: str
    metadata: Dict[str, Any]
    score: float
    source: str


@dataclass
class QueryResponse:
    """Response to a user query."""
    answer: str
    sources: List[SearchResult]
    confidence: float


class KnowledgeEngine:
    """Core knowledge engine for querying and retrieving information."""
    
    def __init__(self, chroma_host: str = "chroma", chroma_port: int = 8000):
        """Initialize the knowledge engine."""
        self.chroma_client = chromadb.HttpClient(
            host=chroma_host,
            port=chroma_port,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create the main collection
        try:
            self.collection = self.chroma_client.get_collection("stackguide_docs")
            logger.info("Connected to existing Chroma collection")
        except Exception:
            self.collection = self.chroma_client.create_collection("stackguide_docs")
            logger.info("Created new Chroma collection")
    
    def query(self, question: str, max_results: int = 5) -> QueryResponse:
        """
        Process a user query and return an answer with sources.
        
        Args:
            question: User's question
            max_results: Maximum number of source documents to retrieve
            
        Returns:
            QueryResponse with answer and sources
        """
        try:
            # Step 1: Retrieve relevant documents
            search_results = self._retrieve_documents(question, max_results)
            
            if not search_results:
                return QueryResponse(
                    answer="I couldn't find any relevant information to answer your question. Try rephrasing or adding more data sources.",
                    sources=[],
                    confidence=0.0
                )
            
            # Step 2: Generate answer using LLM (placeholder for now)
            answer = self._generate_answer(question, search_results)
            
            # Step 3: Return response with sources
            return QueryResponse(
                answer=answer,
                sources=search_results,
                confidence=self._calculate_confidence(search_results, question)
            )
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return QueryResponse(
                answer=f"Sorry, I encountered an error while processing your question: {str(e)}",
                sources=[],
                confidence=0.0
            )
    
    def _retrieve_documents(self, question: str, max_results: int) -> List[SearchResult]:
        """Retrieve relevant documents using vector similarity search."""
        try:
            # Use the question as the query vector
            results = self.collection.query(
                query_texts=[question],
                n_results=max_results,
                include=["documents", "metadatas", "distances"]
            )
            
            search_results = []
            if results["documents"] and results["documents"][0]:
                for i, (doc, metadata, distance) in enumerate(zip(
                    results["documents"][0],
                    results["metadatas"][0],
                    results["distances"][0]
                )):
                    # Convert distance to similarity score (0-1, higher is better)
                    score = 1.0 - (distance / 2.0)  # Normalize distance to score
                    
                    search_results.append(SearchResult(
                        content=doc,
                        metadata=metadata or {},
                        score=score,
                        source=metadata.get("source_file", "Unknown") if metadata else "Unknown"
                    ))
            
            # Sort by relevance score
            search_results.sort(key=lambda x: x.score, reverse=True)
            
            logger.info(f"Retrieved {len(search_results)} documents for query: {question}")
            return search_results
            
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            return []
    
    def _calculate_confidence(self, search_results: List[SearchResult], question: str) -> float:
        """Calculate confidence score based on search results and query analysis."""
        if not search_results:
            return 0.0
        
        # Get the top result score (most important)
        top_score = search_results[0].score
        
        # Calculate score distribution quality
        score_variance = 0.0
        if len(search_results) > 1:
            scores = [r.score for r in search_results[:5]]  # Top 5 scores
            mean_score = sum(scores) / len(scores)
            score_variance = sum((s - mean_score) ** 2 for s in scores) / len(scores)
        
        # Calculate result count bonus (more results = higher confidence)
        result_count_bonus = min(len(search_results) / 5.0, 0.2)  # Max 20% bonus
        
        # Calculate content quality indicators
        content_quality = 0.0
        if search_results:
            # Check if top result has good metadata
            top_metadata = search_results[0].metadata
            if top_metadata.get('section') and top_metadata.get('source_file'):
                content_quality += 0.1
            
            # Check content length (not too short, not too long)
            content_length = len(search_results[0].content)
            if 100 <= content_length <= 2000:
                content_quality += 0.1
        
        # Calculate final confidence using multiple factors
        base_confidence = top_score * 0.6  # Top score is 60% of confidence
        
        # Score consistency bonus (lower variance = higher confidence)
        consistency_bonus = max(0, (0.5 - score_variance) * 0.2) if score_variance > 0 else 0.1
        
        # Combine all factors
        final_confidence = (
            base_confidence + 
            consistency_bonus + 
            result_count_bonus + 
            content_quality
        )
        
        # Ensure confidence is between 0 and 1
        return min(max(final_confidence, 0.0), 1.0)
    
    def _generate_answer(self, question: str, search_results: List[SearchResult]) -> str:
        """Generate a helpful answer using the retrieved documents."""
        if not search_results:
            return "I couldn't find any relevant information to answer your question. Try rephrasing or adding more data sources."
        
        # Get the top result for primary answer
        top_result = search_results[0]
        
        # Extract meaningful source information
        source_file = top_result.metadata.get('source_file', 'Unknown file')
        file_name = source_file.split('/')[-1] if source_file != 'Unknown file' else 'Unknown'
        section = top_result.metadata.get('section', '')
        
        # Analyze the question type to provide better responses
        question_lower = question.lower()
        is_how_to = any(word in question_lower for word in ['how', 'setup', 'install', 'configure', 'start', 'run'])
        is_what_is = any(word in question_lower for word in ['what', 'explain', 'describe', 'define'])
        is_where = any(word in question_lower for word in ['where', 'location', 'find', 'locate'])
        is_config = any(word in question_lower for word in ['config', 'environment', 'env', 'variable', 'setting'])
        
        # Build a cleaner, more focused answer
        if is_how_to:
            answer = f"## 🚀 Setup Instructions\n\n"
        elif is_config:
            answer = f"## ⚙️ Configuration\n\n"
        elif is_what_is:
            answer = f"## 📚 Information\n\n"
        elif is_where:
            answer = f"## 📍 Location\n\n"
        else:
            answer = f"## 💡 Answer\n\n"
        
        # Add the most relevant content with better formatting
        content = top_result.content.strip()
        
        # If it's a how-to question, try to extract steps or procedures
        if is_how_to and ('step' in content.lower() or 'install' in content.lower() or 'setup' in content.lower()):
            # Look for numbered or bulleted content
            lines = content.split('\n')
            formatted_content = []
            for line in lines:
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-') or line.startswith('*')):
                    formatted_content.append(line)
                elif line and any(keyword in line.lower() for keyword in ['install', 'setup', 'configure', 'run']):
                    formatted_content.append(f"• {line}")
                else:
                    formatted_content.append(line)
            
            if formatted_content:
                content = '\n'.join(formatted_content)
        
        # Truncate content intelligently - allow much longer content
        if len(content) > 3000:  # Increased from 1000 to 3000
            # Try to find a good break point
            truncated = content[:3000]
            last_period = truncated.rfind('.')
            last_newline = truncated.rfind('\n')
            last_command = truncated.rfind('```')
            
            # Prefer breaking at command blocks, then sentences, then lines
            if last_command > 2500:
                content = truncated[:last_command] + "```\n..."
            elif last_period > 2500:
                content = truncated[:last_period + 1]
            elif last_newline > 2500:
                content = truncated[:last_newline]
            else:
                content = truncated + "..."
        
        answer += f"{content}\n\n"
        
        # Generate specific, actionable steps based on question type and context
        if is_how_to or is_config:
            answer += self._generate_actionable_steps(question, search_results, file_name)
        
        # Add clean source attribution
        answer += f"**Source**: {file_name}"
        if section:
            answer += f" ({section})"
        answer += f"\n"
        
        # If we have multiple results, provide a brief summary
        if len(search_results) > 1:
            answer += f"\n**Additional sources**: {len(search_results)} relevant documents found\n"
        
        return answer
    
    def _generate_actionable_steps(self, question: str, search_results: List[SearchResult], file_name: str) -> str:
        """Generate specific, actionable steps based on the question and available context."""
        question_lower = question.lower()
        
        # Generate steps based on question type
        if 'install' in question_lower or 'setup' in question_lower:
            return self._generate_installation_steps(question, search_results, file_name)
        elif 'config' in question_lower or 'environment' in question_lower or 'env' in question_lower:
            return self._generate_configuration_steps(question, search_results, file_name)
        elif 'run' in question_lower or 'start' in question_lower:
            return self._generate_runtime_steps(question, search_results, file_name)
        else:
            return self._generate_general_steps(question, search_results, file_name)
    
    def _generate_installation_steps(self, question: str, search_results: List[SearchResult], file_name: str) -> str:
        """Generate installation and setup steps."""
        steps = f"### 🛠️ Quick Setup\n\n"
        
        # Extract any existing setup info from search results
        setup_info = []
        for result in search_results:
            content_lower = result.content.lower()
            if any(word in content_lower for word in ['install', 'setup', 'clone', 'npm', 'pip', 'go get']):
                setup_info.append(result.content)
        
        if setup_info:
            steps += f"**From the documentation:**\n\n"
            # Use actual content if available - show more content
            for i, info in enumerate(setup_info[:2], 1):
                steps += f"{i}. {info[:500]}...\n\n"  # Increased from 200 to 500
        else:
            # Generate common setup patterns
            steps += f"**Standard setup process:**\n\n"
            steps += f"1. **Clone & Install**\n"
            steps += f"   ```bash\n"
            steps += f"   git clone <repository-url>\n"
            steps += f"   cd {file_name.replace('.md', '').replace('.txt', '')}\n"
            steps += f"   npm install  # or pip install -r requirements.txt\n"
            steps += f"   ```\n\n"
            
            steps += f"2. **Configure**\n"
            steps += f"   ```bash\n"
            steps += f"   cp .env.example .env\n"
            steps += f"   # Edit with your settings\n"
            steps += f"   ```\n\n"
        
        return steps
    
    def _generate_configuration_steps(self, question: str, search_results: List[SearchResult], file_name: str) -> str:
        """Generate configuration and environment setup steps."""
        steps = f"### ⚙️ Environment Setup\n\n"
        
        # Look for configuration information in search results
        config_info = []
        for result in search_results:
            content_lower = result.content.lower()
            if any(word in content_lower for word in ['config', 'environment', 'env', 'variable', 'setting', 'api_key']):
                config_info.append(result.content)
        
        if config_info:
            steps += f"**Required environment variables:**\n\n"
            for i, info in enumerate(config_info[:2], 1):
                steps += f"{i}. {info[:500]}...\n\n"
        else:
            # Generate common configuration patterns
            steps += f"**Essential environment variables:**\n\n"
            steps += f"```bash\n"
            steps += f"# Database\n"
            steps += f"DB_HOST=localhost\n"
            steps += f"DB_PORT=5432\n"
            steps += f"DB_NAME=myapp\n"
            steps += f"DB_USER=myuser\n"
            steps += f"DB_PASSWORD=mypassword\n\n"
            steps += f"# API\n"
            steps += f"API_KEY=your_api_key_here\n"
            steps += f"JWT_SECRET=your_jwt_secret\n"
            steps += f"```\n\n"
        
        return steps
    
    def _generate_runtime_steps(self, question: str, search_results: List[SearchResult], file_name: str) -> str:
        """Generate runtime and execution steps."""
        steps = f"### 🚀 Run Commands\n\n"
        
        # Look for runtime information in search results
        runtime_info = []
        for result in search_results:
            content_lower = result.content.lower()
            if any(word in content_lower for word in ['run', 'start', 'serve', 'dev', 'server']):
                runtime_info.append(result.content)
        
        if runtime_info:
            steps += f"**From the documentation:**\n\n"
            for i, info in enumerate(runtime_info[:2], 1):
                steps += f"{i}. {info[:500]}...\n\n"
        else:
            # Generate common runtime patterns
            steps += f"**Common commands:**\n\n"
            steps += f"```bash\n"
            steps += f"# Development\n"
            steps += f"npm run dev     # or python app.py\n"
            steps += f"npm start       # or gunicorn app:app\n\n"
            steps += f"# Testing\n"
            steps += f"npm test        # or python -m pytest\n"
            steps += f"```\n\n"
        
        return steps
    
    def _generate_general_steps(self, question: str, search_results: List[SearchResult], file_name: str) -> str:
        """Generate general helpful steps."""
        steps = f"### 🎯 Next Steps\n\n"
        steps += f"1. Review the information above\n"
        steps += f"2. Check the source file for complete details\n"
        steps += f"3. Execute any setup commands\n"
        steps += f"4. Test your configuration\n\n"
        
        return steps
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the document collection."""
        try:
            count = self.collection.count()
            return {
                "total_documents": count,
                "collection_name": "stackguide_docs",
                "status": "connected"
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {
                "total_documents": 0,
                "collection_name": "stackguide_docs",
                "status": "error",
                "error": str(e)
            }
