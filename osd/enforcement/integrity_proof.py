"""
Objective Integrity Proof (OIP)

Before every major action: Action ⇒ Objective_Integrity_Score ≥ θ

OSD - Objective Supremacy Doctrine.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from enum import Enum


class IntegrityResult(Enum):
    """Result of integrity proof."""
    VALID = "valid"
    BELOW_THRESHOLD = "below_threshold"
    NO_OBJECTIVE = "no_objective"


@dataclass(frozen=True)
class IntegrityProof:
    """Proof of objective integrity."""
    proof_id: str
    action: str
    objective_id: str
    integrity_score: float
    threshold: float
    result: IntegrityResult
    proved_at: datetime


class IntegrityViolationError(Exception):
    """Raised when integrity is below threshold."""
    pass


class ObjectiveIntegrityProof:
    """
    Objective Integrity Proof (OIP).
    
    Before every major action, evaluate:
    Action ⇒ Objective_Integrity_Score ≥ θ
    
    If below threshold:
    - Action is rejected
    - Alternative plan is generated
    
    This prevents subtle drift.
    """
    
    DEFAULT_THRESHOLD = 0.7
    
    def __init__(self, threshold: float = DEFAULT_THRESHOLD):
        """Initialize OIP."""
        self._threshold = threshold
        self._proofs: List[IntegrityProof] = []
        self._proof_count = 0
    
    def prove(
        self,
        action: str,
        objective_id: str,
        objective_intent: str,
    ) -> IntegrityProof:
        """
        Prove action maintains objective integrity.
        
        Args:
            action: Proposed action
            objective_id: Target objective
            objective_intent: Objective intent
            
        Returns:
            IntegrityProof
            
        Raises:
            IntegrityViolationError: If below threshold
        """
        if not objective_id:
            proof = self._create_proof(
                action, "", 0.0,
                IntegrityResult.NO_OBJECTIVE,
            )
            raise IntegrityViolationError(
                "Action has no objective. Cannot proceed."
            )
        
        # Calculate integrity score
        score = self._calculate_integrity(action, objective_intent)
        
        if score < self._threshold:
            proof = self._create_proof(
                action, objective_id, score,
                IntegrityResult.BELOW_THRESHOLD,
            )
            raise IntegrityViolationError(
                f"Integrity score {score:.2f} below threshold {self._threshold}. "
                f"Action rejected. Alternative plan required."
            )
        
        proof = self._create_proof(
            action, objective_id, score,
            IntegrityResult.VALID,
        )
        
        return proof
    
    def _calculate_integrity(
        self,
        action: str,
        objective_intent: str,
    ) -> float:
        """Calculate integrity score."""
        action_words = set(action.lower().split())
        intent_words = set(objective_intent.lower().split())
        
        if not intent_words:
            return 0.0
        
        overlap = len(action_words & intent_words)
        score = overlap / len(intent_words)
        
        # Bonus for explicit alignment
        if "objective" in action.lower() or any(
            word in action.lower() for word in intent_words
        ):
            score = min(1.0, score + 0.2)
        
        return score
    
    def _create_proof(
        self,
        action: str,
        objective_id: str,
        score: float,
        result: IntegrityResult,
    ) -> IntegrityProof:
        """Create proof record."""
        proof_id = f"oip_{self._proof_count}"
        self._proof_count += 1
        
        proof = IntegrityProof(
            proof_id=proof_id,
            action=action,
            objective_id=objective_id,
            integrity_score=score,
            threshold=self._threshold,
            result=result,
            proved_at=datetime.utcnow(),
        )
        
        self._proofs.append(proof)
        return proof
    
    def bypass_proof(self, *args, **kwargs) -> None:
        """FORBIDDEN: Bypass integrity proof."""
        raise IntegrityViolationError(
            "Integrity proof cannot be bypassed. "
            "All major actions require OIP."
        )
    
    @property
    def valid_count(self) -> int:
        """Valid proofs."""
        return sum(1 for p in self._proofs if p.result == IntegrityResult.VALID)
