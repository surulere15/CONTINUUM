"""
Memory Influence Invariant

C_t = g(M, S_t)

Memory is active, not archival.
If memory does not influence reasoning, the system is invalid.

NCE INVARIANT 4 - Neural Continuum Engine.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Set, Optional, Tuple


@dataclass(frozen=True)
class MemoryEntry:
    """An entry in the memory substrate."""
    entry_id: str
    content: str
    memory_type: str  # "episodic", "semantic", "working"
    salience: float   # 0.0-1.0
    created_at: datetime


@dataclass(frozen=True)
class ContextField:
    """
    Active context field at time t.
    
    C_t = g(M, S_t)
    
    Context is derived from memory + state.
    """
    field_id: str
    entries: Tuple[str, ...]      # Memory entry IDs
    state_id: str
    influence_score: float        # How much memory influenced
    generated_at: datetime


class MemoryInfluenceError(Exception):
    """Raised when memory influence is absent."""
    pass


class MemoryIsolationError(Exception):
    """Raised when memory is isolated from reasoning."""
    pass


class MemoryInfluence:
    """
    Enforces Invariant 4: Memory Influence.
    
    C_t = g(M, S_t)
    
    Memory must actively influence context.
    Archival-only memory invalidates the system.
    """
    
    MINIMUM_INFLUENCE = 0.1  # Memory must have at least 10% influence
    
    def __init__(self):
        """Initialize memory influence tracker."""
        self._memory: Dict[str, MemoryEntry] = {}
        self._contexts: List[ContextField] = []
        self._influence_history: List[float] = []
    
    def store(self, entry: MemoryEntry) -> None:
        """Store a memory entry."""
        self._memory[entry.entry_id] = entry
    
    def generate_context(
        self,
        state_id: str,
        relevant_memories: Set[str],
    ) -> ContextField:
        """
        Generate context field from memory and state.
        
        C_t = g(M, S_t)
        
        Args:
            state_id: Current state ID
            relevant_memories: Memory IDs to include
            
        Returns:
            ContextField
            
        Raises:
            MemoryInfluenceError: If no memory influence
        """
        if not relevant_memories:
            raise MemoryInfluenceError(
                "Context cannot be generated without memory influence. "
                "C_t = g(M, S_t) requires memory participation."
            )
        
        # Calculate influence score
        total_salience = 0.0
        valid_entries = []
        
        for mem_id in relevant_memories:
            if mem_id in self._memory:
                entry = self._memory[mem_id]
                total_salience += entry.salience
                valid_entries.append(mem_id)
        
        if not valid_entries:
            raise MemoryInfluenceError(
                "No valid memory entries found. "
                "Memory must actively influence context."
            )
        
        influence_score = min(1.0, total_salience / len(valid_entries))
        
        if influence_score < self.MINIMUM_INFLUENCE:
            raise MemoryInfluenceError(
                f"Memory influence ({influence_score:.2f}) below minimum "
                f"({self.MINIMUM_INFLUENCE}). "
                f"Memory must actively participate in reasoning."
            )
        
        context = ContextField(
            field_id=f"context_{len(self._contexts)}",
            entries=tuple(valid_entries),
            state_id=state_id,
            influence_score=influence_score,
            generated_at=datetime.utcnow(),
        )
        
        self._contexts.append(context)
        self._influence_history.append(influence_score)
        
        return context
    
    def verify_influence(self) -> bool:
        """
        Verify memory is actively influencing.
        
        Returns:
            True if memory is active
            
        Raises:
            MemoryIsolationError: If memory isolated
        """
        if not self._contexts:
            return True  # No contexts yet
        
        # Check recent contexts have memory influence
        recent = self._contexts[-5:] if len(self._contexts) >= 5 else self._contexts
        avg_influence = sum(c.influence_score for c in recent) / len(recent)
        
        if avg_influence < self.MINIMUM_INFLUENCE:
            raise MemoryIsolationError(
                f"Memory influence declining ({avg_influence:.2f}). "
                f"Memory must remain active, not archival."
            )
        
        return True
    
    def isolate_memory(self, *args, **kwargs) -> None:
        """FORBIDDEN: Isolate memory from reasoning."""
        raise MemoryIsolationError(
            "Memory isolation is forbidden. "
            "Memory must influence reasoning."
        )
    
    def ignore_memory(self, *args, **kwargs) -> None:
        """FORBIDDEN: Ignore memory in context generation."""
        raise MemoryInfluenceError(
            "Ignoring memory is forbidden. "
            "C_t = g(M, S_t) must hold."
        )
    
    @property
    def memory_count(self) -> int:
        """Number of memory entries."""
        return len(self._memory)
    
    @property
    def average_influence(self) -> float:
        """Average memory influence."""
        if not self._influence_history:
            return 0.0
        return sum(self._influence_history) / len(self._influence_history)
