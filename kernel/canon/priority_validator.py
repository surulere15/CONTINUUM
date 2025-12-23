"""
Priority Validator

Ensures total ordering of objective priorities.
No duplicates, no circular precedence.

KERNEL CANON - Phase B. Zero autonomy.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Set, Tuple

from .objective_schema import Objective


class PriorityValidationError(Exception):
    """Raised when priority validation fails."""
    pass


@dataclass(frozen=True)
class PriorityValidationResult:
    """Result of priority validation."""
    valid: bool
    total_ordering: Tuple[str, ...]  # Objective IDs in priority order
    error: str | None
    validated_at: datetime


class PriorityValidator:
    """
    Validates priority ordering of objectives.
    
    Requirements:
    - Total ordering must exist
    - No duplicate priorities
    - No circular precedence
    - Priorities must be consecutive from 1
    """
    
    def validate(self, objectives: List[Objective]) -> PriorityValidationResult:
        """
        Validate priority ordering.
        
        Args:
            objectives: List of objectives to validate
            
        Returns:
            PriorityValidationResult
        """
        try:
            # Check for empty
            if not objectives:
                raise PriorityValidationError("No objectives to validate")
            
            # Extract priorities
            priorities = [obj.priority for obj in objectives]
            
            # Check for duplicates
            if len(priorities) != len(set(priorities)):
                duplicates = self._find_duplicates(priorities)
                raise PriorityValidationError(
                    f"Duplicate priorities detected: {duplicates}"
                )
            
            # Check for consecutive ordering
            expected = list(range(1, len(priorities) + 1))
            if sorted(priorities) != expected:
                raise PriorityValidationError(
                    f"Priorities must be consecutive from 1 to N. "
                    f"Got: {sorted(priorities)}, expected: {expected}"
                )
            
            # Check for negative or zero priorities
            if any(p <= 0 for p in priorities):
                raise PriorityValidationError(
                    "Priorities must be positive integers"
                )
            
            # Build total ordering
            sorted_objs = sorted(objectives, key=lambda o: o.priority)
            ordering = tuple(obj.objective_id for obj in sorted_objs)
            
            return PriorityValidationResult(
                valid=True,
                total_ordering=ordering,
                error=None,
                validated_at=datetime.utcnow(),
            )
            
        except PriorityValidationError as e:
            return PriorityValidationResult(
                valid=False,
                total_ordering=(),
                error=str(e),
                validated_at=datetime.utcnow(),
            )
    
    def _find_duplicates(self, priorities: List[int]) -> List[int]:
        """Find duplicate priority values."""
        seen: Set[int] = set()
        duplicates: List[int] = []
        
        for p in priorities:
            if p in seen:
                duplicates.append(p)
            seen.add(p)
        
        return duplicates
    
    def get_precedence_order(self, objectives: List[Objective]) -> List[str]:
        """
        Get objectives in precedence order (highest priority first).
        
        Args:
            objectives: List of objectives
            
        Returns:
            List of objective IDs in precedence order
        """
        result = self.validate(objectives)
        if not result.valid:
            raise PriorityValidationError(result.error or "Validation failed")
        return list(result.total_ordering)
