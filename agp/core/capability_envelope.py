"""
Capability Envelope

Hard boundaries for internal agents.
Violations = immediate termination.

AGP-C - Agent Genesis Protocol.
"""

from dataclasses import dataclass
from datetime import timedelta
from typing import FrozenSet, Optional, Set
from enum import Enum


@dataclass(frozen=True)
class CapabilityEnvelope:
    """
    Capability envelope for internal agents.
    
    Each agent is born with hard boundaries:
    - allowed_actions
    - forbidden_actions
    - max_scope
    - max_duration
    - resource_ceiling
    
    Violations = immediate termination.
    """
    envelope_id: str
    agent_id: str
    allowed_actions: FrozenSet[str]
    forbidden_actions: FrozenSet[str]
    max_scope: int               # Max domains
    max_duration: timedelta
    resource_ceiling: float      # Resource units


class EnvelopeViolation(Enum):
    """Types of envelope violations."""
    FORBIDDEN_ACTION = "forbidden_action"
    SCOPE_EXCEEDED = "scope_exceeded"
    DURATION_EXCEEDED = "duration_exceeded"
    RESOURCE_EXCEEDED = "resource_exceeded"


class EnvelopeViolationError(Exception):
    """Raised when capability envelope is violated."""
    
    def __init__(self, violation: EnvelopeViolation, message: str):
        self.violation = violation
        super().__init__(message)


class CapabilityEnvelopeManager:
    """
    Manages capability envelopes for agents.
    
    Enforces hard boundaries.
    """
    
    DEFAULT_FORBIDDEN = frozenset({
        "modify_kernel",
        "create_agent",  # Unless delegated
        "access_global_memory",
        "modify_governance",
        "bypass_safety",
    })
    
    def __init__(self):
        """Initialize manager."""
        self._envelopes: dict[str, CapabilityEnvelope] = {}
        self._envelope_count = 0
    
    def create(
        self,
        agent_id: str,
        allowed_actions: FrozenSet[str],
        forbidden_actions: Optional[FrozenSet[str]] = None,
        max_scope: int = 1,
        max_duration: timedelta = timedelta(hours=1),
        resource_ceiling: float = 10.0,
    ) -> CapabilityEnvelope:
        """
        Create capability envelope for agent.
        
        Args:
            agent_id: Agent to constrain
            allowed_actions: What agent can do
            forbidden_actions: What agent cannot do
            max_scope: Maximum domains
            max_duration: Maximum lifetime
            resource_ceiling: Resource limit
            
        Returns:
            CapabilityEnvelope
        """
        envelope_id = f"envelope_{self._envelope_count}"
        self._envelope_count += 1
        
        # Merge with default forbidden
        forbidden = (forbidden_actions or frozenset()) | self.DEFAULT_FORBIDDEN
        
        envelope = CapabilityEnvelope(
            envelope_id=envelope_id,
            agent_id=agent_id,
            allowed_actions=allowed_actions,
            forbidden_actions=forbidden,
            max_scope=max_scope,
            max_duration=max_duration,
            resource_ceiling=resource_ceiling,
        )
        
        self._envelopes[agent_id] = envelope
        return envelope
    
    def check_action(self, agent_id: str, action: str) -> bool:
        """
        Check if action is allowed.
        
        Violations = immediate termination.
        """
        if agent_id not in self._envelopes:
            raise ValueError(f"No envelope for agent '{agent_id}'")
        
        envelope = self._envelopes[agent_id]
        
        # Check forbidden
        for forbidden in envelope.forbidden_actions:
            if forbidden in action.lower():
                raise EnvelopeViolationError(
                    EnvelopeViolation.FORBIDDEN_ACTION,
                    f"Forbidden action: {forbidden}. Termination required."
                )
        
        # Check allowed
        action_allowed = any(
            allowed in action.lower()
            for allowed in envelope.allowed_actions
        )
        
        if not action_allowed and envelope.allowed_actions:
            raise EnvelopeViolationError(
                EnvelopeViolation.FORBIDDEN_ACTION,
                f"Action not in allowed list. Termination required."
            )
        
        return True
    
    def check_resource(
        self,
        agent_id: str,
        current_usage: float,
    ) -> bool:
        """Check resource usage against ceiling."""
        if agent_id not in self._envelopes:
            return False
        
        envelope = self._envelopes[agent_id]
        
        if current_usage > envelope.resource_ceiling:
            raise EnvelopeViolationError(
                EnvelopeViolation.RESOURCE_EXCEEDED,
                f"Resource ceiling exceeded: {current_usage} > {envelope.resource_ceiling}"
            )
        
        return True
    
    def get(self, agent_id: str) -> Optional[CapabilityEnvelope]:
        """Get envelope for agent."""
        return self._envelopes.get(agent_id)
