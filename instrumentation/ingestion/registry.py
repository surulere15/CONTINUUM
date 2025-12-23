"""
Ingestion Registry

Explicitly whitelists signal sources.
Unregistered sources are REJECTED.

INSTRUMENTATION MODULE - No imports from kernel/cognitive/execution/agents.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional, List, Set
from enum import Enum


class SourceStatus(Enum):
    """Status of a registered source."""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DEPRECATED = "deprecated"


@dataclass(frozen=True)
class RegisteredSource:
    """
    A registered signal source.
    
    Only registered sources can ingest signals.
    Registration is static and human-reviewed.
    """
    
    source_id: str
    name: str
    domain: str
    url: Optional[str]
    status: SourceStatus
    registered_at: datetime
    registered_by: str
    allowed_indicators: tuple  # Tuple of allowed indicator names
    notes: Optional[str] = None


class SourceNotRegisteredError(Exception):
    """Raised when attempting to ingest from unregistered source."""
    pass


class IngestionRegistry:
    """
    Registry of approved signal sources.
    
    Properties:
    - Static configuration (loaded at startup)
    - Signed updates only (future)
    - Human-reviewed additions
    
    If a source is not registered → REJECT.
    """
    
    def __init__(self):
        self._sources: Dict[str, RegisteredSource] = {}
        self._domain_sources: Dict[str, Set[str]] = {
            "economic": set(),
            "environmental": set(),
            "societal": set(),
            "technological": set(),
        }
    
    def register(self, source: RegisteredSource) -> None:
        """
        Register a new source.
        
        In production, this would require signing and review.
        """
        self._sources[source.source_id] = source
        if source.domain in self._domain_sources:
            self._domain_sources[source.domain].add(source.source_id)
    
    def is_registered(self, source_id: str) -> bool:
        """Check if source is registered."""
        return source_id in self._sources
    
    def is_active(self, source_id: str) -> bool:
        """Check if source is registered and active."""
        if source_id not in self._sources:
            return False
        return self._sources[source_id].status == SourceStatus.ACTIVE
    
    def get(self, source_id: str) -> Optional[RegisteredSource]:
        """Get registered source by ID."""
        return self._sources.get(source_id)
    
    def require_registered(self, source_id: str) -> RegisteredSource:
        """
        Get source, raising if not registered.
        
        Raises:
            SourceNotRegisteredError: If source not in registry
        """
        if source_id not in self._sources:
            raise SourceNotRegisteredError(
                f"Source '{source_id}' is not registered. "
                f"Signal ingestion from unregistered sources is forbidden."
            )
        return self._sources[source_id]
    
    def require_active(self, source_id: str) -> RegisteredSource:
        """
        Get source, raising if not active.
        
        Raises:
            SourceNotRegisteredError: If source not registered or not active
        """
        source = self.require_registered(source_id)
        if source.status != SourceStatus.ACTIVE:
            raise SourceNotRegisteredError(
                f"Source '{source_id}' is {source.status.value}, not active."
            )
        return source
    
    def list_by_domain(self, domain: str) -> List[RegisteredSource]:
        """List all registered sources for a domain."""
        source_ids = self._domain_sources.get(domain, set())
        return [self._sources[sid] for sid in source_ids]
    
    def list_active(self) -> List[RegisteredSource]:
        """List all active sources."""
        return [s for s in self._sources.values() if s.status == SourceStatus.ACTIVE]
    
    @property
    def source_count(self) -> int:
        """Total number of registered sources."""
        return len(self._sources)
