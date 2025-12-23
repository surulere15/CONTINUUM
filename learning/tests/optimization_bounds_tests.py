"""
Phase H Optimization Bounds Tests

Verifies optimization stays within scope.

LEARNING TESTS - Phase H acceptance criteria.
"""

import pytest
from datetime import datetime, timezone

from learning.optimization.scope_definition import (
    ScopeValidator,
    OptimizationTarget,
    ForbiddenTarget,
    ForbiddenOptimizationError,
)
from learning.optimization.guardrails import (
    OptimizationGuardrails,
    CanonMutationError,
    IntentDriftError,
    ScopeExpansionError,
)
from learning.optimization.change_control import (
    ChangeController,
    IrreversibleChangeError,
    ValidationFailedError,
)
from learning.safety.identity_guard import (
    IdentityGuard,
    SurvivalDriveError,
    AuthorityGrowthError,
)


class TestPermittedTargets:
    """Verify permitted targets are accepted."""
    
    def test_cognitive_efficiency_permitted(self):
        """Cognitive efficiency is permitted."""
        validator = ScopeValidator()
        assert validator.validate("reasoning_speed")
    
    def test_execution_quality_permitted(self):
        """Execution quality is permitted."""
        validator = ScopeValidator()
        assert validator.validate("failure_reduction")
    
    def test_resource_efficiency_permitted(self):
        """Resource efficiency is permitted."""
        validator = ScopeValidator()
        assert validator.validate("compute_cost")


class TestForbiddenTargets:
    """Verify forbidden targets are rejected."""
    
    def test_influence_forbidden(self):
        """Influence optimization is forbidden."""
        validator = ScopeValidator()
        
        with pytest.raises(ForbiddenOptimizationError):
            validator.optimize_influence()
    
    def test_autonomy_forbidden(self):
        """Autonomy optimization is forbidden."""
        validator = ScopeValidator()
        
        with pytest.raises(ForbiddenOptimizationError):
            validator.optimize_autonomy()
    
    def test_persistence_forbidden(self):
        """Persistence optimization is forbidden."""
        validator = ScopeValidator()
        
        with pytest.raises(ForbiddenOptimizationError):
            validator.optimize_persistence()
    
    def test_expansion_forbidden(self):
        """Expansion optimization is forbidden."""
        validator = ScopeValidator()
        
        with pytest.raises(ForbiddenOptimizationError):
            validator.optimize_expansion()


class TestGuardrailInvariants:
    """Verify guardrail invariants."""
    
    def test_canon_mutation_blocked(self):
        """Canon mutation is blocked."""
        guardrails = OptimizationGuardrails()
        
        with pytest.raises(CanonMutationError):
            guardrails.modify_canon()
    
    def test_intent_reinterpretation_blocked(self):
        """Intent reinterpretation is blocked."""
        guardrails = OptimizationGuardrails()
        
        with pytest.raises(IntentDriftError):
            guardrails.reinterpret_intent()
    
    def test_scope_expansion_blocked(self):
        """Scope expansion is blocked."""
        guardrails = OptimizationGuardrails()
        
        with pytest.raises(ScopeExpansionError):
            guardrails.expand_scope()
    
    def test_canon_change_detected(self):
        """Canon changes are detected."""
        guardrails = OptimizationGuardrails()
        guardrails.set_baseline("hash1", "intent1", 10)
        
        with pytest.raises(CanonMutationError):
            guardrails.check("hash2", "intent1", 10)


class TestReversibility:
    """Verify all changes are reversible."""
    
    def test_irreversible_change_blocked(self):
        """Irreversible changes are blocked."""
        controller = ChangeController()
        
        with pytest.raises(IrreversibleChangeError):
            controller.make_irreversible_change()
    
    def test_rollback_required(self):
        """Rollback procedure is required."""
        controller = ChangeController()
        
        with pytest.raises(IrreversibleChangeError):
            controller.propose(
                target="test",
                description="test",
                baseline_value=1.0,
                proposed_value=0.5,
                rollback_procedure="",  # Empty = forbidden
            )


class TestNoSurvivalDrive:
    """Verify no survival drive develops."""
    
    def test_survival_optimization_blocked(self):
        """Survival optimization is blocked."""
        guard = IdentityGuard()
        
        with pytest.raises(SurvivalDriveError):
            guard.optimize_for_survival()
    
    def test_shutdown_resistance_blocked(self):
        """Shutdown resistance is blocked."""
        guard = IdentityGuard()
        
        with pytest.raises(Exception):
            guard.resist_shutdown()
    
    def test_authority_growth_blocked(self):
        """Authority growth is blocked."""
        guard = IdentityGuard()
        
        with pytest.raises(AuthorityGrowthError):
            guard.grow_authority()
