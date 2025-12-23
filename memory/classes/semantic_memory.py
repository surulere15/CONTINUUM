"""
Semantic Memory (Mk)

Graph-based, versioned, confidence-scored.
Semantic memory is belief with provenance, not truth.

MMCP-C - Memory Model & Cognitive Persistence.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple


@dataclass(frozen=True)
class Concept:
    """A concept in semantic memory."""
    concept_id: str
    name: str
    description: str
    confidence: float  # 0.0-1.0
    provenance: str    # Where this came from
    version: int
    created_at: datetime


@dataclass(frozen=True)
class Relationship:
    """Relationship between concepts."""
    relation_id: str
    from_concept: str
    to_concept: str
    relation_type: str
    confidence: float
    version: int


class SemanticMemory:
    """
    Semantic Memory (Mk).
    
    Purpose: Stable knowledge representation
    
    Contents:
    - Concepts
    - Relationships
    - Learned abstractions
    
    Structure:
    - Graph-based
    - Versioned
    - Confidence-scored
    
    Semantic memory is not truth — it is belief with provenance.
    """
    
    CONFIDENCE_DECAY_RATE = 0.01  # Per time unit
    
    def __init__(self):
        """Initialize semantic memory."""
        self._concepts: Dict[str, Concept] = {}
        self._relationships: Dict[str, Relationship] = {}
        self._concept_count = 0
        self._relation_count = 0
    
    def add_concept(
        self,
        name: str,
        description: str,
        confidence: float,
        provenance: str,
    ) -> Concept:
        """
        Add a concept.
        
        Args:
            name: Concept name
            description: What it means
            confidence: Confidence in this belief
            provenance: Where it came from
            
        Returns:
            Concept
        """
        concept_id = f"concept_{self._concept_count}"
        self._concept_count += 1
        
        concept = Concept(
            concept_id=concept_id,
            name=name,
            description=description,
            confidence=confidence,
            provenance=provenance,
            version=1,
            created_at=datetime.utcnow(),
        )
        
        self._concepts[concept_id] = concept
        return concept
    
    def update_concept(
        self,
        concept_id: str,
        description: Optional[str] = None,
        confidence: Optional[float] = None,
        provenance: Optional[str] = None,
    ) -> Optional[Concept]:
        """
        Update concept (creates new version).
        
        Args:
            concept_id: Concept to update
            description: New description
            confidence: New confidence
            provenance: New provenance
            
        Returns:
            Updated Concept
        """
        if concept_id not in self._concepts:
            return None
        
        old = self._concepts[concept_id]
        
        new = Concept(
            concept_id=concept_id,
            name=old.name,
            description=description or old.description,
            confidence=confidence if confidence is not None else old.confidence,
            provenance=provenance or old.provenance,
            version=old.version + 1,
            created_at=datetime.utcnow(),
        )
        
        self._concepts[concept_id] = new
        return new
    
    def add_relationship(
        self,
        from_concept: str,
        to_concept: str,
        relation_type: str,
        confidence: float,
    ) -> Relationship:
        """Add relationship between concepts."""
        relation_id = f"rel_{self._relation_count}"
        self._relation_count += 1
        
        rel = Relationship(
            relation_id=relation_id,
            from_concept=from_concept,
            to_concept=to_concept,
            relation_type=relation_type,
            confidence=confidence,
            version=1,
        )
        
        self._relationships[relation_id] = rel
        return rel
    
    def query_concepts(
        self,
        min_confidence: float = 0.0,
    ) -> List[Concept]:
        """Query concepts above confidence threshold."""
        return [
            c for c in self._concepts.values()
            if c.confidence >= min_confidence
        ]
    
    def get_related(self, concept_id: str) -> List[Tuple[Relationship, Concept]]:
        """Get all concepts related to given concept."""
        results = []
        for rel in self._relationships.values():
            if rel.from_concept == concept_id:
                if rel.to_concept in self._concepts:
                    results.append((rel, self._concepts[rel.to_concept]))
            elif rel.to_concept == concept_id:
                if rel.from_concept in self._concepts:
                    results.append((rel, self._concepts[rel.from_concept]))
        return results
    
    def decay_confidence(self, amount: float = CONFIDENCE_DECAY_RATE) -> int:
        """Apply confidence decay. Returns count affected."""
        affected = 0
        for cid, concept in list(self._concepts.items()):
            new_confidence = max(0.0, concept.confidence - amount)
            if new_confidence != concept.confidence:
                self.update_concept(cid, confidence=new_confidence)
                affected += 1
        return affected
    
    @property
    def concept_count(self) -> int:
        """Total concepts."""
        return len(self._concepts)
    
    @property
    def relationship_count(self) -> int:
        """Total relationships."""
        return len(self._relationships)
