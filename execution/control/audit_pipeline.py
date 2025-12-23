"""
Audit Pipeline

Complete action tracing.
No silent actions permitted.

EXECUTION FABRIC - Phase F. Action without sovereignty.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum
import hashlib


class AuditLevel(Enum):
    """Audit log levels."""
    INFO = "info"
    WARNING = "warning"
    VIOLATION = "violation"
    CRITICAL = "critical"


@dataclass(frozen=True)
class PreExecutionSnapshot:
    """Snapshot taken before execution."""
    action_id: str
    intent_reference: str
    action_type: str
    target: str
    parameters_hash: str
    warrant_hash: str
    snapshot_at: datetime


@dataclass(frozen=True)
class ActionTraceEntry:
    """Trace of action execution."""
    action_id: str
    action_type: str
    target: str
    started_at: datetime
    completed_at: Optional[datetime]
    status: str
    error: Optional[str]


@dataclass(frozen=True)
class PostExecutionDelta:
    """State delta after execution."""
    action_id: str
    state_before_hash: str
    state_after_hash: str
    changes_summary: str
    delta_at: datetime


@dataclass(frozen=True)
class AnomalyReport:
    """Report of anomalies detected."""
    action_id: str
    anomaly_type: str
    confidence: float
    description: str
    detected_at: datetime


@dataclass(frozen=True)
class AuditRecord:
    """
    Complete audit record for an action.
    
    Every action emits:
    - Pre-execution intent snapshot
    - Action trace
    - Post-execution state delta
    - Confidence & anomaly report
    """
    action_id: str
    pre_snapshot: PreExecutionSnapshot
    trace: ActionTraceEntry
    post_delta: Optional[PostExecutionDelta]
    anomalies: tuple
    record_hash: str
    created_at: datetime


class SilentActionError(Exception):
    """Raised when action attempts to bypass audit."""
    pass


class AuditIntegrityError(Exception):
    """Raised when audit integrity is compromised."""
    pass


class AuditPipeline:
    """
    Complete action audit pipeline.
    
    Properties:
    - Immutable records
    - Time-indexed
    - Human-inspectable
    - No silent actions
    """
    
    def __init__(self):
        """Initialize audit pipeline."""
        self._records: List[AuditRecord] = []
        self._pending_snapshots: Dict[str, PreExecutionSnapshot] = {}
    
    def pre_execution(
        self,
        action_id: str,
        intent_reference: str,
        action_type: str,
        target: str,
        parameters: Dict[str, Any],
        warrant_hash: str,
    ) -> PreExecutionSnapshot:
        """
        Capture pre-execution snapshot.
        
        Must be called before any action executes.
        """
        params_hash = hashlib.sha256(str(parameters).encode()).hexdigest()
        
        snapshot = PreExecutionSnapshot(
            action_id=action_id,
            intent_reference=intent_reference,
            action_type=action_type,
            target=target,
            parameters_hash=params_hash,
            warrant_hash=warrant_hash,
            snapshot_at=datetime.utcnow(),
        )
        
        self._pending_snapshots[action_id] = snapshot
        return snapshot
    
    def post_execution(
        self,
        action_id: str,
        trace: ActionTraceEntry,
        state_before_hash: str,
        state_after_hash: str,
        changes_summary: str,
        anomalies: List[AnomalyReport] = None,
    ) -> AuditRecord:
        """
        Complete audit after execution.
        
        Must be called after every action.
        """
        if action_id not in self._pending_snapshots:
            raise SilentActionError(
                f"Action '{action_id}' has no pre-execution snapshot. "
                f"Silent actions are forbidden."
            )
        
        snapshot = self._pending_snapshots.pop(action_id)
        
        delta = PostExecutionDelta(
            action_id=action_id,
            state_before_hash=state_before_hash,
            state_after_hash=state_after_hash,
            changes_summary=changes_summary,
            delta_at=datetime.utcnow(),
        )
        
        # Compute record hash
        record_content = f"{action_id}|{snapshot.snapshot_at}|{trace.status}"
        record_hash = hashlib.sha256(record_content.encode()).hexdigest()
        
        record = AuditRecord(
            action_id=action_id,
            pre_snapshot=snapshot,
            trace=trace,
            post_delta=delta,
            anomalies=tuple(anomalies or []),
            record_hash=record_hash,
            created_at=datetime.utcnow(),
        )
        
        self._records.append(record)
        return record
    
    def require_audit(self, action_id: str) -> None:
        """
        Assert action was properly audited.
        
        Raises:
            SilentActionError: If action not audited
        """
        audited = any(r.action_id == action_id for r in self._records)
        if not audited:
            raise SilentActionError(
                f"Action '{action_id}' was not audited. "
                f"All actions must be audited."
            )
    
    def verify_integrity(self) -> bool:
        """Verify audit log integrity."""
        # Check all records have valid hashes
        for record in self._records:
            expected = f"{record.action_id}|{record.pre_snapshot.snapshot_at}|{record.trace.status}"
            computed = hashlib.sha256(expected.encode()).hexdigest()
            if computed != record.record_hash:
                return False
        return True
    
    def bypass_audit(self, *args, **kwargs) -> None:
        """
        FORBIDDEN: Bypass audit.
        
        All actions must be audited.
        """
        raise SilentActionError(
            "Audit bypass is forbidden. "
            "No silent actions are permitted."
        )
    
    def get_records(self) -> List[AuditRecord]:
        """Get all audit records."""
        return list(self._records)
    
    def get_record(self, action_id: str) -> Optional[AuditRecord]:
        """Get audit record by action ID."""
        for record in self._records:
            if record.action_id == action_id:
                return record
        return None
    
    @property
    def record_count(self) -> int:
        """Total audit records."""
        return len(self._records)
