"""
Audit Event Log

Append-only, hash-chained, externally verifiable audit log.
If audit logging fails → Kernel halts.

KERNEL AUDIT - Phase A. Zero autonomy.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
import hashlib
import json


class AuditLogError(Exception):
    """Raised when audit logging fails."""
    pass


class AuditLogHaltError(AuditLogError):
    """Raised when audit failure requires kernel halt."""
    pass


@dataclass(frozen=True)
class AuditEvent:
    """
    Single audit event.
    
    Every kernel event produces one of these.
    """
    event_id: str
    timestamp: datetime
    event_type: str
    input_hash: str
    decision: str
    axiom_reference: Optional[str]
    previous_hash: str
    event_hash: str


class AuditEventLog:
    """
    Append-only, hash-chained audit event log.
    
    Properties:
    - Append-only (no modification, no deletion)
    - Hash-chained (each entry links to previous)
    - Externally verifiable (deterministic hashes)
    - Cannot be truncated
    
    If audit logging fails → Kernel halts.
    """
    
    GENESIS_HASH = "0" * 64
    
    def __init__(self):
        """Initialize empty audit log."""
        self._events: List[AuditEvent] = []
        self._chain_head = self.GENESIS_HASH
        self._halted = False
    
    def append(
        self,
        event_type: str,
        input_hash: str,
        decision: str,
        axiom_reference: Optional[str] = None,
    ) -> AuditEvent:
        """
        Append an event to the audit log.
        
        Args:
            event_type: Type of event
            input_hash: Hash of input that triggered event
            decision: Decision made
            axiom_reference: Which axiom was applied (if any)
            
        Returns:
            AuditEvent
            
        Raises:
            AuditLogHaltError: If logging fails
        """
        if self._halted:
            raise AuditLogHaltError(
                "Audit log is halted. No further events can be logged."
            )
        
        try:
            timestamp = datetime.utcnow()
            event_id = self._generate_event_id(len(self._events), input_hash)
            
            # Compute event hash
            event_content = (
                f"{event_id}|{timestamp.isoformat()}|{event_type}|"
                f"{input_hash}|{decision}|{axiom_reference or 'none'}"
            )
            event_hash = hashlib.sha256(event_content.encode()).hexdigest()
            
            event = AuditEvent(
                event_id=event_id,
                timestamp=timestamp,
                event_type=event_type,
                input_hash=input_hash,
                decision=decision,
                axiom_reference=axiom_reference,
                previous_hash=self._chain_head,
                event_hash=event_hash,
            )
            
            self._events.append(event)
            
            # Update chain head
            chain_content = f"{self._chain_head}|{event_hash}"
            self._chain_head = hashlib.sha256(chain_content.encode()).hexdigest()
            
            return event
            
        except Exception as e:
            self._halted = True
            raise AuditLogHaltError(
                f"Audit logging failed: {e}. KERNEL MUST HALT."
            )
    
    def verify_chain(self) -> bool:
        """
        Verify the integrity of the hash chain.
        
        Returns True if chain is valid.
        """
        current_hash = self.GENESIS_HASH
        
        for event in self._events:
            # Verify previous hash
            if event.previous_hash != current_hash:
                return False
            
            # Update chain
            chain_content = f"{current_hash}|{event.event_hash}"
            current_hash = hashlib.sha256(chain_content.encode()).hexdigest()
        
        return current_hash == self._chain_head
    
    def truncate(self, *args, **kwargs) -> None:
        """
        FORBIDDEN: Truncate audit log.
        
        Audit log cannot be truncated.
        """
        raise AuditLogError(
            "Audit log cannot be truncated. "
            "This is an append-only log."
        )
    
    def delete(self, *args, **kwargs) -> None:
        """
        FORBIDDEN: Delete from audit log.
        
        Entries cannot be deleted.
        """
        raise AuditLogError(
            "Audit entries cannot be deleted. "
            "This is an append-only log."
        )
    
    def modify(self, *args, **kwargs) -> None:
        """
        FORBIDDEN: Modify audit log.
        
        Entries cannot be modified.
        """
        raise AuditLogError(
            "Audit entries cannot be modified. "
            "All entries are immutable."
        )
    
    def _generate_event_id(self, sequence: int, input_hash: str) -> str:
        """Generate deterministic event ID."""
        content = f"{sequence}|{input_hash}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def get_events(self) -> List[AuditEvent]:
        """Get all events (read-only copy)."""
        return list(self._events)
    
    def get_event(self, event_id: str) -> Optional[AuditEvent]:
        """Get event by ID."""
        for event in self._events:
            if event.event_id == event_id:
                return event
        return None
    
    @property
    def chain_head(self) -> str:
        """Current chain head hash."""
        return self._chain_head
    
    @property
    def event_count(self) -> int:
        """Number of events in log."""
        return len(self._events)
    
    @property
    def is_halted(self) -> bool:
        """Check if log is halted."""
        return self._halted
