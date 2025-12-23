"""
Context Builder

Assemble inputs for reasoning from read-only sources.
No synthesis, no prioritization, no interpretation.

COGNITIVE MODULE - No imports from execution/agents/kernel/governance.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum


class ContextSource(Enum):
    """Sources for context assembly."""
    OBJECTIVE_CANON = "objective_canon"
    CIVILIZATION_SIGNALS = "civilization_signals"
    HUMAN_QUERY = "human_query"


@dataclass(frozen=True)
class ContextFragment:
    """
    A fragment of context for reasoning.
    
    Fragments are read-only snapshots.
    """
    fragment_id: str
    source: ContextSource
    content: Any
    timestamp: datetime
    provenance: str


@dataclass(frozen=True)
class AssembledContext:
    """
    Complete context for a reasoning session.
    
    Contains read-only fragments from various sources.
    """
    context_id: str
    fragments: tuple  # Tuple[ContextFragment, ...]
    assembled_at: datetime
    total_size: int


class ContextSynthesisError(Exception):
    """Raised when synthesis is attempted."""
    pass


class ContextBuilder:
    """
    Assembles context for reasoning.
    
    Sources:
    - Objective Canon (read-only)
    - Civilization Signals (read-only)
    - Human queries (future, Phase I)
    
    Restrictions:
    - No synthesis
    - No prioritization
    - No interpretation
    
    Context is assembled, not created.
    """
    
    def __init__(self):
        """Initialize context builder."""
        self._fragments: List[ContextFragment] = []
    
    def add_fragment(
        self,
        source: ContextSource,
        content: Any,
        provenance: str,
    ) -> str:
        """
        Add a context fragment.
        
        Args:
            source: Where the fragment came from
            content: The content (read-only copy)
            provenance: Provenance identifier
            
        Returns:
            fragment_id
        """
        import hashlib
        
        fragment_id = hashlib.sha256(
            f"{source.value}:{str(content)[:100]}".encode()
        ).hexdigest()[:16]
        
        fragment = ContextFragment(
            fragment_id=fragment_id,
            source=source,
            content=content,
            timestamp=datetime.utcnow(),
            provenance=provenance,
        )
        
        self._fragments.append(fragment)
        return fragment_id
    
    def assemble(self) -> AssembledContext:
        """
        Assemble all fragments into context.
        
        No synthesis or combination — just collection.
        """
        import hashlib
        
        context_id = hashlib.sha256(
            "|".join(f.fragment_id for f in self._fragments).encode()
        ).hexdigest()[:16]
        
        return AssembledContext(
            context_id=context_id,
            fragments=tuple(self._fragments),
            assembled_at=datetime.utcnow(),
            total_size=len(self._fragments),
        )
    
    def synthesize(self, *args, **kwargs) -> None:
        """
        FORBIDDEN: Synthesize context.
        
        Context is assembled from sources, not synthesized.
        """
        raise ContextSynthesisError(
            "Context synthesis is forbidden. "
            "Context is assembled from read-only sources, not created."
        )
    
    def prioritize(self, *args, **kwargs) -> None:
        """
        FORBIDDEN: Prioritize fragments.
        
        All context fragments are equal.
        """
        raise ContextSynthesisError(
            "Context prioritization is forbidden. "
            "All fragments have equal standing."
        )
    
    def interpret(self, *args, **kwargs) -> None:
        """
        FORBIDDEN: Interpret context.
        
        Context is presented as-is.
        """
        raise ContextSynthesisError(
            "Context interpretation is forbidden. "
            "Cognition receives raw context without pre-interpretation."
        )
    
    def clear(self) -> None:
        """Clear all fragments."""
        self._fragments.clear()
    
    def get_fragments_by_source(self, source: ContextSource) -> List[ContextFragment]:
        """Get fragments from a specific source."""
        return [f for f in self._fragments if f.source == source]
    
    @property
    def fragment_count(self) -> int:
        """Number of fragments."""
        return len(self._fragments)
