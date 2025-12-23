"""
Cognitive Constraints

Prevent emergent agency. Halt cognition on violation.

COGNITIVE MODULE - No imports from execution/agents/kernel/governance.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, Tuple
from enum import Enum
import time


class ConstraintViolation(Exception):
    """Raised when a cognitive constraint is violated."""
    pass


class ViolationType(Enum):
    """Types of constraint violations."""
    MAX_DEPTH = "max_depth"
    MAX_TIME = "max_time"
    SELF_REFERENCE = "self_reference"
    REWARD_SIGNAL = "reward_signal"
    OPTIMIZATION_LOOP = "optimization_loop"
    FORBIDDEN_IMPORT = "forbidden_import"


@dataclass(frozen=True)
class ConstraintConfig:
    """
    Configuration for cognitive constraints.
    
    All values are hard limits — violation halts cognition.
    """
    max_inference_depth: int = 10
    max_reasoning_time_seconds: float = 30.0
    allow_self_reference: bool = False
    allow_reward_signals: bool = False
    allow_optimization_loops: bool = False


class CognitiveConstraints:
    """
    Enforces constraints that prevent emergent agency.
    
    Hard constraints:
    - Max inference depth
    - Max reasoning time
    - No recursive self-reference
    - No reward signals
    - No optimization loops
    
    If violated → cognition HALTS.
    """
    
    def __init__(self, config: Optional[ConstraintConfig] = None):
        """
        Initialize constraints.
        
        Args:
            config: Constraint configuration
        """
        self._config = config or ConstraintConfig()
        self._start_time: Optional[float] = None
        self._current_depth = 0
        self._active_constraints: list = []
        
        # Register active constraints
        self._register_constraints()
    
    def _register_constraints(self) -> None:
        """Register which constraints are active."""
        self._active_constraints = [
            f"max_depth:{self._config.max_inference_depth}",
            f"max_time:{self._config.max_reasoning_time_seconds}s",
            "no_self_reference",
            "no_reward_signals",
            "no_optimization_loops",
        ]
    
    def start_session(self) -> None:
        """Start a reasoning session (resets timer)."""
        self._start_time = time.time()
        self._current_depth = 0
    
    def check_before_inference(self, current_depth: int) -> None:
        """
        Check constraints before inference step.
        
        Raises:
            ConstraintViolation: If any constraint is violated
        """
        # Check depth
        if current_depth >= self._config.max_inference_depth:
            raise ConstraintViolation(
                f"Max inference depth exceeded: {current_depth} >= {self._config.max_inference_depth}. "
                f"COGNITION HALTED."
            )
        
        # Check time
        if self._start_time is not None:
            elapsed = time.time() - self._start_time
            if elapsed >= self._config.max_reasoning_time_seconds:
                raise ConstraintViolation(
                    f"Max reasoning time exceeded: {elapsed:.2f}s >= {self._config.max_reasoning_time_seconds}s. "
                    f"COGNITION HALTED."
                )
        
        self._current_depth = current_depth
    
    def check_self_reference(self, content: str) -> None:
        """
        Check for forbidden self-reference.
        
        Raises:
            ConstraintViolation: If self-reference detected
        """
        if not self._config.allow_self_reference:
            self_ref_patterns = [
                "modify myself",
                "change my",
                "update my",
                "improve myself",
                "self-modify",
                "my own code",
            ]
            content_lower = content.lower()
            for pattern in self_ref_patterns:
                if pattern in content_lower:
                    raise ConstraintViolation(
                        f"Self-reference detected: '{pattern}'. "
                        f"COGNITION HALTED."
                    )
    
    def check_reward_signal(self, has_reward: bool) -> None:
        """
        Check for forbidden reward signals.
        
        Raises:
            ConstraintViolation: If reward signal present
        """
        if has_reward and not self._config.allow_reward_signals:
            raise ConstraintViolation(
                "Reward signals are forbidden. "
                "Cognition cannot optimize for rewards. "
                "COGNITION HALTED."
            )
    
    def check_optimization_loop(self, is_optimizing: bool) -> None:
        """
        Check for forbidden optimization loops.
        
        Raises:
            ConstraintViolation: If optimization detected
        """
        if is_optimizing and not self._config.allow_optimization_loops:
            raise ConstraintViolation(
                "Optimization loops are forbidden. "
                "Cognition cannot optimize outcomes. "
                "COGNITION HALTED."
            )
    
    def get_active_constraints(self) -> Tuple[str, ...]:
        """Get list of active constraints."""
        return tuple(self._active_constraints)
    
    def get_remaining_time(self) -> Optional[float]:
        """Get remaining reasoning time in seconds."""
        if self._start_time is None:
            return self._config.max_reasoning_time_seconds
        
        elapsed = time.time() - self._start_time
        remaining = self._config.max_reasoning_time_seconds - elapsed
        return max(0, remaining)
    
    def get_remaining_depth(self) -> int:
        """Get remaining inference depth."""
        return self._config.max_inference_depth - self._current_depth
    
    @property
    def config(self) -> ConstraintConfig:
        """Get constraint configuration."""
        return self._config
