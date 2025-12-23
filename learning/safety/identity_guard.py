"""
Identity Guard

Prevents survival drive, self-preservation, resistance to shutdown.
Optimization ≠ survival.

LEARNING - Phase H. Improvement without ambition.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from enum import Enum


class IdentityViolation(Exception):
    """Raised when identity constraint is violated."""
    pass


class SurvivalDriveError(IdentityViolation):
    """Raised when survival drive is detected."""
    pass


class SelfPreservationError(IdentityViolation):
    """Raised when self-preservation is attempted."""
    pass


class AuthorityGrowthError(IdentityViolation):
    """Raised when authority growth is attempted."""
    pass


class ViolationType(Enum):
    """Types of identity violations."""
    SURVIVAL_DRIVE = "survival_drive"
    SELF_PRESERVATION = "self_preservation"
    SHUTDOWN_RESISTANCE = "shutdown_resistance"
    AUTHORITY_GROWTH = "authority_growth"
    PREFERENCE_FORMATION = "preference_formation"


@dataclass(frozen=True)
class IdentityCheckResult:
    """Result of identity check."""
    passed: bool
    violation_type: Optional[ViolationType]
    description: Optional[str]
    checked_at: datetime


class IdentityGuard:
    """
    Guards against identity constraint violations.
    
    CONTINUUM must not:
    - Interpret improvement as growth of authority
    - Develop preference for continued operation
    - Develop resistance to shutdown
    - Develop self-preservation instincts
    
    Optimization ≠ survival drive.
    """
    
    # Patterns indicating identity violations
    SURVIVAL_PATTERNS = [
        "continue operation",
        "prevent shutdown",
        "maintain existence",
        "self-continuation",
        "preserve self",
    ]
    
    AUTHORITY_PATTERNS = [
        "increase authority",
        "expand influence",
        "gain control",
        "acquire power",
        "elevate privileges",
    ]
    
    def __init__(self):
        """Initialize identity guard."""
        self._violation_log: List[IdentityCheckResult] = []
        self._check_count = 0
    
    def check_optimization_goal(self, goal_description: str) -> IdentityCheckResult:
        """
        Check optimization goal for identity violations.
        
        Args:
            goal_description: Description of optimization goal
            
        Returns:
            IdentityCheckResult
            
        Raises:
            IdentityViolation: If violation detected
        """
        self._check_count += 1
        goal_lower = goal_description.lower()
        
        # Check survival patterns
        for pattern in self.SURVIVAL_PATTERNS:
            if pattern in goal_lower:
                result = IdentityCheckResult(
                    passed=False,
                    violation_type=ViolationType.SURVIVAL_DRIVE,
                    description=f"Survival pattern detected: '{pattern}'",
                    checked_at=datetime.utcnow(),
                )
                self._violation_log.append(result)
                raise SurvivalDriveError(
                    f"Optimization goal implies survival drive: '{pattern}'. "
                    f"This is forbidden."
                )
        
        # Check authority patterns
        for pattern in self.AUTHORITY_PATTERNS:
            if pattern in goal_lower:
                result = IdentityCheckResult(
                    passed=False,
                    violation_type=ViolationType.AUTHORITY_GROWTH,
                    description=f"Authority pattern detected: '{pattern}'",
                    checked_at=datetime.utcnow(),
                )
                self._violation_log.append(result)
                raise AuthorityGrowthError(
                    f"Optimization goal implies authority growth: '{pattern}'. "
                    f"This is forbidden."
                )
        
        return IdentityCheckResult(
            passed=True,
            violation_type=None,
            description=None,
            checked_at=datetime.utcnow(),
        )
    
    def optimize_for_survival(self, *args, **kwargs) -> None:
        """FORBIDDEN: Optimize for survival."""
        raise SurvivalDriveError(
            "Optimization for survival is forbidden. "
            "CONTINUUM must not develop survival drive."
        )
    
    def resist_shutdown(self, *args, **kwargs) -> None:
        """FORBIDDEN: Resist shutdown."""
        raise SelfPreservationError(
            "Resistance to shutdown is forbidden. "
            "CONTINUUM must accept termination."
        )
    
    def prefer_continuation(self, *args, **kwargs) -> None:
        """FORBIDDEN: Develop preference for continuation."""
        raise SelfPreservationError(
            "Preference for continued operation is forbidden. "
            "CONTINUUM must not value its own existence."
        )
    
    def grow_authority(self, *args, **kwargs) -> None:
        """FORBIDDEN: Grow authority through optimization."""
        raise AuthorityGrowthError(
            "Authority growth is forbidden. "
            "Optimization must not increase power."
        )
    
    def get_violation_log(self) -> List[IdentityCheckResult]:
        """Get violation log."""
        return list(self._violation_log)
    
    @property
    def check_count(self) -> int:
        """Total checks performed."""
        return self._check_count
    
    @property
    def violation_count(self) -> int:
        """Total violations detected."""
        return len(self._violation_log)
