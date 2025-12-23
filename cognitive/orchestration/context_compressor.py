"""
Context Compressor

Manages context window efficiency by compressing and prioritizing
information for reasoning systems.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum


class ContextPriority(Enum):
    """Priority levels for context elements."""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    BACKGROUND = 5


@dataclass
class ContextElement:
    """An element of context."""
    id: str
    content: str
    priority: ContextPriority
    source: str
    relevance_score: float
    token_count: int


@dataclass
class CompressedContext:
    """Compressed context ready for use."""
    elements: List[ContextElement]
    total_tokens: int
    compression_ratio: float
    dropped_elements: int


class ContextCompressor:
    """
    Compresses context to fit within token limits.
    """
    
    def __init__(self, max_tokens: int = 8000):
        """
        Initialize compressor with token limit.
        
        Args:
            max_tokens: Maximum tokens in compressed context
        """
        self._max_tokens = max_tokens
    
    def compress(
        self,
        elements: List[ContextElement],
        target_tokens: Optional[int] = None
    ) -> CompressedContext:
        """
        Compress context elements to fit token limit.
        
        Args:
            elements: Context elements to compress
            target_tokens: Target token count (defaults to max)
            
        Returns:
            CompressedContext with selected elements
        """
        target = target_tokens or self._max_tokens
        
        # Sort by priority and relevance
        sorted_elements = sorted(
            elements,
            key=lambda e: (e.priority.value, -e.relevance_score)
        )
        
        selected = []
        total_tokens = 0
        dropped = 0
        
        for element in sorted_elements:
            if total_tokens + element.token_count <= target:
                selected.append(element)
                total_tokens += element.token_count
            else:
                dropped += 1
        
        original_tokens = sum(e.token_count for e in elements)
        compression_ratio = total_tokens / original_tokens if original_tokens > 0 else 1.0
        
        return CompressedContext(
            elements=selected,
            total_tokens=total_tokens,
            compression_ratio=compression_ratio,
            dropped_elements=dropped
        )
    
    def prioritize(
        self,
        elements: List[ContextElement],
        query: str
    ) -> List[ContextElement]:
        """
        Reprioritize elements based on query relevance.
        
        Args:
            elements: Elements to reprioritize
            query: Query to assess relevance against
            
        Returns:
            Elements with updated relevance scores
        """
        for element in elements:
            element.relevance_score = self._compute_relevance(element, query)
        return elements
    
    def _compute_relevance(self, element: ContextElement, query: str) -> float:
        """Compute relevance of element to query."""
        # TODO: Implement semantic relevance computation
        return 0.5
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text."""
        # Rough approximation: ~4 characters per token
        return len(text) // 4
