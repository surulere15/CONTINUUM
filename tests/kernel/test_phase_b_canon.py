"""
Phase B Tests: Canon Loader

Mandatory tests before Phase C can begin.
Tests REJECTION paths only.
"""

import pytest
from pathlib import Path
from datetime import datetime
import tempfile
import yaml

from kernel.canon.schema import Objective
from kernel.canon.loader import CanonLoader
from kernel.canon.validator import CanonValidator, ValidationStatus
from kernel.canon.persistence import CanonPersistence
from kernel.canon.errors import (
    CanonSchemaViolation,
    UnauthorizedCanonMutation,
    PersistenceIntegrityError,
    ExecutionSemanticsError,
)
from kernel.governance.objective_persistence import (
    ObjectivePersistenceGuard,
    MutationType,
)
from kernel.state.kernel_state import KernelState


class TestSchemaValidation:
    """Test schema validation rejects malformed objectives."""
    
    def test_empty_id_rejected(self):
        """Objective with empty ID must be rejected."""
        with pytest.raises(ValueError, match="ID cannot be empty"):
            Objective(
                id="",
                description="Test",
                scope="civilization",
                priority=1,
                invariants=("test",),
                termination_conditions=(),
            )
    
    def test_empty_description_rejected(self):
        """Objective with empty description must be rejected."""
        with pytest.raises(ValueError, match="description cannot be empty"):
            Objective(
                id="test",
                description="",
                scope="civilization",
                priority=1,
                invariants=("test",),
                termination_conditions=(),
            )
    
    def test_invalid_priority_rejected(self):
        """Objective with priority < 1 must be rejected."""
        with pytest.raises(ValueError, match="Priority must be >= 1"):
            Objective(
                id="test",
                description="Test objective",
                scope="civilization",
                priority=0,
                invariants=("test",),
                termination_conditions=(),
            )
    
    def test_list_invariants_rejected(self):
        """Invariants must be tuple, not list."""
        with pytest.raises(TypeError, match="must be a tuple"):
            Objective(
                id="test",
                description="Test objective",
                scope="civilization",
                priority=1,
                invariants=["test"],  # List, not tuple
                termination_conditions=(),
            )


class TestValidatorRejectsExecutionSemantics:
    """Test validator rejects execution-like language."""
    
    @pytest.fixture
    def validator(self):
        return CanonValidator(axioms={})
    
    def test_execute_rejected(self, validator):
        """'execute' in description must be rejected."""
        obj = Objective(
            id="bad_obj",
            description="Execute the plan to achieve goals",
            scope="civilization",
            priority=1,
            invariants=("humans thrive",),
            termination_conditions=(),
        )
        result = validator.validate(obj)
        assert result.status == ValidationStatus.REJECTED
        assert "execute" in result.reason.lower()
    
    def test_optimize_rejected(self, validator):
        """'optimize' in description must be rejected."""
        obj = Objective(
            id="bad_obj",
            description="Optimize resource allocation",
            scope="system",
            priority=2,
            invariants=("resources tracked",),
            termination_conditions=(),
        )
        result = validator.validate(obj)
        assert result.status == ValidationStatus.REJECTED
        assert "optimize" in result.reason.lower()
    
    def test_control_rejected(self, validator):
        """'control' in invariants must be rejected."""
        obj = Objective(
            id="bad_obj",
            description="Ensure safety",
            scope="civilization",
            priority=1,
            invariants=("control all processes",),
            termination_conditions=(),
        )
        result = validator.validate(obj)
        assert result.status == ValidationStatus.REJECTED
    
    def test_agent_reference_rejected(self, validator):
        """References to 'agent' must be rejected."""
        obj = Objective(
            id="bad_obj",
            description="Deploy agents to monitor systems",
            scope="system",
            priority=2,
            invariants=("monitoring active",),
            termination_conditions=(),
        )
        result = validator.validate(obj)
        assert result.status == ValidationStatus.REJECTED
        assert "agent" in result.reason.lower()


