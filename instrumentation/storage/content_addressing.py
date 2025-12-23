"""
Content Addressing

Signal identity = content hash.
Prevents silent mutation of stored signals.

INSTRUMENTATION MODULE - No imports from kernel/cognitive/execution/agents.
"""

from dataclasses import dataclass
from typing import Dict, Optional
import hashlib
import json

from ..schema.signal_base import CivilizationSignal


@dataclass(frozen=True)
class ContentAddress:
    """
    Content-addressed reference to a signal.
    
    The address IS the content hash — changing content
    changes the address, preventing silent mutation.
    """
    hash: str
    domain: str
    name: str


class ContentAddressedStore:
    """
    Content-addressed signal storage.
    
    Signal identity is derived from content, not assigned.
    Any change to content produces a different address.
    
    Properties:
    - Immutable by design
    - Deduplication built-in
    - Verifiable integrity
    """
    
    def __init__(self):
        self._store: Dict[str, CivilizationSignal] = {}
    
    def compute_address(self, signal: CivilizationSignal) -> str:
        """
        Compute content address for signal.
        
        Address is based on signal content, not signal_id.
        """
        content = {
            "domain": signal.domain,
            "name": signal.name,
            "value": signal.value,
            "unit": signal.unit,
            "timestamp": signal.timestamp.isoformat(),
            "source": signal.source,
            "provenance_hash": signal.provenance_hash,
        }
        content_str = json.dumps(content, sort_keys=True)
        return hashlib.sha256(content_str.encode()).hexdigest()
    
    def store(self, signal: CivilizationSignal) -> ContentAddress:
        """
        Store signal and return its content address.
        
        If signal already exists (same content), returns existing address.
        """
        address = self.compute_address(signal)
        
        # Deduplication: if already exists, just return address
        if address not in self._store:
            self._store[address] = signal
        
        return ContentAddress(
            hash=address,
            domain=signal.domain,
            name=signal.name,
        )
    
    def retrieve(self, address: str) -> Optional[CivilizationSignal]:
        """
        Retrieve signal by content address.
        
        Args:
            address: Content hash
            
        Returns:
            Signal if found, None otherwise
        """
        return self._store.get(address)
    
    def verify(self, address: str) -> bool:
        """
        Verify stored signal matches its address.
        
        Returns True if signal exists and hash matches.
        """
        signal = self._store.get(address)
        if signal is None:
            return False
        
        computed = self.compute_address(signal)
        return computed == address
    
    def exists(self, address: str) -> bool:
        """Check if address exists in store."""
        return address in self._store
    
    @property
    def count(self) -> int:
        """Number of stored signals."""
        return len(self._store)
