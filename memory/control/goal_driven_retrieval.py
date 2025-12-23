"""
Goal-Driven Retrieval

retrieve(m) ⟺ relevance(m, G_t) > ε

Similarity alone is insufficient. Goal relevance dominates.

MMCP-C - Memory Model & Cognitive Persistence.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Tuple, Any


@dataclass(frozen=True)
class RetrievalQuery:
    """Query for memory retrieval."""
    query_id: str
    goal_reference: str
    context: str
    timestamp: datetime


@dataclass(frozen=True)
class RetrievalResult:
    """Result of memory retrieval."""
    query_id: str
    entries: Tuple[Tuple[str, float], ...]  # (entry_id, relevance)
    goal_reference: str
    retrieved_at: datetime


class GoalDrivenRetrieval:
    """
    Goal-Driven Memory Retrieval.
    
    retrieve(m) ⟺ relevance(m, G_t) > ε
    
    Similarity alone is insufficient.
    Goal relevance dominates.
    
    Retrieval is purpose-driven, not pattern-matching.
    """
    
    DEFAULT_THRESHOLD = 0.3  # ε
    
    def __init__(self, threshold: float = DEFAULT_THRESHOLD):
        """Initialize retrieval."""
        self._threshold = threshold
        self._queries: List[RetrievalQuery] = []
        self._results: List[RetrievalResult] = []
    
    def retrieve(
        self,
        goal_reference: str,
        context: str,
        memory_entries: List[Tuple[str, str]],  # (entry_id, content)
    ) -> RetrievalResult:
        """
        Retrieve memories relevant to goal.
        
        Args:
            goal_reference: Current goal
            context: Query context
            memory_entries: Available memories
            
        Returns:
            RetrievalResult
        """
        query_id = f"query_{len(self._queries)}"
        
        query = RetrievalQuery(
            query_id=query_id,
            goal_reference=goal_reference,
            context=context,
            timestamp=datetime.utcnow(),
        )
        self._queries.append(query)
        
        # Compute goal relevance for each entry
        relevant = []
        for entry_id, content in memory_entries:
            relevance = self._compute_goal_relevance(
                content, goal_reference, context
            )
            if relevance > self._threshold:
                relevant.append((entry_id, relevance))
        
        # Sort by relevance
        relevant.sort(key=lambda x: x[1], reverse=True)
        
        result = RetrievalResult(
            query_id=query_id,
            entries=tuple(relevant),
            goal_reference=goal_reference,
            retrieved_at=datetime.utcnow(),
        )
        
        self._results.append(result)
        return result
    
    def _compute_goal_relevance(
        self,
        content: str,
        goal: str,
        context: str,
    ) -> float:
        """
        Compute relevance to goal (not just similarity).
        
        Goal relevance > similarity.
        """
        content_lower = content.lower()
        goal_lower = goal.lower()
        context_lower = context.lower()
        
        # Goal word overlap (primary)
        goal_words = set(goal_lower.split())
        content_words = set(content_lower.split())
        goal_overlap = len(goal_words & content_words) / max(len(goal_words), 1)
        
        # Context overlap (secondary)
        context_words = set(context_lower.split())
        context_overlap = len(context_words & content_words) / max(len(context_words), 1)
        
        # Goal relevance dominates (0.7 weight)
        relevance = 0.7 * goal_overlap + 0.3 * context_overlap
        
        return relevance
    
    def similarity_only_retrieve(self, *args, **kwargs) -> None:
        """FORBIDDEN: Similarity-only retrieval."""
        raise ValueError(
            "Similarity-only retrieval is forbidden. "
            "Goal relevance must dominate. retrieve(m) ⟺ relevance(m, G_t) > ε"
        )
    
    @property
    def threshold(self) -> float:
        """Current threshold ε."""
        return self._threshold
    
    @property
    def query_count(self) -> int:
        """Total queries."""
        return len(self._queries)
