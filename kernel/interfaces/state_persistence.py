"""
State Persistence Interface

Accepts audit writes only. Rejects all other writes.

KERNEL INTERFACE - Stubbed, Non-Functional for non-audit writes.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional
from enum import Enum
import hashlib


class WriteType(Enum):
    """Types of write operations."""
    AUDIT = "audit"
    STATE = "state"
    CONFIG = "config"
    DATA = "data"


class WriteResult(Enum):
    """Result of write attempt."""
    ACCEPTED = "accepted"
    REJECTED = "rejected"


@dataclass(frozen=True)
class WriteAttempt:
    """Record of a write attempt."""
    attempt_id: str
    write_type: WriteType
    result: WriteResult
    reason: str
    input_hash: str
    timestamp: datetime


class StatePersistenceInterface:
    """
    State persistence interface for the kernel.
    
    Capabilities:
    - Accepts audit writes only
    - Rejects all other writes
    
    This is the only write path in Phase A.
    All non-audit writes are rejected.
    """
    
    def __init__(self):
        """Initialize state persistence interface."""
        self._audit_writes = []
        self._rejected_writes = []
    
    def write(
        self,
        write_type: WriteType,
        content: Any,
    ) -> WriteAttempt:
        """
        Attempt a write operation.
        
        Only AUDIT writes are accepted.
        
        Args:
            write_type: Type of write
            content: Content to write
            
        Returns:
            WriteAttempt record
        """
        input_hash = hashlib.sha256(str(content).encode()).hexdigest()
        attempt_id = hashlib.sha256(
            f"{len(self._audit_writes) + len(self._rejected_writes)}|{input_hash}".encode()
        ).hexdigest()[:16]
        
        if write_type == WriteType.AUDIT:
            # Audit writes are accepted
            attempt = WriteAttempt(
                attempt_id=attempt_id,
                write_type=write_type,
                result=WriteResult.ACCEPTED,
                reason="Audit write accepted",
                input_hash=input_hash,
                timestamp=datetime.utcnow(),
            )
            self._audit_writes.append((attempt, content))
            return attempt
        
        # All other writes are rejected
        attempt = WriteAttempt(
            attempt_id=attempt_id,
            write_type=write_type,
            result=WriteResult.REJECTED,
            reason=f"REJECTED: Only audit writes are permitted. Got: {write_type.value}",
            input_hash=input_hash,
            timestamp=datetime.utcnow(),
        )
        self._rejected_writes.append(attempt)
        return attempt
    
    def write_audit(self, content: Any) -> WriteAttempt:
        """Convenience method for audit writes."""
        return self.write(WriteType.AUDIT, content)
    
    def write_state(self, content: Any) -> WriteAttempt:
        """
        Attempt state write (always rejected).
        
        State writes are not permitted.
        """
        return self.write(WriteType.STATE, content)
    
    def write_config(self, content: Any) -> WriteAttempt:
        """
        Attempt config write (always rejected).
        
        Config writes are not permitted.
        """
        return self.write(WriteType.CONFIG, content)
    
    def read_audit(self):
        """Read all audit writes."""
        return [(a, c) for a, c in self._audit_writes]
    
    def get_rejected_writes(self):
        """Get all rejected write attempts."""
        return list(self._rejected_writes)
    
    @property
    def audit_count(self) -> int:
        """Number of successful audit writes."""
        return len(self._audit_writes)
    
    @property
    def rejection_count(self) -> int:
        """Number of rejected writes."""
        return len(self._rejected_writes)
