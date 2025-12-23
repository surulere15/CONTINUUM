"""
Kernel State

Manages the runtime state of the kernel, including loaded axioms,
canon, and current governance configuration.

KERNEL MODULE - Human-written, no AI-generated code permitted.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
from pathlib import Path
import yaml


class KernelStatus(Enum):
    """Operational status of the kernel."""
    INITIALIZING = "initializing"
    RUNNING = "running"
    DEGRADED = "degraded"
    SAFE_MODE = "safe_mode"
    SHUTDOWN = "shutdown"


@dataclass
class StateSnapshot:
    """A snapshot of kernel state at a point in time."""
    timestamp: datetime
    status: KernelStatus
    axioms_loaded: List[str]
    canon_loaded: List[str]
    active_constraints: List[str]
    pending_intents: int
    last_checkpoint: Optional[str]


class KernelState:
    """
    Manages runtime state of the CONTINUUM kernel.
    
    This is the authoritative source for kernel configuration and status.
    """
    
    def __init__(self, config_path: Path):
        """
        Initialize kernel state manager.
        
        Args:
            config_path: Path to kernel configuration directory
        """
        self._config_path = config_path
        self._status = KernelStatus.INITIALIZING
        self._axioms: Dict[str, dict] = {}
        self._canon: Dict[str, dict] = {}
        self._active_constraints: List[str] = []
        self._pending_intents: int = 0
        self._last_checkpoint: Optional[str] = None
        self._initialized_at: Optional[datetime] = None
        
        # Phase B: Objective Canon Hash
        # Set ONCE. Change requires Genesis reset. Mismatch = HALT.
        self._objective_canon_hash: Optional[str] = None
        self._canon_hash_sealed: bool = False
    
    def initialize(self) -> bool:
        """
        Initialize kernel state by loading configuration.
        
        Returns:
            True if initialization successful
        """
        try:
            self._load_axioms()
            self._load_canon()
            self._activate_constraints()
            self._status = KernelStatus.RUNNING
            self._initialized_at = datetime.utcnow()
            return True
        except Exception:
            self._status = KernelStatus.DEGRADED
            return False
    
    def _load_axioms(self) -> None:
        """Load axioms from configuration."""
        axioms_path = self._config_path / "axioms"
        if not axioms_path.exists():
            return
        
        for axiom_file in axioms_path.glob("*.yaml"):
            with open(axiom_file, 'r') as f:
                axiom_data = yaml.safe_load(f)
                axiom_id = axiom_data.get('axiom', {}).get('id')
                if axiom_id:
                    self._axioms[axiom_id] = axiom_data
    
    def _load_canon(self) -> None:
        """Load canon from configuration."""
        canon_path = self._config_path / "canon"
        if not canon_path.exists():
            return
        
        for canon_file in canon_path.glob("*.yaml"):
            with open(canon_file, 'r') as f:
                canon_data = yaml.safe_load(f)
                canon_id = canon_data.get('canon', {}).get('id')
                if canon_id:
                    self._canon[canon_id] = canon_data
    
    def _activate_constraints(self) -> None:
        """Activate constraints from loaded axioms and canon."""
        # Collect all hard constraints
        for axiom_id, axiom_data in self._axioms.items():
            constraints = axiom_data.get('axiom', {}).get('constraints', [])
            for constraint in constraints:
                if constraint.get('enforcement') == 'hard':
                    self._active_constraints.append(f"{axiom_id}:{constraint.get('type')}")
        
        # Collect constraints from invariant constraints canon
        if 'invariant_constraints' in self._canon:
            hard = self._canon['invariant_constraints'].get('hard_constraints', [])
            for constraint in hard:
                self._active_constraints.append(constraint.get('id'))
    
    @property
    def status(self) -> KernelStatus:
        """Get current kernel status."""
        return self._status
    
    @property
    def axioms(self) -> Dict[str, dict]:
        """Get loaded axioms."""
        return self._axioms.copy()
    
    @property
    def canon(self) -> Dict[str, dict]:
        """Get loaded canon."""
        return self._canon.copy()
    
    def get_snapshot(self) -> StateSnapshot:
        """Get current state snapshot."""
        return StateSnapshot(
            timestamp=datetime.utcnow(),
            status=self._status,
            axioms_loaded=list(self._axioms.keys()),
            canon_loaded=list(self._canon.keys()),
            active_constraints=self._active_constraints.copy(),
            pending_intents=self._pending_intents,
            last_checkpoint=self._last_checkpoint
        )
    
    def enter_safe_mode(self, reason: str) -> None:
        """
        Enter safe mode, halting autonomous operations.
        
        Args:
            reason: Reason for entering safe mode
        """
        self._status = KernelStatus.SAFE_MODE
        # TODO: Log reason, notify operators
    
    def shutdown(self, reason: str) -> None:
        """
        Initiate kernel shutdown.
        
        Args:
            reason: Reason for shutdown
        """
        self._status = KernelStatus.SHUTDOWN
        # TODO: Cleanup, persist state, log
    
    def update_pending_intents(self, count: int) -> None:
        """Update pending intent count."""
        self._pending_intents = count
    
    def set_last_checkpoint(self, checkpoint_id: str) -> None:
        """Record last checkpoint."""
        self._last_checkpoint = checkpoint_id
    
    # =========================================================================
    # Phase B: Objective Canon Hash Management
    # =========================================================================
    
    def set_objective_canon_hash(self, canon_hash: str) -> None:
        """
        Set the objective canon hash. CAN ONLY BE SET ONCE.
        
        After sealing, the hash is immutable. Any attempt to change it
        requires a full Genesis reset.
        
        Args:
            canon_hash: SHA-256 hash of the sealed canon
            
        Raises:
            RuntimeError: If hash is already sealed
        """
        if self._canon_hash_sealed:
            raise RuntimeError(
                "CRITICAL: Objective canon hash is sealed. "
                "Modification requires Genesis reset."
            )
        
        self._objective_canon_hash = canon_hash
        self._canon_hash_sealed = True
    
    def verify_canon_hash(self, current_hash: str) -> None:
        """
        Verify canon hash matches sealed value.
        
        If mismatch detected, kernel MUST HALT.
        
        Args:
            current_hash: Current computed canon hash
            
        Raises:
            RuntimeError: On hash mismatch (triggers HALT)
        """
        if self._objective_canon_hash is None:
            raise RuntimeError("Canon hash not set - cannot verify")
        
        if current_hash != self._objective_canon_hash:
            # CRITICAL: Hash mismatch - HALT the kernel
            self._status = KernelStatus.SHUTDOWN
            raise RuntimeError(
                f"CRITICAL: Canon hash mismatch. "
                f"Expected '{self._objective_canon_hash[:16]}...', "
                f"got '{current_hash[:16]}...'. KERNEL HALTED."
            )
    
    @property
    def objective_canon_hash(self) -> Optional[str]:
        """Get sealed canon hash, or None if not sealed."""
        return self._objective_canon_hash
    
    @property
    def is_canon_sealed(self) -> bool:
        """Check if canon hash has been sealed."""
        return self._canon_hash_sealed
