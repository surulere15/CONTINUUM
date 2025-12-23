"""
Failure Rerouter

Handles execution failures with retry logic, alternative routing,
and escalation when needed.
"""

from dataclasses import dataclass
from typing import Optional, List
from enum import Enum


class FailureType(Enum):
    TIMEOUT = "timeout"
    RESOURCE = "resource"
    DEPENDENCY = "dependency"
    RUNTIME = "runtime"
    GOVERNANCE = "governance"


class FailureAction(Enum):
    RETRY = "retry"
    REROUTE = "reroute"
    ESCALATE = "escalate"
    ABORT = "abort"


@dataclass
class FailureContext:
    task_id: str
    failure_type: FailureType
    error_message: str
    attempt_count: int
    max_retries: int


class FailureRerouter:
    """Handles execution failures."""
    
    def __init__(self, max_retries: int = 3):
        self._max_retries = max_retries
    
    def handle(self, context: FailureContext) -> FailureAction:
        """Determine action for failure."""
        # Governance failures are never retried
        if context.failure_type == FailureType.GOVERNANCE:
            return FailureAction.ABORT
        
        # Retry if under limit
        if context.attempt_count < context.max_retries:
            if context.failure_type in [FailureType.TIMEOUT, FailureType.RUNTIME]:
                return FailureAction.RETRY
            elif context.failure_type == FailureType.RESOURCE:
                return FailureAction.REROUTE
        
        # Escalate if retries exhausted
        return FailureAction.ESCALATE
    
    def get_backoff(self, attempt: int) -> float:
        """Calculate retry backoff in seconds."""
        return min(2 ** attempt, 60)  # Exponential, max 60s
