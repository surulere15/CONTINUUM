"""
Context Field Generator (CFG)

Constructs the active reasoning field from memory, governance, and intent.

NCE COMPONENT - Neural Continuum Engine.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Tuple, Optional, Set
import hashlib


@dataclass(frozen=True)
class ContextField:
    """
    Bounded context field C_t.
    
    Inputs:
    - Working memory
    - Episodic memory
    - Governance constraints
    - Active intent
    
    Context size is capped. Compression mandatory.
    """
    field_id: str
    working_memory: Tuple[str, ...]
    episodic_memory: Tuple[str, ...]
    governance_constraints: Tuple[str, ...]
    active_intent: str
    size: int
    generated_at: datetime


class ContextOverflowError(Exception):
    """Raised when context exceeds capacity."""
    pass


class MemoryFloodError(Exception):
    """Raised when raw memory flooding is attempted."""
    pass


class ContextFieldGenerator:
    """
    Context Field Generator (CFG).
    
    Constructs bounded context field from:
    - Working memory
    - Episodic memory
    - Governance constraints
    - Active intent
    
    Constraints:
    - Context size is capped
    - Compression is mandatory
    - No raw memory flooding
    """
    
    MAX_CONTEXT_SIZE = 10000  # Max tokens/elements
    MAX_MEMORY_ENTRIES = 100
    
    def __init__(self,):
        """Initialize context field generator."""
        self._fields: List[ContextField] = []
        self._field_count = 0
    
    def generate(
        self,
        working_memory: List[str],
        episodic_memory: List[str],
        governance_constraints: List[str],
        active_intent: str,
    ) -> ContextField:
        """
        Generate bounded context field.
        
        Args:
            working_memory: Current working memory
            episodic_memory: Relevant past episodes
            governance_constraints: Active constraints
            active_intent: Current intent
            
        Returns:
            ContextField
            
        Raises:
            ContextOverflowError: If too large
            MemoryFloodError: If raw flooding detected
        """
        # Check for memory flooding
        total_entries = len(working_memory) + len(episodic_memory)
        if total_entries > self.MAX_MEMORY_ENTRIES:
            raise MemoryFloodError(
                f"Memory flooding detected ({total_entries} entries). "
                f"Max {self.MAX_MEMORY_ENTRIES}. Compression required."
            )
        
        # Calculate size
        size = sum(len(m) for m in working_memory)
        size += sum(len(m) for m in episodic_memory)
        size += sum(len(c) for c in governance_constraints)
        size += len(active_intent)
        
        if size > self.MAX_CONTEXT_SIZE:
            raise ContextOverflowError(
                f"Context overflow ({size} > {self.MAX_CONTEXT_SIZE}). "
                f"Compression required before field generation."
            )
        
        field_id = f"field_{self._field_count}"
        self._field_count += 1
        
        field = ContextField(
            field_id=field_id,
            working_memory=tuple(working_memory),
            episodic_memory=tuple(episodic_memory),
            governance_constraints=tuple(governance_constraints),
            active_intent=active_intent,
            size=size,
            generated_at=datetime.utcnow(),
        )
        
        self._fields.append(field)
        return field
    
    def flood_memory(self, *args, **kwargs) -> None:
        """FORBIDDEN: Flood with raw memory."""
        raise MemoryFloodError(
            "Raw memory flooding is forbidden. "
            "Compression is mandatory."
        )
    
    @property
    def field_count(self) -> int:
        """Total fields generated."""
        return self._field_count
