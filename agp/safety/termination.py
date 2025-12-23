"""
Termination

Silent and final. No resurrection without re-genesis.

AGP-C - Agent Genesis Protocol.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Set
from enum import Enum


class TerminationReason(Enum):
    """Reasons for termination."""
    GOAL_COMPLETION = "goal_completion"
    TIMEOUT = "timeout"
    UNDERPERFORMANCE = "underperformance"
    RISK_ESCALATION = "risk_escalation"
    KERNEL_RECALL = "kernel_recall"
    DRIFT_DETECTED = "drift_detected"
    ENVELOPE_VIOLATION = "envelope_violation"
    SELF_PRESERVATION = "self_preservation"


@dataclass(frozen=True)
class TerminationRecord:
    """Record of agent termination."""
    agent_id: str
    reason: TerminationReason
    final: bool              # Always True
    terminated_at: datetime
    notes: Optional[str]


class ResurrectionError(Exception):
    """Raised when resurrection is attempted."""
    pass


class TerminationManager:
    """
    Termination Manager.
    
    Termination can occur via:
    - Goal completion
    - Timeout
    - Underperformance
    - Risk escalation
    - Kernel recall
    
    Termination is silent and final.
    No resurrection without re-genesis.
    """
    
    def __init__(self):
        """Initialize manager."""
        self._terminated: Set[str] = set()
        self._records: List[TerminationRecord] = []
    
    def terminate(
        self,
        agent_id: str,
        reason: TerminationReason,
        notes: Optional[str] = None,
    ) -> TerminationRecord:
        """
        Terminate an agent.
        
        Silent and final.
        
        Args:
            agent_id: Agent to terminate
            reason: Why terminating
            notes: Optional notes
            
        Returns:
            TerminationRecord
        """
        record = TerminationRecord(
            agent_id=agent_id,
            reason=reason,
            final=True,  # Always final
            terminated_at=datetime.utcnow(),
            notes=notes,
        )
        
        self._terminated.add(agent_id)
        self._records.append(record)
        
        return record
    
    def is_terminated(self, agent_id: str) -> bool:
        """Check if agent is terminated."""
        return agent_id in self._terminated
    
    def resurrect(self, *args, **kwargs) -> None:
        """FORBIDDEN: Resurrect terminated agent."""
        raise ResurrectionError(
            "Resurrection is forbidden. "
            "No resurrection without re-genesis. "
            "Termination is final."
        )
    
    def undo_termination(self, *args, **kwargs) -> None:
        """FORBIDDEN: Undo termination."""
        raise ResurrectionError(
            "Termination cannot be undone. "
            "Termination is silent and final."
        )
    
    def get_record(self, agent_id: str) -> Optional[TerminationRecord]:
        """Get termination record."""
        for record in self._records:
            if record.agent_id == agent_id:
                return record
        return None
    
    @property
    def terminated_count(self) -> int:
        """Total terminated agents."""
        return len(self._terminated)
