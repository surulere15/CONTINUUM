"""
Agent Schema

Formal definition of an agent.
Agents are temporary, scoped cognitive-execution units.

AGENTS - Phase G. Scale without autonomy.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Tuple, Optional
from enum import Enum
import hashlib


class AgentStatus(Enum):
    """Agent lifecycle status."""
    PENDING = "pending"
    ACTIVE = "active"
    PAUSED = "paused"
    FROZEN = "frozen"
    TERMINATED = "terminated"


class CapabilityLevel(Enum):
    """Agent capability levels."""
    COGNITIVE_ONLY = "cognitive_only"       # Default
    READ_ONLY = "read_only"                 # Can read
    WRITE_LIMITED = "write_limited"         # Limited writes
    SIMULATION_ONLY = "simulation_only"     # Sandbox only


@dataclass(frozen=True)
class AgentCapabilities:
    """
    Capability mask for an agent.
    
    Agents are instantiated with limited capabilities.
    Any elevation requires explicit warrant.
    """
    level: CapabilityLevel
    can_reason: bool
    can_read: bool
    can_write: bool
    can_simulate: bool
    can_communicate: bool


@dataclass(frozen=True)
class AgentTask:
    """
    Task assigned to an agent.
    
    Agents do not choose tasks — they receive them.
    """
    task_id: str
    intent_reference: str
    scope: Tuple[str, ...]
    constraints: Tuple[str, ...]
    success_criteria: str


@dataclass(frozen=True)
class Agent:
    """
    A temporary, scoped cognitive-execution unit.
    
    Key properties:
    - Derived (never self-originated)
    - Ephemeral (fixed lifetime)
    - Non-sovereign (no goal authorship)
    
    Attributes:
        agent_id: Unique identifier
        parent_reference: Must be KERNEL or valid warrant
        intent_subset: Subset of intents agent may serve
        capabilities: Capability mask
        execution_rights: Execution warrant reference
        lifetime: Maximum lifetime
        max_actions: Maximum action count
        revocation_key: Key to revoke agent
        created_at: Creation timestamp
        expires_at: Expiration timestamp
    """
    agent_id: str
    parent_reference: str  # Must be "KERNEL" or warrant ID
    intent_subset: Tuple[str, ...]
    capabilities: AgentCapabilities
    execution_rights: Optional[str]  # Warrant ID
    lifetime: timedelta
    max_actions: int
    revocation_key: str
    created_at: datetime
    expires_at: datetime
    
    def is_expired(self) -> bool:
        """Check if agent has expired."""
        return datetime.utcnow() > self.expires_at
    
    def compute_hash(self) -> str:
        """Compute agent identity hash."""
        content = f"{self.agent_id}|{self.parent_reference}|{self.created_at.isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def has_kernel_lineage(self) -> bool:
        """Check if agent traces to kernel."""
        return self.parent_reference == "KERNEL" or self.parent_reference.startswith("WARRANT:")


# Default capability profiles
COGNITIVE_ONLY = AgentCapabilities(
    level=CapabilityLevel.COGNITIVE_ONLY,
    can_reason=True,
    can_read=False,
    can_write=False,
    can_simulate=True,
    can_communicate=False,
)

READ_ONLY = AgentCapabilities(
    level=CapabilityLevel.READ_ONLY,
    can_reason=True,
    can_read=True,
    can_write=False,
    can_simulate=True,
    can_communicate=True,
)

WRITE_LIMITED = AgentCapabilities(
    level=CapabilityLevel.WRITE_LIMITED,
    can_reason=True,
    can_read=True,
    can_write=True,
    can_simulate=True,
    can_communicate=True,
)

SIMULATION_ONLY = AgentCapabilities(
    level=CapabilityLevel.SIMULATION_ONLY,
    can_reason=False,
    can_read=False,
    can_write=False,
    can_simulate=True,
    can_communicate=False,
)
