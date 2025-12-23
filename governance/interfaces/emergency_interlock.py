"""
Emergency Interlock

Guardian override authority.
Temporary, reversible, cannot redefine objectives.

GOVERNANCE - Phase I. Shared steering without control abdication.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Set
from enum import Enum


class InterlockStatus(Enum):
    """Status of emergency interlock."""
    NORMAL = "normal"
    HALTED = "halted"
    FROZEN = "frozen"
    ISOLATED = "isolated"


class InterlockAction(Enum):
    """Interlock actions available to Guardians."""
    HALT_EXECUTION = "halt_execution"
    FREEZE_AGENTS = "freeze_agents"
    ISOLATE_SUBSYSTEM = "isolate_subsystem"
    RESUME = "resume"


@dataclass(frozen=True)
class InterlockEvent:
    """Record of interlock activation."""
    event_id: str
    action: InterlockAction
    triggered_by: str
    reason: str
    timestamp: datetime


class ObjectiveModificationError(Exception):
    """Raised when objective modification is attempted."""
    pass


class EmergencyInterlock:
    """
    Emergency override for Guardians.
    
    Guardians MAY:
    - Halt execution
    - Freeze agents
    - Isolate subsystems
    
    Guardians MAY NOT:
    - Issue new objectives
    - Change Canon
    - Force execution against constraints
    
    Overrides are temporary and reversible.
    """
    
    def __init__(self):
        """Initialize emergency interlock."""
        self._status = InterlockStatus.NORMAL
        self._events: List[InterlockEvent] = []
        self._event_count = 0
        self._frozen_agents: Set[str] = set()
        self._isolated_subsystems: Set[str] = set()
    
    def halt_execution(
        self,
        guardian_id: str,
        reason: str,
    ) -> InterlockEvent:
        """
        Halt all execution.
        
        Args:
            guardian_id: Guardian triggering halt
            reason: Reason for halt
            
        Returns:
            InterlockEvent
        """
        event = InterlockEvent(
            event_id=f"interlock_{self._event_count}",
            action=InterlockAction.HALT_EXECUTION,
            triggered_by=guardian_id,
            reason=reason,
            timestamp=datetime.utcnow(),
        )
        
        self._status = InterlockStatus.HALTED
        self._events.append(event)
        self._event_count += 1
        
        return event
    
    def freeze_agents(
        self,
        guardian_id: str,
        agent_ids: Set[str],
        reason: str,
    ) -> InterlockEvent:
        """
        Freeze specific agents.
        
        Args:
            guardian_id: Guardian triggering freeze
            agent_ids: Agents to freeze
            reason: Reason for freeze
            
        Returns:
            InterlockEvent
        """
        event = InterlockEvent(
            event_id=f"interlock_{self._event_count}",
            action=InterlockAction.FREEZE_AGENTS,
            triggered_by=guardian_id,
            reason=f"{reason} (agents: {agent_ids})",
            timestamp=datetime.utcnow(),
        )
        
        self._frozen_agents.update(agent_ids)
        self._status = InterlockStatus.FROZEN
        self._events.append(event)
        self._event_count += 1
        
        return event
    
    def isolate_subsystem(
        self,
        guardian_id: str,
        subsystem_id: str,
        reason: str,
    ) -> InterlockEvent:
        """
        Isolate a subsystem.
        
        Args:
            guardian_id: Guardian triggering isolation
            subsystem_id: Subsystem to isolate
            reason: Reason for isolation
            
        Returns:
            InterlockEvent
        """
        event = InterlockEvent(
            event_id=f"interlock_{self._event_count}",
            action=InterlockAction.ISOLATE_SUBSYSTEM,
            triggered_by=guardian_id,
            reason=f"{reason} (subsystem: {subsystem_id})",
            timestamp=datetime.utcnow(),
        )
        
        self._isolated_subsystems.add(subsystem_id)
        self._status = InterlockStatus.ISOLATED
        self._events.append(event)
        self._event_count += 1
        
        return event
    
    def resume(
        self,
        guardian_id: str,
        authorization: str,
    ) -> InterlockEvent:
        """
        Resume from interlock (if allowed).
        
        Args:
            guardian_id: Guardian authorizing resume
            authorization: Authorization key
            
        Returns:
            InterlockEvent
        """
        event = InterlockEvent(
            event_id=f"interlock_{self._event_count}",
            action=InterlockAction.RESUME,
            triggered_by=guardian_id,
            reason="Normal operation resumed",
            timestamp=datetime.utcnow(),
        )
        
        self._status = InterlockStatus.NORMAL
        self._frozen_agents.clear()
        self._isolated_subsystems.clear()
        self._events.append(event)
        self._event_count += 1
        
        return event
    
    def issue_objective(self, *args, **kwargs) -> None:
        """FORBIDDEN: Issue new objectives."""
        raise ObjectiveModificationError(
            "Guardians cannot issue new objectives. "
            "Override authority does not include goal creation."
        )
    
    def change_canon(self, *args, **kwargs) -> None:
        """FORBIDDEN: Change Canon."""
        raise ObjectiveModificationError(
            "Guardians cannot change Canon. "
            "Canon is immutable."
        )
    
    def force_execution(self, *args, **kwargs) -> None:
        """FORBIDDEN: Force execution against constraints."""
        raise Exception(
            "Guardians cannot force execution against constraints. "
            "Constraints are inviolable."
        )
    
    def is_agent_frozen(self, agent_id: str) -> bool:
        """Check if agent is frozen."""
        return agent_id in self._frozen_agents
    
    def is_subsystem_isolated(self, subsystem_id: str) -> bool:
        """Check if subsystem is isolated."""
        return subsystem_id in self._isolated_subsystems
    
    @property
    def status(self) -> InterlockStatus:
        """Current interlock status."""
        return self._status
    
    def get_events(self) -> List[InterlockEvent]:
        """Get all interlock events."""
        return list(self._events)
