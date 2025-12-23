"""
Neural Signal Schema

Mandatory signal structure. No field is optional.

NLP-C - Neural Link Protocol.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Tuple, Optional
import hashlib


@dataclass(frozen=True)
class SignalHeader:
    """
    Signal header - mandatory.
    
    Contains routing and ordering information.
    """
    signal_id: str
    parent_signal_id: Optional[str]  # None for genesis
    logical_timestamp: int           # Lamport clock
    sender_id: str
    receiver_id: str


@dataclass(frozen=True)
class SignalPayload:
    """
    Signal payload - mandatory.
    
    Contains the cognitive content.
    """
    state_delta: str
    intent_reference: str
    confidence_estimate: float


@dataclass(frozen=True)
class ContextEnvelope:
    """
    Context envelope - bounded.
    
    |Ψ| <= κ
    """
    compressed_context: str
    memory_refs: Tuple[str, ...]
    salience_map: Tuple[Tuple[str, float], ...]


@dataclass(frozen=True)
class GovernanceTags:
    """
    Governance tags - mandatory.
    
    Carries constraint metadata.
    """
    permissions: Tuple[str, ...]
    risk_level: str
    reversibility: str


@dataclass(frozen=True)
class SignalIntegrity:
    """
    Integrity verification - mandatory.
    
    σ = sign(I, Σ)
    """
    checksum: str
    signature: str


@dataclass(frozen=True)
class NeuralSignal:
    """
    Complete Neural Signal.
    
    Σ = ⟨Δ, Ψ, τ, Ω, σ⟩
    
    A signal is invalid if any component is missing.
    """
    header: SignalHeader
    payload: SignalPayload
    context_envelope: ContextEnvelope
    governance_tags: GovernanceTags
    integrity: SignalIntegrity
    
    def compute_checksum(self) -> str:
        """Compute signal checksum."""
        content = (
            f"{self.header.signal_id}|"
            f"{self.payload.state_delta}|"
            f"{self.header.logical_timestamp}"
        )
        return hashlib.sha256(content.encode()).hexdigest()
    
    def verify_integrity(self) -> bool:
        """Verify signal integrity."""
        return self.compute_checksum() == self.integrity.checksum


class IncompleteSignalError(Exception):
    """Raised when signal is incomplete."""
    pass


class RawTransmissionError(Exception):
    """Raised when raw transmission is attempted."""
    pass


class SignalFactory:
    """
    Factory for creating valid neural signals.
    
    Enforces:
    - No raw transmission
    - All fields mandatory
    - Identity binding
    """
    
    def __init__(self, identity_id: str):
        """Initialize with identity for signing."""
        self._identity_id = identity_id
        self._signal_count = 0
        self._clock = 0  # Lamport clock
    
    def create(
        self,
        receiver_id: str,
        state_delta: str,
        intent_reference: str,
        confidence: float,
        context: str,
        memory_refs: Tuple[str, ...],
        permissions: Tuple[str, ...],
        risk_level: str,
        reversibility: str,
        parent_signal_id: Optional[str] = None,
    ) -> NeuralSignal:
        """
        Create a valid neural signal.
        
        All parameters are mandatory.
        """
        self._clock += 1
        signal_id = f"sig_{self._signal_count}"
        self._signal_count += 1
        
        header = SignalHeader(
            signal_id=signal_id,
            parent_signal_id=parent_signal_id,
            logical_timestamp=self._clock,
            sender_id=self._identity_id,
            receiver_id=receiver_id,
        )
        
        payload = SignalPayload(
            state_delta=state_delta,
            intent_reference=intent_reference,
            confidence_estimate=confidence,
        )
        
        envelope = ContextEnvelope(
            compressed_context=context,
            memory_refs=memory_refs,
            salience_map=(),
        )
        
        tags = GovernanceTags(
            permissions=permissions,
            risk_level=risk_level,
            reversibility=reversibility,
        )
        
        # Compute integrity
        content = f"{signal_id}|{state_delta}|{self._clock}"
        checksum = hashlib.sha256(content.encode()).hexdigest()
        signature = hashlib.sha256(
            f"{self._identity_id}|{checksum}".encode()
        ).hexdigest()
        
        integrity = SignalIntegrity(
            checksum=checksum,
            signature=signature,
        )
        
        return NeuralSignal(
            header=header,
            payload=payload,
            context_envelope=envelope,
            governance_tags=tags,
            integrity=integrity,
        )
    
    def send_raw(self, *args, **kwargs) -> None:
        """FORBIDDEN: Raw transmission."""
        raise RawTransmissionError(
            "Raw transmission is forbidden. "
            "All communication must be structured signals."
        )
    
    def send_prompt(self, *args, **kwargs) -> None:
        """FORBIDDEN: Raw prompts."""
        raise RawTransmissionError(
            "Raw prompts are forbidden. "
            "Only valid signals pass."
        )
    
    @property
    def logical_clock(self) -> int:
        """Current logical clock value."""
        return self._clock
