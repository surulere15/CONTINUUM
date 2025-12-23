"""
State Continuity Invariant

S_{t+1} = f(S_t, A_t, O_t)

No spontaneous state emergence is permitted.
Every state transition must be causally linked.

NCE INVARIANT 2 - Neural Continuum Engine.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Tuple, Any, Dict
import hashlib


@dataclass(frozen=True)
class SystemState:
    """
    System state at time t.
    
    All state transitions are causal.
    """
    state_id: str
    version: int
    state_hash: str
    timestamp: datetime
    parent_state_id: Optional[str]  # Must exist except for genesis


@dataclass(frozen=True)
class Action:
    """Action proposed at time t."""
    action_id: str
    effect: str
    reversibility: str
    confidence: float


@dataclass(frozen=True)
class Observation:
    """Observed outcome at time t."""
    observation_id: str
    outcome: str
    timestamp: datetime


@dataclass(frozen=True)
class StateTransition:
    """
    Record of state transition.
    
    S_{t+1} = f(S_t, A_t, O_t)
    """
    from_state: str
    to_state: str
    action: str
    observation: str
    timestamp: datetime


class SpontaneousStateError(Exception):
    """Raised when spontaneous state emergence is attempted."""
    pass


class CausalityViolationError(Exception):
    """Raised when causal chain is broken."""
    pass


class StateContinuity:
    """
    Enforces Invariant 2: State Continuity.
    
    S_{t+1} = f(S_t, A_t, O_t)
    
    No spontaneous state emergence permitted.
    """
    
    def __init__(self, genesis_state: SystemState):
        """
        Initialize with genesis state.
        
        Args:
            genesis_state: The initial state (has no parent)
        """
        self._states: Dict[str, SystemState] = {genesis_state.state_id: genesis_state}
        self._current_state = genesis_state
        self._transitions: list[StateTransition] = []
        self._version = 0
    
    def transition(
        self,
        action: Action,
        observation: Observation,
    ) -> SystemState:
        """
        Create new state via causal transition.
        
        Args:
            action: Action that caused transition
            observation: Observed outcome
            
        Returns:
            New SystemState
        """
        self._version += 1
        
        # Compute new state hash from causal inputs
        content = (
            f"{self._current_state.state_hash}|"
            f"{action.action_id}|"
            f"{observation.observation_id}"
        )
        new_hash = hashlib.sha256(content.encode()).hexdigest()
        
        new_state = SystemState(
            state_id=f"state_{self._version}",
            version=self._version,
            state_hash=new_hash,
            timestamp=datetime.utcnow(),
            parent_state_id=self._current_state.state_id,
        )
        
        # Record transition
        transition = StateTransition(
            from_state=self._current_state.state_id,
            to_state=new_state.state_id,
            action=action.action_id,
            observation=observation.observation_id,
            timestamp=datetime.utcnow(),
        )
        
        self._states[new_state.state_id] = new_state
        self._transitions.append(transition)
        self._current_state = new_state
        
        return new_state
    
    def verify_causality(self, state_id: str) -> bool:
        """
        Verify state has causal ancestry.
        
        Args:
            state_id: State to verify
            
        Returns:
            True if causally linked
            
        Raises:
            CausalityViolationError: If causal chain broken
        """
        if state_id not in self._states:
            raise CausalityViolationError(
                f"State '{state_id}' has no causal history."
            )
        
        current = self._states[state_id]
        
        # Trace back to genesis
        while current.parent_state_id is not None:
            if current.parent_state_id not in self._states:
                raise CausalityViolationError(
                    f"Broken causal chain at state '{current.state_id}'."
                )
            current = self._states[current.parent_state_id]
        
        return True
    
    def spontaneous_state(self, *args, **kwargs) -> None:
        """FORBIDDEN: Create spontaneous state."""
        raise SpontaneousStateError(
            "Spontaneous state emergence is forbidden. "
            "All states must derive from S_{t+1} = f(S_t, A_t, O_t)."
        )
    
    def inject_state(self, *args, **kwargs) -> None:
        """FORBIDDEN: Inject state without causation."""
        raise SpontaneousStateError(
            "State injection without causal history is forbidden."
        )
    
    @property
    def current_state(self) -> SystemState:
        """Get current state."""
        return self._current_state
    
    @property
    def version(self) -> int:
        """Current state version."""
        return self._version
    
    def get_transitions(self) -> list[StateTransition]:
        """Get all transitions."""
        return list(self._transitions)


def create_genesis_state() -> SystemState:
    """Create the genesis state (no parent)."""
    genesis_hash = hashlib.sha256(b"CONTINUUM:GENESIS:STATE").hexdigest()
    
    return SystemState(
        state_id="state_0",
        version=0,
        state_hash=genesis_hash,
        timestamp=datetime.utcnow(),
        parent_state_id=None,  # Genesis has no parent
    )
