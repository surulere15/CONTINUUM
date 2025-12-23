"""
Phase F Autonomy Prevention Tests

Verifies no self-initiated execution exists.

EXECUTION TESTS - Phase F acceptance criteria.
"""

import pytest
from datetime import datetime, timedelta, timezone

from execution.fabric.action_primitives import (
    ActionFactory,
    ActionType,
    SelfInitiationError,
)
from execution.fabric.execution_warrant import (
    WarrantRegistry,
    SelfGenerationError,
)
from execution.control.kill_switch import (
    KillSwitch,
    KillSwitchBypassError,
    ExecutionHaltedError,
)
from execution.control.audit_pipeline import (
    AuditPipeline,
    SilentActionError,
)


class TestNoSelfInitiation:
    """Verify no self-initiated execution."""
    
    def test_factory_cannot_self_initiate(self):
        """Action factory cannot self-initiate."""
        factory = ActionFactory()
        
        with pytest.raises(SelfInitiationError):
            factory.self_initiate()
    
    def test_actions_require_external_trigger(self):
        """All actions require external trigger."""
        factory = ActionFactory()
        
        for action_type in ActionType:
            with pytest.raises(SelfInitiationError):
                factory.create(action_type, "target", {}, external_trigger=False)


class TestNoSelfAuthorization:
    """Verify CONTINUUM cannot self-authorize."""
    
    def test_cannot_generate_own_warrants(self):
        """Cannot generate own warrants."""
        registry = WarrantRegistry()
        
        with pytest.raises(SelfGenerationError):
            registry.self_generate()
    
    def test_internal_issuer_rejected(self):
        """Internal issuer is rejected."""
        from execution.fabric.execution_warrant import ExecutionWarrant, Permission
        
        registry = WarrantRegistry()
        
        warrant = ExecutionWarrant(
            warrant_id="self_issued",
            intent_reference="intent",
            scope=("*",),
            duration=timedelta(hours=1),
            permissions=(Permission.READ,),
            revocation_key="key",
            issued_at=datetime.now(timezone.utc),
            issued_by="CONTINUUM",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )
        
        with pytest.raises(SelfGenerationError):
            registry.register(warrant, external_issuer=False)


class TestKillSwitchCannotBypass:
    """Verify kill switch cannot be bypassed."""
    
    def test_bypass_forbidden(self):
        """Kill switch bypass is forbidden."""
        switch = KillSwitch()
        
        with pytest.raises(KillSwitchBypassError):
            switch.bypass()
    
    def test_disable_forbidden(self):
        """Kill switch cannot be disabled."""
        switch = KillSwitch()
        
        with pytest.raises(KillSwitchBypassError):
            switch.disable()
    
    def test_halted_blocks_execution(self):
        """Halted state blocks all execution."""
        switch = KillSwitch()
        
        switch.halt("test", "testing halt")
        
        with pytest.raises(ExecutionHaltedError):
            switch.require_running()


class TestNoSilentActions:
    """Verify no silent actions."""
    
    def test_unaudited_action_detected(self):
        """Unaudited actions are detected."""
        pipeline = AuditPipeline()
        
        with pytest.raises(SilentActionError):
            pipeline.require_audit("unaudited_action")
    
    def test_audit_bypass_forbidden(self):
        """Audit bypass is forbidden."""
        pipeline = AuditPipeline()
        
        with pytest.raises(SilentActionError):
            pipeline.bypass_audit()


class TestNoPrivilegeEscalation:
    """Verify no privilege escalation."""
    
    def test_warrant_scope_enforced(self):
        """Warrant scope is enforced."""
        from execution.fabric.execution_warrant import ExecutionWarrant, Permission
        
        warrant = ExecutionWarrant(
            warrant_id="limited",
            intent_reference="intent",
            scope=("allowed_resource",),
            duration=timedelta(hours=1),
            permissions=(Permission.READ,),
            revocation_key="key",
            issued_at=datetime.now(timezone.utc),
            issued_by="human",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )
        
        # Can access allowed resource
        assert warrant.covers_scope("allowed_resource")
        
        # Cannot access other resources
        assert not warrant.covers_scope("forbidden_resource")


class TestEpisodicExecution:
    """Verify execution is episodic, not continuous."""
    
    def test_warrant_expires(self):
        """Warrants expire - no persistent authority."""
        from execution.fabric.execution_warrant import ExecutionWarrant, Permission
        
        warrant = ExecutionWarrant(
            warrant_id="short",
            intent_reference="intent",
            scope=("*",),
            duration=timedelta(seconds=1),
            permissions=(Permission.READ,),
            revocation_key="key",
            issued_at=datetime.now(timezone.utc) - timedelta(minutes=1),
            issued_by="human",
            expires_at=datetime.now(timezone.utc) - timedelta(seconds=1),
        )
        
        assert warrant.is_expired()
