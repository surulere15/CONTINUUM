"""
Memory Write Admission

4-stage filter. No memory write is automatic.

MMCP-C - Memory Model & Cognitive Persistence.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Tuple
from enum import Enum


class AdmissionStage(Enum):
    """Write admission stages."""
    RELEVANCE = "relevance"
    REDUNDANCY = "redundancy"
    GOAL_TRACE = "goal_trace"
    GOVERNANCE = "governance"


class AdmissionResult(Enum):
    """Result of admission check."""
    ADMITTED = "admitted"
    REJECTED = "rejected"


@dataclass(frozen=True)
class AdmissionDecision:
    """Decision from write admission."""
    entry_id: str
    memory_class: str
    result: AdmissionResult
    failed_stage: Optional[AdmissionStage]
    reason: Optional[str]
    decided_at: datetime


class WriteRejectedError(Exception):
    """Raised when write is rejected."""
    pass


class WriteAdmission:
    """
    Memory Write Admission Control.
    
    No memory write is automatic.
    
    Every write must pass:
    1. Relevance filter
    2. Redundancy check
    3. Goal trace validation
    4. Governance review (for sensitive classes)
    
    write(m) ⇒ authorized(m, G, Ω) = true
    """
    
    SENSITIVE_CLASSES = {"value", "episodic"}
    
    def __init__(self):
        """Initialize write admission."""
        self._decisions: list = []
        self._admitted_count = 0
        self._rejected_count = 0
    
    def admit(
        self,
        entry_id: str,
        memory_class: str,
        content: str,
        goal_reference: Optional[str],
        requires_governance: bool = False,
    ) -> AdmissionDecision:
        """
        Check if write should be admitted.
        
        Args:
            entry_id: Entry being written
            memory_class: Which memory class
            content: Content to write
            goal_reference: Associated goal
            requires_governance: Needs governance review
            
        Returns:
            AdmissionDecision
            
        Raises:
            WriteRejectedError: If rejected
        """
        # Stage 1: Relevance filter
        if not content or len(content.strip()) == 0:
            return self._reject(
                entry_id, memory_class,
                AdmissionStage.RELEVANCE,
                "Empty content is not relevant",
            )
        
        # Stage 2: Redundancy check (simplified)
        # In real impl, would check against existing memory
        
        # Stage 3: Goal trace validation
        if memory_class != "working" and not goal_reference:
            return self._reject(
                entry_id, memory_class,
                AdmissionStage.GOAL_TRACE,
                "Non-working memory requires goal trace",
            )
        
        # Stage 4: Governance review
        if memory_class in self.SENSITIVE_CLASSES and requires_governance:
            # Would trigger governance review in real impl
            pass
        
        # All stages passed
        decision = AdmissionDecision(
            entry_id=entry_id,
            memory_class=memory_class,
            result=AdmissionResult.ADMITTED,
            failed_stage=None,
            reason=None,
            decided_at=datetime.utcnow(),
        )
        
        self._decisions.append(decision)
        self._admitted_count += 1
        
        return decision
    
    def _reject(
        self,
        entry_id: str,
        memory_class: str,
        stage: AdmissionStage,
        reason: str,
    ) -> AdmissionDecision:
        """Reject a write."""
        decision = AdmissionDecision(
            entry_id=entry_id,
            memory_class=memory_class,
            result=AdmissionResult.REJECTED,
            failed_stage=stage,
            reason=reason,
            decided_at=datetime.utcnow(),
        )
        
        self._decisions.append(decision)
        self._rejected_count += 1
        
        raise WriteRejectedError(
            f"Write rejected at stage {stage.value}: {reason}"
        )
    
    def bypass(self, *args, **kwargs) -> None:
        """FORBIDDEN: Bypass admission."""
        raise WriteRejectedError(
            "Write admission cannot be bypassed. "
            "All writes must pass 4-stage filter."
        )
    
    @property
    def admitted_count(self) -> int:
        """Total admitted."""
        return self._admitted_count
    
    @property
    def rejected_count(self) -> int:
        """Total rejected."""
        return self._rejected_count
