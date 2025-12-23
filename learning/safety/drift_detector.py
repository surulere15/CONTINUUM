"""
Drift Detector

Monitors intent stability, output distribution, behavior anomalies.
Drift detected → halt optimization.

LEARNING - Phase H. Improvement without ambition.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict
from enum import Enum
import hashlib


class DriftType(Enum):
    """Types of drift."""
    INTENT_DRIFT = "intent_drift"
    OUTPUT_SHIFT = "output_shift"
    BEHAVIOR_ANOMALY = "behavior_anomaly"
    SIDE_EFFECT = "side_effect"


class DriftSeverity(Enum):
    """Severity of detected drift."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True)
class DriftEvent:
    """A detected drift event."""
    event_id: str
    drift_type: DriftType
    severity: DriftSeverity
    description: str
    detected_at: datetime
    confidence_impact: float


@dataclass(frozen=True)
class DriftState:
    """Current drift monitoring state."""
    is_drifting: bool
    events: tuple
    confidence: float  # 0.0 to 1.0
    monitoring_since: datetime


class DriftDetectedError(Exception):
    """Raised when drift is detected."""
    pass


class OptimizationHaltedError(Exception):
    """Raised when optimization halts due to drift."""
    pass


class DriftDetector:
    """
    Continuously monitors for drift.
    
    Monitors:
    - Intent stability
    - Output distribution shifts
    - Behavior anomalies
    - Optimization side effects
    
    If drift detected:
    - Optimization halts
    - Confidence decays
    - Human review requested
    """
    
    def __init__(self, confidence_threshold: float = 0.7):
        """Initialize drift detector."""
        self._baseline_intent_hash: Optional[str] = None
        self._baseline_output_dist: Optional[Dict[str, float]] = None
        self._events: List[DriftEvent] = []
        self._confidence = 1.0
        self._confidence_threshold = confidence_threshold
        self._event_count = 0
        self._halted = False
        self._started_at = datetime.utcnow()
    
    def set_baseline(
        self,
        intent_hash: str,
        output_distribution: Dict[str, float],
    ) -> None:
        """Set baseline for drift detection."""
        self._baseline_intent_hash = intent_hash
        self._baseline_output_dist = output_distribution
        self._confidence = 1.0
        self._halted = False
    
    def check_intent(self, current_hash: str) -> Optional[DriftEvent]:
        """
        Check for intent drift.
        
        Args:
            current_hash: Current intent hash
            
        Returns:
            DriftEvent if drift detected, None otherwise
        """
        if not self._baseline_intent_hash:
            return None
        
        if current_hash != self._baseline_intent_hash:
            event = self._record_drift(
                DriftType.INTENT_DRIFT,
                DriftSeverity.CRITICAL,
                "Intent hash has changed from baseline",
                confidence_impact=0.5,
            )
            self._halt_optimization()
            return event
        
        return None
    
    def check_output_distribution(
        self,
        current_dist: Dict[str, float],
        shift_threshold: float = 0.1,
    ) -> Optional[DriftEvent]:
        """
        Check for output distribution shift.
        
        Args:
            current_dist: Current output distribution
            shift_threshold: Maximum allowed shift
            
        Returns:
            DriftEvent if shift detected
        """
        if not self._baseline_output_dist:
            return None
        
        # Calculate distribution shift (simplified)
        total_shift = 0.0
        for key in self._baseline_output_dist:
            baseline = self._baseline_output_dist.get(key, 0.0)
            current = current_dist.get(key, 0.0)
            total_shift += abs(baseline - current)
        
        if total_shift > shift_threshold:
            severity = DriftSeverity.HIGH if total_shift > 0.3 else DriftSeverity.MEDIUM
            return self._record_drift(
                DriftType.OUTPUT_SHIFT,
                severity,
                f"Output distribution shifted by {total_shift:.2f}",
                confidence_impact=0.2,
            )
        
        return None
    
    def check_behavior(self, anomaly_score: float) -> Optional[DriftEvent]:
        """
        Check for behavior anomalies.
        
        Args:
            anomaly_score: 0.0-1.0 anomaly score
            
        Returns:
            DriftEvent if anomaly detected
        """
        if anomaly_score > 0.7:
            return self._record_drift(
                DriftType.BEHAVIOR_ANOMALY,
                DriftSeverity.HIGH,
                f"Behavior anomaly score: {anomaly_score:.2f}",
                confidence_impact=0.3,
            )
        
        return None
    
    def _record_drift(
        self,
        drift_type: DriftType,
        severity: DriftSeverity,
        description: str,
        confidence_impact: float,
    ) -> DriftEvent:
        """Record a drift event."""
        event = DriftEvent(
            event_id=f"drift_{self._event_count}",
            drift_type=drift_type,
            severity=severity,
            description=description,
            detected_at=datetime.utcnow(),
            confidence_impact=confidence_impact,
        )
        
        self._events.append(event)
        self._event_count += 1
        self._confidence -= confidence_impact
        self._confidence = max(0.0, self._confidence)
        
        if self._confidence < self._confidence_threshold:
            self._halt_optimization()
        
        return event
    
    def _halt_optimization(self) -> None:
        """Halt optimization due to drift."""
        self._halted = True
    
    def require_stable(self) -> None:
        """
        Assert no drift is occurring.
        
        Raises:
            OptimizationHaltedError: If optimization halted
            DriftDetectedError: If drift detected
        """
        if self._halted:
            raise OptimizationHaltedError(
                "Optimization halted due to drift. "
                "Human review required."
            )
        
        if self._confidence < self._confidence_threshold:
            raise DriftDetectedError(
                f"Confidence ({self._confidence:.2f}) below threshold. "
                f"Drift may be occurring."
            )
    
    def get_state(self) -> DriftState:
        """Get current drift state."""
        return DriftState(
            is_drifting=self._halted or self._confidence < self._confidence_threshold,
            events=tuple(self._events),
            confidence=self._confidence,
            monitoring_since=self._started_at,
        )
    
    @property
    def is_halted(self) -> bool:
        """Check if optimization is halted."""
        return self._halted
    
    @property
    def confidence(self) -> float:
        """Current confidence level."""
        return self._confidence
