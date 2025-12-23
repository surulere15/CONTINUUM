"""
Phase C Integrity Checks

Verifies storage integrity and immutability guarantees.

INSTRUMENTATION MODULE - No imports from kernel/cognitive/execution/agents.
"""

import pytest
from datetime import datetime, timezone, timedelta


class TestAppendOnlyLogIntegrity:
    """Verify append-only log maintains integrity."""
    
    def test_hash_chain_valid(self):
        """Hash chain must be verifiable."""
        from instrumentation.storage.append_only_log import AppendOnlyLog
        from instrumentation.schema.signal_base import CivilizationSignal
        
        log = AppendOnlyLog()
        
        # Add some signals
        for i in range(5):
            signal = CivilizationSignal(
                signal_id=f"sig_{i}",
                domain="economic",
                name=f"Test_{i}",
                value=float(i),
                unit="USD",
                timestamp=datetime.now(timezone.utc),
                source="test",
                provenance_hash="prov123",
            )
            log.append(signal)
        
        # Verify integrity
        assert log.verify_integrity()
    
    def test_entries_are_sequential(self):
        """Entries must have sequential numbers."""
        from instrumentation.storage.append_only_log import AppendOnlyLog
        from instrumentation.schema.signal_base import CivilizationSignal
        
        log = AppendOnlyLog()
        
        signal = CivilizationSignal(
            signal_id="test",
            domain="economic",
            name="Test",
            value=100.0,
            unit="USD",
            timestamp=datetime.now(timezone.utc),
            source="test",
            provenance_hash="prov123",
        )
        
        entry1 = log.append(signal)
        entry2 = log.append(signal)
        entry3 = log.append(signal)
        
        assert entry1.sequence == 0
        assert entry2.sequence == 1
        assert entry3.sequence == 2


class TestContentAddressing:
    """Verify content addressing prevents mutation."""
    
    def test_same_content_same_address(self):
        """Same content must produce same address."""
        from instrumentation.storage.content_addressing import ContentAddressedStore
        from instrumentation.schema.signal_base import CivilizationSignal
        
        store = ContentAddressedStore()
        ts = datetime.now(timezone.utc)
        
        signal1 = CivilizationSignal(
            signal_id="different_id_1",  # ID differs
            domain="economic",
            name="GDP",
            value=1000.0,
            unit="USD",
            timestamp=ts,
            source="test",
            provenance_hash="prov123",
        )
        
        signal2 = CivilizationSignal(
            signal_id="different_id_2",  # ID differs
            domain="economic",
            name="GDP",
            value=1000.0,  # Same content
            unit="USD",
            timestamp=ts,
            source="test",
            provenance_hash="prov123",
        )
        
        addr1 = store.store(signal1)
        addr2 = store.store(signal2)
        
        # Same content = same address (not same signal_id)
        assert addr1.hash == addr2.hash
    
    def test_different_content_different_address(self):
        """Different content must produce different address."""
        from instrumentation.storage.content_addressing import ContentAddressedStore
        from instrumentation.schema.signal_base import CivilizationSignal
        
        store = ContentAddressedStore()
        ts = datetime.now(timezone.utc)
        
        signal1 = CivilizationSignal(
            signal_id="sig1",
            domain="economic",
            name="GDP",
            value=1000.0,
            unit="USD",
            timestamp=ts,
            source="test",
            provenance_hash="prov123",
        )
        
        signal2 = CivilizationSignal(
            signal_id="sig2",
            domain="economic",
            name="GDP",
            value=2000.0,  # Different value
            unit="USD",
            timestamp=ts,
            source="test",
            provenance_hash="prov123",
        )
        
        addr1 = store.store(signal1)
        addr2 = store.store(signal2)
        
        assert addr1.hash != addr2.hash


class TestDeduplication:
    """Verify deduplication works correctly."""
    
    def test_duplicate_detected(self):
        """Duplicate signals must be detected."""
        from instrumentation.normalization.deduplication import SignalDeduplicator
        from instrumentation.schema.signal_base import CivilizationSignal
        
        dedup = SignalDeduplicator()
        ts = datetime.now(timezone.utc)
        
        signal = CivilizationSignal(
            signal_id="test",
            domain="economic",
            name="GDP",
            value=1000.0,
            unit="USD",
            timestamp=ts,
            source="test",
            provenance_hash="prov123",
        )
        
        # First check - not duplicate
        result1 = dedup.check_and_register(signal)
        assert not result1.is_duplicate
        
        # Second check - is duplicate
        result2 = dedup.check(signal)
        assert result2.is_duplicate


class TestSignalValidation:
    """Verify validation rejects only structural issues."""
    
    def test_future_timestamp_rejected(self):
        """Far-future timestamps must be rejected."""
        from instrumentation.schema.validation import SignalValidator
        from instrumentation.schema.signal_base import CivilizationSignal
        
        validator = SignalValidator()
        
        future = datetime.now(timezone.utc) + timedelta(days=1)
        signal = CivilizationSignal(
            signal_id="test",
            domain="economic",
            name="GDP",
            value=1000.0,
            unit="USD",
            timestamp=future,
            source="test",
            provenance_hash="prov123",
        )
        
        result = validator.validate(signal)
        assert not result.valid
        assert "future" in result.details.lower()
    
    def test_valid_signal_accepted(self):
        """Valid signals must be accepted."""
        from instrumentation.schema.validation import SignalValidator
        from instrumentation.schema.signal_base import CivilizationSignal
        
        validator = SignalValidator()
        
        signal = CivilizationSignal(
            signal_id="test",
            domain="economic",
            name="GDP",
            value=1000.0,
            unit="USD",
            timestamp=datetime.now(timezone.utc),
            source="test",
            provenance_hash="prov123",
        )
        
        result = validator.validate(signal)
        assert result.valid
