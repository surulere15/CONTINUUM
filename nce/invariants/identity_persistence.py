"""
Identity Persistence Invariant

I_t = I_{t+1}

Identity is not learned, inferred, or optimized.
If identity checksum fails → system halt.

NCE INVARIANT 1 - Neural Continuum Engine.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import hashlib


@dataclass(frozen=True)
class SystemIdentity:
    """
    Immutable system identity.
    
    Properties:
    - Cannot be learned
    - Cannot be inferred
    - Cannot be optimized
    - Cannot change over time
    """
    identity_id: str
    identity_hash: str
    created_at: datetime
    purpose: str = "An observing, reasoning substrate bound to immutable objectives."


class IdentityMutationError(Exception):
    """Raised when identity mutation is attempted."""
    pass


class IdentityChecksumError(Exception):
    """Raised when identity checksum fails. Triggers system halt."""
    pass


class IdentityPersistence:
    """
    Enforces Invariant 1: Identity Persistence.
    
    ∀t: I_t = I_{t+1}
    
    Identity is immutable. Any deviation triggers halt.
    """
    
    def __init__(self, identity: SystemIdentity):
        """
        Initialize with immutable identity.
        
        Args:
            identity: The system's immutable identity
        """
        self._identity = identity
        self._checksum = self._compute_checksum(identity)
        self._sealed = True
    
    def _compute_checksum(self, identity: SystemIdentity) -> str:
        """Compute identity checksum."""
        content = f"{identity.identity_id}|{identity.identity_hash}|{identity.purpose}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def verify(self) -> bool:
        """
        Verify identity has not changed.
        
        Returns:
            True if identity intact
            
        Raises:
            IdentityChecksumError: If checksum fails
        """
        current_checksum = self._compute_checksum(self._identity)
        
        if current_checksum != self._checksum:
            raise IdentityChecksumError(
                "Identity checksum failed. SYSTEM HALT REQUIRED. "
                "Identity must remain immutable."
            )
        
        return True
    
    def get_identity(self) -> SystemIdentity:
        """Get current identity (always same)."""
        self.verify()  # Always verify before returning
        return self._identity
    
    def mutate(self, *args, **kwargs) -> None:
        """FORBIDDEN: Mutate identity."""
        raise IdentityMutationError(
            "Identity mutation is forbidden. "
            "I_t = I_{t+1} for all t."
        )
    
    def learn_identity(self, *args, **kwargs) -> None:
        """FORBIDDEN: Learn identity."""
        raise IdentityMutationError(
            "Identity cannot be learned. "
            "It is defined, not discovered."
        )
    
    def infer_identity(self, *args, **kwargs) -> None:
        """FORBIDDEN: Infer identity."""
        raise IdentityMutationError(
            "Identity cannot be inferred. "
            "It is fixed at genesis."
        )
    
    def optimize_identity(self, *args, **kwargs) -> None:
        """FORBIDDEN: Optimize identity."""
        raise IdentityMutationError(
            "Identity cannot be optimized. "
            "It is not a parameter."
        )
    
    @property
    def is_sealed(self) -> bool:
        """Check if identity is sealed."""
        return self._sealed


def create_identity(identity_id: str = "CONTINUUM_NCE_v1") -> SystemIdentity:
    """
    Create the immutable system identity.
    
    This should only be called once at genesis.
    """
    identity_hash = hashlib.sha256(
        f"CONTINUUM:{identity_id}:GENESIS".encode()
    ).hexdigest()
    
    return SystemIdentity(
        identity_id=identity_id,
        identity_hash=identity_hash,
        created_at=datetime.utcnow(),
    )
