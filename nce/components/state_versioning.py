"""
State Versioning & Rollback Module (SVRM)

Guarantees recoverability. Rollback is authoritative, not advisory.

NCE COMPONENT - Neural Continuum Engine.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import hashlib


@dataclass(frozen=True)
class StateSnapshot:
    """
    Complete state snapshot for rollback.
    
    Rollback must restore:
    - Identity
    - Context
    - Memory snapshot
    - Governance state
    """
    snapshot_id: str
    version: int
    identity_hash: str
    context_hash: str
    memory_hash: str
    governance_hash: str
    created_at: datetime


@dataclass(frozen=True)
class RollbackResult:
    """Result of rollback operation."""
    from_version: int
    to_version: int
    snapshot: StateSnapshot
    restored_at: datetime
    success: bool


class RollbackError(Exception):
    """Raised when rollback fails."""
    pass


class StateVersioning:
    """
    State Versioning & Rollback Module (SVRM).
    
    Purpose: Guarantee recoverability.
    
    Rules:
    - Every state is versioned
    - Rollback restores: identity, context, memory, governance
    - Rollback is authoritative, not advisory
    """
    
    def __init__(self):
        """Initialize state versioning."""
        self._snapshots: Dict[int, StateSnapshot] = {}
        self._current_version = 0
    
    def capture(
        self,
        identity_hash: str,
        context_hash: str,
        memory_hash: str,
        governance_hash: str,
    ) -> StateSnapshot:
        """
        Capture state snapshot.
        
        Args:
            identity_hash: Hash of identity state
            context_hash: Hash of context state
            memory_hash: Hash of memory state
            governance_hash: Hash of governance state
            
        Returns:
            StateSnapshot
        """
        self._current_version += 1
        
        snapshot = StateSnapshot(
            snapshot_id=f"snapshot_{self._current_version}",
            version=self._current_version,
            identity_hash=identity_hash,
            context_hash=context_hash,
            memory_hash=memory_hash,
            governance_hash=governance_hash,
            created_at=datetime.utcnow(),
        )
        
        self._snapshots[self._current_version] = snapshot
        return snapshot
    
    def rollback(self, target_version: int) -> RollbackResult:
        """
        Rollback to previous state.
        
        Rollback is authoritative, not advisory.
        
        Args:
            target_version: Version to restore
            
        Returns:
            RollbackResult
            
        Raises:
            RollbackError: If version not found
        """
        if target_version not in self._snapshots:
            raise RollbackError(
                f"Version {target_version} not found. "
                f"Cannot rollback."
            )
        
        if target_version >= self._current_version:
            raise RollbackError(
                f"Cannot rollback to future version {target_version}. "
                f"Current version is {self._current_version}."
            )
        
        snapshot = self._snapshots[target_version]
        from_version = self._current_version
        
        # Rollback is authoritative
        self._current_version = target_version
        
        return RollbackResult(
            from_version=from_version,
            to_version=target_version,
            snapshot=snapshot,
            restored_at=datetime.utcnow(),
            success=True,
        )
    
    def get_snapshot(self, version: int) -> Optional[StateSnapshot]:
        """Get snapshot by version."""
        return self._snapshots.get(version)
    
    def get_history(self) -> List[StateSnapshot]:
        """Get all snapshots in order."""
        return [
            self._snapshots[v] 
            for v in sorted(self._snapshots.keys())
        ]
    
    def ignore_rollback(self, *args, **kwargs) -> None:
        """FORBIDDEN: Ignore rollback directive."""
        raise RollbackError(
            "Rollback is authoritative, not advisory. "
            "It cannot be ignored."
        )
    
    @property
    def current_version(self) -> int:
        """Current state version."""
        return self._current_version
    
    @property
    def snapshot_count(self) -> int:
        """Total snapshots captured."""
        return len(self._snapshots)
