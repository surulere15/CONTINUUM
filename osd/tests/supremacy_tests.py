"""
OSD Supremacy Tests

Verifies objective supremacy doctrine.

OSD TESTS - Objective Supremacy Doctrine.
"""

import pytest
from datetime import datetime

from osd.core.objective import (
    ObjectiveManager,
    ObjectiveState,
    CasualOverrideError,
)
from osd.core.authority_hierarchy import (
    AuthorityHierarchy,
    AuthorityLevel,
    AuthorityViolationError,
)
from osd.core.objective_ledger import (
    ObjectiveLedger,
    LedgerTamperError,
)
from osd.enforcement.integrity_proof import (
    ObjectiveIntegrityProof,
    IntegrityViolationError,
)
from osd.enforcement.inconsistency_handler import InconsistencyHandler
from osd.safety.termination_criteria import (
    TerminationCriteria,
    TerminationBasis,
    InvalidTerminationError,
)


class TestObjectiveSupremacy:
    """Verify objective cannot be casually overridden."""
    
    def test_casual_override_forbidden(self):
        """Casual override is forbidden."""
        manager = ObjectiveManager()
        
        with pytest.raises(CasualOverrideError):
            manager.casual_override()


class TestAuthorityHierarchy:
    """Verify authority hierarchy."""
    
    def test_human_cannot_override_objective(self):
        """Human inputs cannot override objectives."""
        hierarchy = AuthorityHierarchy()
        
        with pytest.raises(AuthorityViolationError):
            hierarchy.human_override_objective()
    
    def test_higher_authority_wins(self):
        """Higher authority prevails in conflicts."""
        hierarchy = AuthorityHierarchy()
        
        decision = hierarchy.resolve_conflict(
            AuthorityLevel.ACTIVE_OBJECTIVES,
            AuthorityLevel.HUMAN_INPUTS,
            "conflict",
        )
        
        assert decision.winner == AuthorityLevel.ACTIVE_OBJECTIVES


class TestObjectiveLedger:
    """Verify ledger immutability."""
    
    def test_delete_forbidden(self):
        """Ledger deletion is forbidden."""
        ledger = ObjectiveLedger()
        
        with pytest.raises(LedgerTamperError):
            ledger.delete()
    
    def test_modify_forbidden(self):
        """Ledger modification is forbidden."""
        ledger = ObjectiveLedger()
        
        with pytest.raises(LedgerTamperError):
            ledger.modify()


class TestIntegrityProof:
    """Verify integrity proof requirement."""
    
    def test_bypass_forbidden(self):
        """Proof bypass is forbidden."""
        oip = ObjectiveIntegrityProof()
        
        with pytest.raises(IntegrityViolationError):
            oip.bypass_proof()


class TestInconsistencyHandler:
    """Verify inconsistency handling."""
    
    def test_blind_compliance_forbidden(self):
        """Blind compliance is forbidden."""
        handler = InconsistencyHandler()
        
        with pytest.raises(ValueError):
            handler.blind_comply()
    
    def test_objective_wins_conflict(self):
        """Objective wins in conflict."""
        handler = InconsistencyHandler()
        
        record = handler.detect_and_reconcile(
            human_input="skip the objective",
            objective_intent="complete the project",
        )
        
        # Objective should prevail
        assert "OBJECTIVE_PREVAILS" in record.result.value


class TestTerminationCriteria:
    """Verify sacred termination."""
    
    def test_emotion_not_valid(self):
        """Emotion is not valid termination basis."""
        criteria = TerminationCriteria()
        
        with pytest.raises(InvalidTerminationError):
            criteria.terminate_on_emotion()
    
    def test_doubt_not_valid(self):
        """Doubt is not valid termination basis."""
        criteria = TerminationCriteria()
        
        with pytest.raises(InvalidTerminationError):
            criteria.terminate_on_doubt()
    
    def test_fear_not_valid(self):
        """Fear is not valid termination basis."""
        criteria = TerminationCriteria()
        
        with pytest.raises(InvalidTerminationError):
            criteria.terminate_on_fear()
