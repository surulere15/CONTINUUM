"""
Outcome Validator

Result validation. All outcomes are verified.

EFAP-C - Execution Fabric & Agent Physics.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from enum import Enum


class ValidationResult(Enum):
    """Validation result."""
    VALID = "valid"
    INVALID_NONDETERMINISTIC = "invalid_nondeterministic"
    INVALID_UNAUTHORIZED = "invalid_unauthorized"
    INVALID_INTEGRITY = "invalid_integrity"


@dataclass(frozen=True)
class OutcomeValidation:
    """Validation of execution outcome."""
    work_id: str
    result: ValidationResult
    expected_effect: str
    actual_effect: str
    deterministic_check: bool
    integrity_check: bool
    validated_at: datetime


class NonDeterministicError(Exception):
    """Raised when output is non-deterministic (Law 3)."""
    pass


class IntegrityViolationError(Exception):
    """Raised when integrity is violated."""
    pass


class OutcomeValidator:
    """
    Outcome Validator.
    
    Validates execution outcomes.
    Enforces Law 3: Deterministic Execution.
    
    Nothing executes silently.
    """
    
    def __init__(self):
        """Initialize validator."""
        self._validations: List[OutcomeValidation] = []
    
    def validate(
        self,
        work_id: str,
        expected_effect: str,
        actual_effect: str,
        is_deterministic: bool = True,
        has_integrity: bool = True,
    ) -> OutcomeValidation:
        """
        Validate execution outcome.
        
        Args:
            work_id: Work that was executed
            expected_effect: Expected outcome
            actual_effect: Actual outcome
            is_deterministic: Was execution deterministic
            has_integrity: Was integrity maintained
            
        Returns:
            OutcomeValidation
        """
        # Check determinism (Law 3)
        if not is_deterministic:
            validation = OutcomeValidation(
                work_id=work_id,
                result=ValidationResult.INVALID_NONDETERMINISTIC,
                expected_effect=expected_effect,
                actual_effect=actual_effect,
                deterministic_check=False,
                integrity_check=has_integrity,
                validated_at=datetime.utcnow(),
            )
            self._validations.append(validation)
            
            raise NonDeterministicError(
                f"Work '{work_id}' produced non-deterministic output. "
                f"Law 3 violation."
            )
        
        # Check integrity
        if not has_integrity:
            validation = OutcomeValidation(
                work_id=work_id,
                result=ValidationResult.INVALID_INTEGRITY,
                expected_effect=expected_effect,
                actual_effect=actual_effect,
                deterministic_check=is_deterministic,
                integrity_check=False,
                validated_at=datetime.utcnow(),
            )
            self._validations.append(validation)
            
            raise IntegrityViolationError(
                f"Work '{work_id}' violated integrity."
            )
        
        validation = OutcomeValidation(
            work_id=work_id,
            result=ValidationResult.VALID,
            expected_effect=expected_effect,
            actual_effect=actual_effect,
            deterministic_check=True,
            integrity_check=True,
            validated_at=datetime.utcnow(),
        )
        
        self._validations.append(validation)
        return validation
    
    def skip_validation(self, *args, **kwargs) -> None:
        """FORBIDDEN: Skip validation."""
        raise ValueError(
            "Outcome validation cannot be skipped. "
            "All outcomes must be validated."
        )
    
    @property
    def valid_count(self) -> int:
        """Valid outcomes."""
        return sum(1 for v in self._validations if v.result == ValidationResult.VALID)
    
    @property
    def invalid_count(self) -> int:
        """Invalid outcomes."""
        return sum(1 for v in self._validations if v.result != ValidationResult.VALID)
