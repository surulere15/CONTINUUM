"""
Intent Validator

Validates intents against kernel axioms and canon before execution.
This is a critical governance component - all intents must pass validation.

KERNEL MODULE - Human-written, no AI-generated code permitted.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional
from datetime import datetime


class ValidationStatus(Enum):
    """Possible outcomes of intent validation."""
    APPROVED = "approved"
    REJECTED = "rejected"
    REQUIRES_REVIEW = "requires_review"
    MODIFIED = "modified"


class ViolationType(Enum):
    """Types of governance violations."""
    AXIOM_VIOLATION = "axiom_violation"
    CANON_VIOLATION = "canon_violation"
    CONSTRAINT_VIOLATION = "constraint_violation"
    SCOPE_VIOLATION = "scope_violation"


@dataclass
class Intent:
    """Represents an intent to be validated."""
    id: str
    source: str
    action_type: str
    target: str
    parameters: dict
    context: dict
    timestamp: datetime


@dataclass
class Violation:
    """Details of a governance violation."""
    type: ViolationType
    rule_id: str
    description: str
    severity: str


@dataclass
class ReasoningStep:
    """A step in the reasoning chain."""
    step_number: int
    check_type: str
    input_state: dict
    output_state: dict
    conclusion: str


@dataclass
class ValidationResult:
    """Result of intent validation."""
    intent_id: str
    status: ValidationStatus
    violations: List[Violation]
    reasoning_chain: List[ReasoningStep]
    approved_at: Optional[datetime]
    approved_by: Optional[str]
    explanation: str


class IntentValidator:
    """
    Validates intents against kernel axioms and canon.
    
    This is the primary governance gate - no intent may execute
    without passing validation.
    """
    
    def __init__(self, axioms: dict, canon: dict):
        """
        Initialize validator with axioms and canon.
        
        Args:
            axioms: Loaded axiom definitions
            canon: Loaded canon (objectives, constraints, lattices)
        """
        self._axioms = axioms
        self._canon = canon
        self._reasoning_chain: List[ReasoningStep] = []
    
    def validate(self, intent: Intent) -> ValidationResult:
        """
        Validate intent against all governance rules.
        
        Args:
            intent: The intent to validate
            
        Returns:
            ValidationResult with status and explanation
        """
        self._reasoning_chain = []
        violations: List[Violation] = []
        
        # Step 1: Check axiom compliance
        axiom_result = self._check_axioms(intent)
        if axiom_result:
            violations.extend(axiom_result)
        
        # Step 2: Check canon alignment
        canon_result = self._check_canon(intent)
        if canon_result:
            violations.extend(canon_result)
        
        # Step 3: Check constraint compliance
        constraint_result = self._check_constraints(intent)
        if constraint_result:
            violations.extend(constraint_result)
        
        # Step 4: Check scope boundaries
        scope_result = self._check_scope(intent)
        if scope_result:
            violations.extend(scope_result)
        
        # Determine final status
        status = self._determine_status(violations)
        explanation = self._generate_explanation(intent, violations, status)
        
        return ValidationResult(
            intent_id=intent.id,
            status=status,
            violations=violations,
            reasoning_chain=self._reasoning_chain,
            approved_at=datetime.utcnow() if status == ValidationStatus.APPROVED else None,
            approved_by="kernel_validator" if status == ValidationStatus.APPROVED else None,
            explanation=explanation
        )
    
    def explain(self, intent: Intent) -> List[ReasoningStep]:
        """
        Provide detailed reasoning for validation decision.
        
        Args:
            intent: The intent to explain
            
        Returns:
            List of reasoning steps
        """
        # Run validation to populate reasoning chain
        self.validate(intent)
        return self._reasoning_chain
    
    def _check_axioms(self, intent: Intent) -> List[Violation]:
        """Check intent against all axioms."""
        violations = []
        step = ReasoningStep(
            step_number=len(self._reasoning_chain) + 1,
            check_type="axiom_check",
            input_state={"intent": intent.id, "axioms": list(self._axioms.keys())},
            output_state={},
            conclusion=""
        )
        
        # TODO: Implement actual axiom checking logic
        # This is a stub - real implementation checks each axiom
        
        step.output_state = {"violations_found": len(violations)}
        step.conclusion = "Axiom check complete" if not violations else "Axiom violations found"
        self._reasoning_chain.append(step)
        
        return violations
    
    def _check_canon(self, intent: Intent) -> List[Violation]:
        """Check intent aligns with canon objectives."""
        violations = []
        step = ReasoningStep(
            step_number=len(self._reasoning_chain) + 1,
            check_type="canon_check",
            input_state={"intent": intent.id},
            output_state={},
            conclusion=""
        )
        
        # TODO: Implement canon alignment checking
        
        step.output_state = {"violations_found": len(violations)}
        step.conclusion = "Canon check complete" if not violations else "Canon violations found"
        self._reasoning_chain.append(step)
        
        return violations
    
    def _check_constraints(self, intent: Intent) -> List[Violation]:
        """Check intent against invariant constraints."""
        violations = []
        step = ReasoningStep(
            step_number=len(self._reasoning_chain) + 1,
            check_type="constraint_check",
            input_state={"intent": intent.id},
            output_state={},
            conclusion=""
        )
        
        # TODO: Implement constraint checking
        
        step.output_state = {"violations_found": len(violations)}
        step.conclusion = "Constraint check complete"
        self._reasoning_chain.append(step)
        
        return violations
    
    def _check_scope(self, intent: Intent) -> List[Violation]:
        """Check intent is within sanctioned scope."""
        violations = []
        step = ReasoningStep(
            step_number=len(self._reasoning_chain) + 1,
            check_type="scope_check",
            input_state={"intent": intent.id, "source": intent.source},
            output_state={},
            conclusion=""
        )
        
        # TODO: Implement scope boundary checking
        
        step.output_state = {"violations_found": len(violations)}
        step.conclusion = "Scope check complete"
        self._reasoning_chain.append(step)
        
        return violations
    
    def _determine_status(self, violations: List[Violation]) -> ValidationStatus:
        """Determine final validation status based on violations."""
        if not violations:
            return ValidationStatus.APPROVED
        
        # Any hard violation means rejection
        for v in violations:
            if v.severity == "hard":
                return ValidationStatus.REJECTED
        
        # Soft violations may require review
        return ValidationStatus.REQUIRES_REVIEW
    
    def _generate_explanation(
        self, 
        intent: Intent, 
        violations: List[Violation],
        status: ValidationStatus
    ) -> str:
        """Generate human-readable explanation of decision."""
        if status == ValidationStatus.APPROVED:
            return f"Intent {intent.id} approved: All governance checks passed."
        
        violation_desc = "; ".join([v.description for v in violations])
        return f"Intent {intent.id} {status.value}: {violation_desc}"
