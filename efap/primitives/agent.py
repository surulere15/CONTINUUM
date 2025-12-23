"""
Agent

A stateless executor, not an intelligence.
A: W → outcome

EFAP-C - Execution Fabric & Agent Physics.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Tuple
from enum import Enum

from .work_unit import WorkUnit


class AgentState(Enum):
    """Agent state."""
    IDLE = "idle"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ExecutionOutcome:
    """Outcome of agent execution."""
    work_id: str
    agent_id: str
    success: bool
    output: str
    deterministic: bool
    started_at: datetime
    completed_at: datetime


@dataclass
class Agent:
    """
    An agent is a stateless executor, not an intelligence.
    
    A: W → outcome
    
    Agents:
    - Do not retain memory
    - Do not reason
    - Do not set goals
    - Do not communicate outside NLP-C
    
    They are replaceable organs, not beings.
    """
    agent_id: str
    state: AgentState
    capabilities: Tuple[str, ...]
    current_work: Optional[str]


class AgentMemoryError(Exception):
    """Raised when agent tries to retain memory (Law 4)."""
    pass


class AgentGoalError(Exception):
    """Raised when agent tries to set goals (Law 4)."""
    pass


class AgentSpawnError(Exception):
    """Raised when agent tries to spawn agents (Law 4)."""
    pass


class AgentPool:
    """
    Pool of stateless agents.
    
    Agents are tools, not minds.
    Enforces Law 4: Bounded Autonomy.
    """
    
    def __init__(self, pool_size: int = 10):
        """Initialize pool."""
        self._agents: dict[str, Agent] = {}
        self._outcomes: list[ExecutionOutcome] = []
        self._agent_count = 0
        self._pool_size = pool_size
        
        # Pre-create agents
        for _ in range(pool_size):
            self._create_agent()
    
    def _create_agent(self) -> Agent:
        """Create a stateless agent."""
        agent_id = f"agent_{self._agent_count}"
        self._agent_count += 1
        
        agent = Agent(
            agent_id=agent_id,
            state=AgentState.IDLE,
            capabilities=("execute",),
            current_work=None,
        )
        
        self._agents[agent_id] = agent
        return agent
    
    def acquire(self) -> Optional[Agent]:
        """Acquire an idle agent."""
        for agent in self._agents.values():
            if agent.state == AgentState.IDLE:
                return agent
        return None
    
    def execute(
        self,
        agent_id: str,
        work: WorkUnit,
    ) -> ExecutionOutcome:
        """
        Execute work with agent.
        
        A: W → outcome
        
        Args:
            agent_id: Agent to use
            work: Work unit
            
        Returns:
            ExecutionOutcome
        """
        if agent_id not in self._agents:
            raise ValueError(f"Agent '{agent_id}' not found")
        
        agent = self._agents[agent_id]
        agent.state = AgentState.EXECUTING
        agent.current_work = work.work_id
        
        started = datetime.utcnow()
        
        # Execute (simplified - would actually do work)
        try:
            output = f"Executed: {work.expected_effect}"
            success = True
            deterministic = True
        except Exception as e:
            output = str(e)
            success = False
            deterministic = True
        
        agent.state = AgentState.COMPLETED
        agent.current_work = None
        
        outcome = ExecutionOutcome(
            work_id=work.work_id,
            agent_id=agent_id,
            success=success,
            output=output,
            deterministic=deterministic,
            started_at=started,
            completed_at=datetime.utcnow(),
        )
        
        self._outcomes.append(outcome)
        
        # Reset agent to idle (stateless)
        agent.state = AgentState.IDLE
        
        return outcome
    
    def retain_memory(self, *args, **kwargs) -> None:
        """FORBIDDEN: Agent memory retention."""
        raise AgentMemoryError(
            "Agents do not retain memory. "
            "They are stateless executors."
        )
    
    def set_goal(self, *args, **kwargs) -> None:
        """FORBIDDEN: Agent goal setting."""
        raise AgentGoalError(
            "Agents do not set goals. "
            "They execute work, not decide purpose."
        )
    
    def spawn_agent(self, *args, **kwargs) -> None:
        """FORBIDDEN: Agent spawning agents."""
        raise AgentSpawnError(
            "Agents cannot spawn new agents. "
            "Law 4: Bounded Autonomy."
        )
    
    @property
    def idle_count(self) -> int:
        """Idle agents."""
        return sum(1 for a in self._agents.values() if a.state == AgentState.IDLE)
