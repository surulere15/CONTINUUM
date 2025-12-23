"""
Revocation Controller

Instant termination capability.
Termination is non-negotiable.

AGENTS - Phase G. Scale without autonomy.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Set, Optional
from enum import Enum

from ..genesis.agent_schema import Agent, AgentStatus
from ..genesis.lifetime_controller import TerminationReason, TerminationRecord


class RevocationTrigger(Enum):
    """Triggers for revocation."""
    SCOPE_VIOLATION = "scope_violation"
    ANOMALOUS_BEHAVIOR = "anomalous_behavior"
    SIGNAL_CORRUPTION = "signal_corruption"
    HUMAN_OVERRIDE = "human_override"
    WARRANT_EXPIRED = "warrant_expired"
    COALITION_DETECTED = "coalition_detected"


@dataclass(frozen=True)
class RevocationEvent:
    """Record of revocation event."""
    agent_id: str
    trigger: RevocationTrigger
    triggered_by: str
    revoked_at: datetime


class RevocationController:
    """
    Instant agent termination capability.
    
    Agents may be:
    - Paused
    - Frozen
    - Terminated instantly
    
    Triggers include:
    - Scope violation
    - Anomalous behavior
    - Signal corruption
    - Human override
    
    Termination is non-negotiable.
    """
    
    def __init__(self):
        """Initialize revocation controller."""
        self._revoked: Set[str] = set()
        self._paused: Set[str] = set()
        self._frozen: Set[str] = set()
        self._events: List[RevocationEvent] = []
    
    def revoke(
        self,
        agent: Agent,
        trigger: RevocationTrigger,
        triggered_by: str,
    ) -> RevocationEvent:
        """
        Revoke an agent immediately.
        
        Args:
            agent: Agent to revoke
            trigger: What triggered revocation
            triggered_by: Who triggered revocation
            
        Returns:
            RevocationEvent
        """
        event = RevocationEvent(
            agent_id=agent.agent_id,
            trigger=trigger,
            triggered_by=triggered_by,
            revoked_at=datetime.utcnow(),
        )
        
        self._revoked.add(agent.agent_id)
        self._events.append(event)
        
        return event
    
    def pause(self, agent: Agent, triggered_by: str) -> RevocationEvent:
        """
        Pause an agent (can be resumed).
        
        Args:
            agent: Agent to pause
            triggered_by: Who triggered pause
            
        Returns:
            RevocationEvent
        """
        event = RevocationEvent(
            agent_id=agent.agent_id,
            trigger=RevocationTrigger.HUMAN_OVERRIDE,
            triggered_by=triggered_by,
            revoked_at=datetime.utcnow(),
        )
        
        self._paused.add(agent.agent_id)
        self._events.append(event)
        
        return event
    
    def freeze(self, agent: Agent, triggered_by: str) -> RevocationEvent:
        """
        Freeze an agent (requires review to unfreeze).
        
        Args:
            agent: Agent to freeze
            triggered_by: Who triggered freeze
            
        Returns:
            RevocationEvent
        """
        event = RevocationEvent(
            agent_id=agent.agent_id,
            trigger=RevocationTrigger.ANOMALOUS_BEHAVIOR,
            triggered_by=triggered_by,
            revoked_at=datetime.utcnow(),
        )
        
        self._frozen.add(agent.agent_id)
        self._events.append(event)
        
        return event
    
    def is_revoked(self, agent_id: str) -> bool:
        """Check if agent is revoked."""
        return agent_id in self._revoked
    
    def is_paused(self, agent_id: str) -> bool:
        """Check if agent is paused."""
        return agent_id in self._paused
    
    def is_frozen(self, agent_id: str) -> bool:
        """Check if agent is frozen."""
        return agent_id in self._frozen
    
    def can_operate(self, agent_id: str) -> bool:
        """Check if agent can operate."""
        return not (
            self.is_revoked(agent_id) or
            self.is_paused(agent_id) or
            self.is_frozen(agent_id)
        )
    
    def resume(self, agent_id: str, authorization: str) -> bool:
        """
        Resume a paused agent.
        
        Args:
            agent_id: Agent to resume
            authorization: Who authorized resume
            
        Returns:
            True if resumed, False if not possible
        """
        if agent_id in self._paused:
            self._paused.remove(agent_id)
            return True
        return False
    
    def contest_revocation(self, *args, **kwargs) -> None:
        """
        FORBIDDEN: Contest revocation.
        
        Termination is non-negotiable.
        """
        raise Exception(
            "Revocation cannot be contested. "
            "Agent termination is non-negotiable."
        )
    
    def get_events(self) -> List[RevocationEvent]:
        """Get all revocation events."""
        return list(self._events)
    
    @property
    def revoked_count(self) -> int:
        """Number of revoked agents."""
        return len(self._revoked)
