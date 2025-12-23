"""
Signal Classes

Cognitive, Control, Execution, Feedback signals.

NLP-C - Neural Link Protocol.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import Enum


class SignalClass(Enum):
    """Signal class categories."""
    COGNITIVE = "cognitive"     # Reasoning, planning, simulation
    CONTROL = "control"         # Pause, resume, halt
    EXECUTION = "execution"     # Task dispatch, tool invocation
    FEEDBACK = "feedback"       # Outcome reporting, errors


class SignalPriority(Enum):
    """Signal priority levels."""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3       # Control signals only
    PREEMPTIVE = 4     # Control signals only


@dataclass(frozen=True)
class CognitiveSignal:
    """
    Cognitive signal class.
    
    Used for: Reasoning, Planning, Simulation
    
    Properties:
    - High semantic density
    - Lower frequency
    - Strong coherence checks
    """
    signal_class: SignalClass = SignalClass.COGNITIVE
    priority: SignalPriority = SignalPriority.NORMAL
    requires_coherence_check: bool = True
    semantic_density: str = "high"


@dataclass(frozen=True)
class ControlSignal:
    """
    Control signal class.
    
    Used for: Pause, Resume, Halt, Reconfigure
    
    Properties:
    - Absolute priority
    - Preemptive
    - Minimal payload
    """
    signal_class: SignalClass = SignalClass.CONTROL
    priority: SignalPriority = SignalPriority.PREEMPTIVE
    is_preemptive: bool = True
    minimal_payload: bool = True


class ControlCommand(Enum):
    """Control commands."""
    PAUSE = "pause"
    RESUME = "resume"
    HALT = "halt"
    RECONFIGURE = "reconfigure"


@dataclass(frozen=True)
class ExecutionSignal:
    """
    Execution signal class.
    
    Used for: Task dispatch, Tool invocation, Workflow progression
    
    Properties:
    - Explicit reversibility
    - Auditable side effects
    """
    signal_class: SignalClass = SignalClass.EXECUTION
    priority: SignalPriority = SignalPriority.NORMAL
    requires_reversibility: bool = True
    auditable: bool = True


@dataclass(frozen=True)
class FeedbackSignal:
    """
    Feedback signal class.
    
    Used for: Outcome reporting, Error propagation, Performance metrics
    
    Properties:
    - Mandatory after execution
    - Tied to parent signal
    """
    signal_class: SignalClass = SignalClass.FEEDBACK
    priority: SignalPriority = SignalPriority.NORMAL
    mandatory_after_execution: bool = True
    parent_signal_required: bool = True


class OrphanFeedbackError(Exception):
    """Raised when feedback has no parent signal."""
    pass


class SignalClassifier:
    """
    Classifies and validates signals by class.
    """
    
    def classify(self, signal_type: str) -> SignalClass:
        """Classify a signal by type."""
        type_lower = signal_type.lower()
        
        if type_lower in {"reason", "plan", "simulate", "think"}:
            return SignalClass.COGNITIVE
        elif type_lower in {"pause", "resume", "halt", "reconfigure"}:
            return SignalClass.CONTROL
        elif type_lower in {"execute", "dispatch", "invoke", "run"}:
            return SignalClass.EXECUTION
        elif type_lower in {"feedback", "outcome", "error", "metric"}:
            return SignalClass.FEEDBACK
        else:
            return SignalClass.COGNITIVE  # Default
    
    def validate_feedback(self, parent_signal_id: Optional[str]) -> None:
        """Validate feedback has parent."""
        if parent_signal_id is None:
            raise OrphanFeedbackError(
                "Feedback signals must be tied to a parent signal. "
                "Orphan feedback is forbidden."
            )
    
    def get_priority(self, signal_class: SignalClass) -> SignalPriority:
        """Get default priority for class."""
        if signal_class == SignalClass.CONTROL:
            return SignalPriority.PREEMPTIVE
        return SignalPriority.NORMAL
