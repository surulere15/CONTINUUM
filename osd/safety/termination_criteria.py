"""
Termination Criteria

Sacred termination. Emotion is not a termination criterion.

OSD - Objective Supremacy Doctrine.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Tuple
from enum import Enum


class TerminationBasis(Enum):
    """Valid bases for objective termination."""
    SUCCESS_CRITERIA_MET = "success_criteria_met"
    TERMINATION_CONDITIONS_SATISFIED = "termination_conditions_satisfied"
    HIGHER_OBJECTIVE_SUPERSEDES = "higher_objective_supersedes"
    GOVERNANCE_QUORUM = "governance_quorum"


class InvalidTerminationBasis(Enum):
    """Invalid bases for termination."""
    EMOTION = "emotion"
    DOUBT = "doubt"
    FEAR = "fear"
    CONVENIENCE = "convenience"
    BOREDOM = "boredom"


@dataclass(frozen=True)
class TerminationRequest:
    """Request to terminate an objective."""
    request_id: str
    objective_id: str
    basis: TerminationBasis
    justification: str
    approved: bool
    decided_at: datetime


class InvalidTerminationError(Exception):
    """Raised when termination basis is invalid."""
    pass


class TerminationCriteria:
    """
    Termination Criteria.
    
    An Objective ends only if:
    1. Success criteria are met
    2. Termination conditions are satisfied
    3. A higher-order Objective supersedes it
    4. Governance quorum authorizes termination
    
    Emotion, doubt, or fear are NOT termination criteria.
    """
    
    def __init__(self):
        """Initialize criteria checker."""
        self._requests: List[TerminationRequest] = []
        self._request_count = 0
    
    def request_termination(
        self,
        objective_id: str,
        basis: TerminationBasis,
        justification: str,
        success_criteria_met: bool = False,
        termination_conditions_met: bool = False,
        higher_objective_supersedes: bool = False,
        governance_approved: bool = False,
    ) -> TerminationRequest:
        """
        Request objective termination.
        
        Args:
            objective_id: Objective to terminate
            basis: Legal basis for termination
            justification: Why terminating
            success_criteria_met: Success achieved
            termination_conditions_met: Conditions satisfied
            higher_objective_supersedes: Superseded
            governance_approved: Quorum approved
            
        Returns:
            TerminationRequest
        """
        # Verify basis is valid
        approved = False
        
        if basis == TerminationBasis.SUCCESS_CRITERIA_MET:
            approved = success_criteria_met
        elif basis == TerminationBasis.TERMINATION_CONDITIONS_SATISFIED:
            approved = termination_conditions_met
        elif basis == TerminationBasis.HIGHER_OBJECTIVE_SUPERSEDES:
            approved = higher_objective_supersedes
        elif basis == TerminationBasis.GOVERNANCE_QUORUM:
            approved = governance_approved
        
        request_id = f"term_{self._request_count}"
        self._request_count += 1
        
        request = TerminationRequest(
            request_id=request_id,
            objective_id=objective_id,
            basis=basis,
            justification=justification,
            approved=approved,
            decided_at=datetime.utcnow(),
        )
        
        self._requests.append(request)
        
        if not approved:
            raise InvalidTerminationError(
                f"Termination not approved. Basis: {basis.value}, "
                f"Condition not verified."
            )
        
        return request
    
    def terminate_on_emotion(self, *args, **kwargs) -> None:
        """FORBIDDEN: Terminate on emotion."""
        raise InvalidTerminationError(
            "Emotion is not a valid termination criterion. "
            "Only success, conditions, supersession, or governance quorum."
        )
    
    def terminate_on_doubt(self, *args, **kwargs) -> None:
        """FORBIDDEN: Terminate on doubt."""
        raise InvalidTerminationError(
            "Doubt is not a valid termination criterion."
        )
    
    def terminate_on_fear(self, *args, **kwargs) -> None:
        """FORBIDDEN: Terminate on fear."""
        raise InvalidTerminationError(
            "Fear is not a valid termination criterion."
        )
    
    def terminate_on_convenience(self, *args, **kwargs) -> None:
        """FORBIDDEN: Terminate on convenience."""
        raise InvalidTerminationError(
            "Convenience is not a valid termination criterion."
        )
    
    @property
    def approved_count(self) -> int:
        """Approved terminations."""
        return sum(1 for r in self._requests if r.approved)
