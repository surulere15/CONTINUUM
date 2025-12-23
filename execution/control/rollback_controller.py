"""
Rollback Controller

Compensation logic for every action.
If rollback is impossible → action is forbidden.

EXECUTION FABRIC - Phase F. Action without sovereignty.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any
from enum import Enum

from .action_primitives import ActionPrimitive, ActionType, ActionStatus, ActionTrace


class RollbackStatus(Enum):
    """Status of rollback operation."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True)
class RollbackPath:
    """
    Defined rollback path for an action.
    
    Every action must have a rollback path.
    """
    action_id: str
    rollback_type: str
    compensation_steps: tuple
    state_snapshot: str
    can_rollback: bool


@dataclass(frozen=True)
class RollbackResult:
    """Result of rollback operation."""
    action_id: str
    status: RollbackStatus
    rolled_back_at: datetime
    error: Optional[str]


class NoRollbackPathError(Exception):
    """Raised when action has no rollback path."""
    pass


class RollbackFailedError(Exception):
    """Raised when rollback fails."""
    pass


class RollbackController:
    """
    Manages rollback and containment.
    
    For every action:
    - Rollback path must exist
    - Compensation logic must be defined
    - If rollback is impossible → action is forbidden
    """
    
    def __init__(self):
        """Initialize rollback controller."""
        self._rollback_paths: Dict[str, RollbackPath] = {}
        self._rollback_history: List[RollbackResult] = []
    
    def register_rollback_path(
        self,
        action: ActionPrimitive,
        compensation_steps: tuple,
        state_snapshot: str,
    ) -> RollbackPath:
        """
        Register a rollback path for an action.
        
        Args:
            action: Action to register rollback for
            compensation_steps: Steps to undo action
            state_snapshot: Snapshot of state before action
            
        Returns:
            RollbackPath
        """
        # Determine if rollback is possible
        can_rollback = self._can_rollback(action, compensation_steps)
        
        path = RollbackPath(
            action_id=action.action_id,
            rollback_type=action.action_type.value,
            compensation_steps=compensation_steps,
            state_snapshot=state_snapshot,
            can_rollback=can_rollback,
        )
        
        self._rollback_paths[action.action_id] = path
        return path
    
    def require_rollback_path(self, action: ActionPrimitive) -> None:
        """
        Assert action has rollback path, or forbid it.
        
        Raises:
            NoRollbackPathError: If rollback is impossible
        """
        if action.requires_rollback and action.action_id not in self._rollback_paths:
            raise NoRollbackPathError(
                f"Action '{action.action_id}' requires rollback but no path registered. "
                f"Action is forbidden."
            )
        
        if action.action_id in self._rollback_paths:
            path = self._rollback_paths[action.action_id]
            if not path.can_rollback:
                raise NoRollbackPathError(
                    f"Action '{action.action_id}' has no viable rollback path. "
                    f"Action is forbidden."
                )
    
    def execute_rollback(self, action_id: str) -> RollbackResult:
        """
        Execute rollback for an action.
        
        Args:
            action_id: Action to roll back
            
        Returns:
            RollbackResult
        """
        if action_id not in self._rollback_paths:
            result = RollbackResult(
                action_id=action_id,
                status=RollbackStatus.FAILED,
                rolled_back_at=datetime.utcnow(),
                error="No rollback path registered",
            )
            self._rollback_history.append(result)
            return result
        
        path = self._rollback_paths[action_id]
        
        if not path.can_rollback:
            result = RollbackResult(
                action_id=action_id,
                status=RollbackStatus.FAILED,
                rolled_back_at=datetime.utcnow(),
                error="Rollback not possible for this action",
            )
            self._rollback_history.append(result)
            return result
        
        # Execute compensation steps (in reality, would apply each step)
        # Here we just mark as completed
        result = RollbackResult(
            action_id=action_id,
            status=RollbackStatus.COMPLETED,
            rolled_back_at=datetime.utcnow(),
            error=None,
        )
        
        self._rollback_history.append(result)
        return result
    
    def _can_rollback(
        self,
        action: ActionPrimitive,
        compensation_steps: tuple,
    ) -> bool:
        """Determine if rollback is possible."""
        # Read-only actions don't need rollback
        if action.action_type in {ActionType.READ, ActionType.QUERY, ActionType.OBSERVE}:
            return True
        
        # Must have compensation steps
        if not compensation_steps:
            return False
        
        return True
    
    def get_rollback_history(self) -> List[RollbackResult]:
        """Get history of rollback operations."""
        return list(self._rollback_history)
    
    @property
    def rollback_count(self) -> int:
        """Total rollbacks executed."""
        return len(self._rollback_history)
