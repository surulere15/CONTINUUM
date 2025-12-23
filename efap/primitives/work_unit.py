"""
Work Unit

Atomic unit of execution. Deterministic, side-effect declared, reversible flag.

EFAP-C - Execution Fabric & Agent Physics.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any, Tuple
from enum import Enum


class ActionType(Enum):
    """Types of actions."""
    READ = "read"
    WRITE = "write"
    COMPUTE = "compute"
    NETWORK = "network"
    SYSTEM = "system"


class Reversibility(Enum):
    """Reversibility classification."""
    FULLY_REVERSIBLE = "fully_reversible"
    PARTIALLY_REVERSIBLE = "partially_reversible"
    IRREVERSIBLE = "irreversible"


@dataclass(frozen=True)
class WorkUnit:
    """
    Atomic unit of execution.
    
    Properties:
    - Deterministic
    - Side-effect declared
    - Reversible flag present
    
    No work unit may self-spawn.
    """
    work_id: str
    parent_goal: str
    action_type: ActionType
    input_state: str
    expected_effect: str
    reversibility: Reversibility
    declared_side_effects: Tuple[str, ...]
    created_at: datetime


class FreeWorkError(Exception):
    """Raised when work has no goal (Law 1 violation)."""
    pass


class UndeclaredEffectError(Exception):
    """Raised when side effect is undeclared (Law 2 violation)."""
    pass


class WorkUnitFactory:
    """
    Factory for creating work units.
    
    Enforces:
    - Law 1: No free work (∀W, ∃G: W ≺ G)
    - Law 2: No side effects without declaration
    """
    
    def __init__(self):
        """Initialize factory."""
        self._work_count = 0
    
    def create(
        self,
        parent_goal: str,
        action_type: ActionType,
        input_state: str,
        expected_effect: str,
        reversibility: Reversibility,
        side_effects: Tuple[str, ...] = (),
    ) -> WorkUnit:
        """
        Create a work unit.
        
        Args:
            parent_goal: Goal this work serves (required)
            action_type: Type of action
            input_state: Input state
            expected_effect: Expected outcome
            reversibility: How reversible
            side_effects: Declared side effects
            
        Returns:
            WorkUnit
            
        Raises:
            FreeWorkError: If no goal
            UndeclaredEffectError: If effect not declared
        """
        # Law 1: No free work
        if not parent_goal:
            raise FreeWorkError(
                "Work unit must have parent goal. "
                "∀W, ∃G: W ≺ G - No work exists without purpose."
            )
        
        # Law 2: Effects must be declared
        if expected_effect and not side_effects and action_type != ActionType.READ:
            raise UndeclaredEffectError(
                "Non-read actions must declare side effects. "
                "Effect must be declared, reversibility stated."
            )
        
        work_id = f"work_{self._work_count}"
        self._work_count += 1
        
        return WorkUnit(
            work_id=work_id,
            parent_goal=parent_goal,
            action_type=action_type,
            input_state=input_state,
            expected_effect=expected_effect,
            reversibility=reversibility,
            declared_side_effects=side_effects,
            created_at=datetime.utcnow(),
        )
    
    def self_spawn(self, *args, **kwargs) -> None:
        """FORBIDDEN: Work unit self-spawning."""
        raise FreeWorkError(
            "Work units cannot self-spawn. "
            "All work must be goal-authorized."
        )
    
    @property
    def work_count(self) -> int:
        """Total work units created."""
        return self._work_count
