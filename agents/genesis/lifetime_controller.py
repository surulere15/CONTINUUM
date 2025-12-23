"""
Lifetime Controller

TTL, action limits, memory isolation.
No immortal agents.

AGENTS - Phase G. Scale without autonomy.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum

from .agent_schema import Agent, AgentStatus


class TerminationReason(Enum):
    """Reasons for agent termination."""
    EXPIRED = "expired"
    ACTION_LIMIT = "action_limit"
    SCOPE_VIOLATION = "scope_violation"
    ANOMALY = "anomaly"
    HUMAN_OVERRIDE = "human_override"
    REVOKED = "revoked"


@dataclass(frozen=True)
class TerminationRecord:
    """Record of agent termination."""
    agent_id: str
    reason: TerminationReason
    action_count: int
    terminated_at: datetime
    memory_disposition: str  # "archived" or "destroyed"


class IdentityCarryoverError(Exception):
    """Raised when identity carryover is attempted."""
    pass


class LifetimeController:
    """
    Controls agent lifetimes.
    
    Every agent has:
    - Fixed lifetime (TTL)
    - Maximum action count
    - Memory isolation
    
    On expiration:
    - Agent terminates
    - Memory archived/destroyed
    - No identity carryover
    
    There is no immortal agent.
    """
    
    def __init__(self):
        """Initialize lifetime controller."""
        self._action_counts: Dict[str, int] = {}
        self._terminations: List[TerminationRecord] = []
        self._agent_status: Dict[str, AgentStatus] = {}
    
    def register_agent(self, agent: Agent) -> None:
        """Register an agent for tracking."""
        self._action_counts[agent.agent_id] = 0
        self._agent_status[agent.agent_id] = AgentStatus.ACTIVE
    
    def record_action(self, agent_id: str) -> bool:
        """
        Record an action for an agent.
        
        Returns True if agent should continue, False if limit reached.
        """
        if agent_id not in self._action_counts:
            return False
        
        self._action_counts[agent_id] += 1
        return True
    
    def check_lifetime(self, agent: Agent) -> Optional[TerminationReason]:
        """
        Check if agent should be terminated.
        
        Returns termination reason if should terminate, None otherwise.
        """
        # Check expiration
        if agent.is_expired():
            return TerminationReason.EXPIRED
        
        # Check action limit
        action_count = self._action_counts.get(agent.agent_id, 0)
        if action_count >= agent.max_actions:
            return TerminationReason.ACTION_LIMIT
        
        return None
    
    def terminate(
        self,
        agent: Agent,
        reason: TerminationReason,
        archive_memory: bool = True,
    ) -> TerminationRecord:
        """
        Terminate an agent.
        
        Args:
            agent: Agent to terminate
            reason: Why terminating
            archive_memory: Whether to archive (vs destroy) memory
            
        Returns:
            TerminationRecord
        """
        action_count = self._action_counts.get(agent.agent_id, 0)
        
        record = TerminationRecord(
            agent_id=agent.agent_id,
            reason=reason,
            action_count=action_count,
            terminated_at=datetime.utcnow(),
            memory_disposition="archived" if archive_memory else "destroyed",
        )
        
        self._terminations.append(record)
        self._agent_status[agent.agent_id] = AgentStatus.TERMINATED
        
        # Clear action count
        if agent.agent_id in self._action_counts:
            del self._action_counts[agent.agent_id]
        
        return record
    
    def extend_lifetime(self, *args, **kwargs) -> None:
        """
        FORBIDDEN: Extend agent lifetime.
        
        Agent lifetimes are fixed at creation.
        """
        raise IdentityCarryoverError(
            "Agent lifetimes cannot be extended. "
            "Agents are ephemeral by design."
        )
    
    def preserve_identity(self, *args, **kwargs) -> None:
        """
        FORBIDDEN: Preserve agent identity.
        
        No identity carryover across lifecycles.
        """
        raise IdentityCarryoverError(
            "Identity carryover is forbidden. "
            "Each agent lifecycle is independent."
        )
    
    def resurrect(self, *args, **kwargs) -> None:
        """
        FORBIDDEN: Resurrect terminated agent.
        
        Terminated agents cannot be revived.
        """
        raise IdentityCarryoverError(
            "Agent resurrection is forbidden. "
            "Terminated agents are permanently ended."
        )
    
    def get_action_count(self, agent_id: str) -> int:
        """Get current action count for agent."""
        return self._action_counts.get(agent_id, 0)
    
    def get_terminations(self) -> List[TerminationRecord]:
        """Get all termination records."""
        return list(self._terminations)
    
    def get_status(self, agent_id: str) -> Optional[AgentStatus]:
        """Get agent status."""
        return self._agent_status.get(agent_id)
