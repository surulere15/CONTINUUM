"""
Reversibility Awareness Invariant

A_t = (effect, reversibility, confidence)

Actions without reversibility metadata are rejected.

NCE INVARIANT 5 - Neural Continuum Engine.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from enum import Enum


class Reversibility(Enum):
    """Reversibility classification."""
    FULLY_REVERSIBLE = "fully_reversible"
    PARTIALLY_REVERSIBLE = "partially_reversible"
    IRREVERSIBLE = "irreversible"


@dataclass(frozen=True)
class ActionMetadata:
    """
    Complete action metadata.
    
    A_t = (effect, reversibility, confidence)
    
    Every action must declare this metadata.
    """
    action_id: str
    effect: str
    reversibility: Reversibility
    confidence: float  # 0.0-1.0
    rollback_procedure: Optional[str]
    timestamp: datetime


class MissingMetadataError(Exception):
    """Raised when action lacks required metadata."""
    pass


class ReversibilityAwareness:
    """
    Enforces Invariant 5: Reversibility Awareness.
    
    A_t = (effect, reversibility, confidence)
    
    Actions without reversibility metadata are rejected.
    """
    
    def __init__(self):
        """Initialize reversibility tracker."""
        self._actions: List[ActionMetadata] = []
        self._rejection_count = 0
    
    def validate_action(
        self,
        action_id: str,
        effect: Optional[str] = None,
        reversibility: Optional[Reversibility] = None,
        confidence: Optional[float] = None,
        rollback_procedure: Optional[str] = None,
    ) -> ActionMetadata:
        """
        Validate action has complete metadata.
        
        Args:
            action_id: Action identifier
            effect: What the action does
            reversibility: How reversible
            confidence: Confidence level
            rollback_procedure: How to roll back
            
        Returns:
            ActionMetadata
            
        Raises:
            MissingMetadataError: If metadata incomplete
        """
        errors = []
        
        if effect is None:
            errors.append("effect")
        
        if reversibility is None:
            errors.append("reversibility")
        
        if confidence is None:
            errors.append("confidence")
        
        # Irreversible actions require explicit acknowledgment
        if reversibility == Reversibility.IRREVERSIBLE and rollback_procedure is None:
            errors.append("rollback_procedure (required for irreversible)")
        
        if errors:
            self._rejection_count += 1
            raise MissingMetadataError(
                f"Action '{action_id}' rejected. Missing metadata: {errors}. "
                f"A_t = (effect, reversibility, confidence) is required."
            )
        
        metadata = ActionMetadata(
            action_id=action_id,
            effect=effect,
            reversibility=reversibility,
            confidence=confidence,
            rollback_procedure=rollback_procedure,
            timestamp=datetime.utcnow(),
        )
        
        self._actions.append(metadata)
        return metadata
    
    def submit_incomplete_action(self, *args, **kwargs) -> None:
        """FORBIDDEN: Submit action without metadata."""
        raise MissingMetadataError(
            "Incomplete actions are rejected. "
            "All actions must declare reversibility metadata."
        )
    
    def hide_reversibility(self, *args, **kwargs) -> None:
        """FORBIDDEN: Hide reversibility status."""
        raise MissingMetadataError(
            "Reversibility cannot be hidden. "
            "All actions must be transparent about their reversibility."
        )
    
    def get_irreversible_actions(self) -> List[ActionMetadata]:
        """Get all irreversible actions taken."""
        return [
            a for a in self._actions 
            if a.reversibility == Reversibility.IRREVERSIBLE
        ]
    
    @property
    def action_count(self) -> int:
        """Total validated actions."""
        return len(self._actions)
    
    @property
    def rejection_count(self) -> int:
        """Total rejected actions."""
        return self._rejection_count
