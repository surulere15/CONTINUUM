"""
EFAP-C Physics Tests

Verifies all 5 execution laws.

EFAP-C TESTS - Execution Fabric & Agent Physics.
"""

import pytest
from datetime import datetime

from efap.primitives.work_unit import (
    WorkUnitFactory,
    ActionType,
    Reversibility,
    FreeWorkError,
    UndeclaredEffectError,
)
from efap.primitives.agent import (
    AgentPool,
    AgentMemoryError,
    AgentGoalError,
    AgentSpawnError,
)
from efap.physics.agent_laws import (
    AgentLaws,
    Law1Violation,
    Law2Violation,
    Law3Violation,
    Law4Violation,
    Law5Violation,
)
from efap.lifecycle.execution_lifecycle import (
    ExecutionLifecycle,
    LifecycleSkipError,
)
from efap.lifecycle.outcome_validator import (
    OutcomeValidator,
    NonDeterministicError,
)


class TestLaw1NoFreeWork:
    """Law 1: ∀W, ∃G: W ≺ G"""
    
    def test_work_requires_goal(self):
        """Work without goal is rejected."""
        factory = WorkUnitFactory()
        
        with pytest.raises(FreeWorkError):
            factory.create(
                parent_goal="",  # No goal
                action_type=ActionType.READ,
                input_state="state",
                expected_effect="effect",
                reversibility=Reversibility.FULLY_REVERSIBLE,
            )
    
    def test_law_check_fails_without_goal(self):
        """Law 1 check fails without goal."""
        with pytest.raises(Law1Violation):
            AgentLaws.check_law_1("work_1", None)


class TestLaw2DeclaredEffects:
    """Law 2: No side effects without declaration."""
    
    def test_effects_must_be_declared(self):
        """Non-read actions require declared effects."""
        factory = WorkUnitFactory()
        
        with pytest.raises(UndeclaredEffectError):
            factory.create(
                parent_goal="goal_1",
                action_type=ActionType.WRITE,  # Has effect
                input_state="state",
                expected_effect="effect",
                reversibility=Reversibility.FULLY_REVERSIBLE,
                side_effects=(),  # Not declared
            )


class TestLaw3Determinism:
    """Law 3: Deterministic execution."""
    
    def test_nondeterministic_fails(self):
        """Nondeterministic output is rejected."""
        with pytest.raises(Law3Violation):
            AgentLaws.check_law_3("output_1", "output_2")
    
    def test_deterministic_passes(self):
        """Deterministic output passes."""
        check = AgentLaws.check_law_3("output", "output")
        assert check.passed


class TestLaw4BoundedAutonomy:
    """Law 4: Bounded autonomy."""
    
    def test_no_agent_memory(self):
        """Agents cannot retain memory."""
        pool = AgentPool()
        
        with pytest.raises(AgentMemoryError):
            pool.retain_memory()
    
    def test_no_agent_goals(self):
        """Agents cannot set goals."""
        pool = AgentPool()
        
        with pytest.raises(AgentGoalError):
            pool.set_goal()
    
    def test_no_agent_spawning(self):
        """Agents cannot spawn agents."""
        pool = AgentPool()
        
        with pytest.raises(AgentSpawnError):
            pool.spawn_agent()


class TestLaw5SuperfluidRouting:
    """Law 5: Work flows around failures."""
    
    def test_blocked_system_fails(self):
        """System blocked due to agent is violation."""
        with pytest.raises(Law5Violation):
            AgentLaws.check_law_5(
                work_blocked=True,
                system_blocked=True,
            )
    
    def test_flow_around_failure(self):
        """Work flows around blocked agent."""
        check = AgentLaws.check_law_5(
            work_blocked=True,
            system_blocked=False,
        )
        assert check.passed


class TestExecutionLifecycle:
    """Verify lifecycle enforcement."""
    
    def test_no_stage_skip(self):
        """Lifecycle stages cannot be skipped."""
        lifecycle = ExecutionLifecycle()
        
        with pytest.raises(LifecycleSkipError):
            lifecycle.skip_to()


class TestOutcomeValidation:
    """Verify outcome validation."""
    
    def test_nondeterministic_rejected(self):
        """Nondeterministic outcomes are rejected."""
        validator = OutcomeValidator()
        
        with pytest.raises(NonDeterministicError):
            validator.validate(
                work_id="work_1",
                expected_effect="effect",
                actual_effect="effect",
                is_deterministic=False,
            )