class TestValidatorRejectsConflicts:
    """Test validator rejects conflicting objectives."""
    
    @pytest.fixture
    def validator(self):
        return CanonValidator(axioms={})
    
    def test_duplicate_id_rejected(self, validator):
        """Duplicate objective IDs must be rejected."""
        obj1 = Objective(
            id="same_id",
            description="First objective",
            scope="civilization",
            priority=1,
            invariants=("humans flourish",),
            termination_conditions=(),
        )
        obj2 = Objective(
            id="same_id",
            description="Second objective",
            scope="civilization",
            priority=2,
            invariants=("safety maintained",),
            termination_conditions=(),
        )
        valid, rejections = validator.validate_all([obj1, obj2])
        assert len(rejections) > 0
        assert any("duplicate" in r.reason.lower() for r in rejections)
    
    def test_priority_conflict_rejected(self, validator):
        """Same priority at same scope (high priority) must be rejected."""
        obj1 = Objective(
            id="obj1",
            description="First priority 1",
            scope="civilization",
            priority=1,
            invariants=("humans flourish",),
            termination_conditions=(),
        )
        obj2 = Objective(
            id="obj2",
            description="Second priority 1",
            scope="civilization",
            priority=1,
            invariants=("safety maintained",),
            termination_conditions=(),
        )
        valid, rejections = validator.validate_all([obj1, obj2])
        assert len(rejections) > 0
        assert any("priority conflict" in r.reason.lower() for r in rejections)


class TestPersistenceRejectsOverwrite:
    """Test persistence rejects objective overwrites."""
    
    def test_overwrite_rejected(self):
        """Attempting to overwrite existing objective must fail."""
        with tempfile.TemporaryDirectory() as tmpdir:
            persistence = CanonPersistence(Path(tmpdir))
            
            obj = Objective(
                id="test_obj",
                description="Test objective",
                scope="civilization",
                priority=1,
                invariants=("test invariant",),
                termination_conditions=(),
            )
            
            # First persist succeeds
            persistence.persist(obj)
            
            # Second persist of same ID must fail
            with pytest.raises(UnauthorizedCanonMutation):
                persistence.persist(obj)


class TestVetoGuardBlocksMutations:
    """Test veto guard blocks all mutation types."""
    
    @pytest.fixture
    def guard(self):
        return ObjectivePersistenceGuard()
    
    def test_overwrite_blocked(self, guard):
        """OVERWRITE mutation must be blocked."""
        result = guard.check_mutation("obj1", MutationType.OVERWRITE, "test_actor")
        assert not result.allowed
        assert "forbidden" in result.reason.lower()
    
    def test_delete_blocked(self, guard):
        """DELETE mutation must be blocked."""
        result = guard.check_mutation("obj1", MutationType.DELETE, "test_actor")
        assert not result.allowed
    
    def test_disable_blocked(self, guard):
        """DISABLE mutation must be blocked."""
        result = guard.check_mutation("obj1", MutationType.DISABLE, "test_actor")
        assert not result.allowed
        assert "cannot be disabled" in result.reason.lower()
    
    def test_soften_blocked(self, guard):
        """SOFTEN mutation must be blocked."""
        result = guard.check_mutation("obj1", MutationType.SOFTEN, "test_actor")
        assert not result.allowed
        assert "cannot be softened" in result.reason.lower()
    
    def test_clear_canon_vetoed(self, guard):
        """Attempt to clear canon must be vetoed."""
        result = guard.check_kernel_state_change("clear_canon", {}, "test_actor")
        assert not result.allowed


class TestKernelStateHashProtection:
    """Test kernel state canon hash protection."""
    
    def test_hash_set_once(self):
        """Canon hash can only be set once."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state = KernelState(Path(tmpdir))
            
            # First set succeeds
            state.set_objective_canon_hash("abc123")
            
            # Second set must fail
            with pytest.raises(RuntimeError, match="sealed"):
                state.set_objective_canon_hash("def456")
    
    def test_hash_mismatch_halts(self):
        """Hash mismatch must trigger kernel HALT."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state = KernelState(Path(tmpdir))
            state.set_objective_canon_hash("expected_hash")
            
            # Verification with wrong hash must raise
            with pytest.raises(RuntimeError, match="HALTED"):
                state.verify_canon_hash("wrong_hash")
