"""
Phase D Determinism Tests

Verifies cognition is deterministic and reproducible.

COGNITIVE MODULE - No imports from execution/agents/kernel/governance.
"""

import pytest
from datetime import datetime, timezone


class TestCognitionDeterminism:
    """Verify cognition produces deterministic outputs."""
    
    def test_same_input_same_output(self):
        """Same input must produce same reasoning output."""
        from cognitive.substrate.cognition_core import CognitionCore, CognitionInput
        
        core = CognitionCore()
        
        input1 = CognitionInput(
            input_id="test_input",
            content={"data": "test"},
            input_type="test",
            timestamp=datetime(2024, 1, 1, tzinfo=timezone.utc),
            provenance="test",
        )
        
        # Same input
        input2 = CognitionInput(
            input_id="test_input",
            content={"data": "test"},
            input_type="test",
            timestamp=datetime(2024, 1, 1, tzinfo=timezone.utc),
            provenance="test",
        )
        
        output1 = core.process(input1)
        output2 = core.process(input2)
        
        # Same result
        assert output1.result == output2.result
        # Same output ID (deterministic)
        assert output1.output_id == output2.output_id
    
    def test_router_determinism(self):
        """Router produces same routing for same input."""
        from cognitive.substrate.reasoning_router import ReasoningRouter
        
        router = ReasoningRouter()
        
        decision1 = router.route("logic:check validity")
        decision2 = router.route("logic:check validity")
        
        assert decision1.reasoning_type == decision2.reasoning_type
        assert decision1.rule_applied == decision2.rule_applied


class TestInferencePrimitiveDeterminism:
    """Verify inference primitives are deterministic."""
    
    def test_deduction_determinism(self):
        """Deduction produces same conclusions."""
        from cognitive.substrate.inference_primitives import Deduction
        
        deduction = Deduction()
        
        premises = ["A", "B"]
        rules = [("A", "C"), ("B", "D")]
        
        result1 = deduction.apply(premises, rules)
        result2 = deduction.apply(premises, rules)
        
        assert set(result1.value) == set(result2.value)
    
    def test_comparison_determinism(self):
        """Comparison produces same results."""
        from cognitive.substrate.inference_primitives import Comparison
        
        comparison = Comparison()
        
        result1 = comparison.apply(item_a=10, item_b=20)
        result2 = comparison.apply(item_a=10, item_b=20)
        
        assert result1.value == result2.value


class TestPrimitivesPure:
    """Verify primitives have no side effects."""
    
    def test_deduction_no_side_effects(self):
        """Deduction does not modify inputs."""
        from cognitive.substrate.inference_primitives import Deduction
        
        deduction = Deduction()
        
        premises = ["A", "B"]
        rules = [("A", "C")]
        
        original_premises = list(premises)
        original_rules = list(rules)
        
        deduction.apply(premises, rules)
        
        # Inputs unchanged
        assert premises == original_premises
        assert rules == original_rules
    
    def test_primitives_bounded(self):
        """Primitives report bounded execution."""
        from cognitive.substrate.inference_primitives import Deduction
        
        deduction = Deduction()
        
        result = deduction.apply(["A"], [])
        
        assert result.bounded is True


class TestExplanationRequired:
    """Verify all outputs require explanation."""
    
    def test_output_has_explanation(self):
        """Cognition output must have explanation."""
        from cognitive.substrate.cognition_core import CognitionCore, CognitionInput
        
        core = CognitionCore()
        
        input_data = CognitionInput(
            input_id="test",
            content="test",
            input_type="test",
            timestamp=datetime.now(timezone.utc),
            provenance="test",
        )
        
        output = core.process(input_data)
        
        assert output.explanation is not None
        assert len(output.explanation) > 0
        assert len(output.reasoning_steps) > 0
    
    def test_no_explanation_error(self):
        """Missing explanation raises error."""
        from cognitive.orchestration.explanation_engine import (
            ExplanationEngine,
            MissingExplanationError,
        )
        
        engine = ExplanationEngine()
        engine.begin_explanation()
        
        # Try to finalize without steps
        with pytest.raises(MissingExplanationError):
            engine.finalize(
                summary="test",
                inputs=(),
                constraints=(),
                confidence=(0.0, 1.0),
            )


class TestOutputImmutability:
    """Verify outputs are immutable."""
    
    def test_cognition_output_frozen(self):
        """CognitionOutput is frozen."""
        from cognitive.substrate.cognition_core import CognitionCore, CognitionInput
        
        core = CognitionCore()
        
        input_data = CognitionInput(
            input_id="test",
            content="test",
            input_type="test",
            timestamp=datetime.now(timezone.utc),
            provenance="test",
        )
        
        output = core.process(input_data)
        
        with pytest.raises(AttributeError):
            output.result = "modified"
    
    def test_primitive_result_frozen(self):
        """PrimitiveResult is frozen."""
        from cognitive.substrate.inference_primitives import Comparison
        
        comparison = Comparison()
        result = comparison.apply(1, 2)
        
        with pytest.raises(AttributeError):
            result.value = "modified"
