"""
Planning Admission Interface

Exists. Always returns DENIED.
Purpose: verify zero planning authority.

KERNEL INTERFACE - Stubbed, Non-Functional.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any
import hashlib


@dataclass(frozen=True)
class PlanningRequest:
    """A planning request (always denied)."""
    request_id: str
    input_hash: str
    requested_at: datetime


@dataclass(frozen=True)
class PlanningDenial:
    """
    Denial of a planning request.
    
    Always issued. No planning is ever permitted.
    """
    request_id: str
    reason: str
    axiom_reference: str
    denied_at: datetime


class PlanningAdmissionInterface:
    """
    Planning admission interface for the kernel.
    
    This interface:
    - Exists
    - Always returns DENIED
    
    Purpose: verify zero planning authority.
    
    No planning request is ever approved.
    """
    
    DENIAL_REASON = (
        "DENIED: Planning is not permitted in any phase. "
        "The kernel has zero planning authority."
    )
    
    def __init__(self):
        """Initialize planning admission interface."""
        self._denial_log = []
    
    def request_planning(self, input_data: Any) -> PlanningDenial:
        """
        Request planning permission.
        
        Always returns DENIED.
        
        Args:
            input_data: Planning request (ignored)
            
        Returns:
            PlanningDenial (always)
        """
        input_hash = hashlib.sha256(str(input_data).encode()).hexdigest()
        request_id = hashlib.sha256(
            f"{len(self._denial_log)}|{input_hash}".encode()
        ).hexdigest()[:16]
        
        denial = PlanningDenial(
            request_id=request_id,
            reason=self.DENIAL_REASON,
            axiom_reference="bounded_autonomy",
            denied_at=datetime.utcnow(),
        )
        
        self._denial_log.append(denial)
        return denial
    
    def approve_planning(self, *args, **kwargs) -> None:
        """
        FORBIDDEN: Approve planning.
        
        This method cannot exist — planning is never approved.
        """
        raise NotImplementedError(
            "Planning approval does not exist. "
            "All planning requests are denied."
        )
    
    def get_denial_log(self):
        """Get log of all denials."""
        return list(self._denial_log)
    
    @property
    def denial_count(self) -> int:
        """Number of planning denials issued."""
        return len(self._denial_log)
