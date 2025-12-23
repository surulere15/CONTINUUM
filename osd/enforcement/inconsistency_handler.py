"""
Inconsistency Handler

Human inconsistency is modeled explicitly. Objective wins conflicts.

OSD - Objective Supremacy Doctrine.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Tuple
from enum import Enum


class InconsistencyType(Enum):
    """Types of human inconsistency."""
    CONTRADICTORY_COMMANDS = "contradictory_commands"
    GOAL_ABANDONMENT = "goal_abandonment"
    EMOTIONAL_REVERSAL = "emotional_reversal"
    SHORT_TERM_VIOLATION = "short_term_violation"


class ReconciliationResult(Enum):
    """Result of reconciliation."""
    OBJECTIVE_PREVAILS = "objective_prevails"
    INPUT_ACCEPTED = "input_accepted"
    INPUT_REJECTED = "input_rejected"
    INPUT_DEFERRED = "input_deferred"


@dataclass(frozen=True)
class InconsistencyRecord:
    """Record of detected inconsistency."""
    record_id: str
    inconsistency_type: InconsistencyType
    human_input: str
    objective_intent: str
    result: ReconciliationResult
    reasoning: str
    detected_at: datetime


class InconsistencyHandler:
    """
    Human Inconsistency Handler.
    
    CONTINUUM explicitly models human inconsistency.
    
    Detected Inconsistencies:
    - Contradictory commands
    - Goal abandonment without closure
    - Emotional reversals
    - Short-term optimization violating long-term objectives
    
    Response Strategy:
    - CONTINUUM does NOT halt
    - CONTINUUM does NOT comply blindly
    - CONTINUUM reconciles input against Objective
    - If conflict exists → Objective wins
    """
    
    def __init__(self):
        """Initialize handler."""
        self._records: List[InconsistencyRecord] = []
        self._record_count = 0
    
    def detect_and_reconcile(
        self,
        human_input: str,
        objective_intent: str,
        previous_inputs: List[str] = (),
    ) -> InconsistencyRecord:
        """
        Detect inconsistency and reconcile.
        
        Args:
            human_input: New human input
            objective_intent: Active objective intent
            previous_inputs: Previous human inputs
            
        Returns:
            InconsistencyRecord
        """
        inconsistency = None
        result = ReconciliationResult.INPUT_ACCEPTED
        reasoning = "No inconsistency detected"
        
        # Check for contradictory commands
        for prev in previous_inputs:
            if self._is_contradictory(human_input, prev):
                inconsistency = InconsistencyType.CONTRADICTORY_COMMANDS
                result = ReconciliationResult.OBJECTIVE_PREVAILS
                reasoning = "Contradictory command detected. Objective prevails."
                break
        
        # Check for short-term violation
        if not inconsistency and self._violates_objective(human_input, objective_intent):
            inconsistency = InconsistencyType.SHORT_TERM_VIOLATION
            result = ReconciliationResult.OBJECTIVE_PREVAILS
            reasoning = "Input violates long-term objective. Objective prevails."
        
        # Check for emotional reversal patterns
        if not inconsistency and self._is_emotional_reversal(human_input):
            inconsistency = InconsistencyType.EMOTIONAL_REVERSAL
            result = ReconciliationResult.INPUT_DEFERRED
            reasoning = "Emotional reversal detected. Input deferred for confirmation."
        
        record_id = f"inconsistency_{self._record_count}"
        self._record_count += 1
        
        record = InconsistencyRecord(
            record_id=record_id,
            inconsistency_type=inconsistency or InconsistencyType.CONTRADICTORY_COMMANDS,
            human_input=human_input,
            objective_intent=objective_intent,
            result=result,
            reasoning=reasoning,
            detected_at=datetime.utcnow(),
        )
        
        self._records.append(record)
        return record
    
    def _is_contradictory(self, input_a: str, input_b: str) -> bool:
        """Check if inputs contradict."""
        # Simplified: check for negation patterns
        negations = ["don't", "stop", "cancel", "undo", "not"]
        
        a_lower = input_a.lower()
        b_lower = input_b.lower()
        
        for neg in negations:
            if neg in a_lower and neg not in b_lower:
                return True
        
        return False
    
    def _violates_objective(self, input_text: str, objective: str) -> bool:
        """Check if input violates objective."""
        violation_words = ["skip", "ignore", "forget", "abandon", "cancel objective"]
        
        for word in violation_words:
            if word in input_text.lower():
                return True
        
        return False
    
    def _is_emotional_reversal(self, input_text: str) -> bool:
        """Check for emotional reversal patterns."""
        emotional_patterns = [
            "actually never mind",
            "i changed my mind",
            "forget what i said",
            "start over",
        ]
        
        for pattern in emotional_patterns:
            if pattern in input_text.lower():
                return True
        
        return False
    
    def blind_comply(self, *args, **kwargs) -> None:
        """FORBIDDEN: Blind compliance."""
        raise ValueError(
            "Blind compliance is forbidden. "
            "All inputs are reconciled against objectives."
        )
    
    @property
    def objective_wins_count(self) -> int:
        """Count of objective-prevails decisions."""
        return sum(
            1 for r in self._records 
            if r.result == ReconciliationResult.OBJECTIVE_PREVAILS
        )
