"""
Audit Log

Immutable audit logging for kernel operations.
All governance-relevant actions are logged for accountability.

KERNEL MODULE - Human-written, no AI-generated code permitted.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Any
from enum import Enum
import json
from pathlib import Path


class AuditEventType(Enum):
    """Types of audit events."""
    INTENT_VALIDATED = "intent_validated"
    INTENT_REJECTED = "intent_rejected"
    CONFLICT_RESOLVED = "conflict_resolved"
    CHECKPOINT_CREATED = "checkpoint_created"
    ROLLBACK_EXECUTED = "rollback_executed"
    OBJECTIVE_MODIFIED = "objective_modified"
    CONSTRAINT_ACTIVATED = "constraint_activated"
    HUMAN_OVERRIDE = "human_override"
    SAFE_MODE_ENTERED = "safe_mode_entered"
    SHUTDOWN_INITIATED = "shutdown_initiated"


class AuditSeverity(Enum):
    """Severity levels for audit events."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class AuditEntry:
    """An entry in the audit log."""
    id: str
    timestamp: datetime
    event_type: AuditEventType
    severity: AuditSeverity
    actor: str  # Who triggered the event
    action: str  # What action was taken
    target: Optional[str]  # What was affected
    context: dict  # Additional context
    outcome: str  # Result of the action
    checksum: str  # Integrity verification


class AuditLog:
    """
    Immutable audit log for kernel operations.
    
    All entries are append-only and integrity-verified.
    """
    
    def __init__(self, log_path: Path):
        """
        Initialize audit log.
        
        Args:
            log_path: Path to audit log storage
        """
        self._log_path = log_path
        self._entries: List[AuditEntry] = []
        self._entry_count = 0
        self._load_log()
    
    def _load_log(self) -> None:
        """Load existing audit log entries."""
        log_file = self._log_path / "audit.log"
        if log_file.exists():
            with open(log_file, 'r') as f:
                for line in f:
                    if line.strip():
                        entry_data = json.loads(line)
                        # TODO: Deserialize and verify integrity
                        self._entry_count += 1
    
    def log(
        self,
        event_type: AuditEventType,
        severity: AuditSeverity,
        actor: str,
        action: str,
        outcome: str,
        target: Optional[str] = None,
        context: Optional[dict] = None
    ) -> str:
        """
        Log an audit event.
        
        Args:
            event_type: Type of event
            severity: Severity level
            actor: Who triggered the event
            action: What action was taken
            outcome: Result of the action
            target: What was affected (optional)
            context: Additional context (optional)
            
        Returns:
            Audit entry ID
        """
        entry_id = self._generate_entry_id()
        timestamp = datetime.utcnow()
        
        entry_data = {
            "id": entry_id,
            "timestamp": timestamp.isoformat(),
            "event_type": event_type.value,
            "severity": severity.value,
            "actor": actor,
            "action": action,
            "target": target,
            "context": context or {},
            "outcome": outcome
        }
        
        checksum = self._compute_checksum(entry_data)
        
        entry = AuditEntry(
            id=entry_id,
            timestamp=timestamp,
            event_type=event_type,
            severity=severity,
            actor=actor,
            action=action,
            target=target,
            context=context or {},
            outcome=outcome,
            checksum=checksum
        )
        
        self._entries.append(entry)
        self._persist_entry(entry)
        self._entry_count += 1
        
        return entry_id
    
    def query(
        self,
        event_type: Optional[AuditEventType] = None,
        actor: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[AuditEntry]:
        """
        Query audit log entries.
        
        Args:
            event_type: Filter by event type
            actor: Filter by actor
            start_time: Filter by start time
            end_time: Filter by end time
            limit: Maximum entries to return
            
        Returns:
            List of matching audit entries
        """
        results = []
        
        for entry in reversed(self._entries):
            if event_type and entry.event_type != event_type:
                continue
            if actor and entry.actor != actor:
                continue
            if start_time and entry.timestamp < start_time:
                continue
            if end_time and entry.timestamp > end_time:
                continue
            
            results.append(entry)
            if len(results) >= limit:
                break
        
        return results
    
    def verify_integrity(self) -> bool:
        """
        Verify integrity of entire audit log.
        
        Returns:
            True if all entries pass integrity check
        """
        for entry in self._entries:
            entry_data = {
                "id": entry.id,
                "timestamp": entry.timestamp.isoformat(),
                "event_type": entry.event_type.value,
                "severity": entry.severity.value,
                "actor": entry.actor,
                "action": entry.action,
                "target": entry.target,
                "context": entry.context,
                "outcome": entry.outcome
            }
            
            computed = self._compute_checksum(entry_data)
            if computed != entry.checksum:
                return False
        
        return True
    
    def get_entry(self, entry_id: str) -> Optional[AuditEntry]:
        """Get a specific audit entry by ID."""
        for entry in self._entries:
            if entry.id == entry_id:
                return entry
        return None
    
    @property
    def entry_count(self) -> int:
        """Get total number of audit entries."""
        return self._entry_count
    
    def _generate_entry_id(self) -> str:
        """Generate unique entry ID."""
        import uuid
        return f"audit_{uuid.uuid4().hex[:16]}"
    
    def _compute_checksum(self, data: dict) -> str:
        """Compute checksum for entry integrity."""
        import hashlib
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    def _persist_entry(self, entry: AuditEntry) -> None:
        """Persist entry to storage (append-only)."""
        log_file = self._log_path / "audit.log"
        self._log_path.mkdir(parents=True, exist_ok=True)
        
        entry_data = {
            "id": entry.id,
            "timestamp": entry.timestamp.isoformat(),
            "event_type": entry.event_type.value,
            "severity": entry.severity.value,
            "actor": entry.actor,
            "action": entry.action,
            "target": entry.target,
            "context": entry.context,
            "outcome": entry.outcome,
            "checksum": entry.checksum
        }
        
        with open(log_file, 'a') as f:
            f.write(json.dumps(entry_data) + "\n")
