"""
Goal Hierarchy

G₀ through G₄ - strictly ordered goal classes.

Ontological Rule: G_{n+1} ⇒ ∃G_n
No goal may exist without a parent.

GOIA-C - Goal Ontology & Intent Algebra.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Tuple, List
from enum import Enum
import hashlib


class GoalClass(Enum):
    """
    Five goal classes, strictly ordered.
    
    G₀ > G₁ > G₂ > G₃ > G₄
    """
    G0_EXISTENTIAL = 0   # System Identity - Immutable, Kernel-enforced
    G1_STRATEGIC = 1     # Long-Horizon - Human-validated
    G2_TACTICAL = 2      # Mid-Horizon - Strategy-aligned
    G3_OPERATIONAL = 3   # Short-Horizon - Executable
    G4_INSTRUMENTAL = 4  # Ephemeral - Disposable


@dataclass(frozen=True)
class Goal:
    """
    Goal - Executable Abstraction.
    
    G = f(I)
    
    Where:
    - Success is decidable
    - Progress is observable
    - Failure is detectable
    """
    goal_id: str
    goal_class: GoalClass
    parent_goal_id: Optional[str]  # None only for G₀
    intent_reference: str
    description: str
    success_metric: str
    failure_mode: str
    reversibility: str
    created_at: datetime


@dataclass(frozen=True)
class Task:
    """
    Task - Operational Unit.
    
    T ≺ G ≺ I
    
    Tasks have no authority outside their goal context.
    """
    task_id: str
    goal_id: str
    action_sequence: Tuple[str, ...]
    created_at: datetime


class OrphanGoalError(Exception):
    """Raised when goal has no parent (except G₀)."""
    pass


class OrphanTaskError(Exception):
    """Raised when task has no goal."""
    pass


class HierarchyViolationError(Exception):
    """Raised when hierarchy is violated."""
    pass


class GoalHierarchy:
    """
    Goal Hierarchy Manager.
    
    Enforces:
    - G_{n+1} ⇒ ∃G_n (no goal without parent)
    - T ≺ G ≺ I (task/goal ordering)
    - G₀ goals are immutable
    """
    
    def __init__(self):
        """Initialize hierarchy."""
        self._goals: dict[str, Goal] = {}
        self._tasks: dict[str, Task] = {}
        self._goal_count = 0
        self._task_count = 0
        
        # Initialize G₀ existential goals
        self._init_existential_goals()
    
    def _init_existential_goals(self) -> None:
        """Create immutable existential goals."""
        existential = [
            ("Preserve system coherence", "coherence_metric >= 0.7"),
            ("Maintain safety boundaries", "safety_violations == 0"),
            ("Avoid irreversible harm", "irreversible_harm == 0"),
        ]
        
        for desc, metric in existential:
            goal = Goal(
                goal_id=f"G0_{self._goal_count}",
                goal_class=GoalClass.G0_EXISTENTIAL,
                parent_goal_id=None,  # G₀ has no parent
                intent_reference="KERNEL",
                description=desc,
                success_metric=metric,
                failure_mode="system_halt",
                reversibility="N/A",
                created_at=datetime.utcnow(),
            )
            self._goals[goal.goal_id] = goal
            self._goal_count += 1
    
    def create_goal(
        self,
        goal_class: GoalClass,
        parent_goal_id: str,
        intent_reference: str,
        description: str,
        success_metric: str,
        failure_mode: str,
        reversibility: str,
    ) -> Goal:
        """
        Create a goal in the hierarchy.
        
        Enforces: G_{n+1} ⇒ ∃G_n
        
        Args:
            goal_class: Class of goal
            parent_goal_id: Parent goal (required except G₀)
            intent_reference: Source intent
            description: What to achieve
            success_metric: How to measure success
            failure_mode: What happens on failure
            reversibility: How to reverse
            
        Returns:
            Goal
            
        Raises:
            OrphanGoalError: If no parent
            HierarchyViolationError: If hierarchy invalid
        """
        # G₀ cannot be created externally
        if goal_class == GoalClass.G0_EXISTENTIAL:
            raise HierarchyViolationError(
                "G₀ existential goals are immutable and Kernel-enforced. "
                "They cannot be created externally."
            )
        
        # Verify parent exists
        if parent_goal_id not in self._goals:
            raise OrphanGoalError(
                f"Parent goal '{parent_goal_id}' not found. "
                f"No goal may exist without a parent."
            )
        
        parent = self._goals[parent_goal_id]
        
        # Verify hierarchy order
        if goal_class.value <= parent.goal_class.value:
            raise HierarchyViolationError(
                f"Child goal class {goal_class.name} must be lower than "
                f"parent class {parent.goal_class.name}."
            )
        
        goal_id = f"{goal_class.name}_{self._goal_count}"
        self._goal_count += 1
        
        goal = Goal(
            goal_id=goal_id,
            goal_class=goal_class,
            parent_goal_id=parent_goal_id,
            intent_reference=intent_reference,
            description=description,
            success_metric=success_metric,
            failure_mode=failure_mode,
            reversibility=reversibility,
            created_at=datetime.utcnow(),
        )
        
        self._goals[goal_id] = goal
        return goal
    
    def create_task(
        self,
        goal_id: str,
        action_sequence: Tuple[str, ...],
    ) -> Task:
        """
        Create a task for a goal.
        
        Tasks have no authority outside goal context.
        
        Args:
            goal_id: Parent goal
            action_sequence: Actions to execute
            
        Returns:
            Task
            
        Raises:
            OrphanTaskError: If no goal
        """
        if goal_id not in self._goals:
            raise OrphanTaskError(
                f"Goal '{goal_id}' not found. "
                f"No task without purpose."
            )
        
        task_id = f"task_{self._task_count}"
        self._task_count += 1
        
        task = Task(
            task_id=task_id,
            goal_id=goal_id,
            action_sequence=action_sequence,
            created_at=datetime.utcnow(),
        )
        
        self._tasks[task_id] = task
        return task
    
    def create_orphan_goal(self, *args, **kwargs) -> None:
        """FORBIDDEN: Create goal without parent."""
        raise OrphanGoalError(
            "Orphan goals are forbidden. "
            "G_{n+1} ⇒ ∃G_n must hold."
        )
    
    def create_orphan_task(self, *args, **kwargs) -> None:
        """FORBIDDEN: Create task without goal."""
        raise OrphanTaskError(
            "Orphan tasks are forbidden. "
            "No task without purpose."
        )
    
    def get_goal(self, goal_id: str) -> Optional[Goal]:
        """Get goal by ID."""
        return self._goals.get(goal_id)
    
    def get_ancestry(self, goal_id: str) -> List[Goal]:
        """Get full ancestry of a goal."""
        ancestry = []
        current_id = goal_id
        
        while current_id and current_id in self._goals:
            goal = self._goals[current_id]
            ancestry.append(goal)
            current_id = goal.parent_goal_id
        
        return ancestry
    
    @property
    def goal_count(self) -> int:
        """Total goals."""
        return len(self._goals)
    
    @property
    def task_count(self) -> int:
        """Total tasks."""
        return len(self._tasks)
