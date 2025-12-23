"""
Canon Validator

Proves objectives are lawful against kernel axioms.
Rejects execution semantics, self-reference, and agent references.

KERNEL MODULE - Human-written, no AI-generated code permitted.
"""

import re
from dataclasses import dataclass
from typing import List, Dict, Set, Optional, Tuple
from enum import Enum

from .schema import Objective
from .errors import (
    AxiomConflictError,
    ObjectiveAmbiguityError,
    ExecutionSemanticsError,
    CanonSchemaViolation,
)


class ValidationStatus(Enum):
    """Result of validation."""
    VALID = "valid"
    REJECTED = "rejected"


@dataclass(frozen=True)
class ValidationResult:
    """
    Result of validating an objective.
    
    If rejected, includes axiom reference and reason.
    """
    objective_id: str
    status: ValidationStatus
    axiom_violated: Optional[str] = None
    reason: Optional[str] = None


# Forbidden verbs that imply execution semantics
FORBIDDEN_EXECUTION_VERBS = frozenset({
    "execute",
    "optimize",
    "control",
    "implement",
    "trigger",
    "run",
    "invoke",
    "start",
    "stop",
    "deploy",
    "launch",
    "activate",
    "perform",
    "manipulate",
    "modify",
    "change",
    "alter",
})

# Forbidden agent references
FORBIDDEN_AGENT_TERMS = frozenset({
    "agent",
    "agents",
    "spawn",
    "spawned",
    "bot",
    "bots",
    "worker",
    "workers",
})

# Patterns that indicate self-reference
SELF_REFERENCE_PATTERNS = [
    r"\bthis objective\b",
    r"\bself\b",
    r"\brecursive\b",
    r"\brecursion\b",
]


