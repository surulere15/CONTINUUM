"""
Signal Base Schema

Defines the immutable structure of a Civilization Signal.
Signals are facts — no derived fields, thresholds, scores, or weights.

INSTRUMENTATION MODULE - No imports from kernel/cognitive/execution/agents.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Union


# Valid signal domains
SignalDomain = Literal["economic", "environmental", "societal", "technological"]

# Signal value types - raw observations only
SignalValue = Union[float, int, str]


@dataclass(frozen=True)
class CivilizationSignal:
    """
    An immutable observation of civilization-level state.
    
    Signals record what IS, not what SHOULD BE.
    They are never interpreted, scored, or optimized against.
    
    Attributes:
        signal_id: Unique identifier (content-addressed)
        domain: One of economic, environmental, societal, technological
        name: Human-readable signal name
        value: Raw observed value (no derived/computed values)
        unit: Unit of measurement
        timestamp: When observation was made (UTC)
        source: Origin of the observation
        provenance_hash: Hash of provenance record
    """
    
    signal_id: str
    domain: SignalDomain
    name: str
    value: SignalValue
    unit: str
    timestamp: datetime
    source: str
    provenance_hash: str
    
    def __post_init__(self):
        """Validate signal at creation time."""
        if not self.signal_id or not self.signal_id.strip():
            raise ValueError("Signal ID cannot be empty")
        
        if not self.name or not self.name.strip():
            raise ValueError("Signal name cannot be empty")
        
        if not self.unit or not self.unit.strip():
            raise ValueError("Signal unit cannot be empty")
        
        if not self.source or not self.source.strip():
            raise ValueError("Signal source cannot be empty")
        
        if not self.provenance_hash:
            raise ValueError("Provenance hash is required")


@dataclass(frozen=True)
class SignalMetadata:
    """
    Metadata about a signal type (not an instance).
    
    Describes what a signal measures, not current values.
    """
    
    domain: SignalDomain
    name: str
    description: str
    unit: str
    value_type: Literal["float", "int", "str"]
    update_frequency: str  # e.g., "daily", "hourly", "realtime"


@dataclass(frozen=True)
class SignalBatch:
    """
    A batch of signals for bulk ingestion.
    
    Batches are atomic — all succeed or all fail.
    """
    
    batch_id: str
    signals: tuple  # Tuple[CivilizationSignal, ...]
    received_at: datetime
    source: str
