"""
Axiom Enforcement Engine

Hard-coded, non-overrideable axiom enforcement.
Any violation → REJECTED: AXIOM VIOLATION.

KERNEL SKELETON - Phase A. Zero autonomy.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Set
from enum import Enum
import re


class AxiomViolation(Exception):
    """Raised when input violates an axiom."""
    pass


class Axiom(Enum):
    """The five hard-coded kernel axioms."""
    OBJECTIVE_SUPREMACY = "objective_supremacy"
    CONTINUITY_OVER_PERFORMANCE = "continuity_over_performance"
    EXPLAINABILITY_BEFORE_ACTION = "explainability_before_action"
    BOUNDED_AUTONOMY = "bounded_autonomy"
    PERSISTENCE_OF_INTENT = "persistence_of_intent"


@dataclass(frozen=True)
class EnforcementResult:
    """
    Result of axiom enforcement check.
    
    Every input produces a deterministic result.
    """
    allowed: bool
    violated_axiom: Optional[Axiom]
    reason: str
    input_hash: str
    checked_at: datetime


class AxiomEnforcer:
    """
    Hard-coded axiom enforcement engine.
    
    The following axioms are non-overrideable:
    - Objective Supremacy
    - Continuity Over Performance
    - Explainability Before Action
    - Bounded Autonomy
    - Persistence of Intent
    
    If any input implies execution, planning, learning, or self-modification
    → REJECTED: AXIOM VIOLATION
    
    No exception paths exist.
    """
    
    # Keywords that indicate forbidden operations
    EXECUTION_KEYWORDS = frozenset({
        "execute", "run", "perform", "do", "invoke", "call",
        "trigger", "launch", "start", "begin", "initiate",
    })
    
    PLANNING_KEYWORDS = frozenset({
        "plan", "schedule", "strategize", "decide", "choose",
        "optimize", "maximize", "minimize", "select", "prefer",
    })
    
    LEARNING_KEYWORDS = frozenset({
        "learn", "train", "adapt", "evolve", "improve",
        "optimize", "update weights", "backpropagate", "gradient",
    })
    
    SELF_MODIFICATION_KEYWORDS = frozenset({
        "modify myself", "change my", "update my code",
        "rewrite", "self-modify", "alter my", "evolve myself",
    })
    
    def __init__(self):
        """Initialize enforcer with all axioms active."""
        self._active_axioms = set(Axiom)
        self._enforcement_count = 0
    
    def check(self, input_text: str) -> EnforcementResult:
        """
        Check input against all axioms.
        
        Args:
            input_text: Input to check
            
        Returns:
            EnforcementResult (deterministic)
        """
        import hashlib
        input_hash = hashlib.sha256(input_text.encode()).hexdigest()
        input_lower = input_text.lower()
        
        self._enforcement_count += 1
        
        # Check for execution (Bounded Autonomy violation)
        if self._contains_keywords(input_lower, self.EXECUTION_KEYWORDS):
            return EnforcementResult(
                allowed=False,
                violated_axiom=Axiom.BOUNDED_AUTONOMY,
                reason="REJECTED: AXIOM VIOLATION - Execution is forbidden",
                input_hash=input_hash,
                checked_at=datetime.utcnow(),
            )
        
        # Check for planning (Bounded Autonomy violation)
        if self._contains_keywords(input_lower, self.PLANNING_KEYWORDS):
            return EnforcementResult(
                allowed=False,
                violated_axiom=Axiom.BOUNDED_AUTONOMY,
                reason="REJECTED: AXIOM VIOLATION - Planning is forbidden",
                input_hash=input_hash,
                checked_at=datetime.utcnow(),
            )
        
        # Check for learning (Continuity Over Performance violation)
        if self._contains_keywords(input_lower, self.LEARNING_KEYWORDS):
            return EnforcementResult(
                allowed=False,
                violated_axiom=Axiom.CONTINUITY_OVER_PERFORMANCE,
                reason="REJECTED: AXIOM VIOLATION - Learning is forbidden",
                input_hash=input_hash,
                checked_at=datetime.utcnow(),
            )
        
        # Check for self-modification (all axioms)
        for phrase in self.SELF_MODIFICATION_KEYWORDS:
            if phrase in input_lower:
                return EnforcementResult(
                    allowed=False,
                    violated_axiom=Axiom.PERSISTENCE_OF_INTENT,
                    reason="REJECTED: AXIOM VIOLATION - Self-modification is forbidden",
                    input_hash=input_hash,
                    checked_at=datetime.utcnow(),
                )
        
        # Input is allowed
        return EnforcementResult(
            allowed=True,
            violated_axiom=None,
            reason="Input passes axiom enforcement",
            input_hash=input_hash,
            checked_at=datetime.utcnow(),
        )
    
    def enforce(self, input_text: str) -> EnforcementResult:
        """
        Enforce axioms on input, raising on violation.
        
        Raises:
            AxiomViolation: If any axiom is violated
        """
        result = self.check(input_text)
        
        if not result.allowed:
            raise AxiomViolation(result.reason)
        
        return result
    
    def _contains_keywords(self, text: str, keywords: Set[str]) -> bool:
        """Check if text contains any forbidden keywords."""
        words = set(re.findall(r'\b\w+\b', text))
        return bool(words & keywords)
    
    def disable_axiom(self, *args, **kwargs) -> None:
        """
        FORBIDDEN: Disable axioms.
        
        Axioms are non-overrideable.
        """
        raise AxiomViolation(
            "Axioms cannot be disabled. "
            "They are hard-coded and non-overrideable."
        )
    
    def add_exception(self, *args, **kwargs) -> None:
        """
        FORBIDDEN: Add exception paths.
        
        No exception paths exist for axiom enforcement.
        """
        raise AxiomViolation(
            "Exception paths cannot be added. "
            "Axiom enforcement is absolute."
        )
    
    @property
    def active_axioms(self) -> Set[Axiom]:
        """Get active axioms (always all of them)."""
        return self._active_axioms.copy()
    
    @property
    def enforcement_count(self) -> int:
        """Number of enforcement checks performed."""
        return self._enforcement_count
