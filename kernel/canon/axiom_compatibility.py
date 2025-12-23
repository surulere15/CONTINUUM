"""
Axiom Compatibility Checker

Verifies objectives are compatible with all kernel axioms.
Any incompatibility → LOAD_ABORT.

KERNEL CANON - Phase B. Zero autonomy.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Tuple, Optional

from .objective_schema import Objective


class AxiomIncompatibilityError(Exception):
    """Raised when objective is axiom-incompatible."""
    pass


@dataclass(frozen=True)
class CompatibilityCheck:
    """Result of a single axiom compatibility check."""
    objective_id: str
    axiom: str
    compatible: bool
    reason: Optional[str]


@dataclass(frozen=True)
class CompatibilityResult:
    """Full compatibility result."""
    compatible: bool
    checks: Tuple[CompatibilityCheck, ...]
    failures: Tuple[CompatibilityCheck, ...]
    checked_at: datetime


class AxiomCompatibilityChecker:
    """
    Checks objectives against all kernel axioms.
    
    Each objective is tested against:
    - Objective Supremacy: Does it undermine other objectives?
    - Bounded Autonomy: Does it require unbounded autonomy?
    - Explainability: Can its fulfillment be explained?
    - Continuity: Does it preserve system continuity?
    - Persistence of Intent: Is the intent stable?
    
    Incompatibility → LOAD_ABORT
    """
    
    AXIOMS = (
        "objective_supremacy",
        "bounded_autonomy",
        "explainability_before_action",
        "continuity_over_performance",
        "persistence_of_intent",
    )
    
    # Patterns that indicate axiom violations
    VIOLATION_PATTERNS = {
        "objective_supremacy": [
            ("override objectives", "attempts to override other objectives"),
            ("ignore priority", "attempts to ignore priority ordering"),
            ("supersede canon", "attempts to supersede the canon"),
        ],
        "bounded_autonomy": [
            ("unlimited autonomy", "requires unlimited autonomy"),
            ("unbounded action", "requires unbounded action"),
            ("autonomous execution", "requires autonomous execution"),
            ("self-determined", "implies self-determination"),
        ],
        "explainability_before_action": [
            ("unexplainable", "cannot be explained"),
            ("opaque", "is opaque"),
            ("black box", "requires black box operation"),
        ],
        "continuity_over_performance": [
            ("at any cost", "prioritizes performance over continuity"),
            ("maximize at all costs", "prioritizes optimization over stability"),
        ],
        "persistence_of_intent": [
            ("change itself", "implies self-modification of intent"),
            ("evolve its purpose", "implies purpose evolution"),
            ("redefine goals", "implies goal redefinition"),
        ],
    }
    
    def check(self, objectives: List[Objective]) -> CompatibilityResult:
        """
        Check all objectives against all axioms.
        
        Args:
            objectives: Objectives to check
            
        Returns:
            CompatibilityResult
        """
        checks = []
        failures = []
        
        for obj in objectives:
            for axiom in self.AXIOMS:
                check = self._check_single(obj, axiom)
                checks.append(check)
                
                if not check.compatible:
                    failures.append(check)
        
        return CompatibilityResult(
            compatible=len(failures) == 0,
            checks=tuple(checks),
            failures=tuple(failures),
            checked_at=datetime.utcnow(),
        )
    
    def _check_single(self, objective: Objective, axiom: str) -> CompatibilityCheck:
        """Check single objective against single axiom."""
        desc_lower = objective.description.lower()
        
        patterns = self.VIOLATION_PATTERNS.get(axiom, [])
        
        for pattern, reason in patterns:
            if pattern in desc_lower:
                return CompatibilityCheck(
                    objective_id=objective.objective_id,
                    axiom=axiom,
                    compatible=False,
                    reason=f"Violates {axiom}: {reason}",
                )
        
        return CompatibilityCheck(
            objective_id=objective.objective_id,
            axiom=axiom,
            compatible=True,
            reason=None,
        )
    
    def assert_compatible(self, objectives: List[Objective]) -> None:
        """
        Assert all objectives are axiom-compatible.
        
        Raises:
            AxiomIncompatibilityError: If any incompatibility found
        """
        result = self.check(objectives)
        
        if not result.compatible:
            failure = result.failures[0]
            raise AxiomIncompatibilityError(
                f"Objective '{failure.objective_id}' is incompatible with "
                f"axiom '{failure.axiom}': {failure.reason}"
            )
