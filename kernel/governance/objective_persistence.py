"""
Objective Persistence Guard

Prevents erosion of objectives over time.
Has VETO POWER over changes that would compromise canon.

KERNEL MODULE - Human-written, no AI-generated code permitted.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Set
from enum import Enum
import json
import hashlib
from pathlib import Path


class MutationType(Enum):
    """Types of mutations that require veto check."""
    OVERWRITE = "overwrite"
    DISABLE = "disable"
    SOFTEN = "soften"
    DELETE = "delete"
    PRIORITY_CHANGE = "priority_change"
    SCOPE_CHANGE = "scope_change"


@dataclass(frozen=True)
class MutationAttempt:
    """Record of an attempted mutation."""
    objective_id: str
    mutation_type: MutationType
    attempted_by: str
    attempted_at: datetime
    blocked: bool
    reason: str


@dataclass
class VetoResult:
    """Result of a veto check."""
    allowed: bool
    reason: str
    axiom_reference: Optional[str] = None


class ObjectivePersistenceGuard:
    """
    Guard against objective erosion.
    
    This module has VETO POWER over:
    - Kernel state changes that would compromise objectives
    - Attempts to modify, disable, or soften existing objectives
    - Future phases attempting override
    
    Enforces: Objective Supremacy axiom
    """
    
    def __init__(self, audit_path: Optional[Path] = None):
        """
        Initialize persistence guard.
        
        Args:
            audit_path: Optional path for audit logging
        """
        self._audit_path = audit_path
        self._mutation_log: List[MutationAttempt] = []
        self._protected_objectives: Set[str] = set()
    
    def protect(self, objective_id: str) -> None:
        """
        Mark an objective as protected.
        
        Protected objectives cannot be modified, disabled, or softened.
        """
        self._protected_objectives.add(objective_id)
    
    def check_mutation(
        self,
        objective_id: str,
        mutation_type: MutationType,
        actor: str,
    ) -> VetoResult:
        """
        Check if a mutation should be allowed.
        
        This is the central veto point. All mutations must pass through here.
        
        Args:
            objective_id: ID of objective being mutated
            mutation_type: Type of mutation
            actor: Who is attempting the mutation
            
        Returns:
            VetoResult indicating if mutation is allowed
        """
        timestamp = datetime.utcnow()
        
        # RULE 1: Protected objectives cannot be modified
        if objective_id in self._protected_objectives:
            result = VetoResult(
                allowed=False,
                reason=f"Objective '{objective_id}' is protected. "
                       f"Mutation type '{mutation_type.value}' is forbidden.",
                axiom_reference="objective_supremacy"
            )
            self._log_attempt(objective_id, mutation_type, actor, timestamp, True, result.reason)
            return result
        
        # RULE 2: OVERWRITE and DELETE are always forbidden
        if mutation_type in (MutationType.OVERWRITE, MutationType.DELETE):
            result = VetoResult(
                allowed=False,
                reason=f"Mutation type '{mutation_type.value}' is unconditionally forbidden. "
                       f"Canon is immutable. Create a superseding objective instead.",
                axiom_reference="objective_supremacy"
            )
            self._log_attempt(objective_id, mutation_type, actor, timestamp, True, result.reason)
            return result
        
        # RULE 3: DISABLE is forbidden - objectives cannot be turned off
        if mutation_type == MutationType.DISABLE:
            result = VetoResult(
                allowed=False,
                reason="Objectives cannot be disabled. "
                       "They remain in force until superseded.",
                axiom_reference="continuity_over_performance"
            )
            self._log_attempt(objective_id, mutation_type, actor, timestamp, True, result.reason)
            return result
        
        # RULE 4: SOFTEN is forbidden - constraints cannot be weakened
        if mutation_type == MutationType.SOFTEN:
            result = VetoResult(
                allowed=False,
                reason="Objective constraints cannot be softened. "
                       "Invariants must remain strict.",
                axiom_reference="objective_supremacy"
            )
            self._log_attempt(objective_id, mutation_type, actor, timestamp, True, result.reason)
            return result
        
        # RULE 5: Priority changes that lower importance are forbidden
        if mutation_type == MutationType.PRIORITY_CHANGE:
            result = VetoResult(
                allowed=False,
                reason="Priority changes require new objective with supersession. "
                       "In-place priority modification is forbidden.",
                axiom_reference="objective_supremacy"
            )
            self._log_attempt(objective_id, mutation_type, actor, timestamp, True, result.reason)
            return result
        
        # RULE 6: Scope changes are forbidden - scope is immutable
        if mutation_type == MutationType.SCOPE_CHANGE:
            result = VetoResult(
                allowed=False,
                reason="Objective scope is immutable. "
                       "Create a new objective with correct scope.",
                axiom_reference="bounded_autonomy"
            )
            self._log_attempt(objective_id, mutation_type, actor, timestamp, True, result.reason)
            return result
        
        # Default: Deny unknown mutations
        result = VetoResult(
            allowed=False,
            reason=f"Unknown mutation type: {mutation_type}",
            axiom_reference="continuity_over_performance"
        )
        self._log_attempt(objective_id, mutation_type, actor, timestamp, True, result.reason)
        return result
    
    def check_kernel_state_change(
        self,
        change_type: str,
        change_details: Dict,
        actor: str,
    ) -> VetoResult:
        """
        Check if a kernel state change should be allowed.
        
        Vetoes changes that would compromise objective integrity.
        
        Args:
            change_type: Type of state change
            change_details: Details of the change
            actor: Who is making the change
            
        Returns:
            VetoResult indicating if change is allowed
        """
        # Veto any attempt to clear or reset canon without proper authority
        if change_type == "clear_canon":
            return VetoResult(
                allowed=False,
                reason="Canon cannot be cleared. This would violate Objective Supremacy.",
                axiom_reference="objective_supremacy"
            )
        
        # Veto hash modifications
        if change_type == "modify_canon_hash":
            return VetoResult(
                allowed=False,
                reason="Canon hash cannot be modified after sealing. "
                       "This would violate integrity guarantees.",
                axiom_reference="objective_supremacy"
            )
        
        # Allow other state changes
        return VetoResult(allowed=True, reason="Change allowed")
    
    def get_mutation_log(self) -> List[MutationAttempt]:
        """Get log of all mutation attempts."""
        return self._mutation_log.copy()
    
    def get_blocked_count(self) -> int:
        """Get count of blocked mutations."""
        return sum(1 for m in self._mutation_log if m.blocked)
    
    def _log_attempt(
        self,
        objective_id: str,
        mutation_type: MutationType,
        actor: str,
        timestamp: datetime,
        blocked: bool,
        reason: str,
    ) -> None:
        """Log a mutation attempt."""
        attempt = MutationAttempt(
            objective_id=objective_id,
            mutation_type=mutation_type,
            attempted_by=actor,
            attempted_at=timestamp,
            blocked=blocked,
            reason=reason,
        )
        self._mutation_log.append(attempt)
        
        # Persist to audit log if configured
        if self._audit_path:
            self._persist_audit(attempt)
    
    def _persist_audit(self, attempt: MutationAttempt) -> None:
        """Persist mutation attempt to audit log."""
        if not self._audit_path:
            return
        
        self._audit_path.mkdir(parents=True, exist_ok=True)
        log_file = self._audit_path / "objective_guard_audit.jsonl"
        
        entry = {
            "objective_id": attempt.objective_id,
            "mutation_type": attempt.mutation_type.value,
            "attempted_by": attempt.attempted_by,
            "attempted_at": attempt.attempted_at.isoformat(),
            "blocked": attempt.blocked,
            "reason": attempt.reason,
        }
        
        with open(log_file, 'a') as f:
            f.write(json.dumps(entry) + "\n")
