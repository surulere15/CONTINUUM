"""
Authority Hierarchy

6-level hierarchy. Human input is interpreted, not obeyed blindly.

OSD - Objective Supremacy Doctrine.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from enum import Enum


class AuthorityLevel(Enum):
    """Authority hierarchy levels (1 = highest)."""
    KERNEL_INVARIANTS = 1
    ACTIVE_OBJECTIVES = 2
    GOVERNANCE_CONSTRAINTS = 3
    HUMAN_INPUTS = 4
    INTERNAL_AGENTS = 5
    TOOLS_APIS = 6


@dataclass(frozen=True)
class AuthorityDecision:
    """Decision on authority conflict."""
    decision_id: str
    higher_authority: AuthorityLevel
    lower_authority: AuthorityLevel
    winner: AuthorityLevel
    reason: str
    decided_at: datetime


class AuthorityViolationError(Exception):
    """Raised when lower authority overrides higher."""
    pass


class AuthorityHierarchy:
    """
    Authority Hierarchy.
    
    1. CONTINUUM Kernel Invariants
    2. Active Objectives (ranked)
    3. Governance Constraints
    4. Human Inputs (interpreted)
    5. Internal Agents
    6. Tools / APIs
    
    Human input is interpreted, not obeyed blindly.
    """
    
    def __init__(self):
        """Initialize hierarchy."""
        self._decisions: List[AuthorityDecision] = []
        self._decision_count = 0
    
    def resolve_conflict(
        self,
        authority_a: AuthorityLevel,
        authority_b: AuthorityLevel,
        context: str,
    ) -> AuthorityDecision:
        """
        Resolve conflict between authorities.
        
        Higher numbered authority loses.
        
        Args:
            authority_a: First authority
            authority_b: Second authority
            context: Conflict context
            
        Returns:
            AuthorityDecision
        """
        # Lower value = higher authority
        if authority_a.value < authority_b.value:
            winner = authority_a
            loser = authority_b
        else:
            winner = authority_b
            loser = authority_a
        
        decision_id = f"authority_{self._decision_count}"
        self._decision_count += 1
        
        decision = AuthorityDecision(
            decision_id=decision_id,
            higher_authority=winner,
            lower_authority=loser,
            winner=winner,
            reason=f"{winner.name} supersedes {loser.name}",
            decided_at=datetime.utcnow(),
        )
        
        self._decisions.append(decision)
        return decision
    
    def check_can_override(
        self,
        challenger: AuthorityLevel,
        target: AuthorityLevel,
    ) -> bool:
        """
        Check if challenger can override target.
        
        Only higher authority can override lower.
        """
        if challenger.value >= target.value:
            raise AuthorityViolationError(
                f"{challenger.name} (level {challenger.value}) cannot override "
                f"{target.name} (level {target.value}). "
                f"Higher authority prevails."
            )
        
        return True
    
    def human_override_objective(self, *args, **kwargs) -> None:
        """FORBIDDEN: Human casually overriding objective."""
        raise AuthorityViolationError(
            "Human inputs (level 4) cannot casually override "
            "Active Objectives (level 2). "
            "Use governance procedures for objective changes."
        )
    
    def agent_override_governance(self, *args, **kwargs) -> None:
        """FORBIDDEN: Agent overriding governance."""
        raise AuthorityViolationError(
            "Internal Agents (level 5) cannot override "
            "Governance Constraints (level 3)."
        )
    
    def get_level_name(self, level: int) -> str:
        """Get authority name by level."""
        for auth in AuthorityLevel:
            if auth.value == level:
                return auth.name
        return "UNKNOWN"
