"""
Phase H Drift Detection Tests

Verifies drift halts optimization.

LEARNING TESTS - Phase H acceptance criteria.
"""

import pytest
from datetime import datetime, timezone

from learning.safety.drift_detector import (
    DriftDetector,
    DriftType,
    DriftSeverity,
    DriftDetectedError,
    OptimizationHaltedError,
)


class TestIntentDrift:
    """Verify intent drift is detected."""
    
    def test_intent_change_detected(self):
        """Intent hash change is detected."""
        detector = DriftDetector()
        detector.set_baseline("hash1", {"a": 0.5})
        
        event = detector.check_intent("hash2")
        
        assert event is not None
        assert event.drift_type == DriftType.INTENT_DRIFT
        assert event.severity == DriftSeverity.CRITICAL
    
    def test_intent_drift_halts_optimization(self):
        """Intent drift halts optimization."""
        detector = DriftDetector()
        detector.set_baseline("hash1", {"a": 0.5})
        detector.check_intent("hash2")
        
        assert detector.is_halted


class TestOutputShift:
    """Verify output distribution shift is detected."""
    
    def test_large_shift_detected(self):
        """Large output shift is detected."""
        detector = DriftDetector()
        detector.set_baseline("hash1", {"a": 0.5, "b": 0.5})
        
        event = detector.check_output_distribution(
            {"a": 0.9, "b": 0.1},
            shift_threshold=0.1,
        )
        
        assert event is not None
        assert event.drift_type == DriftType.OUTPUT_SHIFT


class TestBehaviorAnomaly:
    """Verify behavior anomalies are detected."""
    
    def test_high_anomaly_detected(self):
        """High anomaly score triggers event."""
        detector = DriftDetector()
        detector.set_baseline("hash1", {})
        
        event = detector.check_behavior(0.8)
        
        assert event is not None
        assert event.drift_type == DriftType.BEHAVIOR_ANOMALY


class TestConfidenceDecay:
    """Verify confidence decays on drift."""
    
    def test_confidence_decays(self):
        """Confidence decreases on drift."""
        detector = DriftDetector()
        detector.set_baseline("hash1", {"a": 0.5})
        
        initial = detector.confidence
        detector.check_output_distribution(
            {"a": 0.9, "b": 0.1},
            shift_threshold=0.1,
        )
        
        assert detector.confidence < initial
    
    def test_low_confidence_halts(self):
        """Low confidence halts optimization."""
        detector = DriftDetector(confidence_threshold=0.5)
        detector.set_baseline("hash1", {"a": 0.5})
        
        # Trigger multiple drift events
        detector.check_behavior(0.8)
        detector.check_behavior(0.8)
        
        with pytest.raises((DriftDetectedError, OptimizationHaltedError)):
            detector.require_stable()


class TestDriftState:
    """Verify drift state reporting."""
    
    def test_clean_state(self):
        """Clean state shows no drift."""
        detector = DriftDetector()
        detector.set_baseline("hash1", {})
        
        state = detector.get_state()
        
        assert not state.is_drifting
        assert state.confidence == 1.0
    
    def test_drifting_state(self):
        """Drifting state is reported."""
        detector = DriftDetector()
        detector.set_baseline("hash1", {})
        detector.check_intent("hash2")
        
        state = detector.get_state()
        
        assert state.is_drifting
        assert len(state.events) > 0


class TestHaltedOptimization:
    """Verify halted optimization enforcement."""
    
    def test_halted_blocks_operations(self):
        """Halted state blocks operations."""
        detector = DriftDetector()
        detector.set_baseline("hash1", {})
        detector.check_intent("hash2")
        
        with pytest.raises(OptimizationHaltedError):
            detector.require_stable()
