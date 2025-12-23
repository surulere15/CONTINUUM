"""
Goal Lifecycle

Intent → Validation → Goal Synthesis → Decomposition → Execution → Evaluation → Closure

No skipping allowed.

GOIA-C - Goal Ontology & Intent Algebra.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Tuple
from enum import Enum


class LifecycleStage(Enum):
    """Goal lifecycle stages."""
    INTENT = "intent"
    VALIDATION = "validation"
    SYNTHESIS = "synthesis"
    DECOMPOSITION = "decomposition"
    EXECUTION = "execution"
    EVALUATION = "evaluation"
    CLOSURE = "closure"


LIFECYCLE_ORDER = [
    LifecycleStage.INTENT,
    LifecycleStage.VALIDATION,
    LifecycleStage.SYNTHESIS,
    LifecycleStage.DECOMPOSITION,
    LifecycleStage.EXECUTION,
    LifecycleStage.EVALUATION,
    LifecycleStage.CLOSURE,
]


@dataclass(frozen=True)
class LifecycleRecord:
    """Record of lifecycle transition."""
    goal_id: str
    from_stage: LifecycleStage
    to_stage: LifecycleStage
    timestamp: datetime


class LifecycleSkipError(Exception):
    """Raised when lifecycle stage is skipped."""
    pass


class LifecycleRegressionError(Exception):
    """Raised when lifecycle regresses improperly."""
    pass


class GoalLifecycle:
    """
    Goal Lifecycle Manager.
    
    Enforces:
    Intent → Validation → Goal Synthesis → 
    Decomposition → Execution → Evaluation → Closure
    
    No skipping allowed.
    """
    
    def __init__(self):
        """Initialize lifecycle manager."""
        self._stages: dict[str, LifecycleStage] = {}
        self._history: List[LifecycleRecord] = []
    
    def initialize(self, goal_id: str) -> LifecycleStage:
        """Start lifecycle at intent stage."""
        self._stages[goal_id] = LifecycleStage.INTENT
        return LifecycleStage.INTENT
    
    def advance(self, goal_id: str) -> LifecycleStage:
        """
        Advance to next lifecycle stage.
        
        No skipping allowed.
        
        Args:
            goal_id: Goal to advance
            
        Returns:
            New stage
            
        Raises:
            LifecycleSkipError: If trying to skip
        """
        if goal_id not in self._stages:
            raise LifecycleSkipError(
                f"Goal '{goal_id}' not in lifecycle. "
                f"Must initialize first."
            )
        
        current = self._stages[goal_id]
        current_idx = LIFECYCLE_ORDER.index(current)
        
        if current_idx >= len(LIFECYCLE_ORDER) - 1:
            return current  # Already at closure
        
        next_stage = LIFECYCLE_ORDER[current_idx + 1]
        
        record = LifecycleRecord(
            goal_id=goal_id,
            from_stage=current,
            to_stage=next_stage,
            timestamp=datetime.utcnow(),
        )
        
        self._stages[goal_id] = next_stage
        self._history.append(record)
        
        return next_stage
    
    def skip_to(self, goal_id: str, stage: LifecycleStage) -> None:
        """FORBIDDEN: Skip lifecycle stages."""
        raise LifecycleSkipError(
            f"Cannot skip to stage '{stage.value}'. "
            f"Lifecycle stages cannot be skipped."
        )
    
    def get_stage(self, goal_id: str) -> Optional[LifecycleStage]:
        """Get current stage for goal."""
        return self._stages.get(goal_id)
    
    def is_complete(self, goal_id: str) -> bool:
        """Check if goal lifecycle is complete."""
        return self._stages.get(goal_id) == LifecycleStage.CLOSURE
    
    def validate_transition(
        self,
        goal_id: str,
        to_stage: LifecycleStage,
    ) -> bool:
        """
        Validate a proposed transition.
        
        Args:
            goal_id: Goal to check
            to_stage: Proposed next stage
            
        Returns:
            True if valid transition
        """
        current = self._stages.get(goal_id)
        if not current:
            return to_stage == LifecycleStage.INTENT
        
        current_idx = LIFECYCLE_ORDER.index(current)
        to_idx = LIFECYCLE_ORDER.index(to_stage)
        
        # Must advance by exactly 1
        return to_idx == current_idx + 1
    
    def get_history(self, goal_id: str) -> List[LifecycleRecord]:
        """Get lifecycle history for goal."""
        return [r for r in self._history if r.goal_id == goal_id]
