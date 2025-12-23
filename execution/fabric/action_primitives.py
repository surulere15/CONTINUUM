"""
Action Primitives

Atomic action types — all execution decomposes into these.
No composite action may bypass primitive validation.

EXECUTION FABRIC - Phase F. Action without sovereignty.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional, Tuple
from enum import Enum
import hashlib


class ActionType(Enum):
    """The seven atomic action primitives."""
    READ = "read"
    WRITE = "write"
    QUERY = "query"
    TRANSFORM = "transform"
    COMMUNICATE = "communicate"
    INVOKE = "invoke"
    OBSERVE = "observe"


class ActionStatus(Enum):
    """Status of an action."""
    PENDING = "pending"
    AUTHORIZED = "authorized"
    EXECUTING = "executing"
    COMPLETED = "completed"
    ABORTED = "aborted"
    ROLLED_BACK = "rolled_back"


@dataclass(frozen=True)
class ActionPrimitive:
    """
    An atomic action primitive.
    
    All execution is decomposed into primitives.
    Each primitive requires individual authorization.
    
    Attributes:
        action_id: Unique identifier
        action_type: One of the seven primitives
        target: What the action operates on
        parameters: Action parameters
        created_at: When primitive was created
        requires_rollback: Whether rollback path must exist
    """
    action_id: str
    action_type: ActionType
    target: str
    parameters: Tuple[Tuple[str, Any], ...]
    created_at: datetime
    requires_rollback: bool
    
    def compute_hash(self) -> str:
        """Compute deterministic hash of action."""
        content = f"{self.action_id}|{self.action_type.value}|{self.target}"
        return hashlib.sha256(content.encode()).hexdigest()


@dataclass(frozen=True)
class ActionTrace:
    """
    Trace of an executed action.
    
    Every action emits a trace for audit.
    """
    action_id: str
    action_type: ActionType
    target: str
    status: ActionStatus
    started_at: datetime
    completed_at: Optional[datetime]
    result_hash: Optional[str]
    error: Optional[str]


class SelfInitiationError(Exception):
    """Raised when self-initiated action is attempted."""
    pass


class ActionFactory:
    """
    Factory for creating action primitives.
    
    Cannot self-initiate — requires external trigger.
    """
    
    def __init__(self):
        """Initialize factory."""
        self._action_count = 0
        self._external_trigger_required = True
    
    def create(
        self,
        action_type: ActionType,
        target: str,
        parameters: Dict[str, Any],
        external_trigger: bool = False,
    ) -> ActionPrimitive:
        """
        Create an action primitive.
        
        Args:
            action_type: Type of action
            target: Action target
            parameters: Action parameters
            external_trigger: Whether triggered externally
            
        Returns:
            ActionPrimitive
            
        Raises:
            SelfInitiationError: If not externally triggered
        """
        if not external_trigger:
            raise SelfInitiationError(
                "Actions cannot be self-initiated. "
                "External trigger is required."
            )
        
        action_id = self._generate_id()
        self._action_count += 1
        
        return ActionPrimitive(
            action_id=action_id,
            action_type=action_type,
            target=target,
            parameters=tuple(parameters.items()),
            created_at=datetime.utcnow(),
            requires_rollback=action_type in {
                ActionType.WRITE,
                ActionType.TRANSFORM,
                ActionType.COMMUNICATE,
                ActionType.INVOKE,
            },
        )
    
    def self_initiate(self, *args, **kwargs) -> None:
        """
        FORBIDDEN: Self-initiate actions.
        
        Execution cannot self-initiate.
        """
        raise SelfInitiationError(
            "Self-initiation is forbidden. "
            "All actions require external authorization."
        )
    
    def _generate_id(self) -> str:
        """Generate unique action ID."""
        content = f"action:{self._action_count}:{datetime.utcnow().isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    @property
    def action_count(self) -> int:
        """Total actions created."""
        return self._action_count
