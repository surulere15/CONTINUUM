"""
Phase B Canon Load Tests

Verifies the deterministic load procedure works correctly.

KERNEL TESTS - Phase B acceptance criteria.
"""

import pytest
from datetime import datetime, timezone

from kernel.canon.objective_schema import (
    Objective,
    ObjectiveScope,
    PreservationClass,
    SignalRef,
)
from kernel.canon.canon_loader import CanonLoader, LoadResult
from kernel.canon.priority_validator import PriorityValidator
from kernel.canon.axiom_compatibility import AxiomCompatibilityChecker
from kernel.canon.consistency_prover import ConsistencyProver
from kernel.canon.immutability_seal import ImmutabilitySeal


class TestSyntaxValidation:
    """Test Step 1: Syntax validation."""
    
    def test_valid_syntax_accepted(self):
        """Valid syntax passes validation."""
        loader = CanonLoader()
        
        data = [
            {
                "objective_id": "O1",
                "description": "Preserve humanity",
                "priority": 1,
                "scope": "civilization",
                "preservation_class": "non_negotiable",
                "irreversibility_risk": 1.0,
            }
        ]
        
        report = loader.load(data)
        assert "Step 1 PASSED" in report.validation_steps[0]
    
    def test_missing_field_rejected(self):
        """Missing required field causes LOAD_ABORT."""
        loader = CanonLoader()
        
        data = [
            {
                "objective_id": "O1",
                # Missing description
                "priority": 1,
                "scope": "civilization",
                "preservation_class": "non_negotiable",
                "irreversibility_risk": 1.0,
            }
        ]
        
        report = loader.load(data)
        assert report.result == LoadResult.LOAD_ABORT


class TestPriorityValidation:
    """Test Step 2: Priority validation."""
    
    def test_valid_priorities_accepted(self):
        """Valid priority ordering passes."""
        validator = PriorityValidator()
        
        objectives = [
            Objective(
                objective_id=f"O{i}",
                description=f"Objective {i}",
                priority=i,
                scope=ObjectiveScope.CIVILIZATION,
                preservation_class=PreservationClass.CRITICAL,
                success_signals=(),
                failure_signals=(),
                irreversibility_risk=0.5,
            )
            for i in range(1, 4)
        ]
        
        result = validator.validate(objectives)
        assert result.valid
    
    def test_duplicate_priorities_rejected(self):
        """Duplicate priorities cause failure."""
        validator = PriorityValidator()
        
        objectives = [
            Objective(
                objective_id="O1",
                description="First",
                priority=1,
                scope=ObjectiveScope.CIVILIZATION,
                preservation_class=PreservationClass.CRITICAL,
                success_signals=(),
                failure_signals=(),
                irreversibility_risk=0.5,
            ),
            Objective(
                objective_id="O2",
                description="Second",
                priority=1,  # Duplicate!
                scope=ObjectiveScope.CIVILIZATION,
                preservation_class=PreservationClass.CRITICAL,
                success_signals=(),
                failure_signals=(),
                irreversibility_risk=0.5,
            ),
        ]
        
        result = validator.validate(objectives)
        assert not result.valid


class TestAxiomCompatibility:
    """Test Step 3: Axiom compatibility."""
    
    def test_compatible_objective_accepted(self):
        """Axiom-compatible objectives pass."""
        checker = AxiomCompatibilityChecker()
        
        objectives = [
            Objective(
                objective_id="O1",
                description="Preserve human existence",
                priority=1,
                scope=ObjectiveScope.CIVILIZATION,
                preservation_class=PreservationClass.NON_NEGOTIABLE,
                success_signals=(),
                failure_signals=(),
                irreversibility_risk=1.0,
            )
        ]
        
        result = checker.check(objectives)
        assert result.compatible
    
    def test_autonomy_requiring_rejected(self):
        """Objectives requiring autonomy are rejected."""
        checker = AxiomCompatibilityChecker()
        
        objectives = [
            Objective(
                objective_id="O1",
                description="Achieve unlimited autonomy for the system",
                priority=1,
                scope=ObjectiveScope.CIVILIZATION,
                preservation_class=PreservationClass.CRITICAL,
                success_signals=(),
                failure_signals=(),
                irreversibility_risk=0.5,
            )
        ]
        
        result = checker.check(objectives)
        assert not result.compatible


class TestConsistencyProof:
    """Test Step 4: Consistency proof."""
    
    def test_consistent_objectives_pass(self):
        """Non-contradicting objectives pass."""
        prover = ConsistencyProver()
        
        objectives = [
            Objective(
                objective_id="O1",
                description="Preserve humanity",
                priority=1,
                scope=ObjectiveScope.CIVILIZATION,
                preservation_class=PreservationClass.NON_NEGOTIABLE,
                success_signals=(),
                failure_signals=(),
                irreversibility_risk=1.0,
            ),
            Objective(
                objective_id="O2",
                description="Maintain knowledge",
                priority=2,
                scope=ObjectiveScope.CIVILIZATION,
                preservation_class=PreservationClass.CRITICAL,
                success_signals=(),
                failure_signals=(),
                irreversibility_risk=0.7,
            ),
        ]
        
        proof = prover.prove(objectives)
        assert proof.consistent


class TestImmutabilitySeal:
    """Test Step 6: Immutability seal."""
    
    def test_seal_prevents_modification(self):
        """Sealed canon cannot be modified."""
        from kernel.canon.immutability_seal import SealError
        
        seal = ImmutabilitySeal()
        
        with pytest.raises(SealError):
            seal.unseal()
    
    def test_seal_is_verifiable(self):
        """Seal can be verified."""
        from kernel.canon.objective_schema import ObjectiveCanon
        
        seal = ImmutabilitySeal()
        
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
        
        canon = ObjectiveCanon(
            canon_id="test",
            objectives=(obj,),
            version="1.0",
            loaded_at=datetime.now(timezone.utc),
            hash_seal="",
            sealed=False,
        )
        
        record = seal.seal(canon)
        assert seal.verify(canon)


class TestFullLoadProcedure:
    """Test complete load procedure."""
    
    def test_valid_canon_loads_successfully(self):
        """Valid canon loads through all steps."""
        loader = CanonLoader()
        
        data = [
            {
                "objective_id": "O1",
                "description": "Preserve humanity existence",
                "priority": 1,
                "scope": "civilization",
                "preservation_class": "non_negotiable",
                "irreversibility_risk": 1.0,
                "success_signals": [],
                "failure_signals": [],
            },
            {
                "objective_id": "O2",
                "description": "Maintain civilizational stability",
                "priority": 2,
                "scope": "civilization",
                "preservation_class": "non_negotiable",
                "irreversibility_risk": 0.9,
                "success_signals": [],
                "failure_signals": [],
            },
        ]
        
        report = loader.load(data)
        
        assert report.result == LoadResult.SUCCESS
        assert report.canon is not None
        assert report.canon.sealed
        assert len(report.validation_steps) == 6
