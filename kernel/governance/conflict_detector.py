"""
Conflict Detector

Detect logical, scope, and constraint conflicts between intents.
No scoring, no ranking — just detection.

KERNEL MODULE - No imports from execution/agents/learning.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Set, Tuple, Optional
from enum import Enum

from .intent_schema import Intent


class ConflictType(Enum):
    """Types of conflicts between intents."""
    DIRECT_CONTRADICTION = "direct_contradiction"  # A negates B
    SCOPE_COLLISION = "scope_collision"           # Same domain, incompatible
    CANON_VIOLATION = "canon_violation"           # Contradicts objective invariants
    TEMPORAL_INCOHERENCE = "temporal_incoherence" # Mutually exclusive timing
    CONSTRAINT_INCOMPATIBILITY = "constraint_incompatibility"


@dataclass(frozen=True)
class Conflict:
    """
    A detected conflict between intents.
    
    Conflicts are facts, not judgments.
    """
    conflict_id: str
    conflict_type: ConflictType
    intent_a_id: str
    intent_b_id: str
    description: str
    axiom_reference: Optional[str]
    detected_at: datetime


@dataclass(frozen=True)
class ConflictGraph:
    """
    Graph of all detected conflicts.
    
    Nodes are intents, edges are conflicts.
    """
    graph_id: str
    conflicts: Tuple[Conflict, ...]
    intent_ids: Tuple[str, ...]
    generated_at: datetime
    
    @property
    def has_conflicts(self) -> bool:
        """Check if any conflicts exist."""
        return len(self.conflicts) > 0
    
    def get_conflicts_for(self, intent_id: str) -> List[Conflict]:
        """Get all conflicts involving an intent."""
        return [
            c for c in self.conflicts
            if c.intent_a_id == intent_id or c.intent_b_id == intent_id
        ]


class ConflictDetector:
    """
    Detects conflicts between intents.
    
    Conflict types:
    - Direct contradiction (A negates B)
    - Scope collision (same domain, incompatible constraints)
    - Canon violation (intent contradicts objective invariants)
    - Temporal incoherence (mutually exclusive conditions)
    
    Outputs conflict graph with axiom references.
    No scoring, no ranking.
    """
    
    # Negation patterns
    NEGATION_PREFIXES = ("not ", "no ", "never ", "don't ", "do not ")
    
    def __init__(self, canon_invariants: Optional[Dict[str, str]] = None):
        """
        Initialize detector.
        
        Args:
            canon_invariants: Map of invariant IDs to expressions
        """
        self._invariants = canon_invariants or {}
        self._conflict_count = 0
    
    def detect(self, intents: List[Intent]) -> ConflictGraph:
        """
        Detect all conflicts in a set of intents.
        
        Args:
            intents: List of normalized intents
            
        Returns:
            ConflictGraph containing all detected conflicts
        """
        conflicts = []
        
        # Check pairwise conflicts
        for i, intent_a in enumerate(intents):
            for intent_b in intents[i + 1:]:
                pair_conflicts = self._check_pair(intent_a, intent_b)
                conflicts.extend(pair_conflicts)
            
            # Check against Canon invariants
            canon_conflicts = self._check_canon_violation(intent_a)
            conflicts.extend(canon_conflicts)
        
        import hashlib
        graph_id = hashlib.sha256(
            "|".join(c.conflict_id for c in conflicts).encode()
        ).hexdigest()[:16]
        
        return ConflictGraph(
            graph_id=graph_id,
            conflicts=tuple(conflicts),
            intent_ids=tuple(i.intent_id for i in intents),
            generated_at=datetime.utcnow(),
        )
    
    def _check_pair(self, a: Intent, b: Intent) -> List[Conflict]:
        """Check for conflicts between two intents."""
        conflicts = []
        
        # Direct contradiction
        contradiction = self._check_contradiction(a, b)
        if contradiction:
            conflicts.append(contradiction)
        
        # Scope collision
        collision = self._check_scope_collision(a, b)
        if collision:
            conflicts.append(collision)
        
        # Constraint incompatibility
        incompatibility = self._check_constraint_incompatibility(a, b)
        if incompatibility:
            conflicts.append(incompatibility)
        
        return conflicts
    
    def _check_contradiction(self, a: Intent, b: Intent) -> Optional[Conflict]:
        """Check for direct contradiction."""
        # Check if one negates the other
        desc_a = a.description.lower()
        desc_b = b.description.lower()
        
        for prefix in self.NEGATION_PREFIXES:
            if desc_a.startswith(prefix):
                core_a = desc_a[len(prefix):]
                if core_a in desc_b or desc_b in core_a:
                    return self._create_conflict(
                        a, b,
                        ConflictType.DIRECT_CONTRADICTION,
                        f"'{a.description}' negates '{b.description}'",
                        "bounded_autonomy"
                    )
            
            if desc_b.startswith(prefix):
                core_b = desc_b[len(prefix):]
                if core_b in desc_a or desc_a in core_b:
                    return self._create_conflict(
                        a, b,
                        ConflictType.DIRECT_CONTRADICTION,
                        f"'{b.description}' negates '{a.description}'",
                        "bounded_autonomy"
                    )
        
        return None
    
    def _check_scope_collision(self, a: Intent, b: Intent) -> Optional[Conflict]:
        """Check for scope collision."""
        if a.scope == b.scope:
            # Same scope — check for incompatible constraints
            a_constraints = set(a.constraints)
            b_constraints = set(b.constraints)
            
            # Look for opposing constraints
            for c_a in a_constraints:
                for c_b in b_constraints:
                    if self._constraints_oppose(c_a, c_b):
                        return self._create_conflict(
                            a, b,
                            ConflictType.SCOPE_COLLISION,
                            f"Scope '{a.scope}' has opposing constraints: '{c_a}' vs '{c_b}'",
                            "continuity_over_performance"
                        )
        
        return None
    
    def _check_constraint_incompatibility(self, a: Intent, b: Intent) -> Optional[Conflict]:
        """Check for direct constraint incompatibility."""
        shared_refs = set(a.references) & set(b.references)
        
        if shared_refs and a.constraints != b.constraints:
            # Same references but different constraints
            constraint_diff = set(a.constraints) ^ set(b.constraints)
            if constraint_diff:
                return self._create_conflict(
                    a, b,
                    ConflictType.CONSTRAINT_INCOMPATIBILITY,
                    f"Incompatible constraints on shared references: {constraint_diff}",
                    None
                )
        
        return None
    
    def _check_canon_violation(self, intent: Intent) -> List[Conflict]:
        """Check if intent violates Canon invariants."""
        conflicts = []
        
        for inv_id, inv_expr in self._invariants.items():
            if self._violates_invariant(intent, inv_expr):
                self._conflict_count += 1
                conflict = Conflict(
                    conflict_id=f"conflict_{self._conflict_count}",
                    conflict_type=ConflictType.CANON_VIOLATION,
                    intent_a_id=intent.intent_id,
                    intent_b_id=f"invariant:{inv_id}",
                    description=f"Intent violates Canon invariant: {inv_expr}",
                    axiom_reference="objective_supremacy",
                    detected_at=datetime.utcnow(),
                )
                conflicts.append(conflict)
        
        return conflicts
    
    def _violates_invariant(self, intent: Intent, invariant: str) -> bool:
        """Check if intent violates a specific invariant."""
        # Simple keyword-based check
        desc = intent.description.lower()
        inv_lower = invariant.lower()
        
        # Check for negation of invariant terms
        for prefix in self.NEGATION_PREFIXES:
            if prefix in desc:
                negated_part = desc.split(prefix)[1].split()[0:3]
                for word in negated_part:
                    if word in inv_lower:
                        return True
        
        return False
    
    def _constraints_oppose(self, c_a: str, c_b: str) -> bool:
        """Check if two constraints are opposing."""
        # Check for explicit negation
        for prefix in self.NEGATION_PREFIXES:
            if c_a.startswith(prefix) and c_a[len(prefix):] == c_b:
                return True
            if c_b.startswith(prefix) and c_b[len(prefix):] == c_a:
                return True
        
        return False
    
    def _create_conflict(
        self,
        a: Intent,
        b: Intent,
        conflict_type: ConflictType,
        description: str,
        axiom_ref: Optional[str],
    ) -> Conflict:
        """Create a conflict record."""
        self._conflict_count += 1
        return Conflict(
            conflict_id=f"conflict_{self._conflict_count}",
            conflict_type=conflict_type,
            intent_a_id=a.intent_id,
            intent_b_id=b.intent_id,
            description=description,
            axiom_reference=axiom_ref,
            detected_at=datetime.utcnow(),
        )
