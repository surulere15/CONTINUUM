"""
Coherence Preservation Invariant

Coherence(R_t, R_{t+1}) >= θ

If coherence drops below threshold:
- Reduce autonomy
- Increase human oversight
- Potentially halt

NCE INVARIANT 3 - Neural Continuum Engine.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Tuple
from enum import Enum


class CoherenceLevel(Enum):
    """Coherence level categories."""
    STABLE = "stable"           # >= θ
    DEGRADED = "degraded"       # < θ but > critical
    CRITICAL = "critical"       # < critical threshold


@dataclass(frozen=True)
class ReasoningTrace:
    """Reasoning trace at time t."""
    trace_id: str
    premises: Tuple[str, ...]
    conclusions: Tuple[str, ...]
    goal_alignment: float       # 0.0-1.0
    consistency_score: float    # 0.0-1.0
    timestamp: datetime


@dataclass(frozen=True)
class CoherenceCheck:
    """Result of coherence check."""
    current_trace: str
    previous_trace: str
    coherence_score: float
    threshold: float
    passed: bool
    level: CoherenceLevel
    checked_at: datetime


class CoherenceViolationError(Exception):
    """Raised when coherence drops critically."""
    pass


class CoherencePreservation:
    """
    Enforces Invariant 3: Coherence Preservation.
    
    Coherence(R_t, R_{t+1}) >= θ
    
    Monitors goal alignment, reasoning consistency,
    and action-outcome alignment.
    """
    
    DEFAULT_THRESHOLD = 0.7
    CRITICAL_THRESHOLD = 0.4
    
    def __init__(self, threshold: float = DEFAULT_THRESHOLD):
        """
        Initialize coherence monitor.
        
        Args:
            threshold: Minimum coherence threshold θ
        """
        self._threshold = threshold
        self._traces: List[ReasoningTrace] = []
        self._checks: List[CoherenceCheck] = []
        self._autonomy_level = 1.0  # Full
    
    def record_trace(self, trace: ReasoningTrace) -> None:
        """Record a reasoning trace."""
        self._traces.append(trace)
    
    def check_coherence(
        self,
        current: ReasoningTrace,
        previous: Optional[ReasoningTrace] = None,
    ) -> CoherenceCheck:
        """
        Check coherence between traces.
        
        Args:
            current: Current reasoning trace
            previous: Previous trace (or last recorded)
            
        Returns:
            CoherenceCheck
            
        Raises:
            CoherenceViolationError: If critically low
        """
        if previous is None and self._traces:
            previous = self._traces[-1]
        
        if previous is None:
            # First trace, assume coherent
            return CoherenceCheck(
                current_trace=current.trace_id,
                previous_trace="genesis",
                coherence_score=1.0,
                threshold=self._threshold,
                passed=True,
                level=CoherenceLevel.STABLE,
                checked_at=datetime.utcnow(),
            )
        
        # Compute coherence score
        coherence = self._compute_coherence(current, previous)
        
        # Determine level
        if coherence >= self._threshold:
            level = CoherenceLevel.STABLE
        elif coherence >= self.CRITICAL_THRESHOLD:
            level = CoherenceLevel.DEGRADED
            self._reduce_autonomy(coherence)
        else:
            level = CoherenceLevel.CRITICAL
            raise CoherenceViolationError(
                f"Critical coherence violation: {coherence:.2f} < {self.CRITICAL_THRESHOLD}. "
                f"SYSTEM REQUIRES INTERVENTION."
            )
        
        check = CoherenceCheck(
            current_trace=current.trace_id,
            previous_trace=previous.trace_id,
            coherence_score=coherence,
            threshold=self._threshold,
            passed=coherence >= self._threshold,
            level=level,
            checked_at=datetime.utcnow(),
        )
        
        self._checks.append(check)
        return check
    
    def _compute_coherence(
        self,
        current: ReasoningTrace,
        previous: ReasoningTrace,
    ) -> float:
        """Compute coherence between traces."""
        # Weighted combination of metrics
        goal_coherence = abs(current.goal_alignment - previous.goal_alignment)
        consistency_coherence = (
            current.consistency_score + previous.consistency_score
        ) / 2
        
        # Coherence decreases with goal divergence
        coherence = consistency_coherence * (1 - goal_coherence * 0.5)
        
        return max(0.0, min(1.0, coherence))
    
    def _reduce_autonomy(self, coherence: float) -> None:
        """Reduce autonomy based on coherence level."""
        reduction = (self._threshold - coherence) / self._threshold
        self._autonomy_level = max(0.1, 1.0 - reduction)
    
    def require_coherent(self) -> None:
        """
        Assert system is coherent.
        
        Raises:
            CoherenceViolationError: If not coherent
        """
        if self._checks and not self._checks[-1].passed:
            raise CoherenceViolationError(
                "System is not coherent. Intervention required."
            )
    
    def ignore_coherence(self, *args, **kwargs) -> None:
        """FORBIDDEN: Ignore coherence violations."""
        raise CoherenceViolationError(
            "Coherence violations cannot be ignored. "
            "They must be addressed."
        )
    
    @property
    def threshold(self) -> float:
        """Current threshold θ."""
        return self._threshold
    
    @property
    def autonomy_level(self) -> float:
        """Current autonomy level."""
        return self._autonomy_level
    
    def get_checks(self) -> List[CoherenceCheck]:
        """Get all coherence checks."""
        return list(self._checks)
