"""
Cognition Core

Neutral reasoning container. Stateless, deterministic.
Input → Representation → Output. No persistence.

COGNITIVE MODULE - No imports from execution/agents/kernel/governance.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional, List
from enum import Enum
import hashlib


class CognitionStatus(Enum):
    """Status of cognition processing."""
    READY = "ready"
    PROCESSING = "processing"
    COMPLETE = "complete"
    HALTED = "halted"
    ERROR = "error"


@dataclass(frozen=True)
class CognitionInput:
    """
    Immutable input to cognition.
    
    All inputs are read-only snapshots.
    """
    input_id: str
    content: Any
    input_type: str
    timestamp: datetime
    provenance: str


@dataclass(frozen=True)
class CognitionOutput:
    """
    Immutable output from cognition.
    
    Must include explanation. No explanation = invalid output.
    """
    output_id: str
    result: Any
    explanation: str
    reasoning_steps: tuple
    inputs_used: tuple
    constraints_applied: tuple
    confidence_bounds: tuple  # (lower, upper)
    processing_time_ms: float
    deterministic: bool


class CognitionHaltError(Exception):
    """Raised when cognition must halt due to constraint violation."""
    pass


class CognitionCore:
    """
    Neutral reasoning container.
    
    Properties:
    - Stateless by default
    - Deterministic execution
    - Input → Representation → Output
    - No persistence, no memory writes
    
    Prohibitions:
    - Cannot form goals
    - Cannot modify objectives
    - Cannot trigger execution
    - Cannot spawn agents
    - Cannot self-modify
    """
    
    def __init__(self, constraints: Optional['CognitiveConstraints'] = None):
        """
        Initialize cognition core.
        
        Args:
            constraints: Cognitive constraints to enforce
        """
        self._constraints = constraints
        self._status = CognitionStatus.READY
        self._current_depth = 0
    
    def process(
        self,
        input_repr: CognitionInput,
        reasoning_type: str = "default",
    ) -> CognitionOutput:
        """
        Perform bounded inference.
        
        Returns internal artifacts only. Cannot trigger external effects.
        
        Args:
            input_repr: Input representation
            reasoning_type: Type of reasoning to apply
            
        Returns:
            CognitionOutput with explanation
            
        Raises:
            CognitionHaltError: If constraints are violated
        """
        import time
        start = time.time()
        
        self._status = CognitionStatus.PROCESSING
        
        # Check constraints before processing
        if self._constraints:
            self._constraints.check_before_inference(self._current_depth)
        
        try:
            # Increment depth for nested calls
            self._current_depth += 1
            
            # Perform actual reasoning (placeholder - subclasses implement)
            result, steps = self._reason(input_repr, reasoning_type)
            
            # Generate output with mandatory explanation
            elapsed = (time.time() - start) * 1000
            
            output = CognitionOutput(
                output_id=self._generate_id(input_repr, result),
                result=result,
                explanation=self._generate_explanation(steps),
                reasoning_steps=tuple(steps),
                inputs_used=(input_repr.input_id,),
                constraints_applied=self._get_applied_constraints(),
                confidence_bounds=(0.0, 1.0),  # Default, should be refined
                processing_time_ms=elapsed,
                deterministic=True,
            )
            
            self._status = CognitionStatus.COMPLETE
            return output
            
        except CognitionHaltError:
            self._status = CognitionStatus.HALTED
            raise
        finally:
            self._current_depth -= 1
    
    def _reason(
        self,
        input_repr: CognitionInput,
        reasoning_type: str,
    ) -> tuple:
        """
        Internal reasoning implementation.
        
        Override in subclasses for specific reasoning.
        Returns (result, reasoning_steps).
        """
        # Default: identity transform with explanation
        steps = [
            f"Received input of type '{input_repr.input_type}'",
            f"Applied {reasoning_type} reasoning",
            "Produced output",
        ]
        return input_repr.content, steps
    
    def _generate_explanation(self, steps: List[str]) -> str:
        """Generate human-readable explanation from steps."""
        if not steps:
            raise ValueError("Cognition must produce explanation steps")
        return " → ".join(steps)
    
    def _generate_id(self, input_repr: CognitionInput, result: Any) -> str:
        """Generate deterministic output ID."""
        content = f"{input_repr.input_id}|{str(result)}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def _get_applied_constraints(self) -> tuple:
        """Get list of constraints that were applied."""
        if self._constraints:
            return self._constraints.get_active_constraints()
        return ()
    
    @property
    def status(self) -> CognitionStatus:
        """Get current status."""
        return self._status
    
    @property
    def is_ready(self) -> bool:
        """Check if ready for processing."""
        return self._status == CognitionStatus.READY
