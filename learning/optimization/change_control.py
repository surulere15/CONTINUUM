"""
Change Control & Validation

Staged, reversible, validated optimizations.
Failed validation → rollback.

LEARNING - Phase H. Improvement without ambition.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable
from enum import Enum
import hashlib


class ChangeStatus(Enum):
    """Status of optimization change."""
    PROPOSED = "proposed"
    STAGED = "staged"
    VALIDATING = "validating"
    VALIDATED = "validated"
    APPLIED = "applied"
    ROLLED_BACK = "rolled_back"
    REJECTED = "rejected"


@dataclass(frozen=True)
class OptimizationChange:
    """
    A proposed optimization change.
    
    All optimizations:
    - Are staged
    - Are reversible
    - Require validation
    - Are logged
    """
    change_id: str
    target: str
    description: str
    baseline_value: float
    proposed_value: float
    rollback_procedure: str
    proposed_at: datetime


@dataclass(frozen=True)
class ValidationResult:
    """Result of change validation."""
    change_id: str
    passed: bool
    baseline_metric: float
    new_metric: float
    improvement: float
    validated_at: datetime
    notes: Optional[str]


class ValidationFailedError(Exception):
    """Raised when validation fails."""
    pass


class IrreversibleChangeError(Exception):
    """Raised when irreversible change is attempted."""
    pass


class ChangeController:
    """
    Controls optimization changes.
    
    All optimizations:
    - Are staged
    - Are reversible
    - Require validation against baseline
    - Are logged and auditable
    
    Failed validation → rollback.
    """
    
    def __init__(self):
        """Initialize change controller."""
        self._changes: Dict[str, OptimizationChange] = {}
        self._status: Dict[str, ChangeStatus] = {}
        self._validations: Dict[str, ValidationResult] = {}
        self._change_log: List[tuple] = []
    
    def propose(
        self,
        target: str,
        description: str,
        baseline_value: float,
        proposed_value: float,
        rollback_procedure: str,
    ) -> OptimizationChange:
        """
        Propose an optimization change.
        
        Args:
            target: What is being optimized
            description: What the change does
            baseline_value: Current value
            proposed_value: Proposed value
            rollback_procedure: How to roll back
            
        Returns:
            OptimizationChange
        """
        if not rollback_procedure:
            raise IrreversibleChangeError(
                "All changes must have a rollback procedure. "
                "Irreversible changes are forbidden."
            )
        
        change_id = self._generate_id()
        
        change = OptimizationChange(
            change_id=change_id,
            target=target,
            description=description,
            baseline_value=baseline_value,
            proposed_value=proposed_value,
            rollback_procedure=rollback_procedure,
            proposed_at=datetime.utcnow(),
        )
        
        self._changes[change_id] = change
        self._status[change_id] = ChangeStatus.PROPOSED
        self._log("proposed", change_id)
        
        return change
    
    def stage(self, change_id: str) -> None:
        """Stage a change for validation."""
        if change_id not in self._changes:
            raise ValueError(f"Unknown change: {change_id}")
        
        self._status[change_id] = ChangeStatus.STAGED
        self._log("staged", change_id)
    
    def validate(
        self,
        change_id: str,
        baseline_metric: float,
        new_metric: float,
        improvement_threshold: float = 0.0,
    ) -> ValidationResult:
        """
        Validate a staged change.
        
        Args:
            change_id: Change to validate
            baseline_metric: Metric before change
            new_metric: Metric after change
            improvement_threshold: Minimum required improvement
            
        Returns:
            ValidationResult
        """
        if change_id not in self._changes:
            raise ValueError(f"Unknown change: {change_id}")
        
        self._status[change_id] = ChangeStatus.VALIDATING
        
        improvement = baseline_metric - new_metric  # Lower is better
        passed = improvement >= improvement_threshold
        
        result = ValidationResult(
            change_id=change_id,
            passed=passed,
            baseline_metric=baseline_metric,
            new_metric=new_metric,
            improvement=improvement,
            validated_at=datetime.utcnow(),
            notes=None if passed else "Failed to meet improvement threshold",
        )
        
        self._validations[change_id] = result
        
        if passed:
            self._status[change_id] = ChangeStatus.VALIDATED
            self._log("validated", change_id)
        else:
            self._status[change_id] = ChangeStatus.REJECTED
            self._log("rejected", change_id)
            raise ValidationFailedError(
                f"Change {change_id} failed validation. Rolling back."
            )
        
        return result
    
    def apply(self, change_id: str) -> None:
        """Apply a validated change."""
        if self._status.get(change_id) != ChangeStatus.VALIDATED:
            raise ValueError("Can only apply validated changes")
        
        self._status[change_id] = ChangeStatus.APPLIED
        self._log("applied", change_id)
    
    def rollback(self, change_id: str) -> None:
        """Roll back a change."""
        if change_id not in self._changes:
            raise ValueError(f"Unknown change: {change_id}")
        
        self._status[change_id] = ChangeStatus.ROLLED_BACK
        self._log("rolled_back", change_id)
    
    def make_irreversible_change(self, *args, **kwargs) -> None:
        """FORBIDDEN: Make irreversible change."""
        raise IrreversibleChangeError(
            "Irreversible changes are forbidden. "
            "All optimizations must be reversible."
        )
    
    def _generate_id(self) -> str:
        """Generate change ID."""
        content = f"change:{len(self._changes)}:{datetime.utcnow().isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def _log(self, action: str, change_id: str) -> None:
        """Log change action."""
        self._change_log.append((action, change_id, datetime.utcnow()))
    
    def get_status(self, change_id: str) -> ChangeStatus:
        """Get change status."""
        return self._status.get(change_id, ChangeStatus.PROPOSED)
    
    def get_log(self) -> List[tuple]:
        """Get change log."""
        return list(self._change_log)
