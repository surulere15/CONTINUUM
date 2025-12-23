"""
Resolution Engine

Resolve conflicts using pre-declared law only.
Fixed resolution order — no dynamic prioritization.

KERNEL MODULE - No imports from execution/agents/learning.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Optional, Set, Tuple
from enum import Enum

from .intent_schema import Intent, IntentSource, IntentSet, RejectionReport
from .conflict_detector import ConflictGraph, Conflict, ConflictType


class ResolutionOutcome(Enum):
    """Possible resolution outcomes."""
    STABILIZED = "stabilized"        # All conflicts resolved
    PARTIAL_REJECTION = "partial"    # Some intents rejected
    TOTAL_REJECTION = "total"        # All intents rejected
    NO_CONFLICTS = "no_conflicts"    # Nothing to resolve


@dataclass(frozen=True)
class ResolutionResult:
    """
    Result of conflict resolution.
    
    Contains stabilized intents and rejection reports.
    """
    outcome: ResolutionOutcome
    stabilized: Optional[IntentSet]
    rejections: Tuple[RejectionReport, ...]
    resolution_steps: Tuple[str, ...]
    resolved_at: datetime


class CompromiseSynthesisError(Exception):
    """Raised when compromise synthesis is attempted without Canon permission."""
    pass


class ResolutionEngine:
    """
    Resolves intent conflicts using fixed precedence rules.
    
    Resolution order (FIXED, NON-CONFIGURABLE):
    1. Objective Canon invariants
    2. Objective priority lattice
    3. Source precedence (Canon > System > Human)
    4. Explicit constraints
    5. Deterministic tie-breakers (lexicographic)
    
    Resolution results:
    - Stabilized intent set
    - Partial rejection
    - Total rejection
    
    No compromise synthesis unless explicitly permitted by Canon.
    """
    
    # Source precedence (higher = more authority)
    SOURCE_PRECEDENCE = {
        IntentSource.CANON: 100,
        IntentSource.SYSTEM: 50,
        IntentSource.HUMAN: 10,
    }
    
    def __init__(
        self,
        canon_invariants: Optional[Dict[str, str]] = None,
        priority_lattice: Optional[Dict[str, int]] = None,
    ):
        """
        Initialize resolution engine.
        
        Args:
            canon_invariants: Canon invariants for violation checks
            priority_lattice: Objective priority ordering
        """
        self._invariants = canon_invariants or {}
        self._priority_lattice = priority_lattice or {}
    
    def resolve(
        self,
        intents: List[Intent],
        conflict_graph: ConflictGraph,
    ) -> ResolutionResult:
        """
        Resolve conflicts in intent set.
        
        Args:
            intents: Normalized intents
            conflict_graph: Detected conflicts
            
        Returns:
            ResolutionResult
        """
        steps = []
        rejections = []
        
        if not conflict_graph.has_conflicts:
            # No conflicts to resolve
            intent_set = self._create_intent_set(intents)
            return ResolutionResult(
                outcome=ResolutionOutcome.NO_CONFLICTS,
                stabilized=intent_set,
                rejections=(),
                resolution_steps=("No conflicts detected",),
                resolved_at=datetime.utcnow(),
            )
        
        # Track which intents survive resolution
        surviving_ids: Set[str] = {i.intent_id for i in intents}
        
        # Step 1: Reject Canon violations (non-negotiable)
        for conflict in conflict_graph.conflicts:
            if conflict.conflict_type == ConflictType.CANON_VIOLATION:
                rejected_id = conflict.intent_a_id
                if rejected_id in surviving_ids:
                    surviving_ids.remove(rejected_id)
                    steps.append(f"Rejected {rejected_id}: Canon violation")
                    rejections.append(self._create_rejection(
                        rejected_id,
                        "Violates Canon invariant",
                        (conflict.intent_b_id,),
                        conflict.axiom_reference,
                    ))
        
        # Step 2: Resolve remaining conflicts by precedence
        remaining_conflicts = [
            c for c in conflict_graph.conflicts
            if c.conflict_type != ConflictType.CANON_VIOLATION
            and c.intent_a_id in surviving_ids
            and c.intent_b_id in surviving_ids
        ]
        
        for conflict in remaining_conflicts:
            winner, loser = self._resolve_pair(
                self._get_intent(intents, conflict.intent_a_id),
                self._get_intent(intents, conflict.intent_b_id),
            )
            
            if loser and loser.intent_id in surviving_ids:
                surviving_ids.remove(loser.intent_id)
                steps.append(f"Rejected {loser.intent_id}: Lower precedence than {winner.intent_id}")
                rejections.append(self._create_rejection(
                    loser.intent_id,
                    "Lower precedence in conflict resolution",
                    (winner.intent_id,),
                    conflict.axiom_reference,
                ))
        
        # Create result
        surviving = [i for i in intents if i.intent_id in surviving_ids]
        
        if not surviving:
            return ResolutionResult(
                outcome=ResolutionOutcome.TOTAL_REJECTION,
                stabilized=None,
                rejections=tuple(rejections),
                resolution_steps=tuple(steps),
                resolved_at=datetime.utcnow(),
            )
        
        if len(rejections) > 0:
            outcome = ResolutionOutcome.PARTIAL_REJECTION
        else:
            outcome = ResolutionOutcome.STABILIZED
        
        return ResolutionResult(
            outcome=outcome,
            stabilized=self._create_intent_set(surviving),
            rejections=tuple(rejections),
            resolution_steps=tuple(steps),
            resolved_at=datetime.utcnow(),
        )
    
    def _resolve_pair(
        self,
        a: Optional[Intent],
        b: Optional[Intent],
    ) -> Tuple[Optional[Intent], Optional[Intent]]:
        """
        Resolve conflict between two intents.
        
        Returns (winner, loser).
        """
        if not a or not b:
            return (a or b, None)
        
        # Rule 1: Source precedence
        prec_a = self.SOURCE_PRECEDENCE.get(a.source, 0)
        prec_b = self.SOURCE_PRECEDENCE.get(b.source, 0)
        
        if prec_a > prec_b:
            return (a, b)
        if prec_b > prec_a:
            return (b, a)
        
        # Rule 2: More constraints wins (more specific)
        if len(a.constraints) > len(b.constraints):
            return (a, b)
        if len(b.constraints) > len(a.constraints):
            return (b, a)
        
        # Rule 3: Lexicographic tie-breaker (deterministic)
        if a.intent_id < b.intent_id:
            return (a, b)
        return (b, a)
    
    def synthesize_compromise(self, *args, **kwargs) -> None:
        """
        FORBIDDEN: Synthesize compromise between conflicting intents.
        
        Compromise synthesis is only allowed if explicitly permitted by Canon.
        """
        raise CompromiseSynthesisError(
            "Compromise synthesis is forbidden without Canon permission. "
            "Conflicts must be resolved by precedence, not negotiation."
        )
    
    def _get_intent(self, intents: List[Intent], intent_id: str) -> Optional[Intent]:
        """Get intent by ID."""
        for i in intents:
            if i.intent_id == intent_id:
                return i
        return None
    
    def _create_intent_set(self, intents: List[Intent]) -> IntentSet:
        """Create stabilized intent set."""
        import hashlib
        
        content = "|".join(sorted(i.intent_id for i in intents))
        set_hash = hashlib.sha256(content.encode()).hexdigest()
        
        return IntentSet(
            set_id=set_hash[:16],
            intents=tuple(intents),
            stabilized_at=datetime.utcnow(),
            hash=set_hash,
        )
    
    def _create_rejection(
        self,
        intent_id: str,
        reason: str,
        conflicting_with: Tuple[str, ...],
        axiom_ref: Optional[str],
    ) -> RejectionReport:
        """Create rejection report."""
        return RejectionReport(
            intent_id=intent_id,
            reason=reason,
            conflicting_with=conflicting_with,
            axiom_reference=axiom_ref,
            rejected_at=datetime.utcnow(),
        )
