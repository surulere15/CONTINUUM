"""
Immutability Seal

Hash-locks the canon. Permanently revokes write access.

KERNEL CANON - Phase B. Zero autonomy.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import hashlib

from .objective_schema import ObjectiveCanon


class SealError(Exception):
    """Raised on seal errors."""
    pass


class SealViolationError(SealError):
    """Raised when seal is violated."""
    pass


@dataclass(frozen=True)
class SealRecord:
    """Record of canon sealing."""
    canon_id: str
    hash_seal: str
    sealed_at: datetime
    genesis_key_ref: str
    write_access_revoked: bool


class ImmutabilitySeal:
    """
    Seals the Objective Canon permanently.
    
    Once sealed:
    - Canon hash is computed and locked
    - Write access is permanently revoked
    - Any future change requires Genesis Key authority
    
    Seal violation → immediate detection.
    """
    
    def __init__(self):
        """Initialize seal."""
        self._seal_record: Optional[SealRecord] = None
        self._sealed = False
    
    def seal(self, canon: ObjectiveCanon) -> SealRecord:
        """
        Seal the canon.
        
        Args:
            canon: Canon to seal
            
        Returns:
            SealRecord
        """
        if self._sealed:
            raise SealError("Canon is already sealed")
        
        # Compute hash
        content = "|".join(obj.compute_hash() for obj in canon.objectives)
        hash_seal = hashlib.sha256(content.encode()).hexdigest()
        
        record = SealRecord(
            canon_id=canon.canon_id,
            hash_seal=hash_seal,
            sealed_at=datetime.utcnow(),
            genesis_key_ref="GENESIS_AUTHORITY",
            write_access_revoked=True,
        )
        
        self._seal_record = record
        self._sealed = True
        
        return record
    
    def verify(self, canon: ObjectiveCanon) -> bool:
        """
        Verify canon seal integrity.
        
        Args:
            canon: Canon to verify
            
        Returns:
            True if seal is intact
        """
        if not self._seal_record:
            return False
        
        # Recompute hash
        content = "|".join(obj.compute_hash() for obj in canon.objectives)
        current_hash = hashlib.sha256(content.encode()).hexdigest()
        
        return current_hash == self._seal_record.hash_seal
    
    def assert_sealed(self, canon: ObjectiveCanon) -> None:
        """
        Assert canon seal is intact.
        
        Raises:
            SealViolationError: If seal is broken
        """
        if not self._sealed:
            raise SealViolationError("Canon is not sealed")
        
        if not self.verify(canon):
            raise SealViolationError(
                "Seal violation detected. Canon has been modified."
            )
    
    def unseal(self, *args, **kwargs) -> None:
        """
        FORBIDDEN: Unseal the canon.
        
        Write access is permanently revoked.
        """
        raise SealError(
            "Canon cannot be unsealed. "
            "Write access is permanently revoked. "
            "Modification requires Genesis Key authority."
        )
    
    def modify_sealed_canon(self, *args, **kwargs) -> None:
        """
        FORBIDDEN: Modify sealed canon.
        """
        raise SealViolationError(
            "Cannot modify sealed canon. "
            "The canon is immutable after sealing."
        )
    
    @property
    def is_sealed(self) -> bool:
        """Check if seal is active."""
        return self._sealed
    
    @property
    def seal_record(self) -> Optional[SealRecord]:
        """Get seal record."""
        return self._seal_record
