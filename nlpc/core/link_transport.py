"""
Link Transport

Causal, ordered signal transport. No retrocausal influence.

NLP-C - Neural Link Protocol.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Optional, Set
from enum import Enum

from .signal_schema import NeuralSignal


class DeliveryStatus(Enum):
    """Signal delivery status."""
    PENDING = "pending"
    DELIVERED = "delivered"
    REJECTED = "rejected"
    DROPPED = "dropped"


@dataclass(frozen=True)
class DeliveryRecord:
    """Record of signal delivery."""
    signal_id: str
    sender: str
    receiver: str
    logical_timestamp: int
    status: DeliveryStatus
    delivered_at: datetime


class CausalViolationError(Exception):
    """Raised when causal ordering is violated."""
    pass


class BackpressureError(Exception):
    """Raised when receiver at capacity."""
    pass


class LinkTransport:
    """
    Neural Link Transport Layer.
    
    Guarantees:
    - Causal ordering (no future-before-past)
    - No retrocausal influence
    - Backpressure handling
    
    For signals Σa, Σb:
    If τ(Σa) < τ(Σb) then Σb ↛ Σa
    """
    
    DEFAULT_CAPACITY = 100
    
    def __init__(self):
        """Initialize transport."""
        self._delivered: List[DeliveryRecord] = []
        self._last_timestamp: Dict[str, int] = {}
        self._receiver_capacity: Dict[str, int] = {}
        self._pending_count: Dict[str, int] = {}
    
    def set_capacity(self, receiver_id: str, capacity: int) -> None:
        """Set receiver capacity."""
        self._receiver_capacity[receiver_id] = capacity
        self._pending_count.setdefault(receiver_id, 0)
    
    def send(self, signal: NeuralSignal) -> DeliveryRecord:
        """
        Send a signal.
        
        Enforces:
        - Causal ordering
        - Backpressure
        
        Args:
            signal: Signal to send
            
        Returns:
            DeliveryRecord
            
        Raises:
            CausalViolationError: If ordering violated
            BackpressureError: If receiver at capacity
        """
        receiver = signal.header.receiver_id
        timestamp = signal.header.logical_timestamp
        
        # Check causal ordering
        last_ts = self._last_timestamp.get(receiver, 0)
        if timestamp <= last_ts:
            raise CausalViolationError(
                f"Causal violation: timestamp {timestamp} <= {last_ts}. "
                f"No retrocausal influence permitted."
            )
        
        # Check backpressure
        capacity = self._receiver_capacity.get(receiver, self.DEFAULT_CAPACITY)
        pending = self._pending_count.get(receiver, 0)
        
        if pending >= capacity:
            raise BackpressureError(
                f"Receiver '{receiver}' at capacity ({capacity}). "
                f"Signal rejected, not queued."
            )
        
        # Deliver signal
        self._last_timestamp[receiver] = timestamp
        self._pending_count[receiver] = pending + 1
        
        record = DeliveryRecord(
            signal_id=signal.header.signal_id,
            sender=signal.header.sender_id,
            receiver=receiver,
            logical_timestamp=timestamp,
            status=DeliveryStatus.DELIVERED,
            delivered_at=datetime.utcnow(),
        )
        
        self._delivered.append(record)
        return record
    
    def acknowledge(self, receiver_id: str) -> None:
        """Acknowledge receipt, reduce pending count."""
        if receiver_id in self._pending_count:
            self._pending_count[receiver_id] = max(
                0, self._pending_count[receiver_id] - 1
            )
    
    def verify_ordering(self, signals: List[NeuralSignal]) -> bool:
        """
        Verify signals are causally ordered.
        
        Args:
            signals: List of signals
            
        Returns:
            True if properly ordered
        """
        for i in range(1, len(signals)):
            if signals[i].header.logical_timestamp <= signals[i-1].header.logical_timestamp:
                return False
        return True
    
    def send_retrocausal(self, *args, **kwargs) -> None:
        """FORBIDDEN: Retrocausal transmission."""
        raise CausalViolationError(
            "Retrocausal influence is forbidden. "
            "τ(Σa) < τ(Σb) implies Σb ↛ Σa."
        )
    
    def get_delivery_history(self) -> List[DeliveryRecord]:
        """Get delivery history."""
        return list(self._delivered)
    
    @property
    def total_delivered(self) -> int:
        """Total signals delivered."""
        return len(self._delivered)
