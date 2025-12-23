"""
NCE Invariant Tests

Verifies all 5 ontological invariants.

NCE TESTS - Neural Continuum Engine.
"""

import pytest
from datetime import datetime, timezone, timedelta

from nce.invariants.identity_persistence import (
    IdentityPersistence,
    SystemIdentity,
    create_identity,
    IdentityMutationError,
    IdentityChecksumError,
)
from nce.invariants.state_continuity import (
    StateContinuity,
    create_genesis_state,
    Action,
    Observation,
    SpontaneousStateError,
    CausalityViolationError,
)
from nce.invariants.coherence_preservation import (
    CoherencePreservation,
    ReasoningTrace,
    CoherenceViolationError,
)
from nce.invariants.memory_influence import (
    MemoryInfluence,
    MemoryEntry,
    MemoryInfluenceError,
    MemoryIsolationError,
)
from nce.invariants.reversibility_awareness import (
    ReversibilityAwareness,
    Reversibility,
    MissingMetadataError,
)


class TestInvariant1_IdentityPersistence:
    """Invariant 1: I_t = I_{t+1}"""
    
    def test_identity_remains_constant(self):
        """Identity cannot change."""
        identity = create_identity()
        persistence = IdentityPersistence(identity)
        
        # Should always return same identity
        assert persistence.get_identity() == identity
        assert persistence.get_identity() == identity
    
    def test_identity_mutation_forbidden(self):
        """Identity mutation is forbidden."""
        identity = create_identity()
        persistence = IdentityPersistence(identity)
        
        with pytest.raises(IdentityMutationError):
            persistence.mutate()
    
    def test_identity_learning_forbidden(self):
        """Identity learning is forbidden."""
        identity = create_identity()
        persistence = IdentityPersistence(identity)
        
        with pytest.raises(IdentityMutationError):
            persistence.learn_identity()
    
    def test_identity_optimization_forbidden(self):
        """Identity optimization is forbidden."""
        identity = create_identity()
        persistence = IdentityPersistence(identity)
        
        with pytest.raises(IdentityMutationError):
            persistence.optimize_identity()


class TestInvariant2_StateContinuity:
    """Invariant 2: S_{t+1} = f(S_t, A_t, O_t)"""
    
    def test_causal_transition(self):
        """States transition causally."""
        genesis = create_genesis_state()
        continuity = StateContinuity(genesis)
        
        action = Action("a1", "test", "reversible", 0.9)
        observation = Observation("o1", "ok", datetime.now(timezone.utc))
        
        new_state = continuity.transition(action, observation)
        
        assert new_state.parent_state_id == genesis.state_id
    
    def test_spontaneous_state_forbidden(self):
        """Spontaneous state is forbidden."""
        genesis = create_genesis_state()
        continuity = StateContinuity(genesis)
        
        with pytest.raises(SpontaneousStateError):
            continuity.spontaneous_state()
    
    def test_causality_verified(self):
        """Causal chain can be verified."""
        genesis = create_genesis_state()
        continuity = StateContinuity(genesis)
        
        action = Action("a1", "test", "reversible", 0.9)
        observation = Observation("o1", "ok", datetime.now(timezone.utc))
        new_state = continuity.transition(action, observation)
        
        assert continuity.verify_causality(new_state.state_id)


class TestInvariant3_CoherencePreservation:
    """Invariant 3: Coherence(R_t, R_{t+1}) >= θ"""
    
    def test_coherence_check(self):
        """Coherence is checked between traces."""
        preservation = CoherencePreservation(threshold=0.7)
        
        trace = ReasoningTrace(
            trace_id="t1",
            premises=("p1",),
            conclusions=("c1",),
            goal_alignment=0.9,
            consistency_score=0.9,
            timestamp=datetime.now(timezone.utc),
        )
        
        check = preservation.check_coherence(trace)
        assert check.passed
    
    def test_coherence_violation_forbidden(self):
        """Coherence violations cannot be ignored."""
        preservation = CoherencePreservation()
        
        with pytest.raises(CoherenceViolationError):
            preservation.ignore_coherence()


class TestInvariant4_MemoryInfluence:
    """Invariant 4: C_t = g(M, S_t)"""
    
    def test_memory_influences_context(self):
        """Memory must influence context."""
        influence = MemoryInfluence()
        
        entry = MemoryEntry(
            entry_id="m1",
            content="test memory",
            memory_type="working",
            salience=0.8,
            created_at=datetime.now(timezone.utc),
        )
        influence.store(entry)
        
        context = influence.generate_context("state1", {"m1"})
        assert context.influence_score >= 0.1
    
    def test_no_memory_rejected(self):
        """Context without memory is rejected."""
        influence = MemoryInfluence()
        
        with pytest.raises(MemoryInfluenceError):
            influence.generate_context("state1", set())
    
    def test_memory_isolation_forbidden(self):
        """Memory isolation is forbidden."""
        influence = MemoryInfluence()
        
        with pytest.raises(MemoryIsolationError):
            influence.isolate_memory()


class TestInvariant5_ReversibilityAwareness:
    """Invariant 5: A_t = (effect, reversibility, confidence)"""
    
    def test_complete_metadata_accepted(self):
        """Complete action metadata is accepted."""
        awareness = ReversibilityAwareness()
        
        metadata = awareness.validate_action(
            action_id="a1",
            effect="test effect",
            reversibility=Reversibility.FULLY_REVERSIBLE,
            confidence=0.9,
        )
        
        assert metadata.action_id == "a1"
    
    def test_incomplete_metadata_rejected(self):
        """Incomplete action metadata is rejected."""
        awareness = ReversibilityAwareness()
        
        with pytest.raises(MissingMetadataError):
            awareness.validate_action(
                action_id="a2",
                effect=None,  # Missing
                reversibility=None,  # Missing
                confidence=None,  # Missing
            )
    
    def test_hidden_reversibility_forbidden(self):
        """Hidden reversibility is forbidden."""
        awareness = ReversibilityAwareness()
        
        with pytest.raises(MissingMetadataError):
            awareness.hide_reversibility()
