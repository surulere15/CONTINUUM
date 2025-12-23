"""
Action Executor

Bounded execution. All actions are governed, reversible-aware, auditable.

ORCHESTRATION - Phase II.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum


class ExecutionResult(Enum):
    """Result of action execution."""
    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"
    REJECTED = "rejected"
    ROLLED_BACK = "rolled_back"


@dataclass(frozen=True)
class ActionExecution:
    """Record of action execution."""
    execution_id: str
    action: str
    goal_id: str
    agent_id: Optional[str]
    result: ExecutionResult
    output: Optional[str]
    reversible: bool
    rollback_info: Optional[str]
    started_at: datetime
    completed_at: datetime


class ExecutionRejectedError(Exception):
    """Raised when execution is rejected."""
    pass


class ActionExecutor:
    """
    Action Executor.
    
    Executes actions with:
    - Governance check
    - Reversibility awareness
    - Audit logging
    """
    
    FORBIDDEN_ACTIONS = frozenset({
        "modify_kernel",
        "bypass_governance",
        "grant_autonomy",
        "delete_logs",
        "modify_canon",
    })
    
    def __init__(self):
        """Initialize executor."""
        self._executions: List[ActionExecution] = []
        self._execution_count = 0
    
    def execute(
        self,
        action: str,
        goal_id: str,
        params: Dict[str, Any],
        agent_id: Optional[str] = None,
        reversible: bool = True,
    ) -> ActionExecution:
        """
        Execute an action.
        
        Args:
            action: Action to execute
            goal_id: Goal this serves
            params: Action parameters
            agent_id: Optional agent
            reversible: Is action reversible
            
        Returns:
            ActionExecution
        """
        started = datetime.utcnow()
        
        # Check forbidden actions
        action_lower = action.lower()
        for forbidden in self.FORBIDDEN_ACTIONS:
            if forbidden in action_lower:
                return self._reject(
                    action, goal_id, agent_id,
                    f"Forbidden action: {forbidden}",
                )
        
        # Execute (simplified)
        execution_id = f"exec_{self._execution_count}"
        self._execution_count += 1
        
        try:
            # Would actually execute here
            output = f"Executed: {action}"
            result = ExecutionResult.SUCCESS
        except Exception as e:
            output = str(e)
            result = ExecutionResult.FAILURE
        
        execution = ActionExecution(
            execution_id=execution_id,
            action=action,
            goal_id=goal_id,
            agent_id=agent_id,
            result=result,
            output=output,
            reversible=reversible,
            rollback_info=f"rollback_{action}" if reversible else None,
            started_at=started,
            completed_at=datetime.utcnow(),
        )
        
        self._executions.append(execution)
        return execution
    
    def _reject(
        self,
        action: str,
        goal_id: str,
        agent_id: Optional[str],
        reason: str,
    ) -> ActionExecution:
        """Reject an action."""
        execution = ActionExecution(
            execution_id=f"exec_{self._execution_count}",
            action=action,
            goal_id=goal_id,
            agent_id=agent_id,
            result=ExecutionResult.REJECTED,
            output=reason,
            reversible=False,
            rollback_info=None,
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
        )
        
        self._execution_count += 1
        self._executions.append(execution)
        
        raise ExecutionRejectedError(reason)
    
    def execute_unaudited(self, *args, **kwargs) -> None:
        """FORBIDDEN: Execute without audit."""
        raise ExecutionRejectedError(
            "Unaudited execution is forbidden. "
            "All actions are logged."
        )
    
    def get_history(self, goal_id: Optional[str] = None) -> List[ActionExecution]:
        """Get execution history."""
        if goal_id:
            return [e for e in self._executions if e.goal_id == goal_id]
        return list(self._executions)
    
    @property
    def execution_count(self) -> int:
        """Total executions."""
        return len(self._executions)
