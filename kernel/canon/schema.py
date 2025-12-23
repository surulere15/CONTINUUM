"""
Objective Canon Schema

Defines the immutable structure of an Objective.
No executable fields. No weights, rewards, or utilities.
No references to agents or actions.

KERNEL MODULE - Human-written, no AI-generated code permitted.
"""

from dataclasses import dataclass
from typing import Literal, Tuple, Optional
from datetime import datetime


# Valid scope values — objectives can target different levels
ObjectiveScope = Literal["civilization", "system", "humanity"]


@dataclass(frozen=True)
class Objective:
    """
    An immutable objective in the CONTINUUM canon.
    
    Objectives describe WHAT must be preserved or achieved,
    never HOW. They are static declarations, not executable plans.
    
    Attributes:
        id: Unique identifier (content-addressed recommended)
        description: Human-readable description of the objective
        scope: Level at which this objective operates
        priority: Integer priority (lower = higher priority, 1 is highest)
        invariants: Conditions that must always hold
        termination_conditions: When this objective is considered satisfied
        supersedes: Optional ID of objective this supersedes
        created_at: Timestamp of creation (immutable after set)
    """
    
    id: str
    description: str
    scope: ObjectiveScope
    priority: int
    invariants: Tuple[str, ...]
    termination_conditions: Tuple[str, ...]
    supersedes: Optional[str] = None
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Validate objective at creation time."""
        # Verify id is non-empty
        if not self.id or not self.id.strip():
            raise ValueError("Objective ID cannot be empty")
        
        # Verify description exists
        if not self.description or not self.description.strip():
            raise ValueError("Objective description cannot be empty")
        
        # Verify priority is positive
        if self.priority < 1:
            raise ValueError("Priority must be >= 1")
        
        # Verify invariants is a tuple (immutable)
        if not isinstance(self.invariants, tuple):
            raise TypeError("Invariants must be a tuple")
        
        # Verify termination_conditions is a tuple (immutable)
        if not isinstance(self.termination_conditions, tuple):
            raise TypeError("Termination conditions must be a tuple")


@dataclass(frozen=True)
class CanonManifest:
    """
    Manifest of loaded canon — the authoritative list of objectives.
    
    Attributes:
        version: Schema version
        objectives: Tuple of loaded objective IDs
        hash: Content-addressed hash of entire canon
        sealed_at: Timestamp when canon was sealed
    """
    
    version: str
    objectives: Tuple[str, ...]
    hash: str
    sealed_at: datetime


@dataclass(frozen=True)
class ObjectiveReference:
    """
    A reference to an objective for use in supersession chains.
    
    This is a lightweight pointer — does not contain the objective itself.
    """
    
    id: str
    hash: str
    superseded_by: Optional[str] = None
