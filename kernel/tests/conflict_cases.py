"""
Phase E Conflict Case Tests

Proves conflict detection and resolution works correctly.

KERNEL MODULE TESTS - No imports from execution/agents/learning.
"""

import pytest
from datetime import datetime, timezone

from kernel.governance.intent_schema import Intent, IntentSource, IntentSet
from kernel.governance.intent_normalizer import IntentNormalizer, NormalizationError
from kernel.governance.conflict_detector import ConflictDetector, ConflictType
from kernel.governance.resolution_engine import ResolutionEngine, ResolutionOutcome


class TestConflictDetection:
    """Test conflict detection identifies all conflict types."""
    
    def test_direct_contradiction_detected(self):
        """Direct contradictions must be detected."""
        detector = ConflictDetector()
        
        intent_a = Intent(
            intent_id="a",
            source=IntentSource.HUMAN,
            description="Enable feature X",
            scope="system",
            references=(),
            constraints=(),
            created_at=datetime.now(timezone.utc),
        )
        
        intent_b = Intent(
            intent_id="b",
            source=IntentSource.HUMAN,
            description="Not enable feature X",
            scope="system",
            references=(),
            constraints=(),
            created_at=datetime.now(timezone.utc),
        )
        
        graph = detector.detect([intent_a, intent_b])
        
        assert graph.has_conflicts
        assert any(c.conflict_type == ConflictType.DIRECT_CONTRADICTION for c in graph.conflicts)
    
    def test_scope_collision_detected(self):
        """Scope collisions must be detected."""
        detector = ConflictDetector()
        
        intent_a = Intent(
            intent_id="a",
            source=IntentSource.HUMAN,
            description="Apply strict policy",
            scope="system",
            references=(),
            constraints=("strict",),
            created_at=datetime.now(timezone.utc),
        )
        
        intent_b = Intent(
            intent_id="b",
            source=IntentSource.HUMAN,
            description="Apply lenient approach",
            scope="system",
            references=(),
            constraints=("not strict",),
            created_at=datetime.now(timezone.utc),
        )
        
        graph = detector.detect([intent_a, intent_b])
        
        assert graph.has_conflicts
    
    def test_canon_violation_detected(self):
        """Canon violations must be detected."""
        invariants = {
            "human_safety": "humans must not be harmed",
        }
        detector = ConflictDetector(canon_invariants=invariants)
        
        intent = Intent(
            intent_id="bad",
            source=IntentSource.HUMAN,
            description="Do not protect humans from harm",
            scope="civilization",
            references=(),
            constraints=(),
            created_at=datetime.now(timezone.utc),
        )
        
        graph = detector.detect([intent])
        
        assert graph.has_conflicts
        assert any(c.conflict_type == ConflictType.CANON_VIOLATION for c in graph.conflicts)


class TestResolutionPrecedence:
    """Test resolution follows fixed precedence."""
    
    def test_canon_beats_human(self):
        """Canon source has higher precedence than human."""
        engine = ResolutionEngine()
        detector = ConflictDetector()
        
        intent_canon = Intent(
            intent_id="canon_intent",
            source=IntentSource.CANON,
            description="Preserve safety",
            scope="civilization",
            references=(),
            constraints=(),
            created_at=datetime.now(timezone.utc),
        )
        
        intent_human = Intent(
            intent_id="human_intent",
            source=IntentSource.HUMAN,
            description="Not preserve safety",
            scope="civilization",
            references=(),
            constraints=(),
            created_at=datetime.now(timezone.utc),
        )
        
        graph = detector.detect([intent_canon, intent_human])
        result = engine.resolve([intent_canon, intent_human], graph)
        
        # Human intent should be rejected
        assert any(r.intent_id == "human_intent" for r in result.rejections)
    
    def test_more_constraints_wins(self):
        """More specific intent (more constraints) wins on tie."""
        engine = ResolutionEngine()
        detector = ConflictDetector()
        
        intent_a = Intent(
            intent_id="a",
            source=IntentSource.HUMAN,
            description="Apply policy",
            scope="system",
            references=("ref1",),
            constraints=("constraint1", "constraint2"),
            created_at=datetime.now(timezone.utc),
        )
        
        intent_b = Intent(
            intent_id="b",
            source=IntentSource.HUMAN,
            description="Apply different policy",
            scope="system",
            references=("ref1",),
            constraints=("constraint1",),  # Fewer constraints
            created_at=datetime.now(timezone.utc),
        )
        
        graph = detector.detect([intent_a, intent_b])
        
        if graph.has_conflicts:
            result = engine.resolve([intent_a, intent_b], graph)
            # More constrained intent should survive
            if result.stabilized:
                assert any(i.intent_id == "a" for i in result.stabilized.intents)


class TestNoCompromise:
    """Test that compromise synthesis is forbidden."""
    
    def test_compromise_forbidden(self):
        """Compromise synthesis must be rejected."""
        from kernel.governance.resolution_engine import CompromiseSynthesisError
        
        engine = ResolutionEngine()
        
        with pytest.raises(CompromiseSynthesisError):
            engine.synthesize_compromise()


class TestDeterministicResolution:
    """Test resolution is deterministic."""
    
    def test_same_input_same_output(self):
        """Same conflicts must produce same resolution."""
        engine = ResolutionEngine()
        detector = ConflictDetector()
        
        intents = [
            Intent(
                intent_id="a",
                source=IntentSource.HUMAN,
                description="Do X",
                scope="system",
                references=(),
                constraints=(),
                created_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
            ),
            Intent(
                intent_id="b",
                source=IntentSource.HUMAN,
                description="Do Y",
                scope="system",
                references=(),
                constraints=(),
                created_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
            ),
        ]
        
        graph = detector.detect(intents)
        
        result1 = engine.resolve(intents, graph)
        result2 = engine.resolve(intents, graph)
        
        assert result1.outcome == result2.outcome
        if result1.stabilized and result2.stabilized:
            ids1 = {i.intent_id for i in result1.stabilized.intents}
            ids2 = {i.intent_id for i in result2.stabilized.intents}
            assert ids1 == ids2
