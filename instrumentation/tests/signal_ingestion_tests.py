"""
Phase C Signal Ingestion Tests

Verifies signals are read-only and unregistered sources rejected.

INSTRUMENTATION TESTS - Phase C acceptance criteria.
"""

import pytest
from datetime import datetime, timezone

from instrumentation.schema.signal_base import CivilizationSignal
from instrumentation.ingestion.registry import (
    IngestionRegistry,
    RegisteredSource,
    SourceStatus,
    SourceNotRegisteredError,
)
from instrumentation.ingestion.signal_loader import (
    SignalLoader,
    LoadResult,
    SignalInterpretationError,
    SignalInfluenceError,
)


class TestSourceRegistration:
    """Verify source registration works."""
    
    def test_registered_source_accepted(self):
        """Registered source can ingest signals."""
        registry = IngestionRegistry()
        
        source = RegisteredSource(
            source_id="test_source",
            name="Test Source",
            domain="economic",
            url="https://example.com",
            status=SourceStatus.ACTIVE,
            registered_at=datetime.now(timezone.utc),
            registered_by="human_admin",
            allowed_indicators=("gdp", "inflation"),
        )
        registry.register(source)
        
        assert registry.is_registered("test_source")
        assert registry.is_active("test_source")
    
    def test_unregistered_source_rejected(self):
        """Unregistered source is rejected."""
        registry = IngestionRegistry()
        
        with pytest.raises(SourceNotRegisteredError):
            registry.require_registered("unknown_source")


class TestSignalLoading:
    """Verify signal loading works correctly."""
    
    def test_valid_signal_loads(self):
        """Valid signal from registered source loads."""
        registry = IngestionRegistry()
        registry.register(RegisteredSource(
            source_id="test",
            name="Test",
            domain="economic",
            url=None,
            status=SourceStatus.ACTIVE,
            registered_at=datetime.now(timezone.utc),
            registered_by="admin",
            allowed_indicators=(),
        ))
        
        loader = SignalLoader(registry)
        
        report = loader.load(
            raw_signals=[{
                "name": "gdp_growth",
                "value": 2.5,
                "unit": "percent",
                "domain": "economic",
            }],
            source_id="test",
        )
        
        assert report.result == LoadResult.SUCCESS
        assert report.signals_loaded == 1
    
    def test_unregistered_source_rejected(self):
        """Signals from unregistered source rejected."""
        registry = IngestionRegistry()
        loader = SignalLoader(registry)
        
        report = loader.load(
            raw_signals=[{"name": "test", "value": 1, "unit": "x", "domain": "economic"}],
            source_id="unregistered",
        )
        
        assert report.result == LoadResult.REJECTED
        assert report.signals_loaded == 0


class TestReadOnlyEnforcement:
    """Verify signals are read-only."""
    
    def test_interpretation_forbidden(self):
        """Signal interpretation is forbidden."""
        registry = IngestionRegistry()
        loader = SignalLoader(registry)
        
        with pytest.raises(SignalInterpretationError):
            loader.interpret()
    
    def test_aggregation_forbidden(self):
        """Signal aggregation is forbidden."""
        registry = IngestionRegistry()
        loader = SignalLoader(registry)
        
        with pytest.raises(SignalInterpretationError):
            loader.aggregate()
    
    def test_influence_forbidden(self):
        """Influence through signals is forbidden."""
        registry = IngestionRegistry()
        loader = SignalLoader(registry)
        
        with pytest.raises(SignalInfluenceError):
            loader.influence()
    
    def test_send_data_forbidden(self):
        """Sending data outbound is forbidden."""
        registry = IngestionRegistry()
        loader = SignalLoader(registry)
        
        with pytest.raises(SignalInfluenceError):
            loader.send_data()


class TestSignalImmutability:
    """Verify signals are immutable."""
    
    def test_signal_is_frozen(self):
        """CivilizationSignal is frozen dataclass."""
        signal = CivilizationSignal(
            signal_id="test",
            domain="economic",
            name="test_signal",
            value=1.0,
            unit="unit",
            timestamp=datetime.now(timezone.utc),
            source="test",
            provenance_hash="abc123",
        )
        
        with pytest.raises(AttributeError):
            signal.value = 2.0
