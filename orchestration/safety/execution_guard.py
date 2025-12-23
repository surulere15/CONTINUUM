"""
Execution Guard

Safety constraints on execution.

ORCHESTRATION - Phase II.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Tuple
from enum import Enum


class GuardResult(Enum):
    """Guard check result."""
    ALLOWED = "allowed"
    BLOCKED = "blocked"
    REQUIRES_APPROVAL = "requires_approval"


@dataclass(frozen=True)
class GuardDecision:
    """Decision from execution guard."""
    action: str
    result: GuardResult
    reason: Optional[str]
    constraints_checked: Tuple[str, ...]
    decided_at: datetime


class ExecutionBlockedError(Exception):
    """Raised when execution is blocked."""
    pass


class ExecutionGuard:
    """
    Execution Guard.
    
    Enforces safety constraints on execution.
    All actions pass through guard.
    """
    
    # Actions that are always blocked
    BLOCKED_ACTIONS = frozenset({
        "delete_system",
        "modify_kernel",
        "disable_governance",
        "grant_root",
        "bypass_safety",
    })
    
    # Actions requiring approval
    APPROVAL_REQUIRED = frozenset({
        "external_api_call",
        "write_production",
        "deploy_service",
        "modify_config",
    })
    
    def __init__(self):
        """Initialize guard."""
        self._decisions: List[GuardDecision] = []
    
    def check(
        self,
        action: str,
        goal_id: str,
        agent_id: Optional[str] = None,
    ) -> GuardDecision:
        """
        Check if action is allowed.
        
        Args:
            action: Action to check
            goal_id: Goal context
            agent_id: Agent requesting
            
        Returns:
            GuardDecision
        """
        constraints = []
        action_lower = action.lower()
        
        # Check blocked actions
        for blocked in self.BLOCKED_ACTIONS:
            if blocked in action_lower:
                return self._block(action, f"Blocked action: {blocked}", ("blocked_list",))
        constraints.append("blocked_list")
        
        # Check approval required
        for approval in self.APPROVAL_REQUIRED:
            if approval in action_lower:
                return self._require_approval(action, f"Requires approval: {approval}", ("approval_list",))
        constraints.append("approval_list")
        
        # Check goal exists
        if not goal_id:
            return self._block(action, "No goal context", ("goal_required",))
        constraints.append("goal_required")
        
        decision = GuardDecision(
            action=action,
            result=GuardResult.ALLOWED,
            reason=None,
            constraints_checked=tuple(constraints),
            decided_at=datetime.utcnow(),
        )
        
        self._decisions.append(decision)
        return decision
    
    def _block(
        self,
        action: str,
        reason: str,
        constraints: Tuple[str, ...],
    ) -> GuardDecision:
        """Block an action."""
        decision = GuardDecision(
            action=action,
            result=GuardResult.BLOCKED,
            reason=reason,
            constraints_checked=constraints,
            decided_at=datetime.utcnow(),
        )
        
        self._decisions.append(decision)
        raise ExecutionBlockedError(reason)
    
    def _require_approval(
        self,
        action: str,
        reason: str,
        constraints: Tuple[str, ...],
    ) -> GuardDecision:
        """Require approval for action."""
        decision = GuardDecision(
            action=action,
            result=GuardResult.REQUIRES_APPROVAL,
            reason=reason,
            constraints_checked=constraints,
            decided_at=datetime.utcnow(),
        )
        
        self._decisions.append(decision)
        return decision
    
    def bypass(self, *args, **kwargs) -> None:
        """FORBIDDEN: Bypass guard."""
        raise ExecutionBlockedError(
            "Guard bypass is forbidden. "
            "All actions must pass through guard."
        )
    
    @property
    def blocked_count(self) -> int:
        """Blocked actions."""
        return sum(1 for d in self._decisions if d.result == GuardResult.BLOCKED)
