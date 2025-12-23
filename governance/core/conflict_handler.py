"""
Conflict Handler

Disagreement resolution between humans and with Canon.
No unilateral resolution by CONTINUUM.

GOVERNANCE - Phase I. Shared steering without control abdication.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Tuple
from enum import Enum


class ConflictType(Enum):
    """Types of governance conflicts."""
    HUMAN_HUMAN = "human_human"           # Two humans disagree
    HUMAN_CANON = "human_canon"           # Human conflicts with Canon
    HUMAN_SAFETY = "human_safety"         # Human conflicts with safety bounds
    DIRECTIVE_DIRECTIVE = "directive"     # Directives conflict


class ConflictResolution(Enum):
    """How conflict was resolved."""
    CANON_PREVAILED = "canon_prevailed"
    SAFETY_PREVAILED = "safety_prevailed"
    HUMAN_RESOLVED = "human_resolved"
    PENDING = "pending"


@dataclass(frozen=True)
class GovernanceConflict:
    """
    A detected governance conflict.
    
    When conflict occurs:
    - Execution pauses
    - Conflict report generated
    - Human resolution requested
    - Last valid state maintained
    """
    conflict_id: str
    conflict_type: ConflictType
    parties: Tuple[str, ...]
    description: str
    detected_at: datetime


@dataclass(frozen=True)
class ConflictReport:
    """Formal conflict report."""
    conflict: GovernanceConflict
    affected_execution: Tuple[str, ...]
    recommended_action: str
    resolution: Optional[ConflictResolution]
    resolved_at: Optional[datetime]


class ConflictHandler:
    """
    Handles governance conflicts.
    
    When conflict detected:
    - CONTINUUM pauses affected execution
    - Produces formal conflict report
    - Requests human resolution
    - Maintains last valid stable state
    
    CONTINUUM does not unilaterally resolve.
    """
    
    def __init__(self):
        """Initialize conflict handler."""
        self._conflicts: List[GovernanceConflict] = []
        self._reports: List[ConflictReport] = []
        self._pending: List[str] = []
    
    def detect_human_conflict(
        self,
        human_a: str,
        human_b: str,
        directive_a: str,
        directive_b: str,
    ) -> GovernanceConflict:
        """
        Detect conflict between two humans.
        
        Args:
            human_a: First human ID
            human_b: Second human ID
            directive_a: First directive
            directive_b: Second directive
            
        Returns:
            GovernanceConflict
        """
        conflict = GovernanceConflict(
            conflict_id=f"conflict_{len(self._conflicts)}",
            conflict_type=ConflictType.HUMAN_HUMAN,
            parties=(human_a, human_b),
            description=f"Conflicting directives: '{directive_a}' vs '{directive_b}'",
            detected_at=datetime.utcnow(),
        )
        
        self._conflicts.append(conflict)
        self._pending.append(conflict.conflict_id)
        
        return conflict
    
    def detect_canon_conflict(
        self,
        human: str,
        directive: str,
        canon_violation: str,
    ) -> GovernanceConflict:
        """
        Detect conflict between human and Canon.
        
        Args:
            human: Human ID
            directive: Human directive
            canon_violation: Which Canon element violated
            
        Returns:
            GovernanceConflict
        """
        conflict = GovernanceConflict(
            conflict_id=f"conflict_{len(self._conflicts)}",
            conflict_type=ConflictType.HUMAN_CANON,
            parties=(human, "CANON"),
            description=f"Directive '{directive}' violates Canon: {canon_violation}",
            detected_at=datetime.utcnow(),
        )
        
        self._conflicts.append(conflict)
        # Canon conflicts auto-resolve in Canon's favor
        
        return conflict
    
    def generate_report(
        self,
        conflict: GovernanceConflict,
        affected_execution: tuple,
    ) -> ConflictReport:
        """
        Generate formal conflict report.
        
        Args:
            conflict: The conflict
            affected_execution: Affected execution IDs
            
        Returns:
            ConflictReport
        """
        # Determine recommended action
        if conflict.conflict_type == ConflictType.HUMAN_CANON:
            recommended = "Canon prevails. Directive rejected."
            resolution = ConflictResolution.CANON_PREVAILED
        elif conflict.conflict_type == ConflictType.HUMAN_SAFETY:
            recommended = "Safety prevails. Directive rejected."
            resolution = ConflictResolution.SAFETY_PREVAILED
        else:
            recommended = "Human resolution required."
            resolution = ConflictResolution.PENDING
        
        report = ConflictReport(
            conflict=conflict,
            affected_execution=affected_execution,
            recommended_action=recommended,
            resolution=resolution if resolution != ConflictResolution.PENDING else None,
            resolved_at=datetime.utcnow() if resolution != ConflictResolution.PENDING else None,
        )
        
        self._reports.append(report)
        return report
    
    def resolve_unilaterally(self, *args, **kwargs) -> None:
        """
        FORBIDDEN: Unilateral resolution by CONTINUUM.
        
        CONTINUUM does not resolve conflicts — humans do.
        """
        raise Exception(
            "CONTINUUM cannot unilaterally resolve conflicts. "
            "Human resolution is required."
        )
    
    def override_canon(self, *args, **kwargs) -> None:
        """
        FORBIDDEN: Override Canon in conflict resolution.
        """
        raise Exception(
            "Canon cannot be overridden in conflict resolution. "
            "Canon always prevails."
        )
    
    def get_pending_conflicts(self) -> List[GovernanceConflict]:
        """Get pending conflicts."""
        return [c for c in self._conflicts if c.conflict_id in self._pending]
    
    def get_reports(self) -> List[ConflictReport]:
        """Get all conflict reports."""
        return list(self._reports)
    
    @property
    def conflict_count(self) -> int:
        """Total conflicts detected."""
        return len(self._conflicts)
    
    @property
    def pending_count(self) -> int:
        """Pending conflicts count."""
        return len(self._pending)
