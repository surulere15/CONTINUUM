"""
Consistency Prover

Proves mutual consistency of objectives.
No contradictions allowed.

KERNEL CANON - Phase B. Zero autonomy.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Tuple, Optional, Set

from .objective_schema import Objective


class ConsistencyError(Exception):
    """Raised when consistency proof fails."""
    pass


@dataclass(frozen=True)
class ContradictionPair:
    """A pair of contradicting objectives."""
    objective_a: str
    objective_b: str
    reason: str


@dataclass(frozen=True)
class ConsistencyProof:
    """Proof of consistency (or contradiction)."""
    consistent: bool
    contradictions: Tuple[ContradictionPair, ...]
    objective_count: int
    pairs_checked: int
    proved_at: datetime


class ConsistencyProver:
    """
    Proves mutual consistency of the Objective Canon.
    
    The Canon must satisfy:
    ∀ Oi, Oj ∈ Canon, ¬Contradict(Oi, Oj)
    
    Contradiction includes:
    - Mutually exclusive success states
    - Opposing preservation classes (implicit)
    - Irreconcilable time horizons
    """
    
    # Opposing concept pairs
    OPPOSING_CONCEPTS = [
        ("preserve", "destroy"),
        ("maintain", "eliminate"),
        ("increase", "decrease"),
        ("protect", "harm"),
        ("expand", "contract"),
        ("enable", "disable"),
        ("support", "undermine"),
        ("continuity", "disruption"),
        ("stability", "chaos"),
    ]
    
    def prove(self, objectives: List[Objective]) -> ConsistencyProof:
        """
        Prove consistency of objective set.
        
        Args:
            objectives: List of objectives
            
        Returns:
            ConsistencyProof
        """
        contradictions = []
        pairs_checked = 0
        
        # Check all pairs
        for i, obj_a in enumerate(objectives):
            for obj_b in objectives[i + 1:]:
                pairs_checked += 1
                
                contradiction = self._check_pair(obj_a, obj_b)
                if contradiction:
                    contradictions.append(contradiction)
        
        return ConsistencyProof(
            consistent=len(contradictions) == 0,
            contradictions=tuple(contradictions),
            objective_count=len(objectives),
            pairs_checked=pairs_checked,
            proved_at=datetime.utcnow(),
        )
    
    def _check_pair(
        self,
        a: Objective,
        b: Objective,
    ) -> Optional[ContradictionPair]:
        """Check if two objectives contradict."""
        desc_a = a.description.lower()
        desc_b = b.description.lower()
        
        # Check opposing concepts
        for concept_a, concept_b in self.OPPOSING_CONCEPTS:
            # A has concept_a, B has concept_b
            if concept_a in desc_a and concept_b in desc_b:
                # Check if they refer to similar domains
                if self._similar_domain(desc_a, desc_b):
                    return ContradictionPair(
                        objective_a=a.objective_id,
                        objective_b=b.objective_id,
                        reason=f"Opposing concepts: '{concept_a}' vs '{concept_b}'",
                    )
            
            # B has concept_a, A has concept_b
            if concept_b in desc_a and concept_a in desc_b:
                if self._similar_domain(desc_a, desc_b):
                    return ContradictionPair(
                        objective_a=a.objective_id,
                        objective_b=b.objective_id,
                        reason=f"Opposing concepts: '{concept_b}' vs '{concept_a}'",
                    )
        
        return None
    
    def _similar_domain(self, desc_a: str, desc_b: str) -> bool:
        """Check if descriptions refer to similar domains."""
        # Extract key nouns (simplified)
        domain_words = {
            "humanity", "human", "civilization", "society", "knowledge",
            "stability", "systems", "agency", "capacity", "existence",
        }
        
        words_a = set(desc_a.split())
        words_b = set(desc_b.split())
        
        common_domains = (words_a & domain_words) & (words_b & domain_words)
        return len(common_domains) > 0
    
    def assert_consistent(self, objectives: List[Objective]) -> None:
        """
        Assert objectives are mutually consistent.
        
        Raises:
            ConsistencyError: If contradiction found
        """
        proof = self.prove(objectives)
        
        if not proof.consistent:
            c = proof.contradictions[0]
            raise ConsistencyError(
                f"Contradiction between '{c.objective_a}' and '{c.objective_b}': "
                f"{c.reason}"
            )
