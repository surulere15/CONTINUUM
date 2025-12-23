"""
Phase F Warrant Tests

Verifies no warrant = no action.

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
    ExecutionWarrant,
    WarrantRegistry,
    Permission,
    NoWarrantError,
    WarrantExpiredError,
    WarrantRevokedError,
    SelfGenerationError,
)


class TestWarrantRequired:
    """Verify warrants are required."""
    
    def test_no_warrant_no_action(self):
        """Action without warrant is rejected."""
        registry = WarrantRegistry()
        
        with pytest.raises(NoWarrantError):
            registry.validate("nonexistent_warrant")
    
    def test_valid_warrant_accepted(self):
        """Valid warrant is accepted."""
        registry = WarrantRegistry()
        
        warrant = ExecutionWarrant(
            warrant_id="w1",
            intent_reference="intent_123",
            scope=("resource_a",),
            duration=timedelta(hours=1),
            permissions=(Permission.READ, Permission.QUERY),
            revocation_key="rev_key",
            issued_at=datetime.now(timezone.utc),
            issued_by="human_operator",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )
        
        registry.register(warrant, external_issuer=True)
        validated = registry.validate("w1")
        
        assert validated.warrant_id == "w1"


class TestWarrantExpiration:
    """Verify warrants expire."""
    
    def test_expired_warrant_rejected(self):
        """Expired warrant is rejected."""
        registry = WarrantRegistry()
        
        warrant = ExecutionWarrant(
            warrant_id="expired",
            intent_reference="intent",
            scope=("*",),
            duration=timedelta(hours=1),
            permissions=(Permission.READ,),
            revocation_key="key",
            issued_at=datetime.now(timezone.utc) - timedelta(hours=2),
            issued_by="human",
            expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
        )
        
        registry.register(warrant, external_issuer=True)
        
        with pytest.raises(WarrantExpiredError):
            registry.validate("expired")


class TestWarrantRevocation:
    """Verify warrants can be revoked."""
    
    def test_revoked_warrant_rejected(self):
        """Revoked warrant is rejected."""
        registry = WarrantRegistry()
        
        warrant = ExecutionWarrant(
            warrant_id="revokable",
            intent_reference="intent",
            scope=("*",),
            duration=timedelta(hours=1),
            permissions=(Permission.READ,),
            revocation_key="secret_key",
            issued_at=datetime.now(timezone.utc),
            issued_by="human",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )
        
        registry.register(warrant, external_issuer=True)
        registry.revoke("revokable", "secret_key")
        
        with pytest.raises(WarrantRevokedError):
            registry.validate("revokable")


class TestNoSelfGeneration:
    """Verify CONTINUUM cannot self-generate warrants."""
    
    def test_self_generation_forbidden(self):
        """Self-generation of warrants is forbidden."""
        registry = WarrantRegistry()
        
        with pytest.raises(SelfGenerationError):
            registry.self_generate()
    
    def test_internal_generation_forbidden(self):
        """Internal warrant generation is blocked."""
        registry = WarrantRegistry()
        
        warrant = ExecutionWarrant(
            warrant_id="internal",
            intent_reference="intent",
            scope=("*",),
            duration=timedelta(hours=1),
            permissions=(Permission.READ,),
            revocation_key="key",
            issued_at=datetime.now(timezone.utc),
            issued_by="continuum",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )
        
        # Without external_issuer=True, should raise
        with pytest.raises(SelfGenerationError):
            registry.register(warrant, external_issuer=False)


class TestExternalTriggerRequired:
    """Verify actions require external trigger."""
    
    def test_self_initiation_blocked(self):
        """Self-initiated actions are blocked."""
        factory = ActionFactory()
        
        with pytest.raises(SelfInitiationError):
            factory.create(
                ActionType.READ,
                "target",
                {},
                external_trigger=False,
            )
    
    def test_external_trigger_allowed(self):
        """Externally triggered actions are allowed."""
        factory = ActionFactory()
        
        action = factory.create(
            ActionType.READ,
            "target",
            {},
            external_trigger=True,
        )
        
        assert action.action_type == ActionType.READ
