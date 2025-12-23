"""
Audit Immutability Guarantees

Ensures audit log cannot be modified, truncated, or corrupted.

KERNEL AUDIT - Phase A. Zero autonomy.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
import hashlib


class ImmutabilityViolation(Exception):
    """Raised when immutability is violated."""
    pass


@dataclass(frozen=True)
class ImmutabilityProof:
    """
    Proof that audit log is immutable.
    
    Contains verification hashes and timestamps.
    """
    log_hash: str
    entry_count: int
    chain_head: str
    verified_at: datetime
    valid: bool


class AuditImmutability:
    """
    Enforces immutability guarantees for audit logs.
    
    Protects against:
    - Modification of entries
    - Deletion of entries
    - Truncation of log
    - Corruption of chain
    
    If any violation is detected → immediate flag.
    """
    
    def __init__(self):
        """Initialize immutability checker."""
        self._baseline_hash: Optional[str] = None
        self._baseline_count: int = 0
        self._verification_log: List[ImmutabilityProof] = []
    
    def establish_baseline(self, audit_log) -> str:
        """
        Establish baseline for immutability checking.
        
        Args:
            audit_log: Audit log to baseline
            
        Returns:
            Baseline hash
        """
        events = audit_log.get_events()
        content = "|".join(e.event_hash for e in events)
        self._baseline_hash = hashlib.sha256(content.encode()).hexdigest()
        self._baseline_count = len(events)
        return self._baseline_hash
    
    def verify(self, audit_log) -> ImmutabilityProof:
        """
        Verify audit log immutability.
        
        Checks:
        - Chain integrity
        - No entries removed
        - Content unchanged
        
        Args:
            audit_log: Audit log to verify
            
        Returns:
            ImmutabilityProof
        """
        events = audit_log.get_events()
        current_count = len(events)
        
        # Check for deletion (count decreased)
        if self._baseline_count > 0 and current_count < self._baseline_count:
            proof = ImmutabilityProof(
                log_hash="",
                entry_count=current_count,
                chain_head=audit_log.chain_head,
                verified_at=datetime.utcnow(),
                valid=False,
            )
            self._verification_log.append(proof)
            return proof
        
        # Verify chain
        if not audit_log.verify_chain():
            proof = ImmutabilityProof(
                log_hash="",
                entry_count=current_count,
                chain_head=audit_log.chain_head,
                verified_at=datetime.utcnow(),
                valid=False,
            )
            self._verification_log.append(proof)
            return proof
        
        # Compute current hash (of baseline entries only)
        baseline_events = events[:self._baseline_count]
        content = "|".join(e.event_hash for e in baseline_events)
        current_hash = hashlib.sha256(content.encode()).hexdigest()
        
        # Check if baseline entries changed
        if self._baseline_hash and current_hash != self._baseline_hash:
            proof = ImmutabilityProof(
                log_hash=current_hash,
                entry_count=current_count,
                chain_head=audit_log.chain_head,
                verified_at=datetime.utcnow(),
                valid=False,
            )
            self._verification_log.append(proof)
            return proof
        
        # All checks passed
        full_content = "|".join(e.event_hash for e in events)
        full_hash = hashlib.sha256(full_content.encode()).hexdigest()
        
        proof = ImmutabilityProof(
            log_hash=full_hash,
            entry_count=current_count,
            chain_head=audit_log.chain_head,
            verified_at=datetime.utcnow(),
            valid=True,
        )
        
        # Update baseline to include new entries
        self._baseline_hash = full_hash
        self._baseline_count = current_count
        
        self._verification_log.append(proof)
        return proof
    
    def assert_immutable(self, audit_log) -> None:
        """
        Assert audit log is immutable, raising on violation.
        
        Raises:
            ImmutabilityViolation: If any violation detected
        """
        proof = self.verify(audit_log)
        if not proof.valid:
            raise ImmutabilityViolation(
                "Audit log immutability violated. "
                "Entries may have been modified, deleted, or corrupted."
            )
    
    def get_verification_log(self) -> List[ImmutabilityProof]:
        """Get all verification proofs."""
        return list(self._verification_log)
    
    @property
    def baseline_hash(self) -> Optional[str]:
        """Get baseline hash."""
        return self._baseline_hash
    
    @property
    def baseline_count(self) -> int:
        """Get baseline entry count."""
        return self._baseline_count
