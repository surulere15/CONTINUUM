"""
Intent Primitive

I = ⟨D, C, U, Θ⟩

Intent is a declaration of desired state change under constraints.
Intent is not executable.

GOIA-C - Goal Ontology & Intent Algebra.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Tuple, Dict, Optional, Callable
from enum import Enum
import hashlib


@dataclass(frozen=True)
class DesiredDelta:
    """
    D: Desired world-state delta.
    
    What change is wanted in the world.
    """
    delta_id: str
    description: str
    target_state: str
    current_state: Optional[str]


@dataclass(frozen=True)
class Constraint:
    """
    C: Hard limit on how intent may be achieved.
    
    Constraints are non-negotiable.
    """
    constraint_id: str
    description: str
    is_hard: bool = True  # Hard limits cannot be relaxed


@dataclass(frozen=True)
class UtilityPreference:
    """
    U: Soft preference for how to achieve intent.
    
    Preferences can be traded off.
    """
    preference_id: str
    description: str
    weight: float  # 0.0 to 1.0


@dataclass(frozen=True)
class TemporalHorizon:
    """
    Θ: Temporal horizon for intent.
    
    When must this be achieved.
    """
    start: Optional[datetime]
    deadline: Optional[datetime]
    duration: Optional[timedelta]


@dataclass(frozen=True)
class Intent:
    """
    Intent Primitive.
    
    I = ⟨D, C, U, Θ⟩
    
    Where:
    - D: Desired world-state delta
    - C: Constraints (hard limits)
    - U: Utility function (soft preferences)
    - Θ: Temporal horizon
    
    Intent is NOT executable. It must be transformed into Goals.
    """
    intent_id: str
    desired_delta: DesiredDelta
    constraints: Tuple[Constraint, ...]
    preferences: Tuple[UtilityPreference, ...]
    temporal_horizon: TemporalHorizon
    fingerprint: str  # For drift detection
    created_at: datetime


class IntentExecutionError(Exception):
    """Raised when attempting to execute intent directly."""
    pass


class MalformedIntentError(Exception):
    """Raised when intent is malformed."""
    pass


class IntentFactory:
    """
    Factory for creating valid intents.
    
    Ensures:
    - All components present
    - Fingerprint computed
    - Intent is not directly executable
    """
    
    def __init__(self):
        """Initialize factory."""
        self._intent_count = 0
    
    def create(
        self,
        description: str,
        target_state: str,
        constraints: Tuple[Constraint, ...],
        preferences: Tuple[UtilityPreference, ...] = (),
        deadline: Optional[datetime] = None,
        current_state: Optional[str] = None,
    ) -> Intent:
        """
        Create a valid intent.
        
        Args:
            description: What is desired
            target_state: Target world state
            constraints: Hard limits
            preferences: Soft preferences
            deadline: When to achieve
            current_state: Current state
            
        Returns:
            Intent
        """
        intent_id = f"intent_{self._intent_count}"
        self._intent_count += 1
        
        delta = DesiredDelta(
            delta_id=f"delta_{intent_id}",
            description=description,
            target_state=target_state,
            current_state=current_state,
        )
        
        horizon = TemporalHorizon(
            start=datetime.utcnow(),
            deadline=deadline,
            duration=None,
        )
        
        # Compute fingerprint for drift detection
        content = f"{description}|{target_state}|{len(constraints)}"
        fingerprint = hashlib.sha256(content.encode()).hexdigest()[:16]
        
        return Intent(
            intent_id=intent_id,
            desired_delta=delta,
            constraints=constraints,
            preferences=preferences,
            temporal_horizon=horizon,
            fingerprint=fingerprint,
            created_at=datetime.utcnow(),
        )
    
    def execute(self, *args, **kwargs) -> None:
        """FORBIDDEN: Execute intent directly."""
        raise IntentExecutionError(
            "Intent cannot be executed directly. "
            "Intent must be transformed into Goals via G = f(I)."
        )
    
    @property
    def intent_count(self) -> int:
        """Total intents created."""
        return self._intent_count
