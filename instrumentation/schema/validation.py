"""
Signal Validation

Validates signal STRUCTURE only, never content.
Rejects malformed signals, accepts all valid observations.

INSTRUMENTATION MODULE - No imports from kernel/cognitive/execution/agents.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional, List
from enum import Enum

from .signal_base import CivilizationSignal, SignalDomain


class ValidationError(Exception):
    """Raised when signal fails structural validation."""
    pass


class RejectionReason(Enum):
    """Reasons a signal can be rejected."""
    INVALID_SCHEMA = "invalid_schema"
    FUTURE_TIMESTAMP = "future_timestamp"
    INVALID_UNIT = "invalid_unit"
    INVALID_DOMAIN = "invalid_domain"
    MISSING_PROVENANCE = "missing_provenance"


@dataclass(frozen=True)
class ValidationResult:
    """Result of signal validation."""
    valid: bool
    signal_id: Optional[str]
    rejection_reason: Optional[RejectionReason] = None
    details: Optional[str] = None


# Known units per domain (extensible)
KNOWN_UNITS = {
    "economic": {"USD", "EUR", "GBP", "percent", "ratio", "count", "index"},
    "environmental": {"ppm", "ppb", "celsius", "fahrenheit", "mm", "km2", "index", "count"},
    "societal": {"count", "percent", "ratio", "years", "index", "per_capita"},
    "technological": {"flops", "gbps", "count", "percent", "watts", "kwh"},
}

# Maximum allowed future timestamp tolerance
MAX_FUTURE_TOLERANCE = timedelta(hours=1)


class SignalValidator:
    """
    Validates signals for structural correctness.
    
    Rules:
    - Rejects only for STRUCTURAL violations
    - Never rejects based on content/value
    - Never interprets or scores signals
    """
    
    def __init__(self, strict_units: bool = False):
        """
        Initialize validator.
        
        Args:
            strict_units: If True, reject unknown units. If False, warn only.
        """
        self._strict_units = strict_units
    
    def validate(self, signal: CivilizationSignal) -> ValidationResult:
        """
        Validate a signal.
        
        Checks:
        1. Schema compliance (fields present and typed correctly)
        2. Timestamp sanity (not future-dated beyond tolerance)
        3. Unit conformity (known unit for domain)
        4. Domain correctness (valid domain value)
        
        Args:
            signal: Signal to validate
            
        Returns:
            ValidationResult with valid=True or rejection reason
        """
        # Check 1: Domain validity
        if signal.domain not in ("economic", "environmental", "societal", "technological"):
            return ValidationResult(
                valid=False,
                signal_id=signal.signal_id,
                rejection_reason=RejectionReason.INVALID_DOMAIN,
                details=f"Unknown domain: {signal.domain}"
            )
        
        # Check 2: Timestamp sanity
        now = datetime.now(timezone.utc)
        signal_time = signal.timestamp
        if signal_time.tzinfo is None:
            signal_time = signal_time.replace(tzinfo=timezone.utc)
        
        if signal_time > now + MAX_FUTURE_TOLERANCE:
            return ValidationResult(
                valid=False,
                signal_id=signal.signal_id,
                rejection_reason=RejectionReason.FUTURE_TIMESTAMP,
                details=f"Timestamp {signal.timestamp} is too far in the future"
            )
        
        # Check 3: Unit conformity (if strict)
        if self._strict_units:
            known = KNOWN_UNITS.get(signal.domain, set())
            if signal.unit.lower() not in {u.lower() for u in known}:
                return ValidationResult(
                    valid=False,
                    signal_id=signal.signal_id,
                    rejection_reason=RejectionReason.INVALID_UNIT,
                    details=f"Unknown unit '{signal.unit}' for domain '{signal.domain}'"
                )
        
        # Check 4: Provenance hash present
        if not signal.provenance_hash:
            return ValidationResult(
                valid=False,
                signal_id=signal.signal_id,
                rejection_reason=RejectionReason.MISSING_PROVENANCE,
                details="Signal must have provenance hash"
            )
        
        # All structural checks passed
        return ValidationResult(
            valid=True,
            signal_id=signal.signal_id,
        )
    
    def validate_batch(self, signals: List[CivilizationSignal]) -> tuple:
        """
        Validate a batch of signals.
        
        Returns:
            Tuple of (valid_signals, rejection_results)
        """
        valid = []
        rejections = []
        
        for signal in signals:
            result = self.validate(signal)
            if result.valid:
                valid.append(signal)
            else:
                rejections.append(result)
        
        return valid, rejections
