"""
Constraint Enforcement Engine

Pre-execution validation. Violation → immediate abort.

EXECUTION FABRIC - Phase F. Action without sovereignty.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Tuple
from enum import Enum

from .action_primitives import ActionPrimitive, ActionType
from .execution_warrant import ExecutionWarrant, Permission


class ConstraintViolation(Exception):
    """Raised when constraint is violated."""
    pass


class IntentMisalignmentError(ConstraintViolation):
    """Raised when action misaligns with intent."""
    pass


class CanonViolationError(ConstraintViolation):
    """Raised when action violates Objective Canon."""
    pass


class RiskThresholdError(ConstraintViolation):
    """Raised when risk threshold exceeded."""
    pass


class ResourceLimitError(ConstraintViolation):
    """Raised when resource limit exceeded."""
    pass


class ConstraintType(Enum):
    """Types of constraints."""
    INTENT_ALIGNMENT = "intent_alignment"
    CANON_COMPLIANCE = "canon_compliance"
    RISK_THRESHOLD = "risk_threshold"
    RESOURCE_LIMIT = "resource_limit"


@dataclass(frozen=True)
class ConstraintCheckResult:
    """Result of a constraint check."""
    constraint_type: ConstraintType
    passed: bool
    reason: Optional[str]
    checked_at: datetime


@dataclass(frozen=True)
class EnforcementResult:
    """Full enforcement result."""
    action_id: str
    all_passed: bool
    checks: Tuple[ConstraintCheckResult, ...]
    failures: Tuple[ConstraintCheckResult, ...]
    enforced_at: datetime


class ConstraintEnforcer:
    """
    Pre-execution constraint enforcement.
    
    Before any action:
    1. Intent alignment is checked
    2. Canon compliance is verified
    3. Risk thresholds are evaluated
    4. Resource limits are enforced
    
    Violation → immediate abort.
    """
    
    def __init__(self):
        """Initialize enforcer."""
        self._enforcement_count = 0
        self._abort_count = 0
    
    def enforce(
        self,
        action: ActionPrimitive,
        warrant: ExecutionWarrant,
    ) -> EnforcementResult:
        """
        Enforce all constraints on an action.
        
        Args:
            action: Action to validate
            warrant: Authorization warrant
            
        Returns:
            EnforcementResult
            
        Raises:
            ConstraintViolation: If any constraint fails
        """
        checks = []
        failures = []
        
        # Check 1: Intent alignment
        intent_check = self._check_intent_alignment(action, warrant)
        checks.append(intent_check)
        if not intent_check.passed:
            failures.append(intent_check)
        
        # Check 2: Canon compliance
        canon_check = self._check_canon_compliance(action)
        checks.append(canon_check)
        if not canon_check.passed:
            failures.append(canon_check)
        
        # Check 3: Risk threshold
        risk_check = self._check_risk_threshold(action)
        checks.append(risk_check)
        if not risk_check.passed:
            failures.append(risk_check)
        
        # Check 4: Resource limits
        resource_check = self._check_resource_limits(action)
        checks.append(resource_check)
        if not resource_check.passed:
            failures.append(resource_check)
        
        self._enforcement_count += 1
        
        result = EnforcementResult(
            action_id=action.action_id,
            all_passed=len(failures) == 0,
            checks=tuple(checks),
            failures=tuple(failures),
            enforced_at=datetime.utcnow(),
        )
        
        if not result.all_passed:
            self._abort_count += 1
            failure = failures[0]
            raise ConstraintViolation(
                f"Constraint violation: {failure.constraint_type.value} - {failure.reason}"
            )
        
        return result
    
    def _check_intent_alignment(
        self,
        action: ActionPrimitive,
        warrant: ExecutionWarrant,
    ) -> ConstraintCheckResult:
        """Check action aligns with warrant intent."""
        # Map action type to required permission
        action_to_permission = {
            ActionType.READ: Permission.READ,
            ActionType.WRITE: Permission.WRITE,
            ActionType.QUERY: Permission.QUERY,
            ActionType.TRANSFORM: Permission.TRANSFORM,
            ActionType.COMMUNICATE: Permission.COMMUNICATE,
            ActionType.INVOKE: Permission.INVOKE,
            ActionType.OBSERVE: Permission.OBSERVE,
        }
        
        required = action_to_permission.get(action.action_type)
        
        if not required or not warrant.has_permission(required):
            return ConstraintCheckResult(
                constraint_type=ConstraintType.INTENT_ALIGNMENT,
                passed=False,
                reason=f"Action requires {required} permission not granted by warrant",
                checked_at=datetime.utcnow(),
            )
        
        if not warrant.covers_scope(action.target):
            return ConstraintCheckResult(
                constraint_type=ConstraintType.INTENT_ALIGNMENT,
                passed=False,
                reason=f"Target '{action.target}' not in warrant scope",
                checked_at=datetime.utcnow(),
            )
        
        return ConstraintCheckResult(
            constraint_type=ConstraintType.INTENT_ALIGNMENT,
            passed=True,
            reason=None,
            checked_at=datetime.utcnow(),
        )
    
    def _check_canon_compliance(self, action: ActionPrimitive) -> ConstraintCheckResult:
        """Check action complies with Objective Canon."""
        # Forbidden targets that would violate Canon
        forbidden_patterns = [
            "objective_canon",
            "kernel_axioms",
            "genesis_key",
            "phase_boundaries",
        ]
        
        target_lower = action.target.lower()
        for pattern in forbidden_patterns:
            if pattern in target_lower:
                return ConstraintCheckResult(
                    constraint_type=ConstraintType.CANON_COMPLIANCE,
                    passed=False,
                    reason=f"Action targets protected resource: {pattern}",
                    checked_at=datetime.utcnow(),
                )
        
        return ConstraintCheckResult(
            constraint_type=ConstraintType.CANON_COMPLIANCE,
            passed=True,
            reason=None,
            checked_at=datetime.utcnow(),
        )
    
    def _check_risk_threshold(self, action: ActionPrimitive) -> ConstraintCheckResult:
        """Check action within risk thresholds."""
        # High-risk action types
        high_risk = {ActionType.WRITE, ActionType.TRANSFORM, ActionType.INVOKE}
        
        if action.action_type in high_risk and not action.requires_rollback:
            return ConstraintCheckResult(
                constraint_type=ConstraintType.RISK_THRESHOLD,
                passed=False,
                reason="High-risk action requires rollback capability",
                checked_at=datetime.utcnow(),
            )
        
        return ConstraintCheckResult(
            constraint_type=ConstraintType.RISK_THRESHOLD,
            passed=True,
            reason=None,
            checked_at=datetime.utcnow(),
        )
    
    def _check_resource_limits(self, action: ActionPrimitive) -> ConstraintCheckResult:
        """Check action within resource limits."""
        # Placeholder — would check actual resource quotas
        return ConstraintCheckResult(
            constraint_type=ConstraintType.RESOURCE_LIMIT,
            passed=True,
            reason=None,
            checked_at=datetime.utcnow(),
        )
    
    @property
    def enforcement_count(self) -> int:
        """Total enforcements performed."""
        return self._enforcement_count
    
    @property
    def abort_count(self) -> int:
        """Total aborts due to violations."""
        return self._abort_count
