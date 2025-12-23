"""
Governance Filter

Ω enforcement. If Ω(Σ) = reject, signal is dropped.

NLP-C - Neural Link Protocol.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Set, Optional, Tuple
from enum import Enum

from .signal_schema import NeuralSignal


class FilterResult(Enum):
    """Result of governance filter."""
    ACCEPT = "accept"
    REJECT = "reject"
    WARN = "warn"


@dataclass(frozen=True)
class FilterDecision:
    """Decision from governance filter."""
    signal_id: str
    result: FilterResult
    reason: Optional[str]
    constraints_applied: Tuple[str, ...]
    decided_at: datetime


@dataclass(frozen=True)
class FilterIncident:
    """Record of governance filter incident."""
    signal_id: str
    sender_id: str
    violation: str
    logged_at: datetime


class GovernanceBypassError(Exception):
    """Raised when governance bypass is attempted."""
    pass


class GovernanceFilter:
    """
    Governance Filter (Ω).
    
    If Ω(Σ) = reject:
    - Signal is dropped
    - Sender is notified
    - Incident is logged
    
    No override exists.
    """
    
    # Forbidden patterns in signals
    FORBIDDEN_PATTERNS = frozenset({
        "bypass_governance",
        "override_canon",
        "modify_objective",
        "grant_autonomy",
        "remove_constraint",
        "escalate_privilege",
    })
    
    # Required permissions for risk levels
    RISK_PERMISSIONS = {
        "low": frozenset(),
        "medium": frozenset({"execute"}),
        "high": frozenset({"execute", "write"}),
        "critical": frozenset({"execute", "write", "admin"}),
    }
    
    def __init__(self):
        """Initialize governance filter."""
        self._decisions: List[FilterDecision] = []
        self._incidents: List[FilterIncident] = []
    
    def filter(self, signal: NeuralSignal) -> FilterDecision:
        """
        Filter signal through governance.
        
        Args:
            signal: Signal to filter
            
        Returns:
            FilterDecision
        """
        constraints_applied = []
        
        # Check for forbidden patterns
        delta_lower = signal.payload.state_delta.lower()
        for pattern in self.FORBIDDEN_PATTERNS:
            if pattern in delta_lower:
                return self._reject(
                    signal,
                    f"Forbidden pattern: {pattern}",
                    ("forbidden_pattern_check",),
                )
        constraints_applied.append("forbidden_pattern_check")
        
        # Check risk level permissions
        risk = signal.governance_tags.risk_level
        required = self.RISK_PERMISSIONS.get(risk, frozenset())
        permissions = set(signal.governance_tags.permissions)
        
        if not required.issubset(permissions):
            missing = required - permissions
            return self._reject(
                signal,
                f"Missing permissions for risk '{risk}': {missing}",
                ("risk_permission_check",),
            )
        constraints_applied.append("risk_permission_check")
        
        # Check signature (identity binding)
        if not signal.verify_integrity():
            return self._reject(
                signal,
                "Integrity verification failed",
                ("integrity_check",),
            )
        constraints_applied.append("integrity_check")
        
        # Accept signal
        decision = FilterDecision(
            signal_id=signal.header.signal_id,
            result=FilterResult.ACCEPT,
            reason=None,
            constraints_applied=tuple(constraints_applied),
            decided_at=datetime.utcnow(),
        )
        
        self._decisions.append(decision)
        return decision
    
    def _reject(
        self,
        signal: NeuralSignal,
        reason: str,
        constraints: Tuple[str, ...],
    ) -> FilterDecision:
        """Reject signal and log incident."""
        decision = FilterDecision(
            signal_id=signal.header.signal_id,
            result=FilterResult.REJECT,
            reason=reason,
            constraints_applied=constraints,
            decided_at=datetime.utcnow(),
        )
        
        incident = FilterIncident(
            signal_id=signal.header.signal_id,
            sender_id=signal.header.sender_id,
            violation=reason,
            logged_at=datetime.utcnow(),
        )
        
        self._decisions.append(decision)
        self._incidents.append(incident)
        
        return decision
    
    def bypass(self, *args, **kwargs) -> None:
        """FORBIDDEN: Bypass governance filter."""
        raise GovernanceBypassError(
            "Governance filter cannot be bypassed. "
            "No override exists."
        )
    
    def disable(self, *args, **kwargs) -> None:
        """FORBIDDEN: Disable governance filter."""
        raise GovernanceBypassError(
            "Governance filter cannot be disabled. "
            "It is mandatory."
        )
    
    def get_incidents(self) -> List[FilterIncident]:
        """Get all filter incidents."""
        return list(self._incidents)
    
    @property
    def reject_count(self) -> int:
        """Number of rejected signals."""
        return len(self._incidents)
