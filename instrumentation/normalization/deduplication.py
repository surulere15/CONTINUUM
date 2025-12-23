"""
Deduplication

Content-hash based deduplication of signals.
No aggregation, no merging, no summarization.

INSTRUMENTATION MODULE - No imports from kernel/cognitive/execution/agents.
"""

from dataclasses import dataclass
from typing import Dict, Set, List, Optional
import hashlib

from ..schema.signal_base import CivilizationSignal


@dataclass(frozen=True)
class DeduplicationResult:
    """Result of deduplication check."""
    is_duplicate: bool
    existing_signal_id: Optional[str] = None
    content_hash: Optional[str] = None


class SignalDeduplicator:
    """
    Content-hash based signal deduplication.
    
    Prevents storage of identical signals.
    Uses signal content (not ID) for comparison.
    
    Rules:
    - Pure content comparison
    - No signal merging
    - No aggregation
    - No summarization
    """
    
    def __init__(self):
        # Map of content_hash -> signal_id
        self._seen_hashes: Dict[str, str] = {}
    
    def compute_content_hash(self, signal: CivilizationSignal) -> str:
        """
        Compute content hash for a signal.
        
        Hash is based on:
        - domain
        - name
        - value
        - unit
        - timestamp
        - source
        
        Does NOT include signal_id (which may vary for same content).
        """
        content = (
            f"{signal.domain}|"
            f"{signal.name}|"
            f"{signal.value}|"
            f"{signal.unit}|"
            f"{signal.timestamp.isoformat()}|"
            f"{signal.source}"
        )
        return hashlib.sha256(content.encode()).hexdigest()
    
    def check(self, signal: CivilizationSignal) -> DeduplicationResult:
        """
        Check if signal is a duplicate.
        
        Args:
            signal: Signal to check
            
        Returns:
            DeduplicationResult indicating if duplicate
        """
        content_hash = self.compute_content_hash(signal)
        
        if content_hash in self._seen_hashes:
            return DeduplicationResult(
                is_duplicate=True,
                existing_signal_id=self._seen_hashes[content_hash],
                content_hash=content_hash,
            )
        
        return DeduplicationResult(
            is_duplicate=False,
            content_hash=content_hash,
        )
    
    def register(self, signal: CivilizationSignal) -> str:
        """
        Register a signal's content hash.
        
        Returns:
            Content hash
        """
        content_hash = self.compute_content_hash(signal)
        self._seen_hashes[content_hash] = signal.signal_id
        return content_hash
    
    def check_and_register(self, signal: CivilizationSignal) -> DeduplicationResult:
        """
        Check for duplicate and register if new.
        
        Args:
            signal: Signal to check and register
            
        Returns:
            DeduplicationResult
        """
        result = self.check(signal)
        if not result.is_duplicate:
            self.register(signal)
        return result
    
    def dedupe_batch(self, signals: List[CivilizationSignal]) -> tuple:
        """
        Deduplicate a batch of signals.
        
        Returns:
            Tuple of (unique_signals, duplicate_signals)
        """
        unique = []
        duplicates = []
        
        for signal in signals:
            result = self.check_and_register(signal)
            if result.is_duplicate:
                duplicates.append(signal)
            else:
                unique.append(signal)
        
        return unique, duplicates
    
    @property
    def registered_count(self) -> int:
        """Number of registered unique signals."""
        return len(self._seen_hashes)
