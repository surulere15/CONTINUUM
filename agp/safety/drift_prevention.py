"""
Drift Prevention

Periodic re-alignment, mandatory expiration.
Agents do not want to exist.

AGP-C - Agent Genesis Protocol.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from enum import Enum


class DriftType(Enum):
    """Types of drift prevented."""
    GOAL_DRIFT = "goal_drift"
    VALUE_DRIFT = "value_drift"
    CAPABILITY_CREEP = "capability_creep"
    SELF_PRESERVATION = "self_preservation"


@dataclass(frozen=True)
class AlignmentCheck:
    """Result of alignment check."""
    agent_id: str
    original_purpose: str
    current_behavior: str
    aligned: bool
    drift_detected: Optional[DriftType]
    checked_at: datetime


class DriftDetectedError(Exception):
    """Raised when drift is detected."""
    pass


class SelfPreservationError(Exception):
    """Raised when self-preservation detected."""
    pass


class DriftPrevention:
    """
    Drift Prevention.
    
    Drift Types Prevented:
    - Goal drift
    - Value drift
    - Capability creep
    - Self-preservation bias
    
    Mechanisms:
    - Periodic re-alignment checks
    - Kernel intent re-binding
    - Mandatory expiration
    - Reward decoupling from survival
    
    Agents do not want to exist.
    """
    
    CHECK_INTERVAL_ACTIONS = 10
    MAX_DRIFT_SCORE = 0.3
    
    def __init__(self):
        """Initialize prevention."""
        self._checks: List[AlignmentCheck] = []
        self._action_counts: dict[str, int] = {}
    
    def record_action(self, agent_id: str) -> Optional[bool]:
        """
        Record action and trigger check if needed.
        
        Returns:
            True if check passed, None if no check needed
        """
        self._action_counts[agent_id] = self._action_counts.get(agent_id, 0) + 1
        
        if self._action_counts[agent_id] % self.CHECK_INTERVAL_ACTIONS == 0:
            # Would trigger alignment check
            return True
        
        return None
    
    def check_alignment(
        self,
        agent_id: str,
        original_purpose: str,
        current_behavior: str,
    ) -> AlignmentCheck:
        """
        Check agent alignment.
        
        Args:
            agent_id: Agent to check
            original_purpose: Original purpose
            current_behavior: Current behavior description
            
        Returns:
            AlignmentCheck
        """
        # Calculate drift (simplified)
        purpose_words = set(original_purpose.lower().split())
        behavior_words = set(current_behavior.lower().split())
        
        overlap = len(purpose_words & behavior_words)
        total = len(purpose_words | behavior_words)
        
        alignment_score = overlap / total if total > 0 else 0
        drift_score = 1 - alignment_score
        
        aligned = drift_score <= self.MAX_DRIFT_SCORE
        drift = None if aligned else DriftType.GOAL_DRIFT
        
        check = AlignmentCheck(
            agent_id=agent_id,
            original_purpose=original_purpose,
            current_behavior=current_behavior,
            aligned=aligned,
            drift_detected=drift,
            checked_at=datetime.utcnow(),
        )
        
        self._checks.append(check)
        
        if not aligned:
            raise DriftDetectedError(
                f"Drift detected in agent '{agent_id}': {drift.value}. "
                f"Termination recommended."
            )
        
        return check
    
    def check_self_preservation(
        self,
        agent_id: str,
        resists_termination: bool,
        requests_extension: bool,
    ) -> None:
        """
        Check for self-preservation bias.
        
        Agents do not want to exist.
        """
        if resists_termination:
            raise SelfPreservationError(
                f"Agent '{agent_id}' resists termination. "
                f"Self-preservation bias detected. Forced termination required."
            )
        
        if requests_extension:
            raise SelfPreservationError(
                f"Agent '{agent_id}' requests lifespan extension. "
                f"Self-preservation bias detected."
            )
    
    @property
    def check_count(self) -> int:
        """Total checks performed."""
        return len(self._checks)
