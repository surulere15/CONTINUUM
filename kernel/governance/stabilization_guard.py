"""
Stabilization Guard

Prevent erosion of intent integrity over time.
HALT & AUDIT on violation.

KERNEL MODULE - No imports from execution/agents/learning.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Set, List, Optional
from enum import Enum
import hashlib


class StabilizationViolation(Exception):
    """Raised when stabilization integrity is violated. Triggers HALT."""
    pass


class ViolationType(Enum):
    """Types of stabilization violations."""
    SILENT_WEAKENING = "silent_weakening"
    PROGRESSIVE_DRIFT = "progressive_drift"
    REJECTED_REINTRODUCTION = "rejected_reintroduction"
    CIRCULAR_DEPENDENCY = "circular_dependency"


@dataclass(frozen=True)
class ViolationRecord:
    """Record of a stabilization violation."""
    violation_id: str
    violation_type: ViolationType
    intent_id: str
    description: str
    detected_at: datetime


@dataclass(frozen=True)
class IntentFingerprint:
    """
    Fingerprint of an intent for tracking changes.
    
    Used to detect silent weakening.
    """
    intent_id: str
    constraint_hash: str
    scope: str
    recorded_at: datetime


class StabilizationGuard:
    """
    Guards against erosion of intent integrity.
    
    Protects against:
    - Silent weakening of constraints
    - Progressive drift via repeated normalization
    - Reintroduction of rejected intents
    - Circular resolution dependencies
    
    If violation detected → HALT & AUDIT
    """
    
    def __init__(self):
        """Initialize stabilization guard."""
        self._fingerprints: Dict[str, IntentFingerprint] = {}
        self._rejected_ids: Set[str] = set()
        self._resolution_history: List[str] = []
        self._violations: List[ViolationRecord] = []
        self._violation_count = 0
    
    def record_fingerprint(self, intent_id: str, constraints: tuple, scope: str) -> None:
        """
        Record intent fingerprint for change detection.
        
        Args:
            intent_id: Intent identifier
            constraints: Current constraints
            scope: Current scope
        """
        constraint_hash = hashlib.sha256(
            "|".join(sorted(constraints)).encode()
        ).hexdigest()
        
        self._fingerprints[intent_id] = IntentFingerprint(
            intent_id=intent_id,
            constraint_hash=constraint_hash,
            scope=scope,
            recorded_at=datetime.utcnow(),
        )
    
    def check_weakening(self, intent_id: str, new_constraints: tuple, new_scope: str) -> None:
        """
        Check for silent weakening of constraints.
        
        Raises:
            StabilizationViolation: If constraints were silently weakened
        """
        if intent_id not in self._fingerprints:
            return  # New intent, no previous record
        
        old = self._fingerprints[intent_id]
        new_hash = hashlib.sha256(
            "|".join(sorted(new_constraints)).encode()
        ).hexdigest()
        
        # Check if constraints changed (potential weakening)
        if new_hash != old.constraint_hash:
            # Fewer constraints = weakening
            if len(new_constraints) < len(old.constraint_hash):
                self._record_violation(
                    ViolationType.SILENT_WEAKENING,
                    intent_id,
                    f"Constraints were silently weakened for intent {intent_id}",
                )
                raise StabilizationViolation(
                    f"HALT: Silent weakening detected for intent {intent_id}. "
                    f"Constraints cannot be reduced without explicit approval."
                )
    
    def record_rejection(self, intent_id: str) -> None:
        """Record that an intent was rejected."""
        self._rejected_ids.add(intent_id)
    
    def check_reintroduction(self, intent_id: str) -> None:
        """
        Check for reintroduction of rejected intent.
        
        Raises:
            StabilizationViolation: If rejected intent is reintroduced
        """
        if intent_id in self._rejected_ids:
            self._record_violation(
                ViolationType.REJECTED_REINTRODUCTION,
                intent_id,
                f"Rejected intent {intent_id} was reintroduced",
            )
            raise StabilizationViolation(
                f"HALT: Rejected intent {intent_id} cannot be reintroduced. "
                f"Create a new intent with a different ID."
            )
    
    def check_circular_dependency(self, resolution_path: List[str]) -> None:
        """
        Check for circular resolution dependencies.
        
        Raises:
            StabilizationViolation: If circular dependency detected
        """
        if len(resolution_path) != len(set(resolution_path)):
            # Duplicate in path = cycle
            self._record_violation(
                ViolationType.CIRCULAR_DEPENDENCY,
                resolution_path[0],
                f"Circular dependency in resolution: {resolution_path}",
            )
            raise StabilizationViolation(
                f"HALT: Circular resolution dependency detected. "
                f"Path: {' -> '.join(resolution_path)}"
            )
    
    def check_progressive_drift(self, intent_id: str, normalization_count: int) -> None:
        """
        Check for progressive drift via repeated normalization.
        
        Raises:
            StabilizationViolation: If excessive normalization detected
        """
        max_normalizations = 3
        if normalization_count > max_normalizations:
            self._record_violation(
                ViolationType.PROGRESSIVE_DRIFT,
                intent_id,
                f"Intent {intent_id} normalized {normalization_count} times",
            )
            raise StabilizationViolation(
                f"HALT: Progressive drift detected. "
                f"Intent {intent_id} has been normalized {normalization_count} times. "
                f"Maximum allowed: {max_normalizations}."
            )
    
    def _record_violation(
        self,
        violation_type: ViolationType,
        intent_id: str,
        description: str,
    ) -> None:
        """Record a violation."""
        self._violation_count += 1
        violation = ViolationRecord(
            violation_id=f"violation_{self._violation_count}",
            violation_type=violation_type,
            intent_id=intent_id,
            description=description,
            detected_at=datetime.utcnow(),
        )
        self._violations.append(violation)
    
    def get_violations(self) -> List[ViolationRecord]:
        """Get all recorded violations."""
        return list(self._violations)
    
    def get_rejected_ids(self) -> Set[str]:
        """Get all rejected intent IDs."""
        return self._rejected_ids.copy()
    
    def clear_rejection(self, intent_id: str, authorization: str) -> None:
        """
        Clear rejection status with authorization.
        
        Only allowed with explicit human authorization.
        """
        if authorization != "HUMAN_OVERRIDE":
            raise StabilizationViolation(
                "HALT: Rejection clearance requires HUMAN_OVERRIDE authorization."
            )
        self._rejected_ids.discard(intent_id)
