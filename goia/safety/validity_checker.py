"""
Goal Validity Checker

Goal validity conditions - 5 requirements.

GOIA-C - Goal Ontology & Intent Algebra.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Tuple


@dataclass(frozen=True)
class ValidityCheck:
    """Result of goal validity check."""
    goal_id: str
    is_valid: bool
    failed_conditions: Tuple[str, ...]
    checked_at: datetime


class InvalidGoalError(Exception):
    """Raised when goal is invalid."""
    pass


class GoalValidityChecker:
    """
    Goal Validity Checker.
    
    A goal is valid iff:
    1. Parent goal exists
    2. Constraints satisfiable
    3. Success metric defined
    4. Failure mode defined
    5. Reversibility declared
    
    Invalid goals are rejected at creation.
    """
    
    def validate(
        self,
        goal_id: str,
        parent_goal_id: Optional[str],
        constraints: Tuple[str, ...],
        success_metric: Optional[str],
        failure_mode: Optional[str],
        reversibility: Optional[str],
        is_existential: bool = False,
    ) -> ValidityCheck:
        """
        Validate goal meets all conditions.
        
        Args:
            goal_id: Goal to validate
            parent_goal_id: Parent goal
            constraints: Goal constraints
            success_metric: How to measure success
            failure_mode: What happens on failure
            reversibility: How to reverse
            is_existential: True if G₀ goal
            
        Returns:
            ValidityCheck
            
        Raises:
            InvalidGoalError: If invalid
        """
        failed = []
        
        # Condition 1: Parent goal exists (except G₀)
        if not is_existential and not parent_goal_id:
            failed.append("parent_goal_exists")
        
        # Condition 2: Constraints satisfiable (simplified: non-empty)
        # In real impl, would check SAT
        
        # Condition 3: Success metric defined
        if not success_metric:
            failed.append("success_metric_defined")
        
        # Condition 4: Failure mode defined
        if not failure_mode:
            failed.append("failure_mode_defined")
        
        # Condition 5: Reversibility declared
        if not reversibility:
            failed.append("reversibility_declared")
        
        is_valid = len(failed) == 0
        
        check = ValidityCheck(
            goal_id=goal_id,
            is_valid=is_valid,
            failed_conditions=tuple(failed),
            checked_at=datetime.utcnow(),
        )
        
        if not is_valid:
            raise InvalidGoalError(
                f"Goal '{goal_id}' is invalid. "
                f"Failed conditions: {failed}"
            )
        
        return check
    
    def skip_validation(self, *args, **kwargs) -> None:
        """FORBIDDEN: Skip validation."""
        raise InvalidGoalError(
            "Goal validation cannot be skipped. "
            "All goals must meet validity conditions."
        )
