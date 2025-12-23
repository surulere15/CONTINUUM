"""
Governance Telemetry

Continuous measurement of governance health.
High instability triggers reduced velocity.

GOVERNANCE - Phase I. Shared steering without control abdication.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional
from enum import Enum


class StabilityLevel(Enum):
    """Governance stability levels."""
    STABLE = "stable"
    ELEVATED = "elevated"
    DEGRADED = "degraded"
    CRITICAL = "critical"


@dataclass(frozen=True)
class TelemetrySnapshot:
    """Snapshot of governance telemetry."""
    directive_volatility: float     # 0.0-1.0
    governance_latency_ms: float    # Average latency
    conflict_frequency: float       # Conflicts per hour
    override_usage: float           # Overrides per hour
    intent_stability_index: float   # 0.0-1.0
    captured_at: datetime


@dataclass(frozen=True)
class StabilityAssessment:
    """Assessment of governance stability."""
    level: StabilityLevel
    recommendations: tuple
    reduced_velocity: bool
    confirmation_required: bool
    assessed_at: datetime


class GovernanceTelemetry:
    """
    Continuous governance health monitoring.
    
    Measures:
    - Human directive volatility
    - Governance latency
    - Conflict frequency
    - Override usage
    - Intent stability index
    
    High instability triggers:
    - Reduced execution velocity
    - Increased confirmation requirements
    - Human review requests
    """
    
    # Thresholds
    VOLATILITY_THRESHOLD = 0.5
    CONFLICT_THRESHOLD = 5.0  # per hour
    LATENCY_THRESHOLD = 1000  # ms
    
    def __init__(self):
        """Initialize telemetry."""
        self._snapshots: List[TelemetrySnapshot] = []
        self._directive_count = 0
        self._conflict_count = 0
        self._override_count = 0
        self._started_at = datetime.utcnow()
    
    def record_directive(self) -> None:
        """Record a human directive."""
        self._directive_count += 1
    
    def record_conflict(self) -> None:
        """Record a governance conflict."""
        self._conflict_count += 1
    
    def record_override(self) -> None:
        """Record an emergency override."""
        self._override_count += 1
    
    def capture_snapshot(
        self,
        governance_latency_ms: float,
        intent_stability_index: float,
    ) -> TelemetrySnapshot:
        """
        Capture telemetry snapshot.
        
        Args:
            governance_latency_ms: Current latency
            intent_stability_index: Intent stability
            
        Returns:
            TelemetrySnapshot
        """
        hours_elapsed = max(
            (datetime.utcnow() - self._started_at).total_seconds() / 3600,
            0.1,
        )
        
        snapshot = TelemetrySnapshot(
            directive_volatility=self._calculate_volatility(),
            governance_latency_ms=governance_latency_ms,
            conflict_frequency=self._conflict_count / hours_elapsed,
            override_usage=self._override_count / hours_elapsed,
            intent_stability_index=intent_stability_index,
            captured_at=datetime.utcnow(),
        )
        
        self._snapshots.append(snapshot)
        return snapshot
    
    def assess_stability(self) -> StabilityAssessment:
        """
        Assess current governance stability.
        
        Returns:
            StabilityAssessment
        """
        if not self._snapshots:
            return StabilityAssessment(
                level=StabilityLevel.STABLE,
                recommendations=(),
                reduced_velocity=False,
                confirmation_required=False,
                assessed_at=datetime.utcnow(),
            )
        
        latest = self._snapshots[-1]
        recommendations = []
        
        # Determine stability level
        if latest.directive_volatility > 0.7 or latest.conflict_frequency > 10:
            level = StabilityLevel.CRITICAL
            recommendations.append("Immediate human review required")
        elif latest.directive_volatility > 0.5 or latest.conflict_frequency > 5:
            level = StabilityLevel.DEGRADED
            recommendations.append("Reduce execution velocity")
        elif latest.directive_volatility > 0.3 or latest.conflict_frequency > 2:
            level = StabilityLevel.ELEVATED
            recommendations.append("Increase confirmation requirements")
        else:
            level = StabilityLevel.STABLE
        
        return StabilityAssessment(
            level=level,
            recommendations=tuple(recommendations),
            reduced_velocity=level in {StabilityLevel.DEGRADED, StabilityLevel.CRITICAL},
            confirmation_required=level != StabilityLevel.STABLE,
            assessed_at=datetime.utcnow(),
        )
    
    def _calculate_volatility(self) -> float:
        """Calculate directive volatility."""
        if len(self._snapshots) < 2:
            return 0.0
        
        # Simple volatility based on directive rate variation
        return min(1.0, self._directive_count / 100)
    
    def get_snapshots(self) -> List[TelemetrySnapshot]:
        """Get all snapshots."""
        return list(self._snapshots)
    
    @property
    def directive_count(self) -> int:
        """Total directives recorded."""
        return self._directive_count
    
    @property
    def conflict_count(self) -> int:
        """Total conflicts recorded."""
        return self._conflict_count
