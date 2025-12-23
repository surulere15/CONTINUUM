"""
Objective

Formal definition of an Objective - supreme law.

Objective := ⟨intent, constraints, success_criteria, termination_conditions, priority⟩

OSD - Objective Supremacy Doctrine.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Tuple
from enum import Enum


class ObjectiveState(Enum):
    """Objective lifecycle state."""
    DRAFT = "draft"
    REVIEWED = "reviewed"
    COMMITTED = "committed"
    ACTIVE = "active"
    COMPLETED = "completed"
    TERMINATED = "terminated"


@dataclass(frozen=True)
class Objective:
    """
    An Objective - formal, persistent, supreme.
    
    Objective := ⟨intent, constraints, success_criteria,
                  termination_conditions, priority⟩
    
    Once activated:
    - Becomes non-volatile
    - Cannot be overridden casually
    - Governs all planning, execution, and self-expansion
    """
    objective_id: str
    intent: str
    constraints: Tuple[str, ...]
    success_criteria: Tuple[str, ...]
    termination_conditions: Tuple[str, ...]
    priority: int  # Higher = more important
    state: ObjectiveState
    version: int
    created_at: datetime
    committed_at: Optional[datetime]


class ObjectiveViolationError(Exception):
    """Raised when objective is violated."""
    pass


class CasualOverrideError(Exception):
    """Raised when casual override is attempted."""
    pass


class ObjectiveManager:
    """
    Objective Manager.
    
    Manages objective lifecycle with high-friction changes.
    """
    
    def __init__(self):
        """Initialize manager."""
        self._objectives: dict[str, Objective] = {}
        self._objective_count = 0
    
    def create(
        self,
        intent: str,
        constraints: Tuple[str, ...],
        success_criteria: Tuple[str, ...],
        termination_conditions: Tuple[str, ...],
        priority: int = 50,
    ) -> Objective:
        """
        Create an objective in draft state.
        
        Args:
            intent: What to achieve
            constraints: Hard limits
            success_criteria: How to measure success
            termination_conditions: When to end
            priority: Importance (higher = more)
            
        Returns:
            Objective
        """
        objective_id = f"obj_{self._objective_count}"
        self._objective_count += 1
        
        objective = Objective(
            objective_id=objective_id,
            intent=intent,
            constraints=constraints,
            success_criteria=success_criteria,
            termination_conditions=termination_conditions,
            priority=priority,
            state=ObjectiveState.DRAFT,
            version=1,
            created_at=datetime.utcnow(),
            committed_at=None,
        )
        
        self._objectives[objective_id] = objective
        return objective
    
    def commit(self, objective_id: str) -> Objective:
        """
        Commit an objective. High-friction operation.
        
        Once committed:
        - Cannot be casually overridden
        - Governs system behavior
        """
        if objective_id not in self._objectives:
            raise ValueError(f"Objective '{objective_id}' not found")
        
        old = self._objectives[objective_id]
        
        if old.state not in (ObjectiveState.DRAFT, ObjectiveState.REVIEWED):
            raise ValueError(f"Cannot commit objective in state {old.state}")
        
        committed = Objective(
            objective_id=old.objective_id,
            intent=old.intent,
            constraints=old.constraints,
            success_criteria=old.success_criteria,
            termination_conditions=old.termination_conditions,
            priority=old.priority,
            state=ObjectiveState.COMMITTED,
            version=old.version,
            created_at=old.created_at,
            committed_at=datetime.utcnow(),
        )
        
        self._objectives[objective_id] = committed
        return committed
    
    def activate(self, objective_id: str) -> Objective:
        """Activate a committed objective."""
        if objective_id not in self._objectives:
            raise ValueError(f"Objective '{objective_id}' not found")
        
        old = self._objectives[objective_id]
        
        if old.state != ObjectiveState.COMMITTED:
            raise ValueError("Only committed objectives can be activated")
        
        active = Objective(
            objective_id=old.objective_id,
            intent=old.intent,
            constraints=old.constraints,
            success_criteria=old.success_criteria,
            termination_conditions=old.termination_conditions,
            priority=old.priority,
            state=ObjectiveState.ACTIVE,
            version=old.version,
            created_at=old.created_at,
            committed_at=old.committed_at,
        )
        
        self._objectives[objective_id] = active
        return active
    
    def casual_override(self, *args, **kwargs) -> None:
        """FORBIDDEN: Casual override."""
        raise CasualOverrideError(
            "Casual objective override is forbidden. "
            "Only high-friction governance actions can modify objectives."
        )
    
    def get_active(self) -> list:
        """Get all active objectives, sorted by priority."""
        active = [
            o for o in self._objectives.values()
            if o.state == ObjectiveState.ACTIVE
        ]
        return sorted(active, key=lambda x: x.priority, reverse=True)
    
    def get(self, objective_id: str) -> Optional[Objective]:
        """Get objective by ID."""
        return self._objectives.get(objective_id)
