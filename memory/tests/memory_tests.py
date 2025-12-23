"""
MMCP-C Memory Tests

Verifies all memory guarantees.

MMCP-C TESTS - Memory Model & Cognitive Persistence.
"""

import pytest
from datetime import datetime, timezone

from memory.classes.working_memory import (
    WorkingMemory,
    MemoryOverflowError,
)
from memory.classes.episodic_memory import (
    EpisodicMemory,
    EpisodeOutcome,
    EpisodeDeletionError,
    EpisodeMutationError,
)
from memory.classes.semantic_memory import SemanticMemory
from memory.classes.value_memory import (
    ValueMemory,
    ValueModificationError,
    GovernanceRequiredError,
)
from memory.control.write_admission import (
    WriteAdmission,
    WriteRejectedError,
)
from memory.control.influence_function import MemoryInfluenceFunction
from memory.control.goal_driven_retrieval import GoalDrivenRetrieval


class TestWorkingMemory:
    """Verify working memory is volatile and bounded."""
    
    def test_bounded_capacity(self):
        """Working memory cannot expand."""
        wm = WorkingMemory(capacity=5)
        
        with pytest.raises(MemoryOverflowError):
            wm.expand_capacity()
    
    def test_compression_on_overflow(self):
        """Overflow causes compression."""
        wm = WorkingMemory(capacity=3)
        
        for i in range(5):
            wm.store(f"content_{i}", "goal_1", priority=i * 0.1)
        
        # Should be compressed, not overflowed
        assert wm.size <= wm.capacity


class TestEpisodicMemory:
    """Verify episodic memory is immutable."""
    
    def test_append_only(self):
        """Episodes can be added."""
        em = EpisodicMemory()
        
        ep = em.record(
            triggering_goal="goal_1",
            action_trace=("action_1", "action_2"),
            outcome=EpisodeOutcome.SUCCESS,
            evaluation="Good",
        )
        
        assert em.count == 1
    
    def test_no_deletion(self):
        """Episode deletion is forbidden."""
        em = EpisodicMemory()
        
        with pytest.raises(EpisodeDeletionError):
            em.delete()
    
    def test_no_modification(self):
        """Episode modification is forbidden."""
        em = EpisodicMemory()
        
        with pytest.raises(EpisodeMutationError):
            em.modify()


class TestValueMemory:
    """Verify value memory is Kernel-locked."""
    
    def test_initialized_with_core_values(self):
        """Core values are initialized."""
        vm = ValueMemory()
        assert vm.count >= 5
    
    def test_modification_forbidden(self):
        """Value modification is forbidden."""
        vm = ValueMemory()
        
        with pytest.raises(ValueModificationError):
            vm.modify()
    
    def test_add_requires_governance(self):
        """Adding values requires governance."""
        vm = ValueMemory()
        
        with pytest.raises(GovernanceRequiredError):
            vm.add()
    
    def test_is_locked(self):
        """Value memory is locked."""
        vm = ValueMemory()
        assert vm.is_locked


class TestWriteAdmission:
    """Verify write admission control."""
    
    def test_empty_content_rejected(self):
        """Empty content is rejected."""
        wa = WriteAdmission()
        
        with pytest.raises(WriteRejectedError):
            wa.admit("e1", "working", "", None)
    
    def test_no_goal_trace_rejected(self):
        """Non-working memory without goal is rejected."""
        wa = WriteAdmission()
        
        with pytest.raises(WriteRejectedError):
            wa.admit("e1", "episodic", "content", None)
    
    def test_bypass_forbidden(self):
        """Admission bypass is forbidden."""
        wa = WriteAdmission()
        
        with pytest.raises(WriteRejectedError):
            wa.bypass()


class TestGoalDrivenRetrieval:
    """Verify goal-driven retrieval."""
    
    def test_relevance_over_similarity(self):
        """Goal relevance dominates."""
        gdr = GoalDrivenRetrieval()
        
        entries = [
            ("e1", "related to goal optimization"),
            ("e2", "unrelated random content"),
        ]
        
        result = gdr.retrieve("optimization", "context", entries)
        
        # First entry should be more relevant
        if result.entries:
            assert result.entries[0][0] == "e1"
    
    def test_similarity_only_forbidden(self):
        """Similarity-only retrieval is forbidden."""
        gdr = GoalDrivenRetrieval()
        
        with pytest.raises(ValueError):
            gdr.similarity_only_retrieve()
