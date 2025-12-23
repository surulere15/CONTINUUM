"""
Explanation Engine

Force cognition to explain itself.
No explanation = no output.

COGNITIVE MODULE - No imports from execution/agents/kernel/governance.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Any, Tuple


@dataclass(frozen=True)
class ExplanationStep:
    """
    A single step in an explanation.
    
    Every reasoning step must be explainable.
    """
    step_number: int
    description: str
    inputs_used: tuple
    primitive_applied: str
    output_produced: str


@dataclass(frozen=True)
class Explanation:
    """
    Complete explanation for a cognitive output.
    
    Required fields — no explanation = invalid output.
    """
    explanation_id: str
    summary: str
    steps: tuple  # Tuple[ExplanationStep, ...]
    inputs_used: tuple
    constraints_applied: tuple
    confidence_bounds: Tuple[float, float]
    generated_at: datetime


class MissingExplanationError(Exception):
    """Raised when output lacks explanation."""
    pass


class ExplanationEngine:
    """
    Forces all cognition to produce explanations.
    
    Every output must include:
    - Reasoning steps
    - Inputs used
    - Constraints applied
    - Confidence bounds
    
    No explanation → no output.
    """
    
    def __init__(self):
        """Initialize explanation engine."""
        self._current_steps: List[ExplanationStep] = []
        self._step_counter = 0
    
    def begin_explanation(self) -> None:
        """Begin a new explanation."""
        self._current_steps.clear()
        self._step_counter = 0
    
    def add_step(
        self,
        description: str,
        inputs_used: Tuple,
        primitive: str,
        output: str,
    ) -> int:
        """
        Add a step to the current explanation.
        
        Args:
            description: What happened
            inputs_used: What inputs were used
            primitive: Which inference primitive
            output: What was produced
            
        Returns:
            Step number
        """
        self._step_counter += 1
        step = ExplanationStep(
            step_number=self._step_counter,
            description=description,
            inputs_used=inputs_used,
            primitive_applied=primitive,
            output_produced=output,
        )
        self._current_steps.append(step)
        return self._step_counter
    
    def finalize(
        self,
        summary: str,
        inputs: Tuple,
        constraints: Tuple,
        confidence: Tuple[float, float],
    ) -> Explanation:
        """
        Finalize and return explanation.
        
        Raises:
            MissingExplanationError: If no steps recorded
        """
        if not self._current_steps:
            raise MissingExplanationError(
                "Cannot finalize explanation with no steps. "
                "All cognition must be explainable."
            )
        
        import hashlib
        explanation_id = hashlib.sha256(
            "|".join(s.description for s in self._current_steps).encode()
        ).hexdigest()[:16]
        
        explanation = Explanation(
            explanation_id=explanation_id,
            summary=summary,
            steps=tuple(self._current_steps),
            inputs_used=inputs,
            constraints_applied=constraints,
            confidence_bounds=confidence,
            generated_at=datetime.utcnow(),
        )
        
        return explanation
    
    def validate_output(
        self,
        output: Any,
        explanation: Optional[Explanation],
    ) -> bool:
        """
        Validate that output has proper explanation.
        
        Returns True if valid, raises if not.
        
        Raises:
            MissingExplanationError: If explanation is missing or incomplete
        """
        if explanation is None:
            raise MissingExplanationError(
                "Output must have explanation. "
                "No explanation = no output."
            )
        
        if not explanation.steps:
            raise MissingExplanationError(
                "Explanation must have steps. "
                "Empty explanations are invalid."
            )
        
        if not explanation.summary:
            raise MissingExplanationError(
                "Explanation must have summary."
            )
        
        return True
    
    def format_for_human(self, explanation: Explanation) -> str:
        """
        Format explanation for human reading.
        
        Args:
            explanation: Explanation to format
            
        Returns:
            Human-readable string
        """
        lines = [
            f"Summary: {explanation.summary}",
            f"Confidence: {explanation.confidence_bounds[0]:.0%} - {explanation.confidence_bounds[1]:.0%}",
            "",
            "Steps:",
        ]
        
        for step in explanation.steps:
            lines.append(f"  {step.step_number}. {step.description}")
            lines.append(f"     Primitive: {step.primitive_applied}")
        
        lines.append("")
        lines.append(f"Constraints: {', '.join(explanation.constraints_applied)}")
        
        return "\n".join(lines)
    
    @property
    def step_count(self) -> int:
        """Current number of steps."""
        return len(self._current_steps)
