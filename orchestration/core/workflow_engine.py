"""
Workflow Engine

DAG execution. Workflows are goal-aligned, observable, reversible.

ORCHESTRATION - Phase II.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple
from enum import Enum


class NodeState(Enum):
    """Workflow node state."""
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class WorkflowNode:
    """A node in the workflow DAG."""
    node_id: str
    action: str
    dependencies: Tuple[str, ...]  # Node IDs
    state: NodeState
    result: Optional[str]


@dataclass
class Workflow:
    """A workflow (DAG of nodes)."""
    workflow_id: str
    goal_id: str
    nodes: Dict[str, WorkflowNode]
    created_at: datetime
    completed_at: Optional[datetime]


class WorkflowCycleError(Exception):
    """Raised when workflow has cycles."""
    pass


class OrphanWorkflowError(Exception):
    """Raised when workflow has no goal."""
    pass


class WorkflowEngine:
    """
    Workflow Engine.
    
    Executes DAGs of actions.
    Workflows are:
    - Goal-aligned
    - Observable
    - Reversible (where possible)
    """
    
    def __init__(self):
        """Initialize engine."""
        self._workflows: Dict[str, Workflow] = {}
        self._workflow_count = 0
    
    def create(
        self,
        goal_id: str,
        nodes: List[Tuple[str, str, Tuple[str, ...]]],  # (id, action, deps)
    ) -> Workflow:
        """
        Create a workflow.
        
        Args:
            goal_id: Goal this workflow serves
            nodes: List of (node_id, action, dependencies)
            
        Returns:
            Workflow
        """
        if not goal_id:
            raise OrphanWorkflowError(
                "Workflow must have a goal. "
                "No execution without purpose."
            )
        
        # Build nodes
        workflow_nodes = {}
        for node_id, action, deps in nodes:
            workflow_nodes[node_id] = WorkflowNode(
                node_id=node_id,
                action=action,
                dependencies=deps,
                state=NodeState.PENDING,
                result=None,
            )
        
        # Check for cycles
        if self._has_cycle(workflow_nodes):
            raise WorkflowCycleError(
                "Workflow contains cycles. "
                "Only DAGs are permitted."
            )
        
        workflow_id = f"workflow_{self._workflow_count}"
        self._workflow_count += 1
        
        workflow = Workflow(
            workflow_id=workflow_id,
            goal_id=goal_id,
            nodes=workflow_nodes,
            created_at=datetime.utcnow(),
            completed_at=None,
        )
        
        self._workflows[workflow_id] = workflow
        self._update_ready_nodes(workflow)
        
        return workflow
    
    def _has_cycle(self, nodes: Dict[str, WorkflowNode]) -> bool:
        """Check if DAG has cycles."""
        visited = set()
        path = set()
        
        def dfs(node_id: str) -> bool:
            if node_id in path:
                return True
            if node_id in visited:
                return False
            
            visited.add(node_id)
            path.add(node_id)
            
            if node_id in nodes:
                for dep in nodes[node_id].dependencies:
                    if dfs(dep):
                        return True
            
            path.remove(node_id)
            return False
        
        for node_id in nodes:
            if dfs(node_id):
                return True
        
        return False
    
    def _update_ready_nodes(self, workflow: Workflow) -> None:
        """Update nodes that are ready to run."""
        for node in workflow.nodes.values():
            if node.state != NodeState.PENDING:
                continue
            
            # Check if all dependencies completed
            deps_complete = all(
                workflow.nodes[dep].state == NodeState.COMPLETED
                for dep in node.dependencies
                if dep in workflow.nodes
            )
            
            if deps_complete:
                node.state = NodeState.READY
    
    def get_ready_nodes(self, workflow_id: str) -> List[WorkflowNode]:
        """Get nodes ready for execution."""
        if workflow_id not in self._workflows:
            return []
        
        return [
            n for n in self._workflows[workflow_id].nodes.values()
            if n.state == NodeState.READY
        ]
    
    def complete_node(
        self,
        workflow_id: str,
        node_id: str,
        result: str,
        success: bool = True,
    ) -> None:
        """Mark node complete."""
        if workflow_id not in self._workflows:
            return
        
        workflow = self._workflows[workflow_id]
        if node_id not in workflow.nodes:
            return
        
        node = workflow.nodes[node_id]
        node.state = NodeState.COMPLETED if success else NodeState.FAILED
        node.result = result
        
        self._update_ready_nodes(workflow)
        
        # Check if workflow complete
        if all(n.state in (NodeState.COMPLETED, NodeState.SKIPPED) 
               for n in workflow.nodes.values()):
            workflow.completed_at = datetime.utcnow()
    
    def create_orphan(self, *args, **kwargs) -> None:
        """FORBIDDEN: Create orphan workflow."""
        raise OrphanWorkflowError(
            "Orphan workflows are forbidden. "
            "All workflows must serve a goal."
        )
    
    @property
    def active_count(self) -> int:
        """Active workflows."""
        return sum(1 for w in self._workflows.values() if w.completed_at is None)
