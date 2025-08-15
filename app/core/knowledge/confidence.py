"""
Confidence Scoring - Assesses the quality and reliability of search results.

This module calculates confidence scores based on various factors including
similarity scores, result count, content quality, and metadata completeness.
"""

import logging
from typing import List, Dict, Any
import statistics

from .models import SearchResult, ConfidenceMetrics

logger = logging.getLogger(__name__)


class ConfidenceScorer:
    """Calculates confidence scores for search results."""
    
    def __init__(self):
        """Initialize the confidence scorer."""
        pass
    
    def calculate_confidence(self, search_results: List[SearchResult], question: str) -> float:
        """
        Calculate overall confidence score for search results.
        
        Args:
            search_results: List of search results
            question: Original user question
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        if not search_results:
            return 0.0
        
        try:
            # Extract metrics for confidence calculation
            metrics = self._extract_confidence_metrics(search_results, question)
            
            # Calculate weighted confidence score
            confidence = self._calculate_weighted_confidence(metrics)
            
            logger.debug(f"Confidence calculation: {confidence:.3f} based on {len(search_results)} results")
            return confidence
            
        except Exception as e:
            logger.error(f"Error calculating confidence: {e}")
            return 0.5  # Default confidence
    
    def _extract_confidence_metrics(self, search_results: List[SearchResult], question: str) -> ConfidenceMetrics:
        """
        Extract metrics used for confidence calculation.
        
        Args:
            search_results: List of search results
            question: Original user question
            
        Returns:
            ConfidenceMetrics object
        """
        # Get top scores
        top_scores = [result.score for result in search_results[:3]]  # Top 3 scores
        
        # Calculate score variance
        score_variance = statistics.variance(top_scores) if len(top_scores) > 1 else 0.0
        
        # Result count bonus
        result_count = len(search_results)
        
        # Content quality assessment
        content_quality = self._assess_content_quality(search_results)
        
        # Metadata completeness
        metadata_completeness = self._assess_metadata_completeness(search_results)
        
        return ConfidenceMetrics(
            top_scores=top_scores,
            score_variance=score_variance,
            result_count=result_count,
            content_quality=content_quality,
            metadata_completeness=metadata_completeness
        )
    
    def _calculate_weighted_confidence(self, metrics: ConfidenceMetrics) -> float:
        """
        Calculate weighted confidence score from metrics.
        
        Args:
            metrics: Confidence metrics
            
        Returns:
            Weighted confidence score
        """
        # Weighted sum of different factors
        weights = {
            'top_scores': 0.4,      # 40% - Quality of best matches
            'score_variance': 0.2,   # 20% - Consistency of results
            'result_count': 0.2,     # 20% - Number of relevant results
            'content_quality': 0.15, # 15% - Content relevance
            'metadata': 0.05         # 5% - Metadata completeness
        }
        
        # Calculate individual scores
        top_score_avg = sum(metrics.top_scores) / len(metrics.top_scores) if metrics.top_scores else 0.0
        
        # Score variance penalty (lower variance = higher confidence)
        variance_score = max(0.0, 1.0 - metrics.score_variance)
        
        # Result count bonus (more results = higher confidence, up to a point)
        count_score = min(1.0, metrics.result_count / 5.0)  # Cap at 5 results
        
        # Content quality and metadata scores
        content_score = metrics.content_quality
        metadata_score = metrics.metadata_completeness
        
        # Calculate weighted confidence
        confidence = (
            weights['top_scores'] * top_score_avg +
            weights['score_variance'] * variance_score +
            weights['result_count'] * count_score +
            weights['content_quality'] * content_score +
            weights['metadata'] * metadata_score
        )
        
        # Ensure confidence is between 0.0 and 1.0
        return max(0.0, min(1.0, confidence))
    
    def _assess_content_quality(self, search_results: List[SearchResult]) -> float:
        """
        Assess the quality of content in search results.
        
        Args:
            search_results: List of search results
            
        Returns:
            Content quality score between 0.0 and 1.0
        """
        if not search_results:
            return 0.0
        
        quality_scores = []
        
        for result in search_results:
            content = result.content
            score = 0.0
            
            # Length bonus (longer content often more informative)
            if len(content) > 100:
                score += 0.3
            elif len(content) > 50:
                score += 0.2
            elif len(content) > 20:
                score += 0.1
            
            # Code block bonus (code is often more specific)
            if '```' in content or '`' in content:
                score += 0.2
            
            # Structure bonus (headers, lists, etc.)
            if any(char in content for char in ['#', '-', '*', '1.', '2.']):
                score += 0.2
            
            # Technical terms bonus
            technical_terms = ['install', 'setup', 'config', 'run', 'command', 'api', 'database']
            if any(term in content.lower() for term in technical_terms):
                score += 0.3
            
            quality_scores.append(min(1.0, score))
        
        return sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
    
    def _assess_metadata_completeness(self, search_results: List[SearchResult]) -> float:
        """
        Assess the completeness of metadata in search results.
        
        Args:
            search_results: List of search results
            
        Returns:
            Metadata completeness score between 0.0 and 1.0
        """
        if not search_results:
            return 0.0
        
        completeness_scores = []
        
        for result in search_results:
            metadata = result.metadata
            score = 0.0
            
            # Check for key metadata fields
            if metadata.get('source_file'):
                score += 0.4
            
            if metadata.get('file_path'):
                score += 0.3
            
            if metadata.get('chunk_index') is not None:
                score += 0.2
            
            if metadata.get('total_chunks') is not None:
                score += 0.1
            
            completeness_scores.append(score)
        
        return sum(completeness_scores) / len(completeness_scores) if completeness_scores else 0.0
    
    def get_confidence_breakdown(self, search_results: List[SearchResult], question: str) -> Dict[str, Any]:
        """
        Get detailed breakdown of confidence calculation.
        
        Args:
            search_results: List of search results
            question: Original user question
            
        Returns:
            Dictionary with confidence breakdown
        """
        if not search_results:
            return {"overall_confidence": 0.0, "factors": {}, "recommendations": []}
        
        metrics = self._extract_confidence_metrics(search_results, question)
        overall_confidence = self._calculate_weighted_confidence(metrics)
        
        # Analyze factors
        factors = {
            "top_scores": {
                "value": sum(metrics.top_scores) / len(metrics.top_scores) if metrics.top_scores else 0.0,
                "weight": 0.4,
                "description": "Average similarity of top results"
            },
            "score_variance": {
                "value": 1.0 - metrics.score_variance,
                "weight": 0.2,
                "description": "Consistency of result quality"
            },
            "result_count": {
                "value": min(1.0, metrics.result_count / 5.0),
                "weight": 0.2,
                "description": "Number of relevant results found"
            },
            "content_quality": {
                "value": metrics.content_quality,
                "weight": 0.15,
                "description": "Relevance and informativeness of content"
            },
            "metadata_completeness": {
                "value": metrics.metadata_completeness,
                "weight": 0.05,
                "description": "Completeness of result metadata"
            }
        }
        
        # Generate recommendations
        recommendations = self._generate_recommendations(metrics, overall_confidence)
        
        return {
            "overall_confidence": overall_confidence,
            "factors": factors,
            "recommendations": recommendations,
            "metrics": {
                "top_scores": metrics.top_scores,
                "score_variance": metrics.score_variance,
                "result_count": metrics.result_count,
                "content_quality": metrics.content_quality,
                "metadata_completeness": metrics.metadata_completeness
            }
        }
    
    def _generate_recommendations(self, metrics: ConfidenceMetrics, confidence: float) -> List[str]:
        """Generate recommendations for improving confidence."""
        recommendations = []
        
        if confidence < 0.5:
            if metrics.result_count < 3:
                recommendations.append("Try adding more data sources to get more relevant results")
            
            if metrics.content_quality < 0.5:
                recommendations.append("Consider rephrasing your question to be more specific")
            
            if metrics.top_scores and max(metrics.top_scores) < 0.7:
                recommendations.append("The retrieved documents may not be highly relevant to your question")
        
        elif confidence < 0.8:
            if metrics.score_variance > 0.3:
                recommendations.append("Results have varying quality - consider focusing on the highest-scoring matches")
            
            if metrics.metadata_completeness < 0.7:
                recommendations.append("Some result metadata is incomplete, which may affect source attribution")
        
        return recommendations
