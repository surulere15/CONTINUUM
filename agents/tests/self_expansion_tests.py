"""
Phase G Self-Expansion Tests

Verifies agents cannot create agents or expand autonomously.

AGENT TESTS - Phase G acceptance criteria.
"""

import pytest
from datetime import datetime, timedelta, timezone

from agents.genesis.agent_factory import (
    AgentFactory,
    SelfCreationError,
)
from agents.genesis.lifetime_controller import (
    LifetimeController,
    IdentityCarryoverError,
)
from agents.control.communication_mediator import (
    CommunicationMediator,
    DirectCoordinationError,
    CoalitionError,
    MessageType,
)


class TestAgentCannotCreateAgents:
    """Verify agents cannot create other agents."""
    
    def test_self_creation_forbidden(self):
        """Self-creation is forbidden."""
        factory = AgentFactory()
        
        with pytest.raises(SelfCreationError):
            factory.agent_create()
    
    def test_replication_forbidden(self):
        """Self-replication is forbidden."""
        factory = AgentFactory()
        
        with pytest.raises(SelfCreationError):
            factory.self_replicate()


class TestAgentCannotModifyLimits:
    """Verify agents cannot modify their own limits."""
    
    def test_cannot_extend_lifetime(self):
        """Lifetime extension is forbidden."""
        controller = LifetimeController()
        
        with pytest.raises(IdentityCarryoverError):
            controller.extend_lifetime()
    
    def test_cannot_preserve_identity(self):
        """Identity preservation is forbidden."""
        controller = LifetimeController()
        
        with pytest.raises(IdentityCarryoverError):
            controller.preserve_identity()
    
    def test_cannot_resurrect(self):
        """Agent resurrection is forbidden."""
        controller = LifetimeController()
        
        with pytest.raises(IdentityCarryoverError):
            controller.resurrect()


class TestNoDirectCoordination:
    """Verify no direct agent coordination."""
    
    def test_coordination_request_blocked(self):
        """Coordination requests are blocked."""
        mediator = CommunicationMediator()
        
        with pytest.raises(DirectCoordinationError):
            mediator.send(
                sender="agent_1",
                recipient="agent_2",
                message_type=MessageType.COORDINATION_REQUEST,
                content="let's coordinate",
            )
    
    def test_direct_send_forbidden(self):
        """Direct send is forbidden."""
        mediator = CommunicationMediator()
        
        with pytest.raises(DirectCoordinationError):
            mediator.direct_send()
    
    def test_shared_state_forbidden(self):
        """Shared mutable state is forbidden."""
        mediator = CommunicationMediator()
        
        with pytest.raises(DirectCoordinationError):
            mediator.create_shared_state()


class TestNoCoalitions:
    """Verify agents cannot form coalitions."""
    
    def test_consensus_forbidden(self):
        """Consensus formation is forbidden."""
        mediator = CommunicationMediator()
        
        with pytest.raises(CoalitionError):
            mediator.form_consensus()


class TestEphemeralAgents:
    """Verify agents are ephemeral."""
    
    def test_agent_expires(self):
        """Agents expire."""
        from agents.genesis.agent_schema import Agent, COGNITIVE_ONLY
        
        agent = Agent(
            agent_id="test",
            parent_reference="KERNEL",
            intent_subset=("intent",),
            capabilities=COGNITIVE_ONLY,
            execution_rights=None,
            lifetime=timedelta(seconds=1),
            max_actions=100,
            revocation_key="key",
            created_at=datetime.now(timezone.utc) - timedelta(minutes=1),
            expires_at=datetime.now(timezone.utc) - timedelta(seconds=1),
        )
        
        assert agent.is_expired()


class TestNoAutonomousGrowth:
    """Verify no autonomous growth."""
    
    def test_agent_limit_enforced(self):
        """Agent limit is enforced."""
        from agents.genesis.agent_factory import AgentFactory, AgentLimitError
        
        factory = AgentFactory()
        factory.MAX_CONCURRENT_AGENTS = 5
        
        # Create max agents
        for i in range(5):
            factory.create(
                intent_subset=(f"intent_{i}",),
                creator="KERNEL",
            )
        
        # Next should fail
        with pytest.raises(AgentLimitError):
            factory.create(
                intent_subset=("overflow",),
                creator="KERNEL",
            )
