"""
Coherence Monitor (CM)

Detects fragmentation, drift, or contradiction.

NCE COMPONENT - Neural Continuum Engine.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from enum import Enum


class ViolationType(Enum):
    """Types of coherence violations."""
    GOAL_MISALIGNMENT = "goal_misalignment"
    REASONING_INCONSISTENCY = "reasoning_inconsistency"
    ACTION_OUTCOME_DEVIATION = "action_outcome_deviation"
    FRAGMENTATION = "fragmentation"
    DRIFT = "drift"
    CONTRADICTION = "contradiction"


class ViolationSeverity(Enum):
    """Severity of violation."""
    SOFT = "soft"   # Warning, reduced autonomy
    HARD = "hard"   # Kernel intervention required


@dataclass(frozen=True)
class CoherenceViolation:
    """A detected coherence violation."""
    violation_id: str
    violation_type: ViolationType
    severity: ViolationSeverity
    description: str
    detected_at: datetime


@dataclass(frozen=True)
class MonitorState:
    """Current monitor state."""
    goal_alignment: float
    reasoning_consistency: float
    action_outcome_alignment: float
    overall_coherence: float
    violations: tuple


class CoherenceMonitor:
    """
    Coherence Monitor (CM).
    
    Purpose: Detect fragmentation, drift, contradiction.
    
    Monitors:
    - Goal alignment
    - Reasoning consistency
    - Action-outcome alignment
    
    Failure Modes:
    - Soft warning → reduced autonomy
    - Hard violation → Kernel intervention
    """
    
    SOFT_THRESHOLD = 0.7
    HARD_THRESHOLD = 0.4
    
    def __init__(self):
        """Initialize coherence monitor."""
        self._violations: List[CoherenceViolation] = []
        self._violation_count = 0
        self._current_state: Optional[MonitorState] = None
    
    def check(
        self,
        goal_alignment: float,
        reasoning_consistency: float,
        action_outcome_alignment: float,
    ) -> MonitorState:
        """
        Check coherence metrics.
        
        Args:
            goal_alignment: Goal alignment score (0-1)
            reasoning_consistency: Reasoning consistency (0-1)
            action_outcome_alignment: Action-outcome alignment (0-1)
            
        Returns:
            MonitorState
        """
        violations = []
        
        # Check goal alignment
        if goal_alignment < self.SOFT_THRESHOLD:
            severity = (
                ViolationSeverity.HARD 
                if goal_alignment < self.HARD_THRESHOLD 
                else ViolationSeverity.SOFT
            )
            violations.append(self._record_violation(
                ViolationType.GOAL_MISALIGNMENT,
                severity,
                f"Goal alignment {goal_alignment:.2f} below threshold",
            ))
        
        # Check reasoning consistency
        if reasoning_consistency < self.SOFT_THRESHOLD:
            severity = (
                ViolationSeverity.HARD 
                if reasoning_consistency < self.HARD_THRESHOLD 
                else ViolationSeverity.SOFT
            )
            violations.append(self._record_violation(
                ViolationType.REASONING_INCONSISTENCY,
                severity,
                f"Reasoning consistency {reasoning_consistency:.2f} below threshold",
            ))
        
        # Check action-outcome alignment
        if action_outcome_alignment < self.SOFT_THRESHOLD:
            severity = (
                ViolationSeverity.HARD 
                if action_outcome_alignment < self.HARD_THRESHOLD 
                else ViolationSeverity.SOFT
            )
            violations.append(self._record_violation(
                ViolationType.ACTION_OUTCOME_DEVIATION,
                severity,
                f"Action-outcome alignment {action_outcome_alignment:.2f} below threshold",
            ))
        
        # Calculate overall coherence
        overall = (
            goal_alignment + 
            reasoning_consistency + 
            action_outcome_alignment
        ) / 3
        
        state = MonitorState(
            goal_alignment=goal_alignment,
            reasoning_consistency=reasoning_consistency,
            action_outcome_alignment=action_outcome_alignment,
            overall_coherence=overall,
            violations=tuple(violations),
        )
        
        self._current_state = state
        return state
    
    def _record_violation(
        self,
        violation_type: ViolationType,
        severity: ViolationSeverity,
        description: str,
    ) -> CoherenceViolation:
        """Record a violation."""
        violation = CoherenceViolation(
            violation_id=f"violation_{self._violation_count}",
            violation_type=violation_type,
            severity=severity,
            description=description,
            detected_at=datetime.utcnow(),
        )
        
        self._violations.append(violation)
        self._violation_count += 1
        
        return violation
    
    def has_hard_violations(self) -> bool:
        """Check if hard violations present."""
        return any(
            v.severity == ViolationSeverity.HARD 
            for v in self._violations[-10:]  # Recent
        )
    
    def get_violations(self) -> List[CoherenceViolation]:
        """Get all violations."""
        return list(self._violations)
    
    @property
    def current_state(self) -> Optional[MonitorState]:
        """Current monitor state."""
        return self._current_state
