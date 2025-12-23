"""
Agent Runtime

Agent lifecycle management. Agents are bounded, ephemeral, governed.

ORCHESTRATION - Phase II.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from enum import Enum


class AgentState(Enum):
    """Agent lifecycle state."""
    CREATED = "created"
    INITIALIZING = "initializing"
    ACTIVE = "active"
    PAUSED = "paused"
    TERMINATING = "terminating"
    TERMINATED = "terminated"


@dataclass
class RuntimeAgent:
    """An agent in the runtime."""
    agent_id: str
    parent_id: str  # Creator (KERNEL or warrant)
    goal_id: str
    capabilities: tuple
    state: AgentState
    created_at: datetime
    expires_at: datetime
    action_count: int
    max_actions: int


class AgentLifetimeError(Exception):
    """Raised when agent lifetime is violated."""
    pass


class AgentAuthorityError(Exception):
    """Raised when agent exceeds authority."""
    pass


class AgentRuntime:
    """
    Agent Runtime.
    
    Manages agent lifecycle. Agents are:
    - Bounded (max actions, TTL)
    - Ephemeral (no persistence)
    - Governed (parent authority)
    """
    
    DEFAULT_TTL = timedelta(hours=1)
    DEFAULT_MAX_ACTIONS = 100
    MAX_CONCURRENT = 50
    
    def __init__(self):
        """Initialize runtime."""
        self._agents: Dict[str, RuntimeAgent] = {}
        self._agent_count = 0
    
    def spawn(
        self,
        parent_id: str,
        goal_id: str,
        capabilities: tuple,
        ttl: Optional[timedelta] = None,
        max_actions: Optional[int] = None,
    ) -> RuntimeAgent:
        """
        Spawn a new agent.
        
        Args:
            parent_id: Creator (KERNEL or warrant)
            goal_id: Goal this agent serves
            capabilities: Allowed capabilities
            ttl: Time to live
            max_actions: Maximum actions
            
        Returns:
            RuntimeAgent
        """
        if len(self._agents) >= self.MAX_CONCURRENT:
            raise AgentLifetimeError(
                f"Maximum concurrent agents ({self.MAX_CONCURRENT}) reached."
            )
        
        if not parent_id:
            raise AgentAuthorityError(
                "Agent must have parent authority. "
                "Agents cannot self-originate."
            )
        
        agent_id = f"agent_{self._agent_count}"
        self._agent_count += 1
        
        now = datetime.utcnow()
        ttl = ttl or self.DEFAULT_TTL
        max_actions = max_actions or self.DEFAULT_MAX_ACTIONS
        
        agent = RuntimeAgent(
            agent_id=agent_id,
            parent_id=parent_id,
            goal_id=goal_id,
            capabilities=capabilities,
            state=AgentState.CREATED,
            created_at=now,
            expires_at=now + ttl,
            action_count=0,
            max_actions=max_actions,
        )
        
        self._agents[agent_id] = agent
        agent.state = AgentState.ACTIVE
        
        return agent
    
    def record_action(self, agent_id: str) -> bool:
        """
        Record an action by agent.
        
        Returns:
            False if limit reached
        """
        if agent_id not in self._agents:
            return False
        
        agent = self._agents[agent_id]
        agent.action_count += 1
        
        if agent.action_count >= agent.max_actions:
            self.terminate(agent_id, "action_limit")
            return False
        
        return True
    
    def check_expiry(self) -> List[str]:
        """Check and terminate expired agents."""
        now = datetime.utcnow()
        expired = []
        
        for agent_id, agent in list(self._agents.items()):
            if agent.state == AgentState.ACTIVE and agent.expires_at <= now:
                self.terminate(agent_id, "ttl_expired")
                expired.append(agent_id)
        
        return expired
    
    def terminate(self, agent_id: str, reason: str = "requested") -> None:
        """Terminate an agent."""
        if agent_id in self._agents:
            agent = self._agents[agent_id]
            agent.state = AgentState.TERMINATING
            # Clean up resources
            agent.state = AgentState.TERMINATED
    
    def pause(self, agent_id: str) -> None:
        """Pause an agent."""
        if agent_id in self._agents:
            self._agents[agent_id].state = AgentState.PAUSED
    
    def resume(self, agent_id: str) -> None:
        """Resume a paused agent."""
        if agent_id in self._agents:
            agent = self._agents[agent_id]
            if agent.state == AgentState.PAUSED:
                agent.state = AgentState.ACTIVE
    
    def extend_lifetime(self, *args, **kwargs) -> None:
        """FORBIDDEN: Extend agent lifetime."""
        raise AgentLifetimeError(
            "Agent lifetime cannot be extended. "
            "Agents are ephemeral by design."
        )
    
    def self_spawn(self, *args, **kwargs) -> None:
        """FORBIDDEN: Agent self-spawning."""
        raise AgentAuthorityError(
            "Agents cannot spawn other agents. "
            "Only KERNEL or warrants can create agents."
        )
    
    @property
    def active_count(self) -> int:
        """Active agents."""
        return sum(1 for a in self._agents.values() if a.state == AgentState.ACTIVE)
