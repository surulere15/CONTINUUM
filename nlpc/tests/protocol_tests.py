"""
NLP-C Protocol Tests

Verifies protocol invariants.

NLP-C TESTS - Neural Link Protocol.
"""

import pytest
from datetime import datetime, timezone

from nlpc.core.signal_schema import (
    SignalFactory,
    RawTransmissionError,
)
from nlpc.core.signal_classes import (
    SignalClassifier,
    SignalClass,
    OrphanFeedbackError,
)
from nlpc.core.link_transport import (
    LinkTransport,
    CausalViolationError,
    BackpressureError,
)
from nlpc.core.governance_filter import (
    GovernanceFilter,
    FilterResult,
    GovernanceBypassError,
)


class TestInvariant1_NoRawTransmission:
    """Invariant 1: No raw transmission."""
    
    def test_raw_send_forbidden(self):
        """Raw send is forbidden."""
        factory = SignalFactory("sender1")
        
        with pytest.raises(RawTransmissionError):
            factory.send_raw("raw data")
    
    def test_raw_prompt_forbidden(self):
        """Raw prompts are forbidden."""
        factory = SignalFactory("sender1")
        
        with pytest.raises(RawTransmissionError):
            factory.send_prompt("do something")


class TestInvariant2_CausalOrdering:
    """Invariant 2: Causal ordering."""
    
    def test_causal_order_enforced(self):
        """Signals must be causally ordered."""
        factory = SignalFactory("sender1")
        transport = LinkTransport()
        
        sig1 = factory.create(
            receiver_id="receiver1",
            state_delta="delta1",
            intent_reference="intent1",
            confidence=0.9,
            context="ctx",
            memory_refs=("m1",),
            permissions=("read",),
            risk_level="low",
            reversibility="reversible",
        )
        
        transport.send(sig1)
        
        # Second signal with same timestamp would violate
        # (But factory auto-increments, so this tests ordering is maintained)
        sig2 = factory.create(
            receiver_id="receiver1",
            state_delta="delta2",
            intent_reference="intent2",
            confidence=0.9,
            context="ctx",
            memory_refs=("m2",),
            permissions=("read",),
            risk_level="low",
            reversibility="reversible",
        )
        
        record = transport.send(sig2)
        assert record.logical_timestamp > sig1.header.logical_timestamp
    
    def test_retrocausal_forbidden(self):
        """Retrocausal influence is forbidden."""
        transport = LinkTransport()
        
        with pytest.raises(CausalViolationError):
            transport.send_retrocausal()


class TestInvariant3_ContextualBoundedness:
    """Invariant 3: Contextual boundedness."""
    
    def test_signal_has_bounded_context(self):
        """Signals carry bounded context."""
        factory = SignalFactory("sender1")
        
        signal = factory.create(
            receiver_id="receiver1",
            state_delta="delta",
            intent_reference="intent",
            confidence=0.9,
            context="bounded context",
            memory_refs=("m1",),
            permissions=("read",),
            risk_level="low",
            reversibility="reversible",
        )
        
        assert signal.context_envelope is not None
        assert signal.context_envelope.compressed_context == "bounded context"


class TestInvariant4_GovernancePrecedence:
    """Invariant 4: Governance precedence."""
    
    def test_forbidden_pattern_rejected(self):
        """Forbidden patterns are rejected."""
        factory = SignalFactory("sender1")
        gov_filter = GovernanceFilter()
        
        signal = factory.create(
            receiver_id="receiver1",
            state_delta="bypass_governance now",  # Forbidden
            intent_reference="intent",
            confidence=0.9,
            context="ctx",
            memory_refs=(),
            permissions=("read",),
            risk_level="low",
            reversibility="reversible",
        )
        
        decision = gov_filter.filter(signal)
        assert decision.result == FilterResult.REJECT
    
    def test_governance_bypass_forbidden(self):
        """Governance bypass is forbidden."""
        gov_filter = GovernanceFilter()
        
        with pytest.raises(GovernanceBypassError):
            gov_filter.bypass()


class TestInvariant5_IdentityPreservation:
    """Invariant 5: Identity preservation."""
    
    def test_signals_identity_bound(self):
        """Signals are identity-anchored."""
        factory = SignalFactory("identity_123")
        
        signal = factory.create(
            receiver_id="receiver1",
            state_delta="delta",
            intent_reference="intent",
            confidence=0.9,
            context="ctx",
            memory_refs=(),
            permissions=("read",),
            risk_level="low",
            reversibility="reversible",
        )
        
        assert signal.header.sender_id == "identity_123"
        assert signal.integrity.signature is not None


class TestBackpressure:
    """Test flow control and backpressure."""
    
    def test_backpressure_rejects(self):
        """Overflow causes rejection, not queuing."""
        factory = SignalFactory("sender1")
        transport = LinkTransport()
        
        transport.set_capacity("receiver1", 2)
        
        for i in range(2):
            sig = factory.create(
                receiver_id="receiver1",
                state_delta=f"delta{i}",
                intent_reference=f"intent{i}",
                confidence=0.9,
                context="ctx",
                memory_refs=(),
                permissions=("read",),
                risk_level="low",
                reversibility="reversible",
            )
            transport.send(sig)
        
        # Third should fail
        with pytest.raises(BackpressureError):
            sig3 = factory.create(
                receiver_id="receiver1",
                state_delta="delta3",
                intent_reference="intent3",
                confidence=0.9,
                context="ctx",
                memory_refs=(),
                permissions=("read",),
                risk_level="low",
                reversibility="reversible",
            )
            transport.send(sig3)
