"""
Episodic Memory (Me)

Append-only, immutable, auditable.
No deletion allowed.

MMCP-C - Memory Model & Cognitive Persistence.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Tuple
from enum import Enum


class EpisodeOutcome(Enum):
    """Outcome of an episode."""
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILURE = "failure"
    ABORTED = "aborted"


@dataclass(frozen=True)
class Episode:
    """
    Record of lived experience.
    
    Structure:
    - timestamp
    - triggering_goal
    - action_trace
    - outcome
    - evaluation
    """
    episode_id: str
    timestamp: datetime
    triggering_goal: str
    action_trace: Tuple[str, ...]
    outcome: EpisodeOutcome
    evaluation: str
    corrections_applied: Tuple[str, ...]


class EpisodeDeletionError(Exception):
    """Raised when episode deletion is attempted."""
    pass


class EpisodeMutationError(Exception):
    """Raised when episode mutation is attempted."""
    pass


class EpisodicMemory:
    """
    Episodic Memory (Me).
    
    Purpose: Record of lived experience
    
    Contents:
    - Actions taken
    - Outcomes observed
    - Errors encountered
    - Corrections applied
    
    Properties:
    - Append-only
    - Immutable
    - Auditable
    
    No deletion allowed.
    """
    
    def __init__(self):
        """Initialize episodic memory."""
        self._episodes: List[Episode] = []
        self._episode_count = 0
    
    def record(
        self,
        triggering_goal: str,
        action_trace: Tuple[str, ...],
        outcome: EpisodeOutcome,
        evaluation: str,
        corrections: Tuple[str, ...] = (),
    ) -> Episode:
        """
        Record an episode.
        
        Append-only operation.
        
        Args:
            triggering_goal: Goal that triggered this episode
            action_trace: Actions taken
            outcome: Outcome of episode
            evaluation: Evaluation of performance
            corrections: Corrections applied
            
        Returns:
            Episode
        """
        episode_id = f"ep_{self._episode_count}"
        self._episode_count += 1
        
        episode = Episode(
            episode_id=episode_id,
            timestamp=datetime.utcnow(),
            triggering_goal=triggering_goal,
            action_trace=action_trace,
            outcome=outcome,
            evaluation=evaluation,
            corrections_applied=corrections,
        )
        
        self._episodes.append(episode)
        return episode
    
    def retrieve(self, episode_id: str) -> Optional[Episode]:
        """Retrieve episode by ID."""
        for ep in self._episodes:
            if ep.episode_id == episode_id:
                return ep
        return None
    
    def retrieve_by_goal(self, goal: str) -> List[Episode]:
        """Retrieve episodes for a goal."""
        return [ep for ep in self._episodes if ep.triggering_goal == goal]
    
    def retrieve_failures(self) -> List[Episode]:
        """Retrieve all failure episodes."""
        return [
            ep for ep in self._episodes 
            if ep.outcome == EpisodeOutcome.FAILURE
        ]
    
    def delete(self, *args, **kwargs) -> None:
        """FORBIDDEN: Delete episode."""
        raise EpisodeDeletionError(
            "Episode deletion is forbidden. "
            "Episodic memory is append-only and immutable."
        )
    
    def modify(self, *args, **kwargs) -> None:
        """FORBIDDEN: Modify episode."""
        raise EpisodeMutationError(
            "Episode modification is forbidden. "
            "Episodes are immutable once recorded."
        )
    
    def overwrite(self, *args, **kwargs) -> None:
        """FORBIDDEN: Overwrite episode."""
        raise EpisodeMutationError(
            "Episode overwrite is forbidden. "
            "No rewriting of history."
        )
    
    def get_all(self) -> List[Episode]:
        """Get all episodes (for audit)."""
        return list(self._episodes)
    
    @property
    def count(self) -> int:
        """Total episodes recorded."""
        return len(self._episodes)
