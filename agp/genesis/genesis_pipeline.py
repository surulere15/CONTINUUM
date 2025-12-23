"""
Genesis Pipeline

8 stages. No shortcuts. Ever.

AGP-C - Agent Genesis Protocol.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Tuple
from enum import Enum


class GenesisStage(Enum):
    """Genesis pipeline stages."""
    NEED_DETECTION = "need_detection"
    AGENT_PROPOSAL = "agent_proposal"
    CAPABILITY_SPEC = "capability_spec"
    RISK_ANALYSIS = "risk_analysis"
    KERNEL_APPROVAL = "kernel_approval"
    SANDBOX_BIRTH = "sandbox_birth"
    OBSERVATION_PHASE = "observation_phase"
    PROMOTION_OR_TERMINATION = "promotion_or_termination"


GENESIS_ORDER = [
    GenesisStage.NEED_DETECTION,
    GenesisStage.AGENT_PROPOSAL,
    GenesisStage.CAPABILITY_SPEC,
    GenesisStage.RISK_ANALYSIS,
    GenesisStage.KERNEL_APPROVAL,
    GenesisStage.SANDBOX_BIRTH,
    GenesisStage.OBSERVATION_PHASE,
    GenesisStage.PROMOTION_OR_TERMINATION,
]


@dataclass
class GenesisRecord:
    """Record of genesis stage."""
    proposal_id: str
    stage: GenesisStage
    passed: bool
    notes: Optional[str]
    timestamp: datetime


@dataclass
class GenesisProposal:
    """Proposal for agent genesis."""
    proposal_id: str
    goal_id: str
    purpose: str
    scope: Tuple[str, ...]
    current_stage: GenesisStage
    records: List[GenesisRecord]
    created_at: datetime
    approved: Optional[bool]


class GenesisSkipError(Exception):
    """Raised when genesis stage is skipped."""
    pass


class GenesisRejectedError(Exception):
    """Raised when genesis is rejected."""
    pass


class GenesisPipeline:
    """
    Agent Genesis Pipeline.
    
    Need Detection → Agent Proposal → Formal Capability Spec →
    Risk & Drift Analysis → Kernel Approval → Sandbox Birth →
    Observation Phase → Promotion or Termination
    
    No shortcuts. Ever.
    """
    
    def __init__(self):
        """Initialize pipeline."""
        self._proposals: dict[str, GenesisProposal] = {}
        self._proposal_count = 0
    
    def propose(
        self,
        goal_id: str,
        purpose: str,
        scope: Tuple[str, ...],
    ) -> GenesisProposal:
        """
        Start genesis proposal.
        
        Args:
            goal_id: Goal requiring agent
            purpose: Agent purpose
            scope: Agent scope
            
        Returns:
            GenesisProposal
        """
        proposal_id = f"genesis_{self._proposal_count}"
        self._proposal_count += 1
        
        proposal = GenesisProposal(
            proposal_id=proposal_id,
            goal_id=goal_id,
            purpose=purpose,
            scope=scope,
            current_stage=GenesisStage.NEED_DETECTION,
            records=[],
            created_at=datetime.utcnow(),
            approved=None,
        )
        
        self._proposals[proposal_id] = proposal
        return proposal
    
    def advance(
        self,
        proposal_id: str,
        passed: bool,
        notes: Optional[str] = None,
    ) -> GenesisStage:
        """
        Advance to next stage.
        
        Args:
            proposal_id: Proposal to advance
            passed: Did current stage pass
            notes: Optional notes
            
        Returns:
            New stage
        """
        if proposal_id not in self._proposals:
            raise ValueError(f"Proposal '{proposal_id}' not found")
        
        proposal = self._proposals[proposal_id]
        
        # Record current stage
        record = GenesisRecord(
            proposal_id=proposal_id,
            stage=proposal.current_stage,
            passed=passed,
            notes=notes,
            timestamp=datetime.utcnow(),
        )
        proposal.records.append(record)
        
        # If failed, reject
        if not passed:
            proposal.approved = False
            raise GenesisRejectedError(
                f"Genesis rejected at stage {proposal.current_stage.value}: {notes}"
            )
        
        # Advance
        current_idx = GENESIS_ORDER.index(proposal.current_stage)
        
        if current_idx >= len(GENESIS_ORDER) - 1:
            # Complete - promotion
            proposal.approved = True
            return proposal.current_stage
        
        proposal.current_stage = GENESIS_ORDER[current_idx + 1]
        return proposal.current_stage
    
    def skip_to(self, *args, **kwargs) -> None:
        """FORBIDDEN: Skip genesis stages."""
        raise GenesisSkipError(
            "Genesis stages cannot be skipped. "
            "All 8 stages are mandatory. No shortcuts. Ever."
        )
    
    def get_stage(self, proposal_id: str) -> Optional[GenesisStage]:
        """Get current stage."""
        if proposal_id in self._proposals:
            return self._proposals[proposal_id].current_stage
        return None
    
    def is_approved(self, proposal_id: str) -> Optional[bool]:
        """Check if proposal approved."""
        if proposal_id in self._proposals:
            return self._proposals[proposal_id].approved
        return None
