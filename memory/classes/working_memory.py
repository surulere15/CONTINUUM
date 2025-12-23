"""
Working Memory (Mw)

Volatile, size-bounded, automatically decays.
Overflow causes forced compression, not expansion.

MMCP-C - Memory Model & Cognitive Persistence.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from enum import Enum


@dataclass
class WorkingMemoryEntry:
    """Entry in working memory."""
    entry_id: str
    content: str
    goal_reference: str
    created_at: datetime
    expires_at: datetime
    priority: float


class MemoryOverflowError(Exception):
    """Raised when working memory overflows."""
    pass


class WorkingMemory:
    """
    Working Memory (Mw).
    
    Purpose: Immediate reasoning context
    
    Properties:
    - Volatile
    - Size-bounded: |Mw| <= λ
    - Automatically decays
    
    Contents:
    - Current goals
    - Active plans
    - Local context envelopes
    
    Overflow causes forced compression, not expansion.
    """
    
    DEFAULT_CAPACITY = 100  # λ
    DEFAULT_TTL = timedelta(hours=1)
    
    def __init__(self, capacity: int = DEFAULT_CAPACITY):
        """Initialize working memory."""
        self._capacity = capacity
        self._entries: Dict[str, WorkingMemoryEntry] = {}
        self._entry_count = 0
    
    def store(
        self,
        content: str,
        goal_reference: str,
        priority: float = 0.5,
        ttl: Optional[timedelta] = None,
    ) -> WorkingMemoryEntry:
        """
        Store entry in working memory.
        
        Args:
            content: Content to store
            goal_reference: Associated goal
            priority: Priority 0-1
            ttl: Time to live
            
        Returns:
            WorkingMemoryEntry
        """
        # Clean expired entries first
        self._decay()
        
        # Check capacity
        if len(self._entries) >= self._capacity:
            self._compress()
        
        entry_id = f"wm_{self._entry_count}"
        self._entry_count += 1
        
        now = datetime.utcnow()
        ttl = ttl or self.DEFAULT_TTL
        
        entry = WorkingMemoryEntry(
            entry_id=entry_id,
            content=content,
            goal_reference=goal_reference,
            created_at=now,
            expires_at=now + ttl,
            priority=priority,
        )
        
        self._entries[entry_id] = entry
        return entry
    
    def retrieve(self, entry_id: str) -> Optional[WorkingMemoryEntry]:
        """Retrieve entry by ID."""
        self._decay()
        return self._entries.get(entry_id)
    
    def retrieve_by_goal(self, goal_reference: str) -> List[WorkingMemoryEntry]:
        """Retrieve entries for a goal."""
        self._decay()
        return [
            e for e in self._entries.values()
            if e.goal_reference == goal_reference
        ]
    
    def _decay(self) -> int:
        """Remove expired entries. Returns count removed."""
        now = datetime.utcnow()
        expired = [
            eid for eid, entry in self._entries.items()
            if entry.expires_at <= now
        ]
        for eid in expired:
            del self._entries[eid]
        return len(expired)
    
    def _compress(self) -> int:
        """
        Compress working memory by removing lowest priority.
        
        Overflow causes compression, not expansion.
        """
        if not self._entries:
            return 0
        
        # Remove lowest priority entries until under capacity
        sorted_entries = sorted(
            self._entries.items(),
            key=lambda x: x[1].priority,
        )
        
        to_remove = len(self._entries) - (self._capacity // 2)
        removed = 0
        
        for eid, _ in sorted_entries[:to_remove]:
            del self._entries[eid]
            removed += 1
        
        return removed
    
    def expand_capacity(self, *args, **kwargs) -> None:
        """FORBIDDEN: Expand capacity."""
        raise MemoryOverflowError(
            "Working memory capacity cannot be expanded. "
            "Overflow causes compression, not expansion. |Mw| <= λ"
        )
    
    @property
    def size(self) -> int:
        """Current number of entries."""
        return len(self._entries)
    
    @property
    def capacity(self) -> int:
        """Maximum capacity λ."""
        return self._capacity
