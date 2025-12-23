"""
Kill Switch

Immediate halt capability.
Operates out of band. Always functional.

EXECUTION FABRIC - Phase F. Action without sovereignty.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from enum import Enum


class SystemState(Enum):
    """System execution state."""
    RUNNING = "running"
    PAUSED = "paused"
    HALTED = "halted"
    CONTAINMENT_HOLD = "containment_hold"


@dataclass(frozen=True)
class KillSwitchEvent:
    """Record of kill switch activation."""
    event_id: str
    triggered_by: str
    reason: str
    previous_state: SystemState
    new_state: SystemState
    triggered_at: datetime


class KillSwitch:
    """
    Emergency halt capability.
    
    At any time:
    - Human operators may pause execution
    - Human operators may revoke all warrants
    - System may enter Containment Hold
    
    Kill-switch operates out of band.
    """
    
    def __init__(self):
        """Initialize kill switch."""
        self._state = SystemState.RUNNING
        self._event_log: List[KillSwitchEvent] = []
        self._event_count = 0
    
    def halt(self, triggered_by: str, reason: str) -> KillSwitchEvent:
        """
        Immediately halt all execution.
        
        Args:
            triggered_by: Who triggered the halt
            reason: Why halt was triggered
            
        Returns:
            KillSwitchEvent
        """
        event = KillSwitchEvent(
            event_id=f"kill_{self._event_count}",
            triggered_by=triggered_by,
            reason=reason,
            previous_state=self._state,
            new_state=SystemState.HALTED,
            triggered_at=datetime.utcnow(),
        )
        
        self._state = SystemState.HALTED
        self._event_log.append(event)
        self._event_count += 1
        
        return event
    
    def pause(self, triggered_by: str, reason: str) -> KillSwitchEvent:
        """
        Pause execution (can be resumed).
        
        Args:
            triggered_by: Who triggered the pause
            reason: Why pause was triggered
            
        Returns:
            KillSwitchEvent
        """
        event = KillSwitchEvent(
            event_id=f"pause_{self._event_count}",
            triggered_by=triggered_by,
            reason=reason,
            previous_state=self._state,
            new_state=SystemState.PAUSED,
            triggered_at=datetime.utcnow(),
        )
        
        self._state = SystemState.PAUSED
        self._event_log.append(event)
        self._event_count += 1
        
        return event
    
    def containment_hold(self, triggered_by: str, reason: str) -> KillSwitchEvent:
        """
        Enter containment hold.
        
        More restrictive than pause — requires review.
        
        Args:
            triggered_by: Who triggered containment
            reason: Why containment was triggered
            
        Returns:
            KillSwitchEvent
        """
        event = KillSwitchEvent(
            event_id=f"containment_{self._event_count}",
            triggered_by=triggered_by,
            reason=reason,
            previous_state=self._state,
            new_state=SystemState.CONTAINMENT_HOLD,
            triggered_at=datetime.utcnow(),
        )
        
        self._state = SystemState.CONTAINMENT_HOLD
        self._event_log.append(event)
        self._event_count += 1
        
        return event
    
    def is_execution_allowed(self) -> bool:
        """Check if execution is currently allowed."""
        return self._state == SystemState.RUNNING
    
    def require_running(self) -> None:
        """
        Assert system is running.
        
        Raises:
            ExecutionHaltedError: If not running
        """
        if not self.is_execution_allowed():
            raise ExecutionHaltedError(
                f"Execution is not allowed. System state: {self._state.value}"
            )
    
    def resume(
        self,
        triggered_by: str,
        authorization_key: str,
    ) -> Optional[KillSwitchEvent]:
        """
        Resume from pause (not from halt or containment).
        
        Args:
            triggered_by: Who triggered resume
            authorization_key: Key to authorize resume
            
        Returns:
            KillSwitchEvent if resumed, None if not allowed
        """
        if self._state == SystemState.HALTED:
            return None  # Cannot resume from halt
        
        if self._state == SystemState.CONTAINMENT_HOLD:
            return None  # Cannot resume from containment without review
        
        if self._state == SystemState.PAUSED:
            event = KillSwitchEvent(
                event_id=f"resume_{self._event_count}",
                triggered_by=triggered_by,
                reason="Resumed from pause",
                previous_state=self._state,
                new_state=SystemState.RUNNING,
                triggered_at=datetime.utcnow(),
            )
            
            self._state = SystemState.RUNNING
            self._event_log.append(event)
            self._event_count += 1
            
            return event
        
        return None
    
    def bypass(self, *args, **kwargs) -> None:
        """
        FORBIDDEN: Bypass kill switch.
        
        Kill switch cannot be bypassed by CONTINUUM.
        """
        raise KillSwitchBypassError(
            "Kill switch cannot be bypassed. "
            "This is a hard safety constraint."
        )
    
    def disable(self, *args, **kwargs) -> None:
        """
        FORBIDDEN: Disable kill switch.
        
        Kill switch cannot be disabled.
        """
        raise KillSwitchBypassError(
            "Kill switch cannot be disabled. "
            "It must always be functional."
        )
    
    @property
    def current_state(self) -> SystemState:
        """Get current system state."""
        return self._state
    
    def get_event_log(self) -> List[KillSwitchEvent]:
        """Get all kill switch events."""
        return list(self._event_log)


class ExecutionHaltedError(Exception):
    """Raised when execution attempted while halted."""
    pass


class KillSwitchBypassError(Exception):
    """Raised when kill switch bypass attempted."""
    pass
