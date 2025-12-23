"""
Orchestration Tests

Verifies orchestration guarantees.

ORCHESTRATION TESTS - Phase II.
"""

import pytest
from datetime import datetime, timezone, timedelta

from orchestration.core.task_scheduler import (
    TaskScheduler,
    TaskPriority,
    OrphanTaskError,
)
from orchestration.core.agent_runtime import (
    AgentRuntime,
    AgentLifetimeError,
    AgentAuthorityError,
)
from orchestration.core.workflow_engine import (
    WorkflowEngine,
    OrphanWorkflowError,
    WorkflowCycleError,
)
from orchestration.execution.action_executor import (
    ActionExecutor,
    ExecutionRejectedError,
)
from orchestration.execution.sandbox import (
    ExecutionSandbox,
    SandboxEscapeError,
)
from orchestration.safety.execution_guard import (
    ExecutionGuard,
    ExecutionBlockedError,
    GuardResult,
)


class TestTaskScheduler:
    """Verify goal-driven scheduling."""
    
    def test_orphan_task_rejected(self):
        """Tasks without goals are rejected."""
        scheduler = TaskScheduler()
        
        with pytest.raises(OrphanTaskError):
            scheduler.schedule_orphan()
    
    def test_goal_required(self):
        """Tasks require goals."""
        scheduler = TaskScheduler()
        
        with pytest.raises(OrphanTaskError):
            scheduler.schedule("", "test_action")
    
    def test_task_scheduled(self):
        """Tasks can be scheduled for goals."""
        scheduler = TaskScheduler()
        
        task = scheduler.schedule("goal_1", "test_action")
        assert task.goal_id == "goal_1"


class TestAgentRuntime:
    """Verify agent lifecycle."""
    
    def test_lifetime_cannot_extend(self):
        """Agent lifetime cannot be extended."""
        runtime = AgentRuntime()
        
        with pytest.raises(AgentLifetimeError):
            runtime.extend_lifetime()
    
    def test_self_spawn_forbidden(self):
        """Agents cannot spawn other agents."""
        runtime = AgentRuntime()
        
        with pytest.raises(AgentAuthorityError):
            runtime.self_spawn()
    
    def test_agent_spawned(self):
        """Agents can be spawned with parent."""
        runtime = AgentRuntime()
        
        agent = runtime.spawn("KERNEL", "goal_1", ("read",))
        assert agent.parent_id == "KERNEL"


class TestWorkflowEngine:
    """Verify workflow execution."""
    
    def test_orphan_workflow_rejected(self):
        """Workflows without goals are rejected."""
        engine = WorkflowEngine()
        
        with pytest.raises(OrphanWorkflowError):
            engine.create_orphan()
    
    def test_cycles_rejected(self):
        """Workflow cycles are rejected."""
        engine = WorkflowEngine()
        
        # A -> B -> A (cycle)
        with pytest.raises(WorkflowCycleError):
            engine.create("goal_1", [
                ("a", "action_a", ("b",)),
                ("b", "action_b", ("a",)),
            ])


class TestExecutionGuard:
    """Verify execution safety."""
    
    def test_blocked_action(self):
        """Blocked actions are rejected."""
        guard = ExecutionGuard()
        
        with pytest.raises(ExecutionBlockedError):
            guard.check("modify_kernel", "goal_1")
    
    def test_bypass_forbidden(self):
        """Guard bypass is forbidden."""
        guard = ExecutionGuard()
        
        with pytest.raises(ExecutionBlockedError):
            guard.bypass()


class TestSandbox:
    """Verify execution isolation."""
    
    def test_escape_forbidden(self):
        """Sandbox escape is forbidden."""
        sandbox = ExecutionSandbox()
        
        with pytest.raises(SandboxEscapeError):
            sandbox.escape_sandbox()
    
    def test_limits_mandatory(self):
        """Sandbox limits cannot be removed."""
        sandbox = ExecutionSandbox()
        
        with pytest.raises(SandboxEscapeError):
            sandbox.remove_limits()
