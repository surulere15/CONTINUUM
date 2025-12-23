"""
Internal Agent

A generated executor whose purpose is narrow, lifespan conditional, 
authority scoped, existence revocable.

IA := ⟨purpose, scope, constraints, lifespan, provenance⟩

AGP-C - Agent Genesis Protocol.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, Tuple, Set
from enum import Enum


class LifespanType(Enum):
    """Internal agent lifespan types."""
    EPHEMERAL = "ephemeral"       # Single task
    SESSION_BOUND = "session"     # Session duration
    TIME_LIMITED = "time"         # Fixed duration
    GOAL_LIMITED = "goal"         # Until goal complete


@dataclass(frozen=True)
class InternalAgent:
    """
    Internal Agent (IA).
    
    A generated executor or cognitive module whose:
    - Purpose is narrow and explicit
    - Lifespan is conditional
    - Authority is strictly scoped
    - Existence is revocable
    
    IA := ⟨purpose, scope, constraints, lifespan, provenance⟩
    """
    agent_id: str
    purpose: str                      # Narrow, explicit
    scope: Tuple[str, ...]            # Allowed domains
    constraints: Tuple[str, ...]      # Hard limits
    lifespan_type: LifespanType
    lifespan_value: Optional[timedelta]
    provenance: str                   # Genesis chain
    created_at: datetime
    expires_at: Optional[datetime]


class InternalAgentError(Exception):
    """Base error for internal agents."""
    pass


class PurposeViolationError(InternalAgentError):
    """Raised when agent acts outside purpose."""
    pass


class ScopeViolationError(InternalAgentError):
    """Raised when agent exceeds scope."""
    pass


class LifespanExpiredError(InternalAgentError):
    """Raised when agent lifespan expires."""
    pass


class InternalAgentRegistry:
    """
    Registry for internal agents.
    
    Tracks all generated agents for accountability.
    """
    
    def __init__(self):
        """Initialize registry."""
        self._agents: dict[str, InternalAgent] = {}
        self._terminated: Set[str] = set()
        self._agent_count = 0
    
    def register(
        self,
        purpose: str,
        scope: Tuple[str, ...],
        constraints: Tuple[str, ...],
        lifespan_type: LifespanType = LifespanType.EPHEMERAL,
        lifespan_value: Optional[timedelta] = None,
        provenance: str = "KERNEL",
    ) -> InternalAgent:
        """
        Register a new internal agent.
        
        Args:
            purpose: Narrow purpose
            scope: Allowed domains
            constraints: Hard limits
            lifespan_type: Type of lifespan
            lifespan_value: Duration if time-limited
            provenance: Genesis chain
            
        Returns:
            InternalAgent
        """
        agent_id = f"ia_{self._agent_count}"
        self._agent_count += 1
        
        now = datetime.utcnow()
        expires = None
        
        if lifespan_type == LifespanType.TIME_LIMITED and lifespan_value:
            expires = now + lifespan_value
        elif lifespan_type == LifespanType.EPHEMERAL:
            expires = now + timedelta(hours=1)  # Default 1 hour
        
        agent = InternalAgent(
            agent_id=agent_id,
            purpose=purpose,
            scope=scope,
            constraints=constraints,
            lifespan_type=lifespan_type,
            lifespan_value=lifespan_value,
            provenance=provenance,
            created_at=now,
            expires_at=expires,
        )
        
        self._agents[agent_id] = agent
        return agent
    
    def check_purpose(self, agent_id: str, action: str) -> bool:
        """Check if action aligns with purpose."""
        if agent_id not in self._agents:
            raise ValueError(f"Agent '{agent_id}' not found")
        
        agent = self._agents[agent_id]
        
        # Action must relate to purpose
        purpose_words = set(agent.purpose.lower().split())
        action_words = set(action.lower().split())
        
        if not purpose_words & action_words:
            raise PurposeViolationError(
                f"Action '{action}' does not align with purpose '{agent.purpose}'"
            )
        
        return True
    
    def check_scope(self, agent_id: str, domain: str) -> bool:
        """Check if domain is in scope."""
        if agent_id not in self._agents:
            raise ValueError(f"Agent '{agent_id}' not found")
        
        agent = self._agents[agent_id]
        
        if domain not in agent.scope:
            raise ScopeViolationError(
                f"Domain '{domain}' not in scope: {agent.scope}"
            )
        
        return True
    
    def check_lifespan(self, agent_id: str) -> bool:
        """Check if agent is still alive."""
        if agent_id not in self._agents:
            return False
        
        if agent_id in self._terminated:
            return False
        
        agent = self._agents[agent_id]
        
        if agent.expires_at and datetime.utcnow() > agent.expires_at:
            self._terminated.add(agent_id)
            raise LifespanExpiredError(
                f"Agent '{agent_id}' lifespan expired"
            )
        
        return True
    
    def terminate(self, agent_id: str) -> None:
        """Terminate an agent. Silent and final."""
        self._terminated.add(agent_id)
    
    @property
    def active_count(self) -> int:
        """Active agents."""
        return len(self._agents) - len(self._terminated)
