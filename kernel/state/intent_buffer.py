"""
Intent Buffer

Ephemeral storage for stabilized intents.
Time-bounded, auto-expiring, hash-verified.

KERNEL MODULE - No imports from execution/agents/learning.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import hashlib


class IntentBufferError(Exception):
    """Raised on intent buffer errors."""
    pass


class IntentExpiredError(IntentBufferError):
    """Raised when accessing expired intent."""
    pass


class IntentModificationError(IntentBufferError):
    """Raised when attempting to modify buffered intent."""
    pass


@dataclass(frozen=True)
class BufferedIntent:
    """
    An intent stored in the ephemeral buffer.
    
    Time-bounded and hash-verified.
    """
    intent_id: str
    content_hash: str
    buffered_at: datetime
    expires_at: datetime
    source: str
    verified: bool


class IntentBuffer:
    """
    Ephemeral buffer for stabilized intents.
    
    Properties:
    - Read-only outside Phase E
    - Time-bounded
    - Auto-expiring
    - Hash-verified
    
    No persistence beyond the stabilization window.
    """
    
    DEFAULT_TTL = timedelta(minutes=30)
    
    def __init__(self, ttl: Optional[timedelta] = None):
        """
        Initialize intent buffer.
        
        Args:
            ttl: Time-to-live for buffered intents
        """
        self._ttl = ttl or self.DEFAULT_TTL
        self._buffer: Dict[str, BufferedIntent] = {}
        self._content: Dict[str, any] = {}  # Actual intent content
    
    def add(self, intent_id: str, content: any, source: str) -> str:
        """
        Add intent to buffer.
        
        Args:
            intent_id: Intent identifier
            content: Intent content
            source: Source of intent
            
        Returns:
            Content hash
        """
        now = datetime.utcnow()
        content_hash = self._compute_hash(content)
        
        buffered = BufferedIntent(
            intent_id=intent_id,
            content_hash=content_hash,
            buffered_at=now,
            expires_at=now + self._ttl,
            source=source,
            verified=True,
        )
        
        self._buffer[intent_id] = buffered
        self._content[intent_id] = content
        
        return content_hash
    
    def get(self, intent_id: str) -> any:
        """
        Get intent from buffer.
        
        Args:
            intent_id: Intent identifier
            
        Returns:
            Intent content
            
        Raises:
            IntentExpiredError: If intent has expired
            KeyError: If intent not found
        """
        if intent_id not in self._buffer:
            raise KeyError(f"Intent {intent_id} not in buffer")
        
        buffered = self._buffer[intent_id]
        
        # Check expiry
        if datetime.utcnow() > buffered.expires_at:
            self._remove(intent_id)
            raise IntentExpiredError(
                f"Intent {intent_id} has expired and was removed from buffer."
            )
        
        # Verify integrity
        content = self._content[intent_id]
        current_hash = self._compute_hash(content)
        
        if current_hash != buffered.content_hash:
            raise IntentBufferError(
                f"INTEGRITY VIOLATION: Intent {intent_id} hash mismatch. "
                f"Expected {buffered.content_hash}, got {current_hash}"
            )
        
        return content
    
    def modify(self, *args, **kwargs) -> None:
        """
        FORBIDDEN: Modify buffered intent.
        
        Buffer is read-only.
        """
        raise IntentModificationError(
            "Intent buffer is read-only. "
            "Buffered intents cannot be modified."
        )
    
    def contains(self, intent_id: str) -> bool:
        """Check if intent is in buffer (and not expired)."""
        if intent_id not in self._buffer:
            return False
        
        if datetime.utcnow() > self._buffer[intent_id].expires_at:
            self._remove(intent_id)
            return False
        
        return True
    
    def get_all_valid(self) -> List[str]:
        """Get all non-expired intent IDs."""
        self._cleanup()
        return list(self._buffer.keys())
    
    def clear(self) -> None:
        """Clear all buffered intents."""
        self._buffer.clear()
        self._content.clear()
    
    def _remove(self, intent_id: str) -> None:
        """Remove intent from buffer."""
        self._buffer.pop(intent_id, None)
        self._content.pop(intent_id, None)
    
    def _cleanup(self) -> None:
        """Remove all expired intents."""
        now = datetime.utcnow()
        expired = [
            iid for iid, buffered in self._buffer.items()
            if now > buffered.expires_at
        ]
        for iid in expired:
            self._remove(iid)
    
    def _compute_hash(self, content: any) -> str:
        """Compute hash of content."""
        return hashlib.sha256(str(content).encode()).hexdigest()
    
    @property
    def count(self) -> int:
        """Number of buffered intents (including expired)."""
        return len(self._buffer)
    
    @property
    def valid_count(self) -> int:
        """Number of non-expired intents."""
        self._cleanup()
        return len(self._buffer)
