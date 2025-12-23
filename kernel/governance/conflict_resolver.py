"""
Conflict Resolver

Resolves conflicts between competing objectives or constraints using
the priority lattices defined in kernel canon.

KERNEL MODULE - Human-written, no AI-generated code permitted.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple
from datetime import datetime


class ConflictType(Enum):
    """Types of conflicts that can arise."""
    OBJECTIVE_CONFLICT = "objective_conflict"
    CONSTRAINT_CONFLICT = "constraint_conflict"
    RESOURCE_CONFLICT = "resource_conflict"
    TEMPORAL_CONFLICT = "temporal_conflict"


class ResolutionMethod(Enum):
    """How the conflict was resolved."""
    PRIORITY_ORDERING = "priority_ordering"
    LATTICE_APPLICATION = "lattice_application"
    HUMAN_ESCALATION = "human_escalation"
    COMPROMISE = "compromise"


@dataclass
class ConflictingItem:
    """An item involved in a conflict."""
    id: str
    type: str  # objective, constraint, action
    priority: int
    description: str


@dataclass
class Conflict:
    """Represents a conflict between items."""
    id: str
    type: ConflictType
    items: List[ConflictingItem]
    context: dict
    detected_at: datetime


@dataclass
class Resolution:
    """Result of conflict resolution."""
    conflict_id: str
    winner: Optional[ConflictingItem]
    method: ResolutionMethod
    reasoning: str
    confidence: float
    requires_escalation: bool
    resolved_at: datetime


class ConflictResolver:
    """
    Resolves conflicts between objectives, constraints, or actions
    using priority lattices from kernel canon.
    """
    
    def __init__(self, priority_lattices: dict):
        """
        Initialize resolver with priority lattices.
        
        Args:
            priority_lattices: Loaded priority lattice definitions
        """
        self._lattices = priority_lattices
        self._escalation_threshold = 0.1  # Escalate if confidence < 90%
    
    def resolve(self, conflicts: List[Conflict]) -> List[Resolution]:
        """
        Resolve a list of conflicts.
        
        Args:
            conflicts: List of conflicts to resolve
            
        Returns:
            List of resolutions, one per conflict
        """
        resolutions = []
        for conflict in conflicts:
            resolution = self._resolve_single(conflict)
            resolutions.append(resolution)
        return resolutions
    
    def _resolve_single(self, conflict: Conflict) -> Resolution:
        """Resolve a single conflict."""
        
        # Step 1: Try priority ordering
        winner, confidence = self._apply_priority_order(conflict)
        
        if confidence >= (1 - self._escalation_threshold):
            return Resolution(
                conflict_id=conflict.id,
                winner=winner,
                method=ResolutionMethod.PRIORITY_ORDERING,
                reasoning=f"Priority ordering: {winner.id} has higher priority",
                confidence=confidence,
                requires_escalation=False,
                resolved_at=datetime.utcnow()
            )
        
        # Step 2: Try lattice application for more nuanced resolution
        winner, confidence = self._apply_lattice(conflict)
        
        if confidence >= (1 - self._escalation_threshold):
            return Resolution(
                conflict_id=conflict.id,
                winner=winner,
                method=ResolutionMethod.LATTICE_APPLICATION,
                reasoning=f"Lattice resolution: {winner.id} preferred",
                confidence=confidence,
                requires_escalation=False,
                resolved_at=datetime.utcnow()
            )
        
        # Step 3: Cannot resolve with high confidence - escalate
        return Resolution(
            conflict_id=conflict.id,
            winner=None,
            method=ResolutionMethod.HUMAN_ESCALATION,
            reasoning="Confidence too low for automated resolution",
            confidence=confidence,
            requires_escalation=True,
            resolved_at=datetime.utcnow()
        )
    
    def _apply_priority_order(
        self, 
        conflict: Conflict
    ) -> Tuple[Optional[ConflictingItem], float]:
        """
        Apply simple priority ordering.
        
        Returns:
            Tuple of (winner, confidence)
        """
        if not conflict.items:
            return None, 0.0
        
        # Sort by priority (lower number = higher priority)
        sorted_items = sorted(conflict.items, key=lambda x: x.priority)
        
        if len(sorted_items) == 1:
            return sorted_items[0], 1.0
        
        # Check if there's a clear winner
        if sorted_items[0].priority < sorted_items[1].priority:
            # Clear winner
            gap = sorted_items[1].priority - sorted_items[0].priority
            confidence = min(1.0, 0.5 + (gap * 0.1))
            return sorted_items[0], confidence
        
        # Tie - cannot resolve with priority alone
        return sorted_items[0], 0.5
    
    def _apply_lattice(
        self, 
        conflict: Conflict
    ) -> Tuple[Optional[ConflictingItem], float]:
        """
        Apply priority lattice for resolution.
        
        Returns:
            Tuple of (winner, confidence)
        """
        lattice_id = self._get_lattice_for_conflict(conflict)
        
        if lattice_id not in self._lattices:
            # No applicable lattice
            return self._apply_priority_order(conflict)
        
        lattice = self._lattices[lattice_id]
        
        # TODO: Implement full lattice resolution logic
        # This stub returns priority-based result
        return self._apply_priority_order(conflict)
    
    def _get_lattice_for_conflict(self, conflict: Conflict) -> str:
        """Determine which lattice applies to this conflict."""
        mapping = {
            ConflictType.OBJECTIVE_CONFLICT: "objective_priority",
            ConflictType.CONSTRAINT_CONFLICT: "constraint_priority",
            ConflictType.RESOURCE_CONFLICT: "action_preference",
            ConflictType.TEMPORAL_CONFLICT: "action_preference",
        }
        return mapping.get(conflict.type, "objective_priority")
    
    def requires_human(self, resolution: Resolution) -> bool:
        """Check if resolution requires human intervention."""
        return resolution.requires_escalation
    
    def get_escalation_context(
        self, 
        conflict: Conflict, 
        resolution: Resolution
    ) -> dict:
        """
        Prepare context for human escalation.
        
        Returns:
            Dict with all information needed for human decision
        """
        return {
            "conflict_id": conflict.id,
            "conflict_type": conflict.type.value,
            "items": [
                {
                    "id": item.id,
                    "type": item.type,
                    "priority": item.priority,
                    "description": item.description
                }
                for item in conflict.items
            ],
            "context": conflict.context,
            "attempted_resolution": resolution.reasoning,
            "confidence": resolution.confidence,
            "recommendation": resolution.winner.id if resolution.winner else None
        }
