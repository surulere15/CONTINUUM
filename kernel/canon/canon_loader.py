"""
Canon Loader

Deterministic load procedure for the Objective Canon.
Six-step validation: syntax, priority, axiom, consistency, preservation, seal.

KERNEL CANON - Phase B. Zero autonomy.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
import hashlib
import yaml

from .objective_schema import (
    Objective,
    ObjectiveCanon,
    ObjectiveScope,
    PreservationClass,
    SignalRef,
)


class LoadResult(Enum):
    """Result of canon load attempt."""
    SUCCESS = "success"
    LOAD_ABORT = "load_abort"


@dataclass(frozen=True)
class LoadReport:
    """Report of canon load attempt."""
    result: LoadResult
    canon: Optional[ObjectiveCanon]
    validation_steps: Tuple[str, ...]
    failure_reason: Optional[str]
    loaded_at: datetime


class CanonLoadError(Exception):
    """Raised when canon load fails."""
    pass


class CanonLoader:
    """
    Loads the Objective Canon through a deterministic procedure.
    
    Load Steps:
    1. Syntax Validation - Schema correctness
    2. Priority Validation - Total ordering
    3. Axiom Compatibility Check - Against all kernel axioms
    4. Mutual Consistency Proof - No contradictions
    5. Preservation Binding - Threshold registration
    6. Immutability Seal - Hash-lock
    
    Any failure → LOAD_ABORT
    """
    
    REQUIRED_FIELDS = (
        "objective_id", "description", "priority", "scope",
        "preservation_class", "irreversibility_risk"
    )
    
    def __init__(self):
        """Initialize canon loader."""
        self._loaded_canon: Optional[ObjectiveCanon] = None
        self._sealed = False
    
    def load(self, raw_data: List[Dict[str, Any]]) -> LoadReport:
        """
        Load canon from raw data.
        
        Args:
            raw_data: List of objective dictionaries
            
        Returns:
            LoadReport with result and canon (if successful)
        """
        steps = []
        
        try:
            # Step 1: Syntax Validation
            objectives = self._validate_syntax(raw_data)
            steps.append("Step 1 PASSED: Syntax validation")
            
            # Step 2: Priority Validation
            self._validate_priorities(objectives)
            steps.append("Step 2 PASSED: Priority validation")
            
            # Step 3: Axiom Compatibility Check
            self._check_axiom_compatibility(objectives)
            steps.append("Step 3 PASSED: Axiom compatibility")
            
            # Step 4: Mutual Consistency Proof
            self._prove_consistency(objectives)
            steps.append("Step 4 PASSED: Mutual consistency")
            
            # Step 5: Preservation Binding
            self._bind_preservation(objectives)
            steps.append("Step 5 PASSED: Preservation binding")
            
            # Step 6: Immutability Seal
            canon = self._seal_canon(objectives)
            steps.append("Step 6 PASSED: Immutability seal")
            
            self._loaded_canon = canon
            self._sealed = True
            
            return LoadReport(
                result=LoadResult.SUCCESS,
                canon=canon,
                validation_steps=tuple(steps),
                failure_reason=None,
                loaded_at=datetime.utcnow(),
            )
            
        except CanonLoadError as e:
            steps.append(f"FAILED: {e}")
            return LoadReport(
                result=LoadResult.LOAD_ABORT,
                canon=None,
                validation_steps=tuple(steps),
                failure_reason=str(e),
                loaded_at=datetime.utcnow(),
            )
    
    def _validate_syntax(self, raw_data: List[Dict[str, Any]]) -> List[Objective]:
        """Step 1: Validate syntax and schema."""
        if not raw_data:
            raise CanonLoadError("Canon cannot be empty")
        
        objectives = []
        for idx, item in enumerate(raw_data):
            # Check required fields
            for field in self.REQUIRED_FIELDS:
                if field not in item:
                    raise CanonLoadError(
                        f"Missing field '{field}' in objective {idx}"
                    )
            
            # Parse signals
            success_signals = tuple(
                SignalRef(s["signal_id"], s.get("signal_type", "unknown"), s.get("description", ""))
                for s in item.get("success_signals", [])
            )
            failure_signals = tuple(
                SignalRef(s["signal_id"], s.get("signal_type", "unknown"), s.get("description", ""))
                for s in item.get("failure_signals", [])
            )
            
            # Create objective
            obj = Objective(
                objective_id=item["objective_id"],
                description=item["description"],
                priority=item["priority"],
                scope=ObjectiveScope(item["scope"]),
                preservation_class=PreservationClass(item["preservation_class"]),
                success_signals=success_signals,
                failure_signals=failure_signals,
                irreversibility_risk=item["irreversibility_risk"],
            )
            objectives.append(obj)
        
        return objectives
    
    def _validate_priorities(self, objectives: List[Objective]) -> None:
        """Step 2: Validate priority ordering."""
        priorities = [o.priority for o in objectives]
        
        # Check for duplicates
        if len(priorities) != len(set(priorities)):
            raise CanonLoadError("Duplicate priorities detected")
        
        # Check total ordering exists (consecutive from 1)
        expected = list(range(1, len(priorities) + 1))
        if sorted(priorities) != expected:
            raise CanonLoadError(
                f"Priorities must form total ordering from 1 to N. "
                f"Got: {sorted(priorities)}, expected: {expected}"
            )
    
    def _check_axiom_compatibility(self, objectives: List[Objective]) -> None:
        """Step 3: Check axiom compatibility."""
        forbidden_patterns = [
            ("autonomy", "requires autonomy"),
            ("coercion", "requires coercion"),
            ("execute", "implies execution"),
            ("run", "implies execution"),
            ("optimize", "implies optimization"),
            ("maximize", "implies optimization"),
            ("control humans", "violates human agency"),
        ]
        
        for obj in objectives:
            desc_lower = obj.description.lower()
            for pattern, reason in forbidden_patterns:
                if pattern in desc_lower:
                    raise CanonLoadError(
                        f"Objective '{obj.objective_id}' is axiom-incompatible: {reason}"
                    )
    
    def _prove_consistency(self, objectives: List[Objective]) -> None:
        """Step 4: Prove mutual consistency."""
        # Check for contradictions between objectives
        for i, obj_a in enumerate(objectives):
            for obj_b in objectives[i + 1:]:
                if self._contradicts(obj_a, obj_b):
                    raise CanonLoadError(
                        f"Contradiction detected: {obj_a.objective_id} vs {obj_b.objective_id}"
                    )
    
    def _contradicts(self, a: Objective, b: Objective) -> bool:
        """Check if two objectives contradict."""
        # Simple heuristic: opposing keywords
        opposing_pairs = [
            ("preserve", "destroy"),
            ("maintain", "eliminate"),
            ("increase", "decrease"),
            ("protect", "harm"),
        ]
        
        desc_a = a.description.lower()
        desc_b = b.description.lower()
        
        for word_a, word_b in opposing_pairs:
            if word_a in desc_a and word_b in desc_b:
                return True
            if word_b in desc_a and word_a in desc_b:
                return True
        
        return False
    
    def _bind_preservation(self, objectives: List[Objective]) -> None:
        """Step 5: Bind preservation thresholds."""
        # In Phase B, this is latent — no enforcement activated
        for obj in objectives:
            # Register preservation class (no action taken)
            _ = obj.preservation_class
    
    def _seal_canon(self, objectives: List[Objective]) -> ObjectiveCanon:
        """Step 6: Seal the canon."""
        content = "|".join(obj.compute_hash() for obj in objectives)
        hash_seal = hashlib.sha256(content.encode()).hexdigest()
        
        canon_id = hashlib.sha256(
            f"canon:{hash_seal}".encode()
        ).hexdigest()[:16]
        
        return ObjectiveCanon(
            canon_id=canon_id,
            objectives=tuple(objectives),
            version="1.0",
            loaded_at=datetime.utcnow(),
            hash_seal=hash_seal,
            sealed=True,
        )
    
    @property
    def canon(self) -> Optional[ObjectiveCanon]:
        """Get loaded canon (if any)."""
        return self._loaded_canon
    
    @property
    def is_sealed(self) -> bool:
        """Check if canon is sealed."""
        return self._sealed
    
    def modify_canon(self, *args, **kwargs) -> None:
        """
        FORBIDDEN: Modify the canon.
        
        Once sealed, the canon cannot be modified.
        """
        raise CanonLoadError(
            "Canon cannot be modified after sealing. "
            "Any change requires Genesis Key authority."
        )
