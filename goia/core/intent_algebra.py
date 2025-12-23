"""
Intent Algebra

Formal operations on intent: ⊕, ↓, π, ¬, ⊗

GOIA-C - Goal Ontology & Intent Algebra.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Set, Tuple, Optional
from enum import Enum

from .intent_primitive import Intent, Constraint


class ConflictType(Enum):
    """Types of intent conflict."""
    CONSTRAINT_CONFLICT = "constraint_conflict"
    UTILITY_CONFLICT = "utility_conflict"
    TEMPORAL_CONFLICT = "temporal_conflict"


@dataclass(frozen=True)
class CompositionResult:
    """Result of intent composition."""
    success: bool
    composed_intent: Optional[Intent]
    conflicts: Tuple[str, ...]


@dataclass(frozen=True)
class RefinementResult:
    """Result of intent refinement."""
    intent_id: str
    goals: Tuple[str, ...]


@dataclass(frozen=True)
class ConflictReport:
    """Report of intent conflict."""
    intent_a: str
    intent_b: str
    conflict_type: ConflictType
    description: str


class IntentConflictError(Exception):
    """Raised when intents conflict irreconcilably."""
    pass


class IntentAlgebra:
    """
    Intent Algebra - Formal Operations.
    
    Operations:
    - ⊕ Composition: Combine compatible intents
    - ↓ Refinement: Reduce to goals
    - π Projection: Limit to domain
    - ¬ Negation: Forbid outcomes
    - ⊗ Conflict Detection: Detect incompatibility
    """
    
    def compose(
        self,
        intent_a: Intent,
        intent_b: Intent,
    ) -> CompositionResult:
        """
        ⊕ Composition: Combine intents.
        
        I_a ⊕ I_b = I_c
        
        Valid iff:
        - Constraints do not conflict
        - Utility functions reconcilable
        - Time horizons overlap safely
        
        Args:
            intent_a: First intent
            intent_b: Second intent
            
        Returns:
            CompositionResult
        """
        conflicts = []
        
        # Check constraint compatibility
        constraint_ids_a = {c.constraint_id for c in intent_a.constraints}
        constraint_ids_b = {c.constraint_id for c in intent_b.constraints}
        
        # Check for conflicting constraints (simplified)
        for ca in intent_a.constraints:
            for cb in intent_b.constraints:
                if ca.description.startswith("NOT") and cb.description == ca.description[4:]:
                    conflicts.append(f"Constraint conflict: {ca.constraint_id} vs {cb.constraint_id}")
        
        # Check temporal overlap
        if (intent_a.temporal_horizon.deadline and 
            intent_b.temporal_horizon.deadline and
            intent_a.temporal_horizon.deadline < intent_b.temporal_horizon.start):
            conflicts.append("Temporal conflict: non-overlapping horizons")
        
        if conflicts:
            return CompositionResult(
                success=False,
                composed_intent=None,
                conflicts=tuple(conflicts),
            )
        
        # Composition successful (return first intent with merged constraints)
        return CompositionResult(
            success=True,
            composed_intent=intent_a,  # Simplified
            conflicts=(),
        )
    
    def refine(
        self,
        intent: Intent,
        goal_ids: Tuple[str, ...],
    ) -> RefinementResult:
        """
        ↓ Refinement: Reduce intent to goals.
        
        I↓ = {G₁, G₂, ...}
        
        Used to:
        - Move from human language to system goals
        - Increase executability
        
        Args:
            intent: Intent to refine
            goal_ids: Goals derived from intent
            
        Returns:
            RefinementResult
        """
        return RefinementResult(
            intent_id=intent.intent_id,
            goals=goal_ids,
        )
    
    def project(
        self,
        intent: Intent,
        domain: str,
    ) -> Intent:
        """
        π Projection: Limit intent to domain.
        
        π_domain(I)
        
        Prevents scope explosion.
        
        Args:
            intent: Intent to project
            domain: Domain to limit to
            
        Returns:
            Projected intent
        """
        # Add domain constraint
        domain_constraint = Constraint(
            constraint_id=f"domain_{domain}",
            description=f"Limited to domain: {domain}",
            is_hard=True,
        )
        
        new_constraints = intent.constraints + (domain_constraint,)
        
        return Intent(
            intent_id=f"{intent.intent_id}_proj_{domain}",
            desired_delta=intent.desired_delta,
            constraints=new_constraints,
            preferences=intent.preferences,
            temporal_horizon=intent.temporal_horizon,
            fingerprint=intent.fingerprint,
            created_at=datetime.utcnow(),
        )
    
    def negate(
        self,
        intent: Intent,
    ) -> Constraint:
        """
        ¬ Negation: Forbid outcomes.
        
        ¬I
        
        Used for:
        - Safety constraints
        - Ethical boundaries
        - Regulatory compliance
        
        Args:
            intent: Intent to negate
            
        Returns:
            Constraint forbidding the intent
        """
        return Constraint(
            constraint_id=f"NOT_{intent.intent_id}",
            description=f"NOT: {intent.desired_delta.description}",
            is_hard=True,
        )
    
    def detect_conflict(
        self,
        intent_a: Intent,
        intent_b: Intent,
    ) -> Optional[ConflictReport]:
        """
        ⊗ Conflict Detection.
        
        Two intents conflict if:
        - C_a ∩ C_b = ∅ (constraints empty intersection)
        - U_a↑ ⇒ U_b↓ (utility tradeoff)
        
        Args:
            intent_a: First intent
            intent_b: Second intent
            
        Returns:
            ConflictReport if conflict, None otherwise
        """
        # Check constraint conflict
        desc_a = {c.description for c in intent_a.constraints}
        desc_b = {c.description for c in intent_b.constraints}
        
        for da in desc_a:
            if f"NOT {da}" in desc_b or da.replace("NOT ", "") in desc_b:
                return ConflictReport(
                    intent_a=intent_a.intent_id,
                    intent_b=intent_b.intent_id,
                    conflict_type=ConflictType.CONSTRAINT_CONFLICT,
                    description=f"Constraint '{da}' conflicts",
                )
        
        # Check utility conflict (simplified: opposing preferences)
        pref_a = {p.preference_id for p in intent_a.preferences}
        pref_b = {p.preference_id for p in intent_b.preferences}
        
        for pa in intent_a.preferences:
            for pb in intent_b.preferences:
                if pa.preference_id == pb.preference_id and abs(pa.weight - pb.weight) > 0.5:
                    return ConflictReport(
                        intent_a=intent_a.intent_id,
                        intent_b=intent_b.intent_id,
                        conflict_type=ConflictType.UTILITY_CONFLICT,
                        description=f"Utility '{pa.preference_id}' has conflicting weights",
                    )
        
        return None
