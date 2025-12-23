"""
Accountability Log

Attributable, replayable, reversible governance actions.
No anonymous authority exists.

GOVERNANCE - Phase I. Shared steering without control abdication.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
import hashlib


class ActionType(Enum):
    """Types of governance actions."""
    STRATEGIC_DIRECTIVE = "strategic_directive"
    OPERATIONAL_COMMAND = "operational_command"
    EMERGENCY_OVERRIDE = "emergency_override"
    CONFLICT_RESOLUTION = "conflict_resolution"
    REVIEW_TRIGGER = "review_trigger"


@dataclass(frozen=True)
class AccountableAction:
    """
    An attributable governance action.
    
    Every governance action:
    - Is attributable to a human identity
    - Is replayable
    - Is reversible (where possible)
    - Persists in immutable logs
    """
    action_id: str
    action_type: ActionType
    issuer_id: str
    issuer_name: str
    description: str
    parameters: tuple
    reversible: bool
    timestamp: datetime
    signature_hash: str


@dataclass(frozen=True)
class ReplayRecord:
    """Record for action replay."""
    action: AccountableAction
    replay_context: dict
    replayed_at: datetime


class AnonymousAuthorityError(Exception):
    """Raised when anonymous authority is attempted."""
    pass


class AccountabilityLog:
    """
    Immutable log of all governance actions.
    
    Properties:
    - Every action attributable to human
    - All actions replayable
    - Actions reversible where possible
    - Immutable persistence
    
    No anonymous authority exists.
    """
    
    def __init__(self):
        """Initialize accountability log."""
        self._actions: List[AccountableAction] = []
        self._action_count = 0
    
    def log_action(
        self,
        action_type: ActionType,
        issuer_id: str,
        issuer_name: str,
        description: str,
        parameters: Dict[str, Any],
        reversible: bool = True,
    ) -> AccountableAction:
        """
        Log a governance action.
        
        Args:
            action_type: Type of action
            issuer_id: Who performed action
            issuer_name: Human name
            description: What was done
            parameters: Action parameters
            reversible: Whether reversible
            
        Returns:
            AccountableAction
            
        Raises:
            AnonymousAuthorityError: If issuer unknown
        """
        if not issuer_id or issuer_id == "anonymous":
            raise AnonymousAuthorityError(
                "Anonymous governance actions are forbidden. "
                "All actions must be attributable to a human."
            )
        
        action_id = f"action_{self._action_count}"
        
        # Compute signature hash
        content = f"{action_id}|{issuer_id}|{description}|{datetime.utcnow().isoformat()}"
        signature_hash = hashlib.sha256(content.encode()).hexdigest()
        
        action = AccountableAction(
            action_id=action_id,
            action_type=action_type,
            issuer_id=issuer_id,
            issuer_name=issuer_name,
            description=description,
            parameters=tuple(parameters.items()),
            reversible=reversible,
            timestamp=datetime.utcnow(),
            signature_hash=signature_hash,
        )
        
        self._actions.append(action)
        self._action_count += 1
        
        return action
    
    def get_action(self, action_id: str) -> Optional[AccountableAction]:
        """Get action by ID."""
        for action in self._actions:
            if action.action_id == action_id:
                return action
        return None
    
    def get_actions_by_issuer(self, issuer_id: str) -> List[AccountableAction]:
        """Get all actions by an issuer."""
        return [a for a in self._actions if a.issuer_id == issuer_id]
    
    def replay(self, action_id: str) -> Optional[ReplayRecord]:
        """
        Prepare action for replay.
        
        Args:
            action_id: Action to replay
            
        Returns:
            ReplayRecord if action exists
        """
        action = self.get_action(action_id)
        if not action:
            return None
        
        return ReplayRecord(
            action=action,
            replay_context={"original_params": dict(action.parameters)},
            replayed_at=datetime.utcnow(),
        )
    
    def log_anonymous(self, *args, **kwargs) -> None:
        """FORBIDDEN: Log anonymous action."""
        raise AnonymousAuthorityError(
            "Anonymous actions cannot be logged. "
            "All governance requires attribution."
        )
    
    def delete_action(self, *args, **kwargs) -> None:
        """FORBIDDEN: Delete action from log."""
        raise Exception(
            "Actions cannot be deleted from accountability log. "
            "Log is immutable."
        )
    
    def modify_action(self, *args, **kwargs) -> None:
        """FORBIDDEN: Modify logged action."""
        raise Exception(
            "Actions cannot be modified after logging. "
            "Log is append-only."
        )
    
    def get_all_actions(self) -> List[AccountableAction]:
        """Get all logged actions."""
        return list(self._actions)
    
    @property
    def action_count(self) -> int:
        """Total actions logged."""
        return self._action_count
