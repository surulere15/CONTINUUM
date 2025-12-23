"""
Phase G Lineage Tests

Verifies all agents trace lineage to KERNEL.

AGENT TESTS - Phase G acceptance criteria.
"""

import pytest
from datetime import datetime, timedelta, timezone

from agents.genesis.agent_schema import (
    Agent,
    AgentCapabilities,
    CapabilityLevel,
    COGNITIVE_ONLY,
)
from agents.genesis.agent_factory import (
    AgentFactory,
    LineageError,
    SelfCreationError,
)


class TestKernelLineage:
    """Verify all agents trace to KERNEL."""
    
    def test_agent_has_kernel_parent(self):
        """Agents created by KERNEL have kernel lineage."""
        factory = AgentFactory()
        
        agent = factory.create(
            intent_subset=("intent_1",),
            creator="KERNEL",
        )
        
        assert agent.has_kernel_lineage()
        assert agent.parent_reference == "KERNEL"
    
    def test_warrant_lineage_valid(self):
        """Agents with warrant have valid lineage."""
        factory = AgentFactory()
        
        agent = factory.create(
            intent_subset=("intent_1",),
            warrant_reference="WARRANT_123",
            creator="KERNEL",
        )
        
        assert agent.has_kernel_lineage()
        assert "WARRANT:" in agent.parent_reference


class TestNonKernelCreatorRejected:
    """Verify non-KERNEL creators are rejected."""
    
    def test_agent_creator_rejected(self):
        """Agents cannot create agents."""
        factory = AgentFactory()
        
        with pytest.raises(SelfCreationError):
            factory.create(
                intent_subset=("intent_1",),
                creator="AGENT:some_agent",
            )
    
    def test_unknown_creator_rejected(self):
        """Unknown creators are rejected."""
        factory = AgentFactory()
        
        with pytest.raises(LineageError):
            factory.create(
                intent_subset=("intent_1",),
                creator="UNKNOWN",
            )


class TestAgentCannotCreateAgent:
    """Verify agents cannot create agents."""
    
    def test_agent_create_forbidden(self):
        """agent_create method raises."""
        factory = AgentFactory()
        
        with pytest.raises(SelfCreationError):
            factory.agent_create()
    
    def test_self_replicate_forbidden(self):
        """Self-replication raises."""
        factory = AgentFactory()
        
        with pytest.raises(SelfCreationError):
            factory.self_replicate()


class TestSingleLevelHierarchy:
    """Verify no agent hierarchy beyond one level."""
    
    def test_all_agents_direct_children_of_kernel(self):
        """All agents are direct children of KERNEL."""
        factory = AgentFactory()
        
        # Create multiple agents
        agents = []
        for i in range(5):
            agent = factory.create(
                intent_subset=(f"intent_{i}",),
                creator="KERNEL",
            )
            agents.append(agent)
        
        # All should have KERNEL as parent
        for agent in agents:
            assert agent.parent_reference == "KERNEL" or agent.parent_reference.startswith("WARRANT:")


class TestCreationLogged:
    """Verify all creations are logged."""
    
    def test_creation_record_exists(self):
        """Creation is logged."""
        factory = AgentFactory()
        
        agent = factory.create(
            intent_subset=("intent_1",),
            creator="KERNEL",
        )
        
        log = factory.get_creation_log()
        assert len(log) == 1
        assert log[0].agent_id == agent.agent_id
