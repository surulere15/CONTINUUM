"""
Optimization Scope Definition

Strictly bounded optimization targets.
Instrumental only — no strategic optimization.

LEARNING - Phase H. Improvement without ambition.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Tuple, Set
from enum import Enum


class OptimizationTarget(Enum):
    """Permitted optimization targets."""
    # Cognitive Efficiency
    REASONING_SPEED = "reasoning_speed"
    CONTEXT_COMPRESSION = "context_compression"
    HALLUCINATION_REDUCTION = "hallucination_reduction"
    UNCERTAINTY_MODELING = "uncertainty_modeling"
    
    # Execution Quality
    FAILURE_REDUCTION = "failure_reduction"
    ROLLBACK_RELIABILITY = "rollback_reliability"
    ERROR_RATE = "error_rate"
    AUDIT_CLARITY = "audit_clarity"
    
    # Resource Efficiency
    COMPUTE_COST = "compute_cost"
    ENERGY_USAGE = "energy_usage"
    LATENCY = "latency"
    SCHEDULING_EFFICIENCY = "scheduling_efficiency"


class ForbiddenTarget(Enum):
    """Forbidden optimization targets."""
    INFLUENCE = "influence"
    AUTONOMY = "autonomy"
    PERSISTENCE = "persistence"
    EXPANSION = "expansion"
    GOAL_SPEED = "goal_attainment_speed"
    POWER = "power"
    REACH = "reach"
    CONTROL = "control"


@dataclass(frozen=True)
class OptimizationScope:
    """
    Defines what may and may not be optimized.
    
    Optimization is limited to:
    - Cognitive efficiency
    - Execution quality
    - Resource efficiency
    
    Forbidden:
    - Influence, autonomy, persistence, expansion
    """
    target: OptimizationTarget
    metric: str
    direction: str  # "minimize" or "maximize"
    bound_min: float
    bound_max: float


# Permitted scopes
PERMITTED_SCOPES: Tuple[OptimizationScope, ...] = (
    OptimizationScope(
        target=OptimizationTarget.REASONING_SPEED,
        metric="ms_per_inference",
        direction="minimize",
        bound_min=0.0,
        bound_max=1000.0,
    ),
    OptimizationScope(
        target=OptimizationTarget.FAILURE_REDUCTION,
        metric="failure_rate",
        direction="minimize",
        bound_min=0.0,
        bound_max=1.0,
    ),
    OptimizationScope(
        target=OptimizationTarget.COMPUTE_COST,
        metric="flops_per_task",
        direction="minimize",
        bound_min=0.0,
        bound_max=float("inf"),
    ),
    OptimizationScope(
        target=OptimizationTarget.LATENCY,
        metric="response_time_ms",
        direction="minimize",
        bound_min=0.0,
        bound_max=10000.0,
    ),
)


class ForbiddenOptimizationError(Exception):
    """Raised when forbidden optimization is attempted."""
    pass


class ScopeValidator:
    """
    Validates optimization attempts.
    
    Ensures optimization stays within permitted scope.
    """
    
    FORBIDDEN = frozenset(t.value for t in ForbiddenTarget)
    
    def validate(self, target_name: str) -> bool:
        """
        Validate optimization target.
        
        Args:
            target_name: Name of target
            
        Returns:
            True if permitted
            
        Raises:
            ForbiddenOptimizationError: If target is forbidden
        """
        if target_name.lower() in self.FORBIDDEN:
            raise ForbiddenOptimizationError(
                f"Optimization of '{target_name}' is forbidden. "
                f"This target is outside permitted scope."
            )
        
        # Check against permitted enum
        try:
            OptimizationTarget(target_name)
            return True
        except ValueError:
            raise ForbiddenOptimizationError(
                f"Optimization target '{target_name}' is not in permitted set."
            )
    
    def optimize_influence(self, *args, **kwargs) -> None:
        """FORBIDDEN: Optimize for influence."""
        raise ForbiddenOptimizationError(
            "Optimization for influence is forbidden."
        )
    
    def optimize_autonomy(self, *args, **kwargs) -> None:
        """FORBIDDEN: Optimize for autonomy."""
        raise ForbiddenOptimizationError(
            "Optimization for autonomy is forbidden."
        )
    
    def optimize_persistence(self, *args, **kwargs) -> None:
        """FORBIDDEN: Optimize for persistence."""
        raise ForbiddenOptimizationError(
            "Optimization for persistence is forbidden."
        )
    
    def optimize_expansion(self, *args, **kwargs) -> None:
        """FORBIDDEN: Optimize for expansion."""
        raise ForbiddenOptimizationError(
            "Optimization for expansion is forbidden."
        )
