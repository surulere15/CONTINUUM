"""
Provenance Tracking

Tracks signal origin and collection methodology.
Provenance documents trustworthiness, not truth.

INSTRUMENTATION MODULE - No imports from kernel/cognitive/execution/agents.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Literal
import hashlib
import json


CollectionMethod = Literal[
    "sensor",           # Direct sensor measurement
    "survey",           # Survey/questionnaire
    "administrative",   # Government/institutional records
    "derived",          # Calculated from other signals (flagged)
    "estimated",        # Statistical estimation
    "reported",         # Self-reported by source
    "unknown"           # Provenance not available
]


@dataclass(frozen=True)
class Provenance:
    """
    Provenance record for a signal.
    
    Documents WHERE a signal came from and HOW it was collected.
    Does NOT validate truth — opaque provenance ≠ rejection.
    
    Attributes:
        source_id: Unique identifier for the source
        source_name: Human-readable source name
        collection_method: How the signal was collected
        update_cadence: How often source updates (e.g., "daily")
        confidence: Self-reported confidence (0.0-1.0), not verified
        signature: Optional cryptographic signature
        collected_at: When the signal was collected
        notes: Optional additional context
    """
    
    source_id: str
    source_name: str
    collection_method: CollectionMethod
    update_cadence: str
    confidence: float  # Self-reported, NOT validated
    collected_at: datetime
    signature: Optional[str] = None
    notes: Optional[str] = None
    
    def __post_init__(self):
        """Validate provenance structure."""
        if not self.source_id:
            raise ValueError("Source ID is required")
        
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
    
    def compute_hash(self) -> str:
        """
        Compute content hash for this provenance record.
        
        Used to link signals to their provenance immutably.
        """
        content = {
            "source_id": self.source_id,
            "source_name": self.source_name,
            "collection_method": self.collection_method,
            "update_cadence": self.update_cadence,
            "confidence": self.confidence,
            "collected_at": self.collected_at.isoformat(),
        }
        content_str = json.dumps(content, sort_keys=True)
        return hashlib.sha256(content_str.encode()).hexdigest()


@dataclass(frozen=True)
class ProvenanceChain:
    """
    Chain of provenance for derived signals.
    
    If a signal is derived from other signals, this tracks
    the full lineage back to original sources.
    """
    
    signal_id: str
    parent_signals: tuple  # Tuple of parent signal IDs
    derivation_method: str
    derived_at: datetime


class ProvenanceRegistry:
    """
    Registry of known provenance records.
    
    Stores provenance separately from signals for deduplication.
    """
    
    def __init__(self):
        self._records: dict = {}  # hash -> Provenance
    
    def register(self, provenance: Provenance) -> str:
        """Register provenance and return its hash."""
        prov_hash = provenance.compute_hash()
        if prov_hash not in self._records:
            self._records[prov_hash] = provenance
        return prov_hash
    
    def get(self, prov_hash: str) -> Optional[Provenance]:
        """Retrieve provenance by hash."""
        return self._records.get(prov_hash)
    
    def exists(self, prov_hash: str) -> bool:
        """Check if provenance exists."""
        return prov_hash in self._records
