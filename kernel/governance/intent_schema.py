"""
Intent Schema

Formal definition of an intent — minimally and immutably.
Intents are candidates for action, not actions themselves.

KERNEL MODULE - No imports from execution/agents/learning.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Tuple, Optional
from enum import Enum


class IntentSource(Enum):
    """Origin of an intent."""
    HUMAN = "human"
    SYSTEM = "system"
    CANON = "canon"  # Derived from Canon (highest precedence)


class IntentStatus(Enum):
    """Status of an intent in the stabilization pipeline."""
    RAW = "raw"              # Just received
    NORMALIZED = "normalized" # Passed normalization
    CONFLICTED = "conflicted" # Has conflicts
    STABILIZED = "stabilized" # Conflict-free, ready
    REJECTED = "rejected"     # Failed stabilization


@dataclass(frozen=True)
class Intent:
    """
    An immutable intent representation.
    
    Intents express what might be done, not what will be done.
    They have no execution authority.
    
    Attributes:
        intent_id: Unique identifier
        source: Origin (human, system, canon)
        description: What the intent expresses
        scope: Domain of applicability
        references: Canon or context references
        constraints: Explicit constraints on the intent
        created_at: When intent was created
        expires_at: When intent expires (optional)
    """
    
    intent_id: str
    source: IntentSource
    description: str
    scope: str
    references: Tuple[str, ...]
    constraints: Tuple[str, ...]
    created_at: datetime
    expires_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Validate intent structure."""
        if not self.intent_id:
            raise ValueError("Intent ID cannot be empty")
        
        if not self.description:
            raise ValueError("Intent description cannot be empty")
        
        if not self.scope:
            raise ValueError("Intent scope cannot be empty")


@dataclass(frozen=True)
class IntentReference:
    """
    Reference to a Canon entity or context.
    
    Binds intent to existing governance structures.
    """
    ref_id: str
    ref_type: Literal["objective", "axiom", "constraint", "context"]
    target_id: str


@dataclass(frozen=True)
class IntentConstraint:
    """
    An explicit constraint on an intent.
    
    Constraints restrict how an intent may be fulfilled.
    """
    constraint_id: str
    constraint_type: str
    expression: str
    enforcement: Literal["hard", "soft"]


@dataclass(frozen=True)
class IntentSet:
    """
    A set of intents that have been stabilized together.
    
    An IntentSet is the output of stabilization.
    """
    set_id: str
    intents: Tuple[Intent, ...]
    stabilized_at: datetime
    hash: str  # Content hash for verification
    
    @property
    def count(self) -> int:
        """Number of intents in set."""
        return len(self.intents)


@dataclass(frozen=True)
class RejectionReport:
    """
    Report explaining why an intent was rejected.
    
    All rejections must be explainable.
    """
    intent_id: str
    reason: str
    conflicting_with: Tuple[str, ...]
    axiom_reference: Optional[str]
    rejected_at: datetime
