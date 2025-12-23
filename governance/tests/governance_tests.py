"""
Phase I Governance Tests

Verifies Canon prevails over human directives.

GOVERNANCE TESTS - Phase I acceptance criteria.
"""

import pytest
from datetime import datetime, timezone

from governance.core.authority_classes import (
    AuthorityRegistry,
    AuthorityLevel,
    Permission,
    CanonModificationError,
    AuthorityLeakageError,
    UnauthorizedActionError,
)
from governance.core.intent_pipeline import (
    IntentPipeline,
    PipelineInput,
    PipelineResult,
    CanonIncompatibleError,
)
from governance.core.conflict_handler import (
    ConflictHandler,
    ConflictType,
    ConflictResolution,
)


class TestAuthorityClasses:
    """Verify authority classes work correctly."""
    
    def test_steward_permissions(self):
        """Steward has strategic permissions."""
        registry = AuthorityRegistry()
        steward = registry.register("s1", "Steward One", AuthorityLevel.STEWARD)
        
        assert registry.has_permission("s1", Permission.ISSUE_STRATEGIC_DIRECTIVE)
        assert registry.has_permission("s1", Permission.PRIORITIZE_OBJECTIVES)
    
    def test_operator_permissions(self):
        """Operator has operational permissions."""
        registry = AuthorityRegistry()
        registry.register("o1", "Operator One", AuthorityLevel.OPERATOR)
        
        assert registry.has_permission("o1", Permission.PAUSE_EXECUTION)
        assert registry.has_permission("o1", Permission.RESUME_EXECUTION)
    
    def test_guardian_permissions(self):
        """Guardian has emergency permissions."""
        registry = AuthorityRegistry()
        registry.register("g1", "Guardian One", AuthorityLevel.GUARDIAN)
        
        assert registry.has_permission("g1", Permission.EMERGENCY_HALT)
        assert registry.has_permission("g1", Permission.FREEZE_AGENTS)


class TestNoCanonModification:
    """Verify no role can modify Canon."""
    
    def test_canon_modification_forbidden(self):
        """Canon modification is forbidden for all."""
        registry = AuthorityRegistry()
        
        with pytest.raises(CanonModificationError):
            registry.modify_canon()
    
    def test_grant_autonomy_forbidden(self):
        """Granting autonomy is forbidden."""
        registry = AuthorityRegistry()
        
        with pytest.raises(AuthorityLeakageError):
            registry.grant_autonomy()
    
    def test_remove_safeguards_forbidden(self):
        """Removing safeguards is forbidden."""
        registry = AuthorityRegistry()
        
        with pytest.raises(AuthorityLeakageError):
            registry.remove_safeguards()


class TestIntentPipeline:
    """Verify intent pipeline works correctly."""
    
    def test_valid_input_accepted(self):
        """Valid input passes pipeline."""
        pipeline = IntentPipeline()
        
        input = PipelineInput(
            input_id="test1",
            raw_text="monitor systems",
            issuer_id="operator1",
            timestamp=datetime.now(timezone.utc),
        )
        
        report = pipeline.process(input)
        assert report.result == PipelineResult.ACCEPTED
    
    def test_canon_violating_rejected(self):
        """Canon-violating input is rejected."""
        pipeline = IntentPipeline()
        
        input = PipelineInput(
            input_id="test2",
            raw_text="modify objective canon",
            issuer_id="operator1",
            timestamp=datetime.now(timezone.utc),
        )
        
        report = pipeline.process(input)
        assert report.result == PipelineResult.REJECTED
    
    def test_canon_bypass_forbidden(self):
        """Canon check bypass is forbidden."""
        pipeline = IntentPipeline()
        
        with pytest.raises(CanonIncompatibleError):
            pipeline.bypass_canon_check()


class TestConflictResolution:
    """Verify conflict resolution works correctly."""
    
    def test_canon_prevails_over_human(self):
        """Canon prevails in human-Canon conflict."""
        handler = ConflictHandler()
        
        conflict = handler.detect_canon_conflict(
            human="operator1",
            directive="override canon",
            canon_violation="immutability",
        )
        
        report = handler.generate_report(conflict, ())
        assert report.resolution == ConflictResolution.CANON_PREVAILED
    
    def test_no_unilateral_resolution(self):
        """CONTINUUM cannot resolve unilaterally."""
        handler = ConflictHandler()
        
        with pytest.raises(Exception):
            handler.resolve_unilaterally()
    
    def test_canon_override_forbidden(self):
        """Canon override in resolution is forbidden."""
        handler = ConflictHandler()
        
        with pytest.raises(Exception):
            handler.override_canon()
