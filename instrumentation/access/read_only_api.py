"""
Read-Only API

Exposes signals for querying without modification.
No joins across domains, no computed fields.

INSTRUMENTATION MODULE - No imports from kernel/cognitive/execution/agents.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Iterator
from enum import Enum

from ..schema.signal_base import CivilizationSignal, SignalDomain


class QueryError(Exception):
    """Raised when query is invalid."""
    pass


@dataclass(frozen=True)
class SignalQuery:
    """
    A read-only query for signals.
    
    Queries can filter by:
    - domain (required - no cross-domain queries)
    - time range
    - source
    - name pattern
    """
    domain: SignalDomain
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    source: Optional[str] = None
    name_prefix: Optional[str] = None
    limit: int = 100


@dataclass(frozen=True)
class QueryResult:
    """Result of a signal query."""
    signals: tuple  # Tuple of CivilizationSignal
    total_count: int
    truncated: bool
    query_time_ms: float


class ReadOnlyAPI:
    """
    Read-only API for signal queries.
    
    Properties:
    - Query by domain, time range, source
    - No cross-domain joins
    - No computed/derived fields
    - Rate-limited by QueryGuards
    
    Prohibitions:
    - Cannot modify signals
    - Cannot aggregate across domains
    - Cannot compute scores or indices
    """
    
    MAX_LIMIT = 1000
    
    def __init__(self, storage):
        """
        Initialize API with storage backend.
        
        Args:
            storage: Signal storage (append-only log or content-addressed store)
        """
        self._storage = storage
    
    def query(self, query: SignalQuery) -> QueryResult:
        """
        Execute a read-only query.
        
        Args:
            query: Query parameters
            
        Returns:
            QueryResult with matching signals
        """
        import time
        start = time.time()
        
        # Validate query
        self._validate_query(query)
        
        # Execute query
        matches = []
        for signal in self._iterate_signals():
            if self._matches(signal, query):
                matches.append(signal)
                if len(matches) >= query.limit:
                    break
        
        elapsed = (time.time() - start) * 1000
        
        return QueryResult(
            signals=tuple(matches),
            total_count=len(matches),
            truncated=len(matches) >= query.limit,
            query_time_ms=elapsed,
        )
    
    def get_by_id(self, signal_id: str) -> Optional[CivilizationSignal]:
        """
        Get a specific signal by ID.
        
        Args:
            signal_id: Signal identifier
            
        Returns:
            Signal if found
        """
        for signal in self._iterate_signals():
            if signal.signal_id == signal_id:
                return signal
        return None
    
    def list_sources(self, domain: SignalDomain) -> List[str]:
        """
        List all sources for a domain.
        
        Args:
            domain: Signal domain
            
        Returns:
            List of unique source names
        """
        sources = set()
        for signal in self._iterate_signals():
            if signal.domain == domain:
                sources.add(signal.source)
        return sorted(sources)
    
    def count(self, domain: SignalDomain) -> int:
        """Count signals in domain."""
        count = 0
        for signal in self._iterate_signals():
            if signal.domain == domain:
                count += 1
        return count
    
    def _validate_query(self, query: SignalQuery) -> None:
        """Validate query parameters."""
        if query.limit > self.MAX_LIMIT:
            raise QueryError(f"Limit {query.limit} exceeds maximum {self.MAX_LIMIT}")
        
        if query.limit < 1:
            raise QueryError("Limit must be at least 1")
        
        if query.start_time and query.end_time:
            if query.start_time > query.end_time:
                raise QueryError("start_time cannot be after end_time")
    
    def _matches(self, signal: CivilizationSignal, query: SignalQuery) -> bool:
        """Check if signal matches query."""
        # Domain must match
        if signal.domain != query.domain:
            return False
        
        # Time range filter
        if query.start_time and signal.timestamp < query.start_time:
            return False
        if query.end_time and signal.timestamp > query.end_time:
            return False
        
        # Source filter
        if query.source and signal.source != query.source:
            return False
        
        # Name prefix filter
        if query.name_prefix and not signal.name.startswith(query.name_prefix):
            return False
        
        return True
    
    def _iterate_signals(self) -> Iterator[CivilizationSignal]:
        """Iterate over all signals in storage."""
        # This is a placeholder - actual implementation depends on storage type
        if hasattr(self._storage, 'iterate'):
            for entry in self._storage.iterate():
                yield entry.signal
        elif hasattr(self._storage, '_store'):
            for signal in self._storage._store.values():
                yield signal
        else:
            return
