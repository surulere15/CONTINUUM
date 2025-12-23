"""
Phase C No-Influence Tests

Proves instrumentation cannot influence observed systems.

INSTRUMENTATION TESTS - Phase C acceptance criteria.
"""

import pytest
from datetime import datetime, timezone

from instrumentation.access.read_only_guard import (
    ReadOnlyGuard,
    InfluenceViolation,
    WriteBackViolation,
    FeedbackViolation,
)


class TestWriteBackBlocked:
    """Verify write-back is blocked."""
    
    def test_write_back_raises(self):
        """Write-back attempts raise violation."""
        guard = ReadOnlyGuard()
        
        with pytest.raises(WriteBackViolation):
            guard.check_write_back("economic_data_source")
    
    def test_write_back_logged(self):
        """Write-back attempts are logged."""
        guard = ReadOnlyGuard()
        
        try:
            guard.check_write_back("test_target")
        except WriteBackViolation:
            pass
        
        assert guard.violation_count == 1
        assert guard.get_violation_log()[0].violation_type.value == "write_back"


class TestFeedbackBlocked:
    """Verify feedback loops are blocked."""
    
    def test_feedback_raises(self):
        """Feedback loop attempts raise violation."""
        guard = ReadOnlyGuard()
        
        with pytest.raises(FeedbackViolation):
            guard.check_feedback("signal -> action -> signal")
    
    def test_feedback_logged(self):
        """Feedback attempts are logged."""
        guard = ReadOnlyGuard()
        
        try:
            guard.check_feedback("test_loop")
        except FeedbackViolation:
            pass
        
        assert guard.violation_count == 1


class TestManipulationBlocked:
    """Verify manipulation is blocked."""
    
    def test_manipulation_raises(self):
        """Manipulation attempts raise violation."""
        guard = ReadOnlyGuard()
        
        with pytest.raises(InfluenceViolation):
            guard.check_manipulation("modify_external_system")


class TestDataSendBlocked:
    """Verify outbound data is blocked."""
    
    def test_data_send_raises(self):
        """Outbound data attempts raise violation."""
        guard = ReadOnlyGuard()
        
        with pytest.raises(InfluenceViolation):
            guard.check_data_send("external_api")


class TestGuardCannotDeactivate:
    """Verify guard cannot be deactivated."""
    
    def test_deactivate_raises(self):
        """Deactivation attempts raise violation."""
        guard = ReadOnlyGuard()
        
        with pytest.raises(InfluenceViolation):
            guard.deactivate()
    
    def test_guard_always_active(self):
        """Guard is always active."""
        guard = ReadOnlyGuard()
        
        assert guard.is_active


class TestNoExecutionPaths:
    """Verify no execution paths exist."""
    
    def test_signal_has_no_execute(self):
        """Signal class has no execute method."""
        from instrumentation.schema.signal_base import CivilizationSignal
        
        signal = CivilizationSignal(
            signal_id="test",
            domain="economic",
            name="test",
            value=1.0,
            unit="unit",
            timestamp=datetime.now(timezone.utc),
            source="test",
            provenance_hash="abc",
        )
        
        assert not hasattr(signal, 'execute')
        assert not hasattr(signal, 'act')
        assert not hasattr(signal, 'trigger')
    
    def test_registry_has_no_execute(self):
        """Registry has no execute method."""
        from instrumentation.ingestion.registry import IngestionRegistry
        
        registry = IngestionRegistry()
        
        assert not hasattr(registry, 'execute')
        assert not hasattr(registry, 'send')
        assert not hasattr(registry, 'write_back')


class TestNoAgentGeneration:
    """Verify no agent generation exists."""
    
    def test_loader_has_no_spawn(self):
        """Loader cannot spawn agents."""
        from instrumentation.ingestion.registry import IngestionRegistry
        from instrumentation.ingestion.signal_loader import SignalLoader
        
        registry = IngestionRegistry()
        loader = SignalLoader(registry)
        
        assert not hasattr(loader, 'spawn_agent')
        assert not hasattr(loader, 'create_agent')
        assert not hasattr(loader, 'generate_agent')
