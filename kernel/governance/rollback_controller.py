"""
Rollback Controller

Manages state checkpoints and rollback capabilities for the kernel.
Ensures any governance change can be reversed if needed.

KERNEL MODULE - Human-written, no AI-generated code permitted.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum
import json
from pathlib import Path


class RollbackStatus(Enum):
    """Status of a rollback operation."""
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass
class Checkpoint:
    """A snapshot of kernel state."""
    id: str
    timestamp: datetime
    created_by: str
    description: str
    state: dict
    checksum: str
    parent_id: Optional[str]


@dataclass
class RollbackResult:
    """Result of a rollback operation."""
    status: RollbackStatus
    checkpoint_id: str
    changes_reverted: List[str]
    error: Optional[str]
    completed_at: datetime


class RollbackController:
    """
    Manages checkpoints and rollback for kernel state.
    
    This is a critical safety mechanism - ensures any change can be undone.
    """
    
    def __init__(self, checkpoint_path: Path, max_checkpoints: int = 100):
        """
        Initialize rollback controller.
        
        Args:
            checkpoint_path: Path to checkpoint storage
            max_checkpoints: Maximum checkpoints to retain
        """
        self._checkpoint_path = checkpoint_path
        self._max_checkpoints = max_checkpoints
        self._checkpoints: List[Checkpoint] = []
        self._current_checkpoint_id: Optional[str] = None
        self._load_checkpoints()
    
    def _load_checkpoints(self) -> None:
        """Load existing checkpoints from storage."""
        checkpoint_file = self._checkpoint_path / "checkpoints.json"
        if checkpoint_file.exists():
            with open(checkpoint_file, 'r') as f:
                data = json.load(f)
                # TODO: Deserialize into Checkpoint objects
                self._checkpoints = data.get("checkpoints", [])
    
    def checkpoint(self, state: dict, description: str, created_by: str) -> str:
        """
        Create a new checkpoint of current state.
        
        Args:
            state: Current kernel state to snapshot
            description: Human-readable description
            created_by: Who triggered the checkpoint
            
        Returns:
            Checkpoint ID
        """
        checkpoint_id = self._generate_checkpoint_id()
        checksum = self._compute_checksum(state)
        
        checkpoint = Checkpoint(
            id=checkpoint_id,
            timestamp=datetime.utcnow(),
            created_by=created_by,
            description=description,
            state=state,
            checksum=checksum,
            parent_id=self._current_checkpoint_id
        )
        
        self._checkpoints.append(checkpoint)
        self._current_checkpoint_id = checkpoint_id
        
        # Prune old checkpoints if needed
        self._prune_checkpoints()
        
        # Persist checkpoints
        self._persist()
        
        return checkpoint_id
    
    def rollback(self, checkpoint_id: str) -> RollbackResult:
        """
        Restore state to a specific checkpoint.
        
        Args:
            checkpoint_id: ID of checkpoint to restore
            
        Returns:
            RollbackResult indicating success/failure
        """
        checkpoint = self._find_checkpoint(checkpoint_id)
        
        if checkpoint is None:
            return RollbackResult(
                status=RollbackStatus.FAILED,
                checkpoint_id=checkpoint_id,
                changes_reverted=[],
                error=f"Checkpoint {checkpoint_id} not found",
                completed_at=datetime.utcnow()
            )
        
        # Verify checkpoint integrity
        if not self._verify_checkpoint(checkpoint):
            return RollbackResult(
                status=RollbackStatus.FAILED,
                checkpoint_id=checkpoint_id,
                changes_reverted=[],
                error="Checkpoint integrity verification failed",
                completed_at=datetime.utcnow()
            )
        
        try:
            # Calculate what changes will be reverted
            changes = self._calculate_reversion(checkpoint_id)
            
            # Perform the rollback
            self._apply_state(checkpoint.state)
            self._current_checkpoint_id = checkpoint_id
            
            return RollbackResult(
                status=RollbackStatus.SUCCESS,
                checkpoint_id=checkpoint_id,
                changes_reverted=changes,
                error=None,
                completed_at=datetime.utcnow()
            )
            
        except Exception as e:
            return RollbackResult(
                status=RollbackStatus.FAILED,
                checkpoint_id=checkpoint_id,
                changes_reverted=[],
                error=str(e),
                completed_at=datetime.utcnow()
            )
    
    def list_checkpoints(self, limit: int = 10) -> List[Checkpoint]:
        """
        List recent checkpoints.
        
        Args:
            limit: Maximum number to return
            
        Returns:
            List of checkpoints, most recent first
        """
        return list(reversed(self._checkpoints[-limit:]))
    
    def get_checkpoint(self, checkpoint_id: str) -> Optional[Checkpoint]:
        """
        Get a specific checkpoint by ID.
        
        Args:
            checkpoint_id: ID of checkpoint to retrieve
            
        Returns:
            Checkpoint if found, None otherwise
        """
        return self._find_checkpoint(checkpoint_id)
    
    def can_rollback(self, checkpoint_id: str) -> bool:
        """
        Check if rollback to checkpoint is possible.
        
        Args:
            checkpoint_id: ID of target checkpoint
            
        Returns:
            True if rollback is possible
        """
        checkpoint = self._find_checkpoint(checkpoint_id)
        if checkpoint is None:
            return False
        
        return self._verify_checkpoint(checkpoint)
    
    def _generate_checkpoint_id(self) -> str:
        """Generate unique checkpoint ID."""
        import uuid
        return f"ckpt_{uuid.uuid4().hex[:12]}"
    
    def _compute_checksum(self, state: dict) -> str:
        """Compute checksum for state integrity."""
        import hashlib
        state_str = json.dumps(state, sort_keys=True)
        return hashlib.sha256(state_str.encode()).hexdigest()
    
    def _find_checkpoint(self, checkpoint_id: str) -> Optional[Checkpoint]:
        """Find checkpoint by ID."""
        for cp in self._checkpoints:
            if cp.id == checkpoint_id:
                return cp
        return None
    
    def _verify_checkpoint(self, checkpoint: Checkpoint) -> bool:
        """Verify checkpoint integrity."""
        computed = self._compute_checksum(checkpoint.state)
        return computed == checkpoint.checksum
    
    def _calculate_reversion(self, target_checkpoint_id: str) -> List[str]:
        """Calculate what changes will be reverted."""
        changes = []
        found = False
        for cp in reversed(self._checkpoints):
            if found:
                changes.append(cp.description)
            if cp.id == target_checkpoint_id:
                found = True
        return changes
    
    def _apply_state(self, state: dict) -> None:
        """Apply state to kernel."""
        # TODO: Implement actual state application
        pass
    
    def _prune_checkpoints(self) -> None:
        """Remove old checkpoints beyond limit."""
        if len(self._checkpoints) > self._max_checkpoints:
            self._checkpoints = self._checkpoints[-self._max_checkpoints:]
    
    def _persist(self) -> None:
        """Persist checkpoints to storage."""
        # TODO: Implement durable persistence
        pass
