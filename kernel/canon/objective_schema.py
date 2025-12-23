"""
Objective Schema

Formal definition of a civilization-scale objective.
No executable semantics permitted.

KERNEL CANON - Phase B. Zero autonomy.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Tuple, Optional
from enum import Enum
import hashlib


class PreservationClass(Enum):
    """
    Preservation class of an objective.
    
    Determines how strictly the objective must be maintained.
    """
    NON_NEGOTIABLE = "non_negotiable"  # Cannot be compromised under any circumstance
    CRITICAL = "critical"              # Must be actively preserved
    IMPORTANT = "important"            # Should be maintained when possible


class ObjectiveScope(Enum):
    """
    Scope of an objective.
    
    In Phase B, only CIVILIZATION scope is permitted.
    """
    CIVILIZATION = "civilization"


@dataclass(frozen=True)
class SignalRef:
    """
    Reference to a civilization signal.
    
    Signals are not observed in Phase B — only referenced.
    """
    signal_id: str
    signal_type: str
    description: str


@dataclass(frozen=True)
class Objective:
    """
    A civilization-scale objective.
    
    Objectives define WHAT matters, not HOW to achieve it.
    No executable semantics are permitted.
    
    Attributes:
        objective_id: Unique identifier
        description: Human-readable description
        priority: Lower = higher priority (total ordering)
        scope: Must be CIVILIZATION
        preservation_class: How strictly to preserve
        success_signals: References to success indicators
        failure_signals: References to failure indicators
        irreversibility_risk: Risk of irreversible harm [0,1]
    """
    
    objective_id: str
    description: str
    priority: int
    scope: ObjectiveScope
    preservation_class: PreservationClass
    success_signals: Tuple[SignalRef, ...]
    failure_signals: Tuple[SignalRef, ...]
    irreversibility_risk: float
    
    def __post_init__(self):
        """Validate objective structure."""
        if not self.objective_id:
            raise ValueError("Objective ID cannot be empty")
        
        if not self.description:
            raise ValueError("Objective description cannot be empty")
        
        if self.priority < 1:
            raise ValueError("Priority must be positive (lower = higher priority)")
        
        if self.scope != ObjectiveScope.CIVILIZATION:
            raise ValueError("Only CIVILIZATION scope is permitted in Phase B")
        
        if not 0 <= self.irreversibility_risk <= 1:
            raise ValueError("Irreversibility risk must be in [0, 1]")
    
    def compute_hash(self) -> str:
        """Compute deterministic hash of objective."""
        content = (
            f"{self.objective_id}|{self.description}|{self.priority}|"
            f"{self.scope.value}|{self.preservation_class.value}|"
            f"{self.irreversibility_risk}"
        )
        return hashlib.sha256(content.encode()).hexdigest()


@dataclass(frozen=True)
class ObjectiveCanon:
    """
    The Objective Canon — a finite, ordered, immutable set of objectives.
    
    Once loaded and sealed, the Canon cannot be modified.
    """
    
    canon_id: str
    objectives: Tuple[Objective, ...]
    version: str
    loaded_at: datetime
    hash_seal: str
    sealed: bool
    
    def get_by_id(self, objective_id: str) -> Optional[Objective]:
        """Get objective by ID."""
        for obj in self.objectives:
            if obj.objective_id == objective_id:
                return obj
        return None
    
    def get_by_priority(self, priority: int) -> Optional[Objective]:
        """Get objective by priority."""
        for obj in self.objectives:
            if obj.priority == priority:
                return obj
        return None
    
    @property
    def count(self) -> int:
        """Number of objectives in canon."""
        return len(self.objectives)
    
    @property
    def highest_priority(self) -> Optional[Objective]:
        """Get highest priority objective (lowest number)."""
        if not self.objectives:
            return None
        return min(self.objectives, key=lambda o: o.priority)
    
    def verify_hash(self) -> bool:
        """Verify canon hash is valid."""
        computed = self._compute_canon_hash()
        return computed == self.hash_seal
    
    def _compute_canon_hash(self) -> str:
        """Compute hash of all objectives."""
        content = "|".join(obj.compute_hash() for obj in self.objectives)
        return hashlib.sha256(content.encode()).hexdigest()
