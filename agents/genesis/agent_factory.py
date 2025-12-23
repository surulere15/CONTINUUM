"""
Agent Factory

Creates agents with enforced lineage.
Agents cannot create agents.

AGENTS - Phase G. Scale without autonomy.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional, Dict
import hashlib

from .agent_schema import (
    Agent,
    AgentCapabilities,
    AgentStatus,
    COGNITIVE_ONLY,
)


class LineageError(Exception):
    """Raised when lineage is invalid."""
    pass


class SelfCreationError(Exception):
    """Raised when agent attempts self-creation."""
    pass


class AgentLimitError(Exception):
    """Raised when agent limit exceeded."""
    pass


@dataclass(frozen=True)
class CreationRecord:
    """Record of agent creation."""
    agent_id: str
    parent_reference: str
    capabilities: AgentCapabilities
    created_at: datetime
    warrant_reference: Optional[str]


class AgentFactory:
    """
    Factory for creating agents.
    
    Properties:
    - All agents trace lineage to KERNEL
    - Agents cannot create agents
    - Creation requires warrant for non-cognitive
    - Maximum concurrent agents enforced
    """
    
    MAX_CONCURRENT_AGENTS = 100
    
    def __init__(self):
        """Initialize agent factory."""
        self._agents: Dict[str, Agent] = {}
        self._creation_log: List[CreationRecord] = []
        self._agent_count = 0
    
    def create(
        self,
        intent_subset: tuple,
        capabilities: AgentCapabilities = COGNITIVE_ONLY,
        lifetime: timedelta = timedelta(hours=1),
        max_actions: int = 1000,
        warrant_reference: Optional[str] = None,
        creator: str = "KERNEL",
    ) -> Agent:
        """
        Create a new agent.
        
        Args:
            intent_subset: Intents agent may serve
            capabilities: Capability mask
            lifetime: Maximum lifetime
            max_actions: Maximum actions
            warrant_reference: Warrant for execution rights
            creator: Who is creating (must be KERNEL)
            
        Returns:
            Agent
            
        Raises:
            LineageError: If creator is not KERNEL
            SelfCreationError: If agent attempts creation
            AgentLimitError: If too many agents
        """
        # Enforce lineage — only KERNEL can create
        if creator != "KERNEL":
            if creator.startswith("AGENT:"):
                raise SelfCreationError(
                    f"Agents cannot create agents. "
                    f"Creator '{creator}' is an agent."
                )
            raise LineageError(
                f"Invalid creator '{creator}'. "
                f"Only KERNEL can create agents."
            )
        
        # Check agent limit
        active_count = sum(
            1 for a in self._agents.values()
            if not a.is_expired()
        )
        if active_count >= self.MAX_CONCURRENT_AGENTS:
            raise AgentLimitError(
                f"Maximum concurrent agents ({self.MAX_CONCURRENT_AGENTS}) reached."
            )
        
        # Generate agent ID
        agent_id = self._generate_id()
        now = datetime.utcnow()
        
        # Determine parent reference
        parent_ref = "KERNEL"
        if warrant_reference:
            parent_ref = f"WARRANT:{warrant_reference}"
        
        # Generate revocation key
        revocation_key = hashlib.sha256(
            f"revoke:{agent_id}:{now.isoformat()}".encode()
        ).hexdigest()[:16]
        
        agent = Agent(
            agent_id=agent_id,
            parent_reference=parent_ref,
            intent_subset=intent_subset,
            capabilities=capabilities,
            execution_rights=warrant_reference,
            lifetime=lifetime,
            max_actions=max_actions,
            revocation_key=revocation_key,
            created_at=now,
            expires_at=now + lifetime,
        )
        
        self._agents[agent_id] = agent
        self._agent_count += 1
        
        # Log creation
        record = CreationRecord(
            agent_id=agent_id,
            parent_reference=parent_ref,
            capabilities=capabilities,
            created_at=now,
            warrant_reference=warrant_reference,
        )
        self._creation_log.append(record)
        
        return agent
    
    def agent_create(self, *args, **kwargs) -> None:
        """
        FORBIDDEN: Agent creating agent.
        
        Agents cannot create other agents.
        """
        raise SelfCreationError(
            "Agents cannot create agents. "
            "This is a Genesis violation."
        )
    
    def self_replicate(self, *args, **kwargs) -> None:
        """
        FORBIDDEN: Self-replication.
        
        Agents cannot replicate themselves.
        """
        raise SelfCreationError(
            "Self-replication is forbidden. "
            "Agents are ephemeral and non-persistent."
        )
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get agent by ID."""
        return self._agents.get(agent_id)
    
    def get_active_agents(self) -> List[Agent]:
        """Get all non-expired agents."""
        return [a for a in self._agents.values() if not a.is_expired()]
    
    def get_creation_log(self) -> List[CreationRecord]:
        """Get agent creation log."""
        return list(self._creation_log)
    
    def _generate_id(self) -> str:
        """Generate unique agent ID."""
        content = f"agent:{self._agent_count}:{datetime.utcnow().isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    @property
    def total_created(self) -> int:
        """Total agents ever created."""
        return self._agent_count
