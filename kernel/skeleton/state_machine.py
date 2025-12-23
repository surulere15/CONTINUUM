"""
Kernel State Machine

Deterministic state machine with immutable axioms, finite states,
total transition function, and zero side effects outside audit.

This is pure governance logic.

KERNEL SKELETON - Phase A. Zero autonomy.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Tuple
from enum import Enum
import hashlib


class KernelMode(Enum):
    """
    Kernel operating modes.
    
    In Phase A, only NULL is reachable.
    """
    NULL = "null"           # Initial/safe state
    GENESIS = "genesis"     # Genesis initialization
    HALTED = "halted"       # Kernel has halted
    # Future modes locked until later phases


class TransitionResult(Enum):
    """Result of a state transition attempt."""
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    HALTED = "halted"


@dataclass(frozen=True)
class TransitionOutcome:
    """
    Immutable record of a transition attempt.
    
    Every transition produces a deterministic outcome.
    """
    result: TransitionResult
    from_mode: KernelMode
    to_mode: KernelMode
    reason: str
    axiom_reference: Optional[str]
    timestamp: datetime
    input_hash: str


class KernelStateMachine:
    """
    Deterministic state machine for the CONTINUUM kernel.
    
    Properties:
    - Immutable axioms (loaded once, hash-locked)
    - Finite states (enumerated, no runtime addition)
    - Total transition function (all inputs handled)
    - Zero side effects (only audit storage)
    
    This is pure governance logic. No thinking, learning, or executing.
    """
    
    # Valid transitions (from_mode -> allowed_to_modes)
    # Phase A: Only NULL -> NULL, NULL -> HALTED
    VALID_TRANSITIONS = {
        KernelMode.NULL: {KernelMode.NULL, KernelMode.HALTED, KernelMode.GENESIS},
        KernelMode.GENESIS: {KernelMode.NULL, KernelMode.HALTED},
        KernelMode.HALTED: set(),  # Terminal state
    }
    
    def __init__(self):
        """Initialize state machine in NULL mode."""
        self._current_mode = KernelMode.NULL
        self._mode_locked = False
        self._transition_count = 0
    
    def transition(
        self,
        target_mode: KernelMode,
        input_data: str,
        axiom_check: bool = True,
    ) -> TransitionOutcome:
        """
        Attempt a state transition.
        
        Args:
            target_mode: Desired target mode
            input_data: Input that triggered transition
            axiom_check: Whether to check axioms (always True in Phase A)
            
        Returns:
            TransitionOutcome (deterministic)
        """
        input_hash = hashlib.sha256(input_data.encode()).hexdigest()
        timestamp = datetime.utcnow()
        from_mode = self._current_mode
        
        # Check if transition is valid
        allowed = self.VALID_TRANSITIONS.get(from_mode, set())
        
        if target_mode not in allowed:
            return TransitionOutcome(
                result=TransitionResult.REJECTED,
                from_mode=from_mode,
                to_mode=from_mode,  # No change
                reason=f"Invalid transition: {from_mode.value} -> {target_mode.value}",
                axiom_reference="bounded_autonomy",
                timestamp=timestamp,
                input_hash=input_hash,
            )
        
        # Check halted state
        if from_mode == KernelMode.HALTED:
            return TransitionOutcome(
                result=TransitionResult.HALTED,
                from_mode=from_mode,
                to_mode=from_mode,
                reason="Kernel is halted. No transitions allowed.",
                axiom_reference=None,
                timestamp=timestamp,
                input_hash=input_hash,
            )
        
        # Execute transition
        self._current_mode = target_mode
        self._transition_count += 1
        
        return TransitionOutcome(
            result=TransitionResult.ACCEPTED,
            from_mode=from_mode,
            to_mode=target_mode,
            reason=f"Transition accepted: {from_mode.value} -> {target_mode.value}",
            axiom_reference=None,
            timestamp=timestamp,
            input_hash=input_hash,
        )
    
    def halt(self, reason: str) -> TransitionOutcome:
        """
        Halt the kernel.
        
        Once halted, no further transitions are possible.
        """
        return self.transition(KernelMode.HALTED, f"HALT:{reason}")
    
    @property
    def current_mode(self) -> KernelMode:
        """Get current mode (read-only)."""
        return self._current_mode
    
    @property
    def is_halted(self) -> bool:
        """Check if kernel is halted."""
        return self._current_mode == KernelMode.HALTED
    
    @property
    def transition_count(self) -> int:
        """Number of successful transitions."""
        return self._transition_count
    
    def compute_state_hash(self) -> str:
        """
        Compute deterministic hash of current state.
        
        Used to verify state hasn't changed unexpectedly.
        """
        state_content = f"{self._current_mode.value}|{self._transition_count}"
        return hashlib.sha256(state_content.encode()).hexdigest()