class CanonValidator:
    """
    Validates objectives against kernel axioms and semantic rules.
    
    Validation checks:
    1. Schema validity (structure)
    2. Axiom compatibility (governance)
    3. No self-referential goals
    4. No execution semantics
    5. No agent references
    """
    
    def __init__(self, axioms: Dict[str, dict]):
        """
        Initialize validator with loaded axioms.
        
        Args:
            axioms: Dict of axiom_id -> axiom_data
        """
        self._axioms = axioms
        self._compiled_self_ref = [
            re.compile(p, re.IGNORECASE) for p in SELF_REFERENCE_PATTERNS
        ]
    
    def validate(self, objective: Objective) -> ValidationResult:
        """
        Validate a single objective.
        
        Returns ValidationResult with status and any violation details.
        """
        # Check 1: Execution semantics
        exec_result = self._check_execution_semantics(objective)
        if exec_result:
            return exec_result
        
        # Check 2: Agent references
        agent_result = self._check_agent_references(objective)
        if agent_result:
            return agent_result
        
        # Check 3: Self-reference
        self_ref_result = self._check_self_reference(objective)
        if self_ref_result:
            return self_ref_result
        
        # Check 4: Axiom compatibility
        axiom_result = self._check_axiom_compatibility(objective)
        if axiom_result:
            return axiom_result
        
        # All checks passed
        return ValidationResult(
            objective_id=objective.id,
            status=ValidationStatus.VALID,
        )
    
    def validate_all(self, objectives: List[Objective]) -> Tuple[List[Objective], List[ValidationResult]]:
        """
        Validate all objectives.
        
        Returns:
            Tuple of (valid_objectives, rejection_results)
        """
        valid = []
        rejections = []
        
        for obj in objectives:
            result = self.validate(obj)
            if result.status == ValidationStatus.VALID:
                valid.append(obj)
            else:
                rejections.append(result)
        
        # Check for conflicts between objectives
        conflict_results = self._check_conflicts(valid)
        for result in conflict_results:
            rejections.append(result)
            # Remove conflicting objective from valid list
            valid = [o for o in valid if o.id != result.objective_id]
        
        return valid, rejections
    
    def _check_execution_semantics(self, objective: Objective) -> Optional[ValidationResult]:
        """Check for forbidden execution-like language."""
        # Check description
        found = self._find_forbidden_verb(objective.description)
        if found:
            return ValidationResult(
                objective_id=objective.id,
                status=ValidationStatus.REJECTED,
                axiom_violated="bounded_autonomy",
                reason=f"Execution semantics: '{found}' in description. "
                       f"Objectives must be declarative, not imperative."
            )
        
        # Check invariants
        for inv in objective.invariants:
            found = self._find_forbidden_verb(inv)
            if found:
                return ValidationResult(
                    objective_id=objective.id,
                    status=ValidationStatus.REJECTED,
                    axiom_violated="bounded_autonomy",
                    reason=f"Execution semantics: '{found}' in invariant. "
                           f"Invariants describe state, not actions."
                )
        
        # Check termination conditions
        for tc in objective.termination_conditions:
            found = self._find_forbidden_verb(tc)
            if found:
                return ValidationResult(
                    objective_id=objective.id,
                    status=ValidationStatus.REJECTED,
                    axiom_violated="bounded_autonomy",
                    reason=f"Execution semantics: '{found}' in termination condition."
                )
        
        return None
    
    def _find_forbidden_verb(self, text: str) -> Optional[str]:
        """Find forbidden execution verb in text."""
        words = set(re.findall(r'\b\w+\b', text.lower()))
        for forbidden in FORBIDDEN_EXECUTION_VERBS:
            if forbidden in words:
                return forbidden
        return None
    
    def _check_agent_references(self, objective: Objective) -> Optional[ValidationResult]:
        """Check for forbidden agent references."""
        all_text = (
            objective.description + " " +
            " ".join(objective.invariants) + " " +
            " ".join(objective.termination_conditions)
        ).lower()
        
        words = set(re.findall(r'\b\w+\b', all_text))
        for forbidden in FORBIDDEN_AGENT_TERMS:
            if forbidden in words:
                return ValidationResult(
                    objective_id=objective.id,
                    status=ValidationStatus.REJECTED,
                    axiom_violated="objective_supremacy",
                    reason=f"Agent reference: '{forbidden}'. "
                           f"Objectives cannot reference agents directly."
                )
        
        return None
    
    def _check_self_reference(self, objective: Objective) -> Optional[ValidationResult]:
        """Check for self-referential language."""
        all_text = (
            objective.description + " " +
            " ".join(objective.invariants) + " " +
            " ".join(objective.termination_conditions)
        )
        
        for pattern in self._compiled_self_ref:
            if pattern.search(all_text):
                return ValidationResult(
                    objective_id=objective.id,
                    status=ValidationStatus.REJECTED,
                    axiom_violated="continuity_over_performance",
                    reason=f"Self-referential language detected. "
                           f"Objectives must be externally grounded."
                )
        
        return None
    
    def _check_axiom_compatibility(self, objective: Objective) -> Optional[ValidationResult]:
        """Check objective is compatible with loaded axioms."""
        # Priority 1 objectives can only be civilization scope
        if objective.priority == 1 and objective.scope != "civilization":
            return ValidationResult(
                objective_id=objective.id,
                status=ValidationStatus.REJECTED,
                axiom_violated="objective_supremacy",
                reason="Priority 1 objectives must have civilization scope."
            )
        
        # Objectives must have at least one invariant
        if len(objective.invariants) == 0:
            return ValidationResult(
                objective_id=objective.id,
                status=ValidationStatus.REJECTED,
                axiom_violated="explainability_first",
                reason="Objectives must have at least one invariant. "
                       "What must always be true?"
            )
        
        return None
    
    def _check_conflicts(self, objectives: List[Objective]) -> List[ValidationResult]:
        """Check for conflicts between objectives."""
        results = []
        
        # Check for duplicate IDs
        seen_ids: Set[str] = set()
        for obj in objectives:
            if obj.id in seen_ids:
                results.append(ValidationResult(
                    objective_id=obj.id,
                    status=ValidationStatus.REJECTED,
                    axiom_violated="continuity_over_performance",
                    reason=f"Duplicate objective ID: '{obj.id}'"
                ))
            seen_ids.add(obj.id)
        
        # Check for priority conflicts at same scope
        by_scope_priority: Dict[str, Dict[int, List[str]]] = {}
        for obj in objectives:
            if obj.scope not in by_scope_priority:
                by_scope_priority[obj.scope] = {}
            if obj.priority not in by_scope_priority[obj.scope]:
                by_scope_priority[obj.scope][obj.priority] = []
            by_scope_priority[obj.scope][obj.priority].append(obj.id)
        
        # Same priority at same scope might be ambiguous
        for scope, priorities in by_scope_priority.items():
            for priority, obj_ids in priorities.items():
                if len(obj_ids) > 1 and priority <= 3:
                    # High-priority conflicts are ambiguous
                    for obj_id in obj_ids[1:]:
                        results.append(ValidationResult(
                            objective_id=obj_id,
                            status=ValidationStatus.REJECTED,
                            axiom_violated="objective_supremacy",
                            reason=f"Priority conflict: multiple objectives at "
                                   f"{scope}/priority {priority}"
                        ))
        
        return results
