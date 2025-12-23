"""
Need Detector

Trigger conditions for agent genesis.
Necessity-based creation, not curiosity-based.

AGP-C - Agent Genesis Protocol.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from enum import Enum


class NeedTrigger(Enum):
    """Reasons for agent creation need."""
    EFFICIENCY_GAP = "efficiency_gap"
    PATTERN_DETECTED = "pattern_detected"
    THRESHOLD_EXCEEDED = "threshold_exceeded"
    KERNEL_PREDICTION = "kernel_prediction"


@dataclass(frozen=True)
class NeedAssessment:
    """Assessment of need for new agent."""
    assessment_id: str
    trigger: NeedTrigger
    goal_id: str
    existing_agents: int
    description: str
    net_utility: float       # Must be positive
    required: bool
    assessed_at: datetime


class NeedNotJustifiedError(Exception):
    """Raised when agent creation is not justified."""
    pass


class NeedDetector:
    """
    Need Detector.
    
    An agent may be proposed only if:
    1. Existing agents cannot satisfy goal efficiently
    2. Repeated work patterns detected
    3. Latency/cost/complexity thresholds exceeded
    4. Kernel predicts net positive utility
    
    Necessity-based creation, not curiosity-based.
    """
    
    EFFICIENCY_THRESHOLD = 0.5
    PATTERN_THRESHOLD = 3      # Repeated occurrences
    LATENCY_THRESHOLD = 5.0    # Seconds
    UTILITY_THRESHOLD = 0.0    # Must be positive
    
    def __init__(self):
        """Initialize detector."""
        self._assessments: List[NeedAssessment] = []
        self._assessment_count = 0
    
    def assess(
        self,
        goal_id: str,
        existing_agents: int,
        current_efficiency: float,
        pattern_count: int,
        current_latency: float,
        predicted_utility: float,
    ) -> NeedAssessment:
        """
        Assess need for new agent.
        
        Args:
            goal_id: Goal requiring agent
            existing_agents: Current agent count
            current_efficiency: Current efficiency (0-1)
            pattern_count: Repeated pattern occurrences
            current_latency: Current latency
            predicted_utility: Predicted net utility
            
        Returns:
            NeedAssessment
            
        Raises:
            NeedNotJustifiedError: If not justified
        """
        triggers = []
        
        # Check trigger conditions
        if current_efficiency < self.EFFICIENCY_THRESHOLD:
            triggers.append(NeedTrigger.EFFICIENCY_GAP)
        
        if pattern_count >= self.PATTERN_THRESHOLD:
            triggers.append(NeedTrigger.PATTERN_DETECTED)
        
        if current_latency > self.LATENCY_THRESHOLD:
            triggers.append(NeedTrigger.THRESHOLD_EXCEEDED)
        
        if predicted_utility > self.UTILITY_THRESHOLD:
            triggers.append(NeedTrigger.KERNEL_PREDICTION)
        
        # Must have at least one trigger
        if not triggers:
            raise NeedNotJustifiedError(
                f"Agent creation not justified for goal '{goal_id}'. "
                f"No trigger conditions met."
            )
        
        # Must have positive utility
        if predicted_utility <= 0:
            raise NeedNotJustifiedError(
                f"Net utility must be positive. Got: {predicted_utility}"
            )
        
        assessment_id = f"need_{self._assessment_count}"
        self._assessment_count += 1
        
        assessment = NeedAssessment(
            assessment_id=assessment_id,
            trigger=triggers[0],  # Primary trigger
            goal_id=goal_id,
            existing_agents=existing_agents,
            description=f"Triggers: {[t.value for t in triggers]}",
            net_utility=predicted_utility,
            required=True,
            assessed_at=datetime.utcnow(),
        )
        
        self._assessments.append(assessment)
        return assessment
    
    def curiosity_create(self, *args, **kwargs) -> None:
        """FORBIDDEN: Curiosity-based creation."""
        raise NeedNotJustifiedError(
            "Curiosity-based agent creation is forbidden. "
            "Creation must be necessity-based."
        )
    
    @property
    def assessment_count(self) -> int:
        """Total assessments."""
        return len(self._assessments)
