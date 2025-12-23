"""
Append-Only Log

Immutable, hash-chained signal storage.
No updates, only supersessions. Never deletes audit trail.

INSTRUMENTATION MODULE - No imports from kernel/cognitive/execution/agents.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Iterator
import hashlib
import json
from pathlib import Path

from ..schema.signal_base import CivilizationSignal


@dataclass(frozen=True)
class LogEntry:
    """
    A single entry in the append-only log.
    
    Each entry is hash-chained to the previous.
    """
    sequence: int
    signal: CivilizationSignal
    timestamp: datetime
    content_hash: str
    previous_hash: str


class AppendOnlyLogError(Exception):
    """Raised when log integrity is violated."""
    pass


class AppendOnlyLog:
    """
    Append-only, hash-chained signal log.
    
    Properties:
    - Every signal is an event
    - No updates, only supersessions
    - Hash-chained for integrity
    - Never deletes any entry
    
    Rules:
    - Cannot modify existing entries
    - Cannot delete entries
    - Can only append
    """
    
    GENESIS_HASH = "0" * 64  # Genesis block hash
    
    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize append-only log.
        
        Args:
            storage_path: Optional path for persistent storage
        """
        self._entries: List[LogEntry] = []
        self._storage_path = storage_path
        self._current_hash = self.GENESIS_HASH
        
        if storage_path:
            self._load()
    
    def append(self, signal: CivilizationSignal) -> LogEntry:
        """
        Append a signal to the log.
        
        Args:
            signal: Signal to append
            
        Returns:
            LogEntry with hash chain
        """
        sequence = len(self._entries)
        timestamp = datetime.utcnow()
        
        # Compute content hash
        content = self._serialize_signal(signal)
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        
        # Create chain hash
        chain_input = f"{self._current_hash}|{content_hash}"
        chain_hash = hashlib.sha256(chain_input.encode()).hexdigest()
        
        entry = LogEntry(
            sequence=sequence,
            signal=signal,
            timestamp=timestamp,
            content_hash=content_hash,
            previous_hash=self._current_hash,
        )
        
        self._entries.append(entry)
        self._current_hash = chain_hash
        
        if self._storage_path:
            self._persist_entry(entry)
        
        return entry
    
    def get(self, sequence: int) -> Optional[LogEntry]:
        """Get entry by sequence number."""
        if 0 <= sequence < len(self._entries):
            return self._entries[sequence]
        return None
    
    def get_latest(self) -> Optional[LogEntry]:
        """Get the most recent entry."""
        if self._entries:
            return self._entries[-1]
        return None
    
    def iterate(self, start: int = 0, end: Optional[int] = None) -> Iterator[LogEntry]:
        """Iterate over entries in range."""
        end = end or len(self._entries)
        for i in range(start, min(end, len(self._entries))):
            yield self._entries[i]
    
    def verify_integrity(self) -> bool:
        """
        Verify hash chain integrity.
        
        Returns:
            True if chain is valid, False if corrupted
        """
        current_hash = self.GENESIS_HASH
        
        for entry in self._entries:
            if entry.previous_hash != current_hash:
                return False
            
            # Recompute chain hash
            content = self._serialize_signal(entry.signal)
            content_hash = hashlib.sha256(content.encode()).hexdigest()
            
            if content_hash != entry.content_hash:
                return False
            
            chain_input = f"{current_hash}|{content_hash}"
            current_hash = hashlib.sha256(chain_input.encode()).hexdigest()
        
        return True
    
    @property
    def length(self) -> int:
        """Number of entries in log."""
        return len(self._entries)
    
    @property
    def current_hash(self) -> str:
        """Current chain head hash."""
        return self._current_hash
    
    def _serialize_signal(self, signal: CivilizationSignal) -> str:
        """Serialize signal for hashing."""
        return (
            f"{signal.signal_id}|{signal.domain}|{signal.name}|"
            f"{signal.value}|{signal.unit}|{signal.timestamp.isoformat()}|"
            f"{signal.source}|{signal.provenance_hash}"
        )
    
    def _persist_entry(self, entry: LogEntry) -> None:
        """Persist entry to storage."""
        if not self._storage_path:
            return
        
        self._storage_path.mkdir(parents=True, exist_ok=True)
        log_file = self._storage_path / "signal_log.jsonl"
        
        data = {
            "sequence": entry.sequence,
            "signal_id": entry.signal.signal_id,
            "domain": entry.signal.domain,
            "name": entry.signal.name,
            "value": entry.signal.value,
            "unit": entry.signal.unit,
            "timestamp": entry.signal.timestamp.isoformat(),
            "source": entry.signal.source,
            "provenance_hash": entry.signal.provenance_hash,
            "content_hash": entry.content_hash,
            "previous_hash": entry.previous_hash,
            "logged_at": entry.timestamp.isoformat(),
        }
        
        with open(log_file, 'a') as f:
            f.write(json.dumps(data) + "\n")
    
    def _load(self) -> None:
        """Load entries from storage."""
        if not self._storage_path:
            return
        
        log_file = self._storage_path / "signal_log.jsonl"
        if not log_file.exists():
            return
        
        # TODO: Implement loading from persistent storage
        pass
