"""
Execution Lifecycle

8 stages. No stage is optional.

EFAP-C - Execution Fabric & Agent Physics.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from enum import Enum


class LifecycleStage(Enum):
    """Execution lifecycle stages."""
    KERNEL_AUTHORIZATION = "kernel_authorization"
    WORK_UNIT_CREATION = "work_unit_creation"
    CHANNEL_ASSIGNMENT = "channel_assignment"
    AGENT_BINDING = "agent_binding"
    EXECUTION = "execution"
    OUTCOME_VALIDATION = "outcome_validation"
    FEEDBACK_SIGNAL = "feedback_signal"
    MEMORY_UPDATE = "memory_update"


LIFECYCLE_ORDER = [
    LifecycleStage.KERNEL_AUTHORIZATION,
    LifecycleStage.WORK_UNIT_CREATION,
    LifecycleStage.CHANNEL_ASSIGNMENT,
    LifecycleStage.AGENT_BINDING,
    LifecycleStage.EXECUTION,
    LifecycleStage.OUTCOME_VALIDATION,
    LifecycleStage.FEEDBACK_SIGNAL,
    LifecycleStage.MEMORY_UPDATE,
]


@dataclass
class LifecycleRecord:
    """Record of lifecycle transition."""
    work_id: str
    stage: LifecycleStage
    entered_at: datetime
    exited_at: Optional[datetime]
    success: bool


class LifecycleSkipError(Exception):
    """Raised when lifecycle stage is skipped."""
    pass


class ExecutionLifecycle:
    """
    Execution Lifecycle Manager.
    
    8 stages:
    Kernel Authorization → Work Unit Creation →
    Channel Assignment → Agent Binding →
    Execution → Outcome Validation →
    Feedback Signal → Memory Update
    
    No stage is optional.
    """
    
    def __init__(self):
        """Initialize lifecycle manager."""
        self._stages: dict[str, LifecycleStage] = {}
        self._records: List[LifecycleRecord] = []
    
    def start(self, work_id: str) -> LifecycleRecord:
        """Start lifecycle at kernel authorization."""
        stage = LifecycleStage.KERNEL_AUTHORIZATION
        self._stages[work_id] = stage
        
        record = LifecycleRecord(
            work_id=work_id,
            stage=stage,
            entered_at=datetime.utcnow(),
            exited_at=None,
            success=True,
        )
        
        self._records.append(record)
        return record
    
    def advance(self, work_id: str) -> LifecycleRecord:
        """
        Advance to next stage.
        
        No skipping allowed.
        """
        if work_id not in self._stages:
            raise LifecycleSkipError(
                f"Work '{work_id}' not in lifecycle. Start first."
            )
        
        current = self._stages[work_id]
        current_idx = LIFECYCLE_ORDER.index(current)
        
        if current_idx >= len(LIFECYCLE_ORDER) - 1:
            # Already at end
            return LifecycleRecord(
                work_id=work_id,
                stage=current,
                entered_at=datetime.utcnow(),
                exited_at=datetime.utcnow(),
                success=True,
            )
        
        next_stage = LIFECYCLE_ORDER[current_idx + 1]
        self._stages[work_id] = next_stage
        
        record = LifecycleRecord(
            work_id=work_id,
            stage=next_stage,
            entered_at=datetime.utcnow(),
            exited_at=None,
            success=True,
        )
        
        self._records.append(record)
        return record
    
    def skip_to(self, *args, **kwargs) -> None:
        """FORBIDDEN: Skip lifecycle stages."""
        raise LifecycleSkipError(
            "Lifecycle stages cannot be skipped. "
            "All 8 stages are mandatory."
        )
    
    def get_stage(self, work_id: str) -> Optional[LifecycleStage]:
        """Get current stage."""
        return self._stages.get(work_id)
    
    def is_complete(self, work_id: str) -> bool:
        """Check if lifecycle complete."""
        return self._stages.get(work_id) == LifecycleStage.MEMORY_UPDATE
