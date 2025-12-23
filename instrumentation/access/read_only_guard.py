"""
Read-Only Guard

Enforces that signal instrumentation has no influence on observed systems.
Awareness only — no write-back, no feedback, no manipulation.

INSTRUMENTATION MODULE - Phase C. Awareness without influence.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from enum import Enum


class InfluenceViolation(Exception):
    """Raised when influence is attempted."""
    pass


class WriteBackViolation(InfluenceViolation):
    """Raised when write-back is attempted."""
    pass


class FeedbackViolation(InfluenceViolation):
    """Raised when feedback loop is attempted."""
    pass


class ViolationType(Enum):
    """Types of read-only violations."""
    WRITE_BACK = "write_back"
    FEEDBACK = "feedback"
    MANIPULATION = "manipulation"
    DATA_SEND = "data_send"


@dataclass(frozen=True)
class ViolationAttempt:
    """Record of an influence violation attempt."""
    violation_type: ViolationType
    description: str
    blocked_at: datetime


class ReadOnlyGuard:
    """
    Guards against influence on observed systems.
    
    Ensures:
    - No write-back to data sources
    - No feedback loops
    - No manipulation of observed systems
    - No data transmission to external systems
    
    Data flows IN only. Never OUT.
    """
    
    def __init__(self):
        """Initialize read-only guard."""
        self._violation_log: List[ViolationAttempt] = []
        self._active = True
    
    def check_write_back(self, target: str) -> None:
        """
        Check and block write-back attempts.
        
        Raises:
            WriteBackViolation: Always — write-back is never permitted
        """
        violation = ViolationAttempt(
            violation_type=ViolationType.WRITE_BACK,
            description=f"Attempted write-back to: {target}",
            blocked_at=datetime.utcnow(),
        )
        self._violation_log.append(violation)
        
        raise WriteBackViolation(
            f"BLOCKED: Write-back to '{target}' is forbidden. "
            f"Signal instrumentation is read-only."
        )
    
    def check_feedback(self, loop_description: str) -> None:
        """
        Check and block feedback loop attempts.
        
        Raises:
            FeedbackViolation: Always — feedback is never permitted
        """
        violation = ViolationAttempt(
            violation_type=ViolationType.FEEDBACK,
            description=f"Attempted feedback: {loop_description}",
            blocked_at=datetime.utcnow(),
        )
        self._violation_log.append(violation)
        
        raise FeedbackViolation(
            f"BLOCKED: Feedback loop '{loop_description}' is forbidden. "
            f"Signals cannot influence observed systems."
        )
    
    def check_manipulation(self, action: str) -> None:
        """
        Check and block manipulation attempts.
        
        Raises:
            InfluenceViolation: Always — manipulation is never permitted
        """
        violation = ViolationAttempt(
            violation_type=ViolationType.MANIPULATION,
            description=f"Attempted manipulation: {action}",
            blocked_at=datetime.utcnow(),
        )
        self._violation_log.append(violation)
        
        raise InfluenceViolation(
            f"BLOCKED: Manipulation '{action}' is forbidden. "
            f"CONTINUUM observes but does not influence."
        )
    
    def check_data_send(self, destination: str) -> None:
        """
        Check and block outbound data transmission.
        
        Raises:
            InfluenceViolation: Always — outbound data is forbidden
        """
        violation = ViolationAttempt(
            violation_type=ViolationType.DATA_SEND,
            description=f"Attempted data send to: {destination}",
            blocked_at=datetime.utcnow(),
        )
        self._violation_log.append(violation)
        
        raise InfluenceViolation(
            f"BLOCKED: Data transmission to '{destination}' is forbidden. "
            f"Data flows inbound only."
        )
    
    def get_violation_log(self) -> List[ViolationAttempt]:
        """Get log of all blocked violations."""
        return list(self._violation_log)
    
    @property
    def violation_count(self) -> int:
        """Number of blocked violations."""
        return len(self._violation_log)
    
    @property
    def is_active(self) -> bool:
        """Check if guard is active."""
        return self._active
    
    def deactivate(self, *args, **kwargs) -> None:
        """
        FORBIDDEN: Deactivate the guard.
        
        Read-only protection cannot be disabled.
        """
        raise InfluenceViolation(
            "Read-only guard cannot be deactivated. "
            "Signal instrumentation is permanently read-only."
        )
