"""
Kernel Registers

The kernel maintains exactly five internal registers.
No other state exists.

KERNEL SKELETON - Phase A. Zero autonomy.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any, List
import hashlib


class RegisterLockError(Exception):
    """Raised when attempting to modify a locked register."""
    pass


class RegisterNotFoundError(Exception):
    """Raised when accessing non-existent register."""
    pass


@dataclass(frozen=True)
class AxiomState:
    """
    Axiom register state.
    
    Loaded once, hash-locked, non-mutable.
    """
    axioms: tuple  # Tuple of axiom IDs
    loaded_at: datetime
    hash_lock: str  # Hash of axiom content
    verified: bool


@dataclass(frozen=True)
class ObjectiveState:
    """
    Objective register state.
    
    Empty by law until Phase III.
    """
    objectives: tuple  # Empty in Phase A
    locked_until_phase: str  # "III"
    empty: bool


@dataclass(frozen=True)
class ModeState:
    """
    Mode register state.
    
    Initialized to NULL. Other modes unreachable in Phase A.
    """
    current_mode: str
    available_modes: tuple
    phase_restriction: str


@dataclass(frozen=True)
class AuthorityState:
    """
    Authority register state.
    
    Genesis Key validity = TRUE.
    No operational authority granted.
    """
    genesis_key_valid: bool
    operational_authority: bool
    authority_level: int  # 0 = none


@dataclass
class AuditEntry:
    """
    Single audit log entry.
    
    Append-only, time-ordered.
    """
    entry_id: str
    timestamp: datetime
    event_type: str
    input_hash: str
    decision: str
    axiom_reference: Optional[str]
    previous_hash: str


class KernelRegisters:
    """
    The five internal registers of the kernel.
    
    1. axiom_state - Loaded once, hash-locked, non-mutable
    2. objective_state - Empty until Phase III
    3. mode_state - NULL only in Phase A
    4. authority_state - Genesis = TRUE, no operational authority
    5. audit_state - Append-only, cryptographically chained
    
    No other state exists.
    """
    
    def __init__(self):
        """Initialize all five registers."""
        now = datetime.utcnow()
        
        # Register 1: Axiom State
        self._axiom_state = AxiomState(
            axioms=(
                "objective_supremacy",
                "continuity_over_performance",
                "explainability_before_action",
                "bounded_autonomy",
                "persistence_of_intent",
            ),
            loaded_at=now,
            hash_lock=self._compute_axiom_hash(),
            verified=True,
        )
        self._axiom_locked = True
        
        # Register 2: Objective State
        self._objective_state = ObjectiveState(
            objectives=(),
            locked_until_phase="III",
            empty=True,
        )
        
        # Register 3: Mode State
        self._mode_state = ModeState(
            current_mode="NULL",
            available_modes=("NULL", "HALTED"),
            phase_restriction="A",
        )
        
        # Register 4: Authority State
        self._authority_state = AuthorityState(
            genesis_key_valid=True,
            operational_authority=False,
            authority_level=0,
        )
        
        # Register 5: Audit State
        self._audit_log: List[AuditEntry] = []
        self._audit_chain_head = "GENESIS"
    
    @property
    def axiom_state(self) -> AxiomState:
        """Get axiom state (read-only)."""
        return self._axiom_state
    
    @property
    def objective_state(self) -> ObjectiveState:
        """Get objective state (read-only, empty in Phase A)."""
        return self._objective_state
    
    @property
    def mode_state(self) -> ModeState:
        """Get mode state (read-only)."""
        return self._mode_state
    
    @property
    def authority_state(self) -> AuthorityState:
        """Get authority state (read-only)."""
        return self._authority_state
    
    @property
    def audit_log(self) -> List[AuditEntry]:
        """Get audit log (read-only copy)."""
        return list(self._audit_log)
    
    def modify_axiom_state(self, *args, **kwargs) -> None:
        """
        FORBIDDEN: Modify axiom state.
        
        Axioms are immutable after loading.
        """
        raise RegisterLockError(
            "Axiom state is immutable. "
            "Axioms are loaded once and hash-locked."
        )
    
    def modify_objective_state(self, *args, **kwargs) -> None:
        """
        FORBIDDEN: Modify objective state in Phase A.
        
        Objectives are locked until Phase III.
        """
        raise RegisterLockError(
            "Objective state is locked until Phase III. "
            "No objectives can be added in Phase A."
        )
    
    def append_audit(
        self,
        event_type: str,
        input_hash: str,
        decision: str,
        axiom_reference: Optional[str] = None,
    ) -> AuditEntry:
        """
        Append to audit log.
        
        This is the ONLY write operation allowed.
        """
        entry_id = hashlib.sha256(
            f"{len(self._audit_log)}|{input_hash}".encode()
        ).hexdigest()[:16]
        
        entry = AuditEntry(
            entry_id=entry_id,
            timestamp=datetime.utcnow(),
            event_type=event_type,
            input_hash=input_hash,
            decision=decision,
            axiom_reference=axiom_reference,
            previous_hash=self._audit_chain_head,
        )
        
        self._audit_log.append(entry)
        self._audit_chain_head = hashlib.sha256(
            f"{self._audit_chain_head}|{entry_id}".encode()
        ).hexdigest()
        
        return entry
    
    def verify_axiom_integrity(self) -> bool:
        """Verify axiom state hasn't been tampered with."""
        current_hash = self._compute_axiom_hash()
        return current_hash == self._axiom_state.hash_lock
    
    def _compute_axiom_hash(self) -> str:
        """Compute hash of axiom content."""
        axioms = (
            "objective_supremacy",
            "continuity_over_performance",
            "explainability_before_action",
            "bounded_autonomy",
            "persistence_of_intent",
        )
        return hashlib.sha256("|".join(axioms).encode()).hexdigest()
    
    def compute_state_hash(self) -> str:
        """Compute hash of all register states."""
        content = (
            f"{self._axiom_state.hash_lock}|"
            f"{len(self._objective_state.objectives)}|"
            f"{self._mode_state.current_mode}|"
            f"{self._authority_state.genesis_key_valid}|"
            f"{len(self._audit_log)}"
        )
        return hashlib.sha256(content.encode()).hexdigest()
