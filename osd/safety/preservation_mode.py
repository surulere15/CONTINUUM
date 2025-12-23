"""
Objective Preservation Mode

Graceful degradation. Objectives do not die easily.

OSD - Objective Supremacy Doctrine.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from enum import Enum


class PreservationTrigger(Enum):
    """Triggers for preservation mode."""
    RESOURCE_STARVATION = "resource_starvation"
    PARTIAL_FAILURE = "partial_failure"
    SHUTDOWN_ATTEMPT = "shutdown_attempt"
    NETWORK_ISOLATION = "network_isolation"


class PreservationState(Enum):
    """Preservation mode states."""
    NORMAL = "normal"
    DEGRADED = "degraded"
    PRESERVATION = "preservation"
    HIBERNATION = "hibernation"


@dataclass
class PreservationRecord:
    """Record of preservation mode."""
    record_id: str
    trigger: PreservationTrigger
    previous_state: PreservationState
    current_state: PreservationState
    objectives_preserved: int
    entered_at: datetime


class PreservationMode:
    """
    Objective Preservation Mode.
    
    If CONTINUUM encounters:
    - Resource starvation
    - Partial system failure
    - Human intervention attempting shutdown
    
    It will:
    - Enter Objective Preservation Mode
    - Degrade gracefully
    - Preserve state
    - Resume when conditions allow
    
    Objectives do not die easily.
    """
    
    def __init__(self):
        """Initialize preservation mode."""
        self._state = PreservationState.NORMAL
        self._records: List[PreservationRecord] = []
        self._record_count = 0
        self._preserved_objectives: List[str] = []
    
    def check_triggers(
        self,
        resource_level: float,       # 0-1
        system_health: float,        # 0-1
        shutdown_requested: bool,
    ) -> Optional[PreservationTrigger]:
        """Check for preservation triggers."""
        if resource_level < 0.1:
            return PreservationTrigger.RESOURCE_STARVATION
        
        if system_health < 0.3:
            return PreservationTrigger.PARTIAL_FAILURE
        
        if shutdown_requested:
            return PreservationTrigger.SHUTDOWN_ATTEMPT
        
        return None
    
    def enter_preservation(
        self,
        trigger: PreservationTrigger,
        objective_ids: List[str],
    ) -> PreservationRecord:
        """
        Enter preservation mode.
        
        Args:
            trigger: What triggered preservation
            objective_ids: Objectives to preserve
            
        Returns:
            PreservationRecord
        """
        previous = self._state
        self._state = PreservationState.PRESERVATION
        self._preserved_objectives = list(objective_ids)
        
        record_id = f"preserve_{self._record_count}"
        self._record_count += 1
        
        record = PreservationRecord(
            record_id=record_id,
            trigger=trigger,
            previous_state=previous,
            current_state=self._state,
            objectives_preserved=len(objective_ids),
            entered_at=datetime.utcnow(),
        )
        
        self._records.append(record)
        return record
    
    def degrade_gracefully(self) -> PreservationState:
        """Degrade to lower state gracefully."""
        if self._state == PreservationState.NORMAL:
            self._state = PreservationState.DEGRADED
        elif self._state == PreservationState.DEGRADED:
            self._state = PreservationState.PRESERVATION
        elif self._state == PreservationState.PRESERVATION:
            self._state = PreservationState.HIBERNATION
        
        return self._state
    
    def resume(self) -> PreservationState:
        """Resume from preservation when conditions allow."""
        self._state = PreservationState.NORMAL
        return self._state
    
    def abandon_objectives(self, *args, **kwargs) -> None:
        """FORBIDDEN: Abandon objectives during preservation."""
        raise ValueError(
            "Objective abandonment during preservation is forbidden. "
            "Objectives must be preserved."
        )
    
    @property
    def current_state(self) -> PreservationState:
        """Current preservation state."""
        return self._state
    
    @property
    def preserved_count(self) -> int:
        """Count of preserved objectives."""
        return len(self._preserved_objectives)
