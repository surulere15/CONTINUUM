"""
Drift Prevention

Intent fingerprint, deviation tolerance, drift score.

GOIA-C - Goal Ontology & Intent Algebra.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
import hashlib


@dataclass(frozen=True)
class DriftMeasurement:
    """Measurement of intent drift."""
    goal_id: str
    original_fingerprint: str
    current_fingerprint: str
    drift_score: float  # 0.0 = no drift, 1.0 = total drift
    tolerance: float
    exceeded: bool
    measured_at: datetime


class DriftExceededError(Exception):
    """Raised when drift exceeds threshold."""
    pass


class DriftPrevention:
    """
    Intent Drift Prevention.
    
    Every goal maintains:
    - Intent fingerprint
    - Deviation tolerance
    - Drift score
    
    If drift exceeds threshold:
    - Execution pauses
    - Kernel review triggered
    """
    
    DEFAULT_TOLERANCE = 0.2
    
    def __init__(self, tolerance: float = DEFAULT_TOLERANCE):
        """Initialize drift prevention."""
        self._tolerance = tolerance
        self._fingerprints: dict[str, str] = {}
        self._history: List[DriftMeasurement] = []
    
    def register(
        self,
        goal_id: str,
        intent_fingerprint: str,
    ) -> None:
        """Register goal's intent fingerprint."""
        self._fingerprints[goal_id] = intent_fingerprint
    
    def measure_drift(
        self,
        goal_id: str,
        current_state: str,
    ) -> DriftMeasurement:
        """
        Measure drift from original intent.
        
        Args:
            goal_id: Goal to measure
            current_state: Current execution state
            
        Returns:
            DriftMeasurement
            
        Raises:
            DriftExceededError: If drift exceeds tolerance
        """
        if goal_id not in self._fingerprints:
            raise ValueError(f"Goal '{goal_id}' not registered")
        
        original = self._fingerprints[goal_id]
        current = hashlib.sha256(current_state.encode()).hexdigest()[:16]
        
        # Calculate drift (simplified: character difference ratio)
        diff = sum(1 for a, b in zip(original, current) if a != b)
        drift_score = diff / len(original)
        
        exceeded = drift_score > self._tolerance
        
        measurement = DriftMeasurement(
            goal_id=goal_id,
            original_fingerprint=original,
            current_fingerprint=current,
            drift_score=drift_score,
            tolerance=self._tolerance,
            exceeded=exceeded,
            measured_at=datetime.utcnow(),
        )
        
        self._history.append(measurement)
        
        if exceeded:
            raise DriftExceededError(
                f"Drift exceeded for goal '{goal_id}': "
                f"{drift_score:.2f} > {self._tolerance}. "
                f"Execution paused. Kernel review required."
            )
        
        return measurement
    
    def get_measurements(self, goal_id: str) -> List[DriftMeasurement]:
        """Get drift measurements for goal."""
        return [m for m in self._history if m.goal_id == goal_id]
    
    @property
    def tolerance(self) -> float:
        """Current tolerance threshold."""
        return self._tolerance
