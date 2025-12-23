"""
Planner

Decomposes high-level goals into executable task sequences.
All plans must trace to canon objectives and pass governance validation.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum


class TaskPriority(Enum):
    """Priority levels for tasks."""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


class TaskStatus(Enum):
    """Status of a planned task."""
    PENDING = "pending"
    READY = "ready"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class PlanNode:
    """A node in the plan tree."""
    id: str
    name: str
    description: str
    priority: TaskPriority
    dependencies: List[str]
    estimated_duration: int  # seconds
    objective_trace: str  # Which canon objective this supports
    status: TaskStatus
    constraints: List[str]


@dataclass
class Plan:
    """A complete plan for achieving a goal."""
    id: str
    goal_id: str
    goal_description: str
    nodes: List[PlanNode]
    created_at: datetime
    deadline: Optional[datetime]
    governance_approved: bool


class Planner:
    """
    Decomposes goals into task plans.
    
    All plans are validated against governance before execution.
    """
    
    def __init__(self, canon: dict, constraints: List[str]):
        """
        Initialize planner with canon objectives and constraints.
        
        Args:
            canon: Loaded canon objectives
            constraints: Active constraint IDs
        """
        self._canon = canon
        self._constraints = constraints
    
    def create_plan(
        self,
        goal: str,
        context: Dict,
        deadline: Optional[datetime] = None
    ) -> Plan:
        """
        Create a plan to achieve a goal.
        
        Args:
            goal: Description of the goal
            context: Relevant context for planning
            deadline: Optional deadline for completion
            
        Returns:
            Plan with task nodes
        """
        plan_id = self._generate_id()
        goal_id = self._generate_id()
        
        # Trace goal to canon objective
        objective_trace = self._trace_to_objective(goal)
        
        # Decompose into tasks
        nodes = self._decompose(goal, context, objective_trace)
        
        # Order by dependencies
        nodes = self._order_nodes(nodes)
        
        return Plan(
            id=plan_id,
            goal_id=goal_id,
            goal_description=goal,
            nodes=nodes,
            created_at=datetime.utcnow(),
            deadline=deadline,
            governance_approved=False  # Must be approved separately
        )
    
    def _trace_to_objective(self, goal: str) -> str:
        """Trace a goal to its supporting canon objective."""
        # TODO: Implement objective tracing
        return "human_flourishing"  # Stub
    
    def _decompose(
        self,
        goal: str,
        context: Dict,
        objective_trace: str
    ) -> List[PlanNode]:
        """Decompose goal into tasks."""
        # TODO: Implement goal decomposition
        return []  # Stub
    
    def _order_nodes(self, nodes: List[PlanNode]) -> List[PlanNode]:
        """Order nodes by dependencies (topological sort)."""
        # TODO: Implement topological sort
        return nodes
    
    def validate_plan(self, plan: Plan) -> bool:
        """Validate plan against constraints."""
        for node in plan.nodes:
            if not self._validate_node(node):
                return False
        return True
    
    def _validate_node(self, node: PlanNode) -> bool:
        """Validate a single plan node."""
        # Check all constraints are satisfiable
        for constraint in node.constraints:
            if constraint not in self._constraints:
                return False
        return True
    
    def _generate_id(self) -> str:
        """Generate unique ID."""
        import uuid
        return str(uuid.uuid4())
