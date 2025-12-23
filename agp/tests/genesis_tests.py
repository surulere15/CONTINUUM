"""
AGP-C Genesis Tests

Verifies controlled morphogenesis.

AGP-C TESTS - Agent Genesis Protocol.
"""

import pytest
from datetime import timedelta

from agp.core.internal_agent import (
    InternalAgentRegistry,
    LifespanType,
    PurposeViolationError,
    LifespanExpiredError,
)
from agp.core.capability_envelope import (
    CapabilityEnvelopeManager,
    EnvelopeViolationError,
)
from agp.core.agent_lineage import (
    LineageTracker,
    LineageDepthError,
)
from agp.genesis.need_detector import (
    NeedDetector,
    NeedNotJustifiedError,
)
from agp.genesis.genesis_pipeline import (
    GenesisPipeline,
    GenesisSkipError,
    GenesisRejectedError,
)
from agp.safety.emergence_ceiling import (
    EmergenceCeiling,
    EmergenceCeilingExceeded,
)
from agp.safety.drift_prevention import (
    DriftPrevention,
    SelfPreservationError,
)
from agp.safety.termination import (
    TerminationManager,
    TerminationReason,
    ResurrectionError,
)


class TestInternalAgent:
    """Verify internal agent constraints."""
    
    def test_purpose_enforcement(self):
        """Actions must align with purpose."""
        registry = InternalAgentRegistry()
        
        agent = registry.register(
            purpose="data analysis",
            scope=("data",),
            constraints=(),
        )
        
        # Unrelated action should fail
        with pytest.raises(PurposeViolationError):
            registry.check_purpose(agent.agent_id, "delete system files")


class TestCapabilityEnvelope:
    """Verify capability boundaries."""
    
    def test_forbidden_action_rejected(self):
        """Forbidden actions are rejected."""
        manager = CapabilityEnvelopeManager()
        
        manager.create(
            agent_id="agent_1",
            allowed_actions=frozenset({"read", "write"}),
        )
        
        with pytest.raises(EnvelopeViolationError):
            manager.check_action("agent_1", "modify_kernel")


class TestAgentLineage:
    """Verify lineage constraints."""
    
    def test_max_depth_enforced(self):
        """Maximum lineage depth is enforced."""
        tracker = LineageTracker()
        
        # Create chain up to max
        tracker.create("agent_1", "KERNEL", "goal_1")
        tracker.create("agent_2", "agent_1", "goal_1")
        tracker.create("agent_3", "agent_2", "goal_1")
        
        # Next should fail (depth 4 > max 3)
        with pytest.raises(LineageDepthError):
            tracker.create("agent_4", "agent_3", "goal_1")


class TestNeedDetector:
    """Verify necessity-based creation."""
    
    def test_curiosity_creation_forbidden(self):
        """Curiosity-based creation is forbidden."""
        detector = NeedDetector()
        
        with pytest.raises(NeedNotJustifiedError):
            detector.curiosity_create()
    
    def test_need_requires_triggers(self):
        """Need assessment requires triggers."""
        detector = NeedDetector()
        
        # All good metrics = no need
        with pytest.raises(NeedNotJustifiedError):
            detector.assess(
                goal_id="goal_1",
                existing_agents=5,
                current_efficiency=0.9,  # High
                pattern_count=1,         # Low
                current_latency=1.0,     # Low
                predicted_utility=0.0,   # Zero
            )


class TestGenesisPipeline:
    """Verify genesis pipeline."""
    
    def test_no_stage_skip(self):
        """Genesis stages cannot be skipped."""
        pipeline = GenesisPipeline()
        
        with pytest.raises(GenesisSkipError):
            pipeline.skip_to()


class TestEmergenceCeiling:
    """Verify emergence ceiling."""
    
    def test_ceiling_enforced(self):
        """Ceiling cannot be exceeded."""
        ceiling = EmergenceCeiling(base_max=2)
        
        ceiling.request_slot()
        ceiling.request_slot()
        
        with pytest.raises(EmergenceCeilingExceeded):
            ceiling.request_slot()


class TestDriftPrevention:
    """Verify drift prevention."""
    
    def test_self_preservation_detected(self):
        """Self-preservation is detected."""
        prevention = DriftPrevention()
        
        with pytest.raises(SelfPreservationError):
            prevention.check_self_preservation(
                agent_id="agent_1",
                resists_termination=True,
                requests_extension=False,
            )


class TestTermination:
    """Verify termination semantics."""
    
    def test_resurrection_forbidden(self):
        """Resurrection is forbidden."""
        manager = TerminationManager()
        
        manager.terminate("agent_1", TerminationReason.GOAL_COMPLETION)
        
        with pytest.raises(ResurrectionError):
            manager.resurrect()
    
    def test_termination_is_final(self):
        """Termination cannot be undone."""
        manager = TerminationManager()
        
        manager.terminate("agent_1", TerminationReason.TIMEOUT)
        
        assert manager.is_terminated("agent_1")
        
        with pytest.raises(ResurrectionError):
            manager.undo_termination()
