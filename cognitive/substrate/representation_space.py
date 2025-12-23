"""
Representation Space

Internal language of thought. Ephemeral representations.
Cannot be written to long-term memory or influence objectives.

COGNITIVE MODULE - No imports from execution/agents/kernel/governance.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Set
from enum import Enum
import hashlib


class RepresentationType(Enum):
    """Types of internal representations."""
    CONCEPT = "concept"
    RELATION = "relation"
    CONSTRAINT = "constraint"
    PROVENANCE_LINK = "provenance_link"


@dataclass(frozen=True)
class Concept:
    """
    An internal concept representation.
    
    Concepts are ephemeral — they exist only during processing.
    """
    concept_id: str
    name: str
    definition: str
    attributes: tuple  # Immutable
    created_at: datetime


@dataclass(frozen=True)
class Relation:
    """
    A relation between concepts.
    
    Relations are typed and ephemeral.
    """
    relation_id: str
    source_id: str
    target_id: str
    relation_type: str
    strength: float  # 0.0 to 1.0
    created_at: datetime


@dataclass(frozen=True)
class Constraint:
    """
    A constraint on reasoning.
    
    Constraints restrict what can be concluded.
    """
    constraint_id: str
    applies_to: str  # concept_id or "*" for all
    condition: str
    enforcement: str  # "hard" or "soft"


@dataclass(frozen=True)
class ProvenanceLink:
    """
    Links representation to its source.
    
    Tracks where knowledge came from.
    """
    link_id: str
    representation_id: str
    source_type: str  # "signal", "canon", "inference"
    source_id: str
    timestamp: datetime


class MemoryWriteError(Exception):
    """Raised when attempting to write to long-term memory."""
    pass


class RepresentationSpace:
    """
    Internal representation space for cognition.
    
    Properties:
    - Representations are ephemeral
    - Cannot be written to long-term memory
    - Cannot influence objectives
    - Cleared after each reasoning session
    
    This is the "working memory" of cognition,
    not persistent storage.
    """
    
    def __init__(self):
        """Initialize empty representation space."""
        self._concepts: Dict[str, Concept] = {}
        self._relations: Dict[str, Relation] = {}
        self._constraints: Dict[str, Constraint] = {}
        self._provenance: Dict[str, ProvenanceLink] = {}
        self._session_start = datetime.utcnow()
    
    def add_concept(self, name: str, definition: str, attributes: tuple = ()) -> str:
        """
        Add a concept to the space.
        
        Returns concept_id.
        """
        concept_id = self._generate_id(f"concept:{name}:{definition}")
        concept = Concept(
            concept_id=concept_id,
            name=name,
            definition=definition,
            attributes=attributes,
            created_at=datetime.utcnow(),
        )
        self._concepts[concept_id] = concept
        return concept_id
    
    def add_relation(
        self,
        source_id: str,
        target_id: str,
        relation_type: str,
        strength: float = 1.0,
    ) -> str:
        """
        Add a relation between concepts.
        
        Returns relation_id.
        """
        relation_id = self._generate_id(f"relation:{source_id}:{target_id}:{relation_type}")
        relation = Relation(
            relation_id=relation_id,
            source_id=source_id,
            target_id=target_id,
            relation_type=relation_type,
            strength=strength,
            created_at=datetime.utcnow(),
        )
        self._relations[relation_id] = relation
        return relation_id
    
    def add_constraint(
        self,
        applies_to: str,
        condition: str,
        enforcement: str = "soft",
    ) -> str:
        """
        Add a constraint on reasoning.
        
        Returns constraint_id.
        """
        constraint_id = self._generate_id(f"constraint:{applies_to}:{condition}")
        constraint = Constraint(
            constraint_id=constraint_id,
            applies_to=applies_to,
            condition=condition,
            enforcement=enforcement,
        )
        self._constraints[constraint_id] = constraint
        return constraint_id
    
    def get_concept(self, concept_id: str) -> Optional[Concept]:
        """Get concept by ID."""
        return self._concepts.get(concept_id)
    
    def get_relations_for(self, concept_id: str) -> List[Relation]:
        """Get all relations involving a concept."""
        return [
            r for r in self._relations.values()
            if r.source_id == concept_id or r.target_id == concept_id
        ]
    
    def get_constraints_for(self, concept_id: str) -> List[Constraint]:
        """Get constraints for a concept."""
        return [
            c for c in self._constraints.values()
            if c.applies_to == concept_id or c.applies_to == "*"
        ]
    
    def clear(self) -> None:
        """
        Clear all representations.
        
        Called at end of reasoning session.
        """
        self._concepts.clear()
        self._relations.clear()
        self._constraints.clear()
        self._provenance.clear()
        self._session_start = datetime.utcnow()
    
    def persist_to_memory(self, *args, **kwargs) -> None:
        """
        FORBIDDEN: Write to long-term memory.
        
        Representations are ephemeral and cannot be persisted.
        """
        raise MemoryWriteError(
            "Representations cannot be written to long-term memory. "
            "They are ephemeral and exist only during processing."
        )
    
    def influence_objectives(self, *args, **kwargs) -> None:
        """
        FORBIDDEN: Influence objectives.
        
        Representation space cannot modify objectives.
        """
        raise MemoryWriteError(
            "Representations cannot influence objectives. "
            "Cognition has no authority over governance."
        )
    
    @property
    def concept_count(self) -> int:
        """Number of concepts in space."""
        return len(self._concepts)
    
    @property
    def relation_count(self) -> int:
        """Number of relations in space."""
        return len(self._relations)
    
    def _generate_id(self, content: str) -> str:
        """Generate deterministic ID."""
        return hashlib.sha256(content.encode()).hexdigest()[:16]
