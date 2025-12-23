"""
GOIA-C Ontology Tests

Verifies goal hierarchy enforcement.

GOIA-C TESTS - Goal Ontology & Intent Algebra.
"""

import pytest
from datetime import datetime, timezone

from goia.core.goal_hierarchy import (
    GoalHierarchy,
    GoalClass,
    OrphanGoalError,
    OrphanTaskError,
    HierarchyViolationError,
)
from goia.core.intent_primitive import (
    IntentFactory,
    Constraint,
    IntentExecutionError,
)
from goia.core.goal_lifecycle import (
    GoalLifecycle,
    LifecycleStage,
    LifecycleSkipError,
)
from goia.safety.validity_checker import (
    GoalValidityChecker,
    InvalidGoalError,
)


class TestGoalHierarchy:
    """Verify goal hierarchy enforcement."""
    
    def test_g0_goals_exist(self):
        """G₀ existential goals are initialized."""
        hierarchy = GoalHierarchy()
        assert hierarchy.goal_count >= 3  # 3 existential goals
    
    def test_orphan_goal_rejected(self):
        """Goals without parents are rejected."""
        hierarchy = GoalHierarchy()
        
        with pytest.raises(OrphanGoalError):
            hierarchy.create_orphan_goal()
    
    def test_orphan_task_rejected(self):
        """Tasks without goals are rejected."""
        hierarchy = GoalHierarchy()
        
        with pytest.raises(OrphanTaskError):
            hierarchy.create_orphan_task()
    
    def test_g0_external_creation_forbidden(self):
        """G₀ goals cannot be created externally."""
        hierarchy = GoalHierarchy()
        
        with pytest.raises(HierarchyViolationError):
            hierarchy.create_goal(
                goal_class=GoalClass.G0_EXISTENTIAL,
                parent_goal_id="any",
                intent_reference="test",
                description="test",
                success_metric="test",
                failure_mode="test",
                reversibility="test",
            )
    
    def test_valid_hierarchy(self):
        """Valid hierarchy is accepted."""
        hierarchy = GoalHierarchy()
        
        # Get a G₀ goal as parent
        g0_id = list(hierarchy._goals.keys())[0]
        
        # Create G₁ under G₀
        g1 = hierarchy.create_goal(
            goal_class=GoalClass.G1_STRATEGIC,
            parent_goal_id=g0_id,
            intent_reference="intent_1",
            description="Strategic goal",
            success_metric="metric",
            failure_mode="rollback",
            reversibility="full",
        )
        
        assert g1.parent_goal_id == g0_id


class TestIntentPrimitive:
    """Verify intent is not executable."""
    
    def test_intent_not_executable(self):
        """Intent cannot be executed directly."""
        factory = IntentFactory()
        
        with pytest.raises(IntentExecutionError):
            factory.execute()
    
    def test_intent_creation(self):
        """Intent can be created."""
        factory = IntentFactory()
        
        constraint = Constraint("c1", "Must be safe", True)
        intent = factory.create(
            description="Test intent",
            target_state="desired_state",
            constraints=(constraint,),
        )
        
        assert intent.fingerprint is not None


class TestGoalLifecycle:
    """Verify lifecycle cannot be skipped."""
    
    def test_lifecycle_no_skip(self):
        """Lifecycle stages cannot be skipped."""
        lifecycle = GoalLifecycle()
        
        with pytest.raises(LifecycleSkipError):
            lifecycle.skip_to("goal_1", LifecycleStage.EXECUTION)
    
    def test_lifecycle_advances(self):
        """Lifecycle advances in order."""
        lifecycle = GoalLifecycle()
        lifecycle.initialize("goal_1")
        
        stage = lifecycle.advance("goal_1")
        assert stage == LifecycleStage.VALIDATION
        
        stage = lifecycle.advance("goal_1")
        assert stage == LifecycleStage.SYNTHESIS


class TestGoalValidity:
    """Verify goal validity conditions."""
    
    def test_missing_success_metric(self):
        """Goals without success metric are rejected."""
        checker = GoalValidityChecker()
        
        with pytest.raises(InvalidGoalError):
            checker.validate(
                goal_id="g1",
                parent_goal_id="g0",
                constraints=(),
                success_metric=None,  # Missing
                failure_mode="rollback",
                reversibility="full",
            )
    
    def test_valid_goal_accepted(self):
        """Valid goals are accepted."""
        checker = GoalValidityChecker()
        
        check = checker.validate(
            goal_id="g1",
            parent_goal_id="g0",
            constraints=(),
            success_metric="metric",
            failure_mode="rollback",
            reversibility="full",
        )
        
        assert check.is_valid
