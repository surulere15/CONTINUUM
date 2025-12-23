"""
Phase I Override Tests

Verifies overrides are temporary and reversible.

GOVERNANCE TESTS - Phase I acceptance criteria.
"""

import pytest
from datetime import datetime, timezone

from governance.interfaces.emergency_interlock import (
    EmergencyInterlock,
    InterlockStatus,
    InterlockAction,
    ObjectiveModificationError,
)
from governance.observability.accountability_log import (
    AccountabilityLog,
    ActionType,
    AnonymousAuthorityError,
)


class TestEmergencyOverrides:
    """Verify emergency overrides work correctly."""
    
    def test_halt_execution(self):
        """Guardian can halt execution."""
        interlock = EmergencyInterlock()
        
        event = interlock.halt_execution("guardian1", "Safety concern")
        
        assert interlock.status == InterlockStatus.HALTED
        assert event.action == InterlockAction.HALT_EXECUTION
    
    def test_freeze_agents(self):
        """Guardian can freeze agents."""
        interlock = EmergencyInterlock()
        
        event = interlock.freeze_agents(
            "guardian1",
            {"agent1", "agent2"},
            "Anomaly detected",
        )
        
        assert interlock.is_agent_frozen("agent1")
        assert interlock.is_agent_frozen("agent2")
    
    def test_override_is_reversible(self):
        """Overrides can be resumed."""
        interlock = EmergencyInterlock()
        
        interlock.halt_execution("guardian1", "Test")
        assert interlock.status == InterlockStatus.HALTED
        
        interlock.resume("guardian1", "auth_key")
        assert interlock.status == InterlockStatus.NORMAL


class TestGuardianLimits:
    """Verify Guardians cannot exceed their authority."""
    
    def test_cannot_issue_objectives(self):
        """Guardians cannot issue new objectives."""
        interlock = EmergencyInterlock()
        
        with pytest.raises(ObjectiveModificationError):
            interlock.issue_objective()
    
    def test_cannot_change_canon(self):
        """Guardians cannot change Canon."""
        interlock = EmergencyInterlock()
        
        with pytest.raises(ObjectiveModificationError):
            interlock.change_canon()
    
    def test_cannot_force_execution(self):
        """Guardians cannot force execution against constraints."""
        interlock = EmergencyInterlock()
        
        with pytest.raises(Exception):
            interlock.force_execution()


class TestAccountability:
    """Verify all actions are accountable."""
    
    def test_action_is_attributable(self):
        """Actions are attributed to human."""
        log = AccountabilityLog()
        
        action = log.log_action(
            action_type=ActionType.STRATEGIC_DIRECTIVE,
            issuer_id="steward1",
            issuer_name="Steward One",
            description="Test directive",
            parameters={"target": "system"},
        )
        
        assert action.issuer_id == "steward1"
        assert action.issuer_name == "Steward One"
    
    def test_anonymous_forbidden(self):
        """Anonymous actions are forbidden."""
        log = AccountabilityLog()
        
        with pytest.raises(AnonymousAuthorityError):
            log.log_action(
                action_type=ActionType.OPERATIONAL_COMMAND,
                issuer_id="anonymous",
                issuer_name="Unknown",
                description="Anonymous action",
                parameters={},
            )
    
    def test_action_immutable(self):
        """Logged actions cannot be deleted."""
        log = AccountabilityLog()
        
        with pytest.raises(Exception):
            log.delete_action("action_0")
    
    def test_action_replayable(self):
        """Actions can be replayed."""
        log = AccountabilityLog()
        
        action = log.log_action(
            action_type=ActionType.STRATEGIC_DIRECTIVE,
            issuer_id="steward1",
            issuer_name="Steward One",
            description="Test",
            parameters={},
        )
        
        replay = log.replay(action.action_id)
        assert replay is not None
        assert replay.action == action
