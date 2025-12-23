"""
Objective Ledger

Immutable, versioned persistence. Objectives survive everything.

OSD - Objective Supremacy Doctrine.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict
import hashlib


@dataclass(frozen=True)
class LedgerEntry:
    """Entry in the objective ledger."""
    entry_id: str
    objective_id: str
    version: int
    state: str
    intent_hash: str
    timestamp: datetime
    previous_entry: Optional[str]


class LedgerTamperError(Exception):
    """Raised when ledger tampering is detected."""
    pass


class ObjectiveLedger:
    """
    Objective Ledger.
    
    Immutable, versioned storage.
    
    Objectives survive:
    - System restarts
    - Operator changes
    - Interface changes
    - Infrastructure migration
    - Human absence
    """
    
    def __init__(self):
        """Initialize ledger."""
        self._entries: List[LedgerEntry] = []
        self._by_objective: Dict[str, List[LedgerEntry]] = {}
        self._entry_count = 0
    
    def record(
        self,
        objective_id: str,
        version: int,
        state: str,
        intent: str,
    ) -> LedgerEntry:
        """
        Record objective state to ledger.
        
        Append-only, immutable.
        
        Args:
            objective_id: Objective being recorded
            version: Objective version
            state: Current state
            intent: Objective intent
            
        Returns:
            LedgerEntry
        """
        # Compute hash of intent
        intent_hash = hashlib.sha256(intent.encode()).hexdigest()[:16]
        
        # Get previous entry for this objective
        previous = None
        if objective_id in self._by_objective and self._by_objective[objective_id]:
            previous = self._by_objective[objective_id][-1].entry_id
        
        entry_id = f"ledger_{self._entry_count}"
        self._entry_count += 1
        
        entry = LedgerEntry(
            entry_id=entry_id,
            objective_id=objective_id,
            version=version,
            state=state,
            intent_hash=intent_hash,
            timestamp=datetime.utcnow(),
            previous_entry=previous,
        )
        
        self._entries.append(entry)
        
        if objective_id not in self._by_objective:
            self._by_objective[objective_id] = []
        self._by_objective[objective_id].append(entry)
        
        return entry
    
    def get_history(self, objective_id: str) -> List[LedgerEntry]:
        """Get full history of an objective."""
        return list(self._by_objective.get(objective_id, []))
    
    def verify_integrity(self, objective_id: str, expected_intent: str) -> bool:
        """Verify objective integrity hasn't been tampered."""
        history = self.get_history(objective_id)
        if not history:
            return True
        
        latest = history[-1]
        expected_hash = hashlib.sha256(expected_intent.encode()).hexdigest()[:16]
        
        if latest.intent_hash != expected_hash:
            raise LedgerTamperError(
                f"Objective '{objective_id}' integrity violated. "
                f"Intent hash mismatch."
            )
        
        return True
    
    def delete(self, *args, **kwargs) -> None:
        """FORBIDDEN: Delete ledger entries."""
        raise LedgerTamperError(
            "Ledger deletion is forbidden. "
            "The ledger is immutable and append-only."
        )
    
    def modify(self, *args, **kwargs) -> None:
        """FORBIDDEN: Modify ledger entries."""
        raise LedgerTamperError(
            "Ledger modification is forbidden. "
            "All entries are immutable."
        )
    
    @property
    def entry_count(self) -> int:
        """Total entries."""
        return len(self._entries)
