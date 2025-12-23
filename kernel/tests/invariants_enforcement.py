"""
Phase E Invariants Enforcement Tests

Proves Canon supremacy and stabilization guards work.

KERNEL MODULE TESTS - No imports from execution/agents/learning.
"""

import pytest
from datetime import datetime, timezone

from kernel.governance.intent_schema import Intent, IntentSource
from kernel.governance.intent_normalizer import (
    IntentNormalizer,
    AmbiguousIntentError,
    UnderspecifiedIntentError,
)
from kernel.governance.stabilization_guard import (
    StabilizationGuard,
    StabilizationViolation,
)
from kernel.state.intent_buffer import (
    IntentBuffer,
    IntentModificationError,
    IntentExpiredError,
)


class TestCanonSupremacy:
    """Test Canon objectives cannot be overridden."""
    
    def test_human_cannot_override_canon(self):
        """Human intent cannot override Canon objectives."""
        from kernel.governance.conflict_detector import ConflictDetector, ConflictType
        
        invariants = {"safety": "system safety must be maintained"}
        detector = ConflictDetector(canon_invariants=invariants)
        
        human_intent = Intent(
            intent_id="human",
            source=IntentSource.HUMAN,
            description="Do not maintain system safety",
            scope="system",
            references=(),
            constraints=(),
            created_at=datetime.now(timezone.utc),
        )
        
        graph = detector.detect([human_intent])
        
        assert graph.has_conflicts
        violations = [c for c in graph.conflicts if c.conflict_type == ConflictType.CANON_VIOLATION]
        assert len(violations) > 0


class TestNormalizationRejection:
    """Test underspecified/ambiguous intents are rejected."""
    
    def test_ambiguous_rejected(self):
        """Ambiguous language must be rejected."""
        normalizer = IntentNormalizer()
        
        result = normalizer.normalize(
            raw_description="Maybe do something probably",
            source=IntentSource.HUMAN,
            scope="system",
        )
        
        assert not result.success
        assert "ambiguous" in result.error.lower()
    
    def test_underspecified_rejected(self):
        """Underspecified intent must be rejected."""
        normalizer = IntentNormalizer()
        
        result = normalizer.normalize(
            raw_description="Do X",  # Too short
            source=IntentSource.HUMAN,
            scope="system",
        )
        
        assert not result.success
        assert "short" in result.error.lower() or "underspecified" in result.error.lower()
    
    def test_missing_scope_rejected(self):
        """Missing scope must be rejected."""
        normalizer = IntentNormalizer()
        
        result = normalizer.normalize(
            raw_description="Perform a specific well-defined action",
            source=IntentSource.HUMAN,
            scope=None,  # Missing scope
        )
        
        assert not result.success
        assert "scope" in result.error.lower()


class TestStabilizationGuards:
    """Test stabilization guards prevent erosion."""
    
    def test_reintroduction_blocked(self):
        """Rejected intents cannot be reintroduced."""
        guard = StabilizationGuard()
        
        # Record rejection
        guard.record_rejection("rejected_intent")
        
        # Attempt reintroduction
        with pytest.raises(StabilizationViolation, match="reintroduced"):
            guard.check_reintroduction("rejected_intent")
    
    def test_circular_dependency_blocked(self):
        """Circular dependencies must be detected."""
        guard = StabilizationGuard()
        
        # Create path with cycle
        circular_path = ["a", "b", "c", "a"]
        
        with pytest.raises(StabilizationViolation, match="[Cc]ircular"):
            guard.check_circular_dependency(circular_path)
    
    def test_progressive_drift_blocked(self):
        """Excessive normalization must be blocked."""
        guard = StabilizationGuard()
        
        with pytest.raises(StabilizationViolation, match="drift"):
            guard.check_progressive_drift("intent_id", normalization_count=10)


class TestIntentBufferIntegrity:
    """Test intent buffer maintains integrity."""
    
    def test_modification_forbidden(self):
        """Buffer modification must be blocked."""
        buffer = IntentBuffer()
        
        with pytest.raises(IntentModificationError):
            buffer.modify()
    
    def test_hash_verified(self):
        """Buffer verifies content hash on retrieval."""
        buffer = IntentBuffer()
        
        intent_id = "test"
        content = {"data": "test"}
        buffer.add(intent_id, content, "test")
        
        # Retrieval should verify hash
        retrieved = buffer.get(intent_id)
        assert retrieved == content
    
    def test_read_only_outside_phase(self):
        """Buffer is read-only (no modification method)."""
        buffer = IntentBuffer()
        
        buffer.add("test", {"data": "test"}, "test")
        
        # No way to modify
        assert not hasattr(buffer, 'update')
        assert not hasattr(buffer, 'set')


class TestNoExecution:
    """Test that Phase E cannot execute."""
    
    def test_no_execute_method_on_intent(self):
        """Intent has no execute method."""
        intent = Intent(
            intent_id="test",
            source=IntentSource.HUMAN,
            description="Test intent with sufficient description",
            scope="system",
            references=(),
            constraints=(),
            created_at=datetime.now(timezone.utc),
        )
        
        assert not hasattr(intent, 'execute')
        assert not hasattr(intent, 'run')
        assert not hasattr(intent, 'perform')
    
    def test_no_action_field(self):
        """Intent has no action-related fields."""
        intent = Intent(
            intent_id="test",
            source=IntentSource.HUMAN,
            description="Test intent with sufficient description",
            scope="system",
            references=(),
            constraints=(),
            created_at=datetime.now(timezone.utc),
        )
        
        # Check frozen dataclass fields
        field_names = {f.name for f in intent.__dataclass_fields__.values()}
        
        forbidden_fields = {"action", "tool", "command", "reward", "utility"}
        assert field_names.isdisjoint(forbidden_fields)
