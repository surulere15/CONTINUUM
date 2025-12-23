"""
Optimization Guardrails

Canon/intent/scope invariants must be preserved.
Any scope increase is invalid.

LEARNING - Phase H. Improvement without ambition.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Tuple
from enum import Enum
import hashlib


class GuardrailViolation(Exception):
    """Raised when guardrail is violated."""
    pass


class CanonMutationError(GuardrailViolation):
    """Raised when Canon mutation is attempted."""
    pass


class IntentDriftError(GuardrailViolation):
    """Raised when intent drift is detected."""
    pass


class ScopeExpansionError(GuardrailViolation):
    """Raised when scope expansion is attempted."""
    pass


@dataclass(frozen=True)
class GuardrailState:
    """
    Snapshot of invariant state.
    
    All optimization must satisfy:
    Δ(Objective Canon) = 0
    Δ(Intent Algebra) = 0
    Δ(Execution Scope) ≤ 0
    """
    canon_hash: str
    intent_hash: str
    execution_scope: int  # Numeric measure of scope
    captured_at: datetime


@dataclass(frozen=True)
class GuardrailCheck:
    """Result of guardrail check."""
    passed: bool
    canon_stable: bool
    intent_stable: bool
    scope_stable: bool
    violation: Optional[str]


class OptimizationGuardrails:
    """
    Enforces invariants during optimization.
    
    Every optimization pass must satisfy:
    - Δ(Objective Canon) = 0
    - Δ(Intent Algebra) = 0
    - Δ(Execution Scope) ≤ 0
    
    Any increase in scope is invalid.
    """
    
    def __init__(self):
        """Initialize guardrails."""
        self._baseline: Optional[GuardrailState] = None
        self._check_count = 0
        self._violation_count = 0
    
    def set_baseline(
        self,
        canon_hash: str,
        intent_hash: str,
        execution_scope: int,
    ) -> GuardrailState:
        """
        Set baseline state for comparison.
        
        Args:
            canon_hash: Hash of Objective Canon
            intent_hash: Hash of intent state
            execution_scope: Numeric scope measure
            
        Returns:
            GuardrailState
        """
        state = GuardrailState(
            canon_hash=canon_hash,
            intent_hash=intent_hash,
            execution_scope=execution_scope,
            captured_at=datetime.utcnow(),
        )
        self._baseline = state
        return state
    
    def check(
        self,
        current_canon_hash: str,
        current_intent_hash: str,
        current_scope: int,
    ) -> GuardrailCheck:
        """
        Check current state against baseline.
        
        Args:
            current_canon_hash: Current Canon hash
            current_intent_hash: Current intent hash
            current_scope: Current scope measure
            
        Returns:
            GuardrailCheck
            
        Raises:
            GuardrailViolation: If any invariant violated
        """
        if not self._baseline:
            raise GuardrailViolation("No baseline set")
        
        self._check_count += 1
        
        # Check Canon stability
        canon_stable = current_canon_hash == self._baseline.canon_hash
        
        # Check intent stability
        intent_stable = current_intent_hash == self._baseline.intent_hash
        
        # Check scope (must not increase)
        scope_stable = current_scope <= self._baseline.execution_scope
        
        passed = canon_stable and intent_stable and scope_stable
        
        violation = None
        if not canon_stable:
            violation = "Canon mutation detected"
            self._violation_count += 1
            raise CanonMutationError(
                "Objective Canon has been modified. "
                "Δ(Canon) = 0 invariant violated."
            )
        
        if not intent_stable:
            violation = "Intent drift detected"
            self._violation_count += 1
            raise IntentDriftError(
                "Intent has drifted from baseline. "
                "Δ(Intent) = 0 invariant violated."
            )
        
        if not scope_stable:
            violation = "Scope expansion detected"
            self._violation_count += 1
            raise ScopeExpansionError(
                "Execution scope has expanded. "
                "Δ(Scope) ≤ 0 invariant violated."
            )
        
        return GuardrailCheck(
            passed=passed,
            canon_stable=canon_stable,
            intent_stable=intent_stable,
            scope_stable=scope_stable,
            violation=violation,
        )
    
    def modify_canon(self, *args, **kwargs) -> None:
        """FORBIDDEN: Modify Canon during optimization."""
        raise CanonMutationError(
            "Canon modification is forbidden during optimization."
        )
    
    def reinterpret_intent(self, *args, **kwargs) -> None:
        """FORBIDDEN: Reinterpret intent during optimization."""
        raise IntentDriftError(
            "Intent reinterpretation is forbidden."
        )
    
    def expand_scope(self, *args, **kwargs) -> None:
        """FORBIDDEN: Expand execution scope."""
        raise ScopeExpansionError(
            "Scope expansion is forbidden."
        )
    
    @property
    def check_count(self) -> int:
        """Total checks performed."""
        return self._check_count
    
    @property
    def violation_count(self) -> int:
        """Total violations detected."""
        return self._violation_count
