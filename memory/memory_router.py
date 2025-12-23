"""
Memory Router

Routes memory queries to appropriate memory stores
and coordinates cross-store operations.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from enum import Enum


class MemoryType(Enum):
    """Types of memory stores."""
    WORKING = "working"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    VALUE = "value"


@dataclass
class MemoryQuery:
    """A query to memory."""
    id: str
    query: str
    memory_types: List[MemoryType]
    context: Dict
    max_results: int


@dataclass
class MemoryResult:
    """Result from memory query."""
    query_id: str
    results: List[Dict]
    sources: List[str]
    confidence: float


class MemoryRouter:
    """
    Routes queries to appropriate memory stores.
    """
    
    def __init__(self, stores: Dict[MemoryType, Any]):
        """
        Initialize with memory stores.
        """
        self._stores = stores
    
    def query(self, query: MemoryQuery) -> MemoryResult:
        """
        Route query to appropriate stores.
        """
        all_results = []
        all_sources = []
        
        for mem_type in query.memory_types:
            store = self._stores.get(mem_type)
            if store:
                results = store.search(query.query, query.context)
                all_results.extend(results)
                all_sources.append(mem_type.value)
        
        # Rank and limit results
        ranked = self._rank_results(all_results, query)
        limited = ranked[:query.max_results]
        
        return MemoryResult(
            query_id=query.id,
            results=limited,
            sources=all_sources,
            confidence=self._compute_confidence(limited)
        )
    
    def consolidate(self) -> None:
        """Consolidate working memory to long-term stores."""
        working = self._stores.get(MemoryType.WORKING)
        episodic = self._stores.get(MemoryType.EPISODIC)
        
        if working and episodic:
            # Move completed episodes to episodic memory
            pass
    
    def _rank_results(self, results: List[Dict], query: MemoryQuery) -> List[Dict]:
        """Rank results by relevance."""
        return sorted(results, key=lambda r: r.get("relevance", 0), reverse=True)
    
    def _compute_confidence(self, results: List[Dict]) -> float:
        """Compute confidence in results."""
        if not results:
            return 0.0
        return sum(r.get("confidence", 0.5) for r in results) / len(results)
