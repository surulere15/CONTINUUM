"""
Agent Lineage

Every agent carries a lineage chain for accountability.

AGP-C - Agent Genesis Protocol.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass(frozen=True)
class AgentLineage:
    """
    Agent lineage chain.
    
    Every agent carries:
    - creator_agent
    - originating_goal
    - kernel_version
    - creation_time
    
    Ensures:
    - Accountability
    - Post-mortem analysis
    - Evolutionary traceability
    """
    lineage_id: str
    agent_id: str
    creator_agent: str       # "KERNEL" or parent agent ID
    originating_goal: str
    kernel_version: str
    creation_time: datetime
    depth: int               # Generation depth (KERNEL = 0)


class LineageDepthError(Exception):
    """Raised when lineage depth exceeded."""
    pass


class LineageTracker:
    """
    Tracks agent lineage for accountability.
    
    Enforces non-recursive creation limits.
    """
    
    MAX_DEPTH = 3  # Maximum generation depth
    
    def __init__(self, kernel_version: str = "1.0.0"):
        """Initialize tracker."""
        self._lineages: dict[str, AgentLineage] = {}
        self._lineage_count = 0
        self._kernel_version = kernel_version
    
    def create(
        self,
        agent_id: str,
        creator_agent: str,
        originating_goal: str,
    ) -> AgentLineage:
        """
        Create lineage for agent.
        
        Args:
            agent_id: New agent
            creator_agent: Creator (KERNEL or agent ID)
            originating_goal: Goal that triggered creation
            
        Returns:
            AgentLineage
        """
        # Calculate depth
        if creator_agent == "KERNEL":
            depth = 1
        elif creator_agent in self._lineages:
            parent_depth = self._lineages[creator_agent].depth
            depth = parent_depth + 1
            
            # Check max depth
            if depth > self.MAX_DEPTH:
                raise LineageDepthError(
                    f"Maximum lineage depth ({self.MAX_DEPTH}) exceeded. "
                    f"Non-recursive creation law violated."
                )
        else:
            depth = 1
        
        lineage_id = f"lineage_{self._lineage_count}"
        self._lineage_count += 1
        
        lineage = AgentLineage(
            lineage_id=lineage_id,
            agent_id=agent_id,
            creator_agent=creator_agent,
            originating_goal=originating_goal,
            kernel_version=self._kernel_version,
            creation_time=datetime.utcnow(),
            depth=depth,
        )
        
        self._lineages[agent_id] = lineage
        return lineage
    
    def get_ancestry(self, agent_id: str) -> List[AgentLineage]:
        """Get full ancestry of agent."""
        ancestry = []
        current_id = agent_id
        
        while current_id in self._lineages:
            lineage = self._lineages[current_id]
            ancestry.append(lineage)
            
            if lineage.creator_agent == "KERNEL":
                break
            
            current_id = lineage.creator_agent
        
        return ancestry
    
    def get_descendants(self, agent_id: str) -> List[AgentLineage]:
        """Get all descendants of agent."""
        return [
            l for l in self._lineages.values()
            if l.creator_agent == agent_id
        ]
    
    def get(self, agent_id: str) -> Optional[AgentLineage]:
        """Get lineage for agent."""
        return self._lineages.get(agent_id)
    
    @property
    def total_agents(self) -> int:
        """Total agents tracked."""
        return len(self._lineages)
