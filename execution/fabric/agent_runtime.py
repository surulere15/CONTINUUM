"""
Agent Runtime

Manages agent instances, their lifecycle, and resource consumption.
"""

from dataclasses import dataclass
from typing import Dict, Optional
from datetime import datetime
from enum import Enum


class AgentState(Enum):
    PENDING = "pending"
    SPAWNING = "spawning"
    RUNNING = "running"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"


@dataclass
class AgentInstance:
    id: str
    template_id: str
    state: AgentState
    spawned_at: datetime
    resources: Dict
    task_id: Optional[str]


class AgentRuntime:
    """Manages agent instances."""
    
    def __init__(self, resource_limits: Dict):
        self._agents: Dict[str, AgentInstance] = {}
        self._limits = resource_limits
    
    def spawn(self, template_id: str, task_id: str) -> AgentInstance:
        """Spawn new agent instance."""
        agent_id = self._generate_id()
        agent = AgentInstance(
            id=agent_id,
            template_id=template_id,
            state=AgentState.SPAWNING,
            spawned_at=datetime.utcnow(),
            resources={},
            task_id=task_id
        )
        self._agents[agent_id] = agent
        agent.state = AgentState.RUNNING
        return agent
    
    def suspend(self, agent_id: str) -> bool:
        """Suspend agent."""
        if agent_id in self._agents:
            self._agents[agent_id].state = AgentState.SUSPENDED
            return True
        return False
    
    def resume(self, agent_id: str) -> bool:
        """Resume suspended agent."""
        if agent_id in self._agents and self._agents[agent_id].state == AgentState.SUSPENDED:
            self._agents[agent_id].state = AgentState.RUNNING
            return True
        return False
    
    def terminate(self, agent_id: str) -> bool:
        """Terminate agent."""
        if agent_id in self._agents:
            self._agents[agent_id].state = AgentState.TERMINATED
            return True
        return False
    
    def get(self, agent_id: str) -> Optional[AgentInstance]:
        """Get agent by ID."""
        return self._agents.get(agent_id)
    
    def _generate_id(self) -> str:
        import uuid
        return f"agent_{uuid.uuid4().hex[:8]}"
