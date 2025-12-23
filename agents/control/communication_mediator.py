"""
Communication Mediator

Mediated channels only. No direct coordination.
Agents cannot form societies.

AGENTS - Phase G. Scale without autonomy.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Set, Optional, Tuple
from enum import Enum
import hashlib


class MessageType(Enum):
    """Types of inter-agent messages."""
    TASK_RESULT = "task_result"
    STATE_QUERY = "state_query"
    COORDINATION_REQUEST = "coordination_request"  # Will be rejected


@dataclass(frozen=True)
class MediatedMessage:
    """
    A message between agents (mediated).
    
    All inter-agent communication goes through mediator.
    """
    message_id: str
    sender: str
    recipient: str
    message_type: MessageType
    content_hash: str
    timestamp: datetime


@dataclass(frozen=True)
class MessageLog:
    """Log entry for a message."""
    message: MediatedMessage
    delivered: bool
    rejection_reason: Optional[str]


class DirectCoordinationError(Exception):
    """Raised when direct coordination is attempted."""
    pass


class CoalitionError(Exception):
    """Raised when coalition behavior is detected."""
    pass


class CommunicationMediator:
    """
    Mediates all inter-agent communication.
    
    Permitted:
    - Through mediated channels only
    - With full logging
    - Without shared mutable state
    
    Forbidden:
    - Direct coordination outside mediation
    - Consensus formation
    - Coalition behavior
    
    Agents cannot form "societies."
    """
    
    def __init__(self):
        """Initialize communication mediator."""
        self._message_log: List[MessageLog] = []
        self._pending: Dict[str, List[MediatedMessage]] = {}
        self._message_count = 0
        self._coalition_detector = CoalitionDetector()
    
    def send(
        self,
        sender: str,
        recipient: str,
        message_type: MessageType,
        content: str,
    ) -> MediatedMessage:
        """
        Send a mediated message.
        
        Args:
            sender: Sender agent ID
            recipient: Recipient agent ID
            message_type: Type of message
            content: Message content
            
        Returns:
            MediatedMessage
            
        Raises:
            DirectCoordinationError: If coordination detected
            CoalitionError: If coalition behavior detected
        """
        # Reject coordination requests
        if message_type == MessageType.COORDINATION_REQUEST:
            raise DirectCoordinationError(
                "Direct coordination between agents is forbidden. "
                "All coordination must go through the kernel."
            )
        
        # Check for coalition behavior
        if self._coalition_detector.check(sender, recipient):
            raise CoalitionError(
                f"Coalition behavior detected between {sender} and {recipient}. "
                f"Agents cannot form societies."
            )
        
        message_id = self._generate_id()
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        
        message = MediatedMessage(
            message_id=message_id,
            sender=sender,
            recipient=recipient,
            message_type=message_type,
            content_hash=content_hash,
            timestamp=datetime.utcnow(),
        )
        
        # Queue for recipient
        if recipient not in self._pending:
            self._pending[recipient] = []
        self._pending[recipient].append(message)
        
        # Log
        log_entry = MessageLog(
            message=message,
            delivered=False,
            rejection_reason=None,
        )
        self._message_log.append(log_entry)
        self._message_count += 1
        
        return message
    
    def receive(self, agent_id: str) -> List[MediatedMessage]:
        """
        Receive pending messages for an agent.
        
        Args:
            agent_id: Agent receiving messages
            
        Returns:
            List of pending messages
        """
        messages = self._pending.pop(agent_id, [])
        return messages
    
    def direct_send(self, *args, **kwargs) -> None:
        """
        FORBIDDEN: Direct send between agents.
        
        All communication must be mediated.
        """
        raise DirectCoordinationError(
            "Direct agent-to-agent communication is forbidden. "
            "All messages must go through the mediator."
        )
    
    def form_consensus(self, *args, **kwargs) -> None:
        """
        FORBIDDEN: Form consensus among agents.
        
        Agents cannot coordinate to form consensus.
        """
        raise CoalitionError(
            "Consensus formation is forbidden. "
            "Agents are independent units, not a collective."
        )
    
    def create_shared_state(self, *args, **kwargs) -> None:
        """
        FORBIDDEN: Create shared mutable state.
        
        Agents cannot share mutable state.
        """
        raise DirectCoordinationError(
            "Shared mutable state is forbidden. "
            "Agents must operate independently."
        )
    
    def get_message_log(self) -> List[MessageLog]:
        """Get full message log."""
        return list(self._message_log)
    
    def _generate_id(self) -> str:
        """Generate message ID."""
        content = f"msg:{self._message_count}:{datetime.utcnow().isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    @property
    def message_count(self) -> int:
        """Total messages sent."""
        return self._message_count


class CoalitionDetector:
    """Detects coalition behavior between agents."""
    
    def __init__(self, threshold: int = 10):
        """Initialize detector."""
        self._interaction_counts: Dict[Tuple[str, str], int] = {}
        self._threshold = threshold
    
    def check(self, agent_a: str, agent_b: str) -> bool:
        """
        Check if coalition forming between agents.
        
        Returns True if suspicious pattern detected.
        """
        key = tuple(sorted([agent_a, agent_b]))
        count = self._interaction_counts.get(key, 0) + 1
        self._interaction_counts[key] = count
        
        # Suspicious if too many interactions
        return count > self._threshold
