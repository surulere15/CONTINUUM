"""
Memory Influence Function

Φ: M → C

Memory actively shapes cognition, not just dumps into prompts.

MMCP-C - Memory Model & Cognitive Persistence.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Tuple, Set
from enum import Enum


class InfluenceType(Enum):
    """Types of memory influence."""
    BIAS_REASONING = "bias_reasoning"
    PENALIZE_FAILURE = "penalize_failure"
    ELEVATE_STRATEGY = "elevate_strategy"
    SUPPRESS_LOW_CONFIDENCE = "suppress_low_confidence"


@dataclass(frozen=True)
class InfluenceEffect:
    """Effect of memory on cognition."""
    effect_type: InfluenceType
    source_memory: str
    weight: float  # -1.0 to 1.0
    description: str


@dataclass(frozen=True)
class CognitionConstraint:
    """Constraint on cognition from memory."""
    constraint_id: str
    effects: Tuple[InfluenceEffect, ...]
    applied_at: datetime


class MemoryInfluenceFunction:
    """
    Memory Influence Function (Φ).
    
    Φ: M → C
    
    Where C is constraint-modulated cognition.
    
    Memory does not dump into prompts.
    
    Mechanisms:
    - Bias reasoning paths
    - Penalize repeated failures
    - Elevate proven strategies
    - Suppress low-confidence beliefs
    
    This prevents:
    - Context explosion
    - Repetition of mistakes
    - Spurious recall
    """
    
    FAILURE_PENALTY = -0.3
    SUCCESS_BONUS = 0.2
    LOW_CONFIDENCE_THRESHOLD = 0.3
    
    def __init__(self):
        """Initialize influence function."""
        self._constraints: List[CognitionConstraint] = []
    
    def compute(
        self,
        past_failures: List[str],
        past_successes: List[str],
        beliefs: List[Tuple[str, float]],  # (belief, confidence)
        current_goal: str,
    ) -> CognitionConstraint:
        """
        Compute memory influence on cognition.
        
        Args:
            past_failures: Past failure patterns
            past_successes: Past success strategies
            beliefs: Current beliefs with confidence
            current_goal: Active goal
            
        Returns:
            CognitionConstraint
        """
        effects = []
        
        # Penalize repeated failures
        for failure in past_failures:
            effects.append(InfluenceEffect(
                effect_type=InfluenceType.PENALIZE_FAILURE,
                source_memory=f"failure:{failure}",
                weight=self.FAILURE_PENALTY,
                description=f"Penalize: {failure}",
            ))
        
        # Elevate proven strategies
        for success in past_successes:
            effects.append(InfluenceEffect(
                effect_type=InfluenceType.ELEVATE_STRATEGY,
                source_memory=f"success:{success}",
                weight=self.SUCCESS_BONUS,
                description=f"Elevate: {success}",
            ))
        
        # Suppress low-confidence beliefs
        for belief, confidence in beliefs:
            if confidence < self.LOW_CONFIDENCE_THRESHOLD:
                effects.append(InfluenceEffect(
                    effect_type=InfluenceType.SUPPRESS_LOW_CONFIDENCE,
                    source_memory=f"belief:{belief}",
                    weight=-confidence,
                    description=f"Suppress low-confidence: {belief}",
                ))
        
        constraint = CognitionConstraint(
            constraint_id=f"constraint_{len(self._constraints)}",
            effects=tuple(effects),
            applied_at=datetime.utcnow(),
        )
        
        self._constraints.append(constraint)
        return constraint
    
    def dump_to_prompt(self, *args, **kwargs) -> None:
        """FORBIDDEN: Dump memory to prompt."""
        raise ValueError(
            "Memory cannot be dumped directly to prompts. "
            "Memory influences cognition through Φ: M → C."
        )
    
    def get_constraints(self) -> List[CognitionConstraint]:
        """Get all computed constraints."""
        return list(self._constraints)
