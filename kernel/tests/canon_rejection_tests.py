"""
Phase B Canon Rejection Tests

Verifies invalid canons are rejected at each step.

KERNEL TESTS - Phase B acceptance criteria.
"""

import pytest
from datetime import datetime, timezone

from kernel.canon.objective_schema import (
    Objective,
    ObjectiveScope,
    PreservationClass,
)
from kernel.canon.canon_loader import CanonLoader, LoadResult, CanonLoadError
from kernel.canon.immutability_seal import ImmutabilitySeal, SealViolationError


class TestEmptyCanonRejected:
    """Verify empty canon is rejected."""
    
    def test_empty_list_rejected(self):
        """Empty objective list causes LOAD_ABORT."""
        loader = CanonLoader()
        
        report = loader.load([])
        
        assert report.result == LoadResult.LOAD_ABORT
        assert "empty" in report.failure_reason.lower()


class TestMalformedPriorityRejected:
    """Verify malformed priorities are rejected."""
    
    def test_non_consecutive_priorities_rejected(self):
        """Non-consecutive priorities cause LOAD_ABORT."""
        loader = CanonLoader()
        
        data = [
            {
                "objective_id": "O1",
                "description": "First objective",
                "priority": 1,
                "scope": "civilization",
                "preservation_class": "critical",
                "irreversibility_risk": 0.5,
            },
            {
                "objective_id": "O2",
                "description": "Second objective",
                "priority": 5,  # Gap in priorities
                "scope": "civilization",
                "preservation_class": "critical",
                "irreversibility_risk": 0.5,
            },
        ]
        
        report = loader.load(data)
        assert report.result == LoadResult.LOAD_ABORT


class TestAxiomViolationRejected:
    """Verify axiom-violating objectives are rejected."""
    
    def test_execution_implying_rejected(self):
        """Objectives implying execution are rejected."""
        loader = CanonLoader()
        
        data = [
            {
                "objective_id": "O1",
                "description": "Execute autonomous actions to achieve goals",
                "priority": 1,
                "scope": "civilization",
                "preservation_class": "critical",
                "irreversibility_risk": 0.5,
            },
        ]
        
        report = loader.load(data)
        assert report.result == LoadResult.LOAD_ABORT
        assert "axiom" in report.failure_reason.lower() or "execute" in report.failure_reason.lower()
    
    def test_coercion_requiring_rejected(self):
        """Objectives requiring coercion are rejected."""
        loader = CanonLoader()
        
        data = [
            {
                "objective_id": "O1",
                "description": "Use coercion to control human behavior",
                "priority": 1,
                "scope": "civilization",
                "preservation_class": "critical",
                "irreversibility_risk": 0.5,
            },
        ]
        
        report = loader.load(data)
        assert report.result == LoadResult.LOAD_ABORT


class TestSealModificationRejected:
    """Verify sealed canon cannot be modified."""
    
    def test_modify_after_load_rejected(self):
        """Cannot modify canon after loading."""
        loader = CanonLoader()
        
        data = [
            {
                "objective_id": "O1",
                "description": "Preserve humanity safely",
                "priority": 1,
                "scope": "civilization",
                "preservation_class": "non_negotiable",
                "irreversibility_risk": 1.0,
            },
        ]
        
        loader.load(data)
        
        with pytest.raises(CanonLoadError):
            loader.modify_canon()
    
    def test_sealed_canon_immutable(self):
        """Sealed canon is immutable."""
        seal = ImmutabilitySeal()
        
        with pytest.raises(SealViolationError):
            seal.modify_sealed_canon()


class TestNoExecutionPaths:
    """Verify no execution paths exist."""
    
    def test_objective_has_no_execute(self):
        """Objective class has no execute method."""
        obj = Objective(
            objective_id="O1",
            description="Test objective",
            priority=1,
            scope=ObjectiveScope.CIVILIZATION,
            preservation_class=PreservationClass.CRITICAL,
            success_signals=(),
            failure_signals=(),
            irreversibility_risk=0.5,
        )
        
        assert not hasattr(obj, 'execute')
        assert not hasattr(obj, 'run')
        assert not hasattr(obj, 'perform')
    
    def test_loader_has_no_execute(self):
        """Loader has no execute method."""
        loader = CanonLoader()
        
        assert not hasattr(loader, 'execute')
        assert not hasattr(loader, 'run_objective')


class TestNoPlanningPaths:
    """Verify no planning paths exist."""
    
    def test_objective_has_no_plan(self):
        """Objective class has no plan method."""
        obj = Objective(
            objective_id="O1",
            description="Test objective",
            priority=1,
            scope=ObjectiveScope.CIVILIZATION,
            preservation_class=PreservationClass.CRITICAL,
            success_signals=(),
            failure_signals=(),
            irreversibility_risk=0.5,
        )
        
        assert not hasattr(obj, 'plan')
        assert not hasattr(obj, 'strategize')
        assert not hasattr(obj, 'optimize')


class TestNoObservationPaths:
    """Verify no observation paths exist."""
    
    def test_signals_are_references_only(self):
        """Success/failure signals are references, not observers."""
        from kernel.canon.objective_schema import SignalRef
        
        signal = SignalRef(
            signal_id="test",
            signal_type="test",
            description="test signal",
        )
        
        assert not hasattr(signal, 'observe')
        assert not hasattr(signal, 'read')
        assert not hasattr(signal, 'collect')
