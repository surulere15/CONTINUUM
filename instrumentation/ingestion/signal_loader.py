"""
Signal Loader

Deterministic signal ingestion procedure.
Signals are read-only facts — no interpretation, aggregation, or influence.

INSTRUMENTATION MODULE - Phase C. Awareness without influence.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
import hashlib

from ..schema.signal_base import CivilizationSignal, SignalBatch
from ..ingestion.registry import IngestionRegistry, SourceNotRegisteredError


class LoadResult(Enum):
    """Result of signal load attempt."""
    SUCCESS = "success"
    REJECTED = "rejected"
    PARTIAL = "partial"


@dataclass(frozen=True)
class LoadReport:
    """Report of signal load attempt."""
    result: LoadResult
    signals_loaded: int
    signals_rejected: int
    rejection_reasons: Tuple[str, ...]
    loaded_at: datetime
    batch_hash: str


class SignalInfluenceError(Exception):
    """Raised when attempting to influence through signals."""
    pass


class SignalInterpretationError(Exception):
    """Raised when attempting to interpret signals."""
    pass


class SignalLoader:
    """
    Loads civilization signals through a deterministic procedure.
    
    Signals are:
    - Read-only observations
    - Never interpreted or scored
    - Never aggregated or smoothed
    - Never used to influence the observed system
    
    Awareness without influence.
    """
    
    def __init__(self, registry: IngestionRegistry):
        """
        Initialize signal loader.
        
        Args:
            registry: Registry of approved sources
        """
        self._registry = registry
        self._load_count = 0
        self._loaded_signals: List[CivilizationSignal] = []
    
    def load(
        self,
        raw_signals: List[Dict[str, Any]],
        source_id: str,
    ) -> LoadReport:
        """
        Load signals from a registered source.
        
        Args:
            raw_signals: Raw signal data
            source_id: Source identifier
            
        Returns:
            LoadReport
        """
        rejection_reasons = []
        loaded = []
        
        # Step 1: Verify source is registered
        try:
            source = self._registry.require_active(source_id)
        except SourceNotRegisteredError as e:
            return LoadReport(
                result=LoadResult.REJECTED,
                signals_loaded=0,
                signals_rejected=len(raw_signals),
                rejection_reasons=(str(e),),
                loaded_at=datetime.utcnow(),
                batch_hash="",
            )
        
        # Step 2: Validate and load each signal
        for idx, raw in enumerate(raw_signals):
            try:
                signal = self._validate_and_create(raw, source_id)
                loaded.append(signal)
            except Exception as e:
                rejection_reasons.append(f"Signal {idx}: {e}")
        
        # Step 3: Store loaded signals
        self._loaded_signals.extend(loaded)
        self._load_count += len(loaded)
        
        # Compute batch hash
        batch_content = "|".join(s.signal_id for s in loaded)
        batch_hash = hashlib.sha256(batch_content.encode()).hexdigest()
        
        # Determine result
        if not loaded:
            result = LoadResult.REJECTED
        elif rejection_reasons:
            result = LoadResult.PARTIAL
        else:
            result = LoadResult.SUCCESS
        
        return LoadReport(
            result=result,
            signals_loaded=len(loaded),
            signals_rejected=len(rejection_reasons),
            rejection_reasons=tuple(rejection_reasons),
            loaded_at=datetime.utcnow(),
            batch_hash=batch_hash,
        )
    
    def _validate_and_create(
        self,
        raw: Dict[str, Any],
        source_id: str,
    ) -> CivilizationSignal:
        """Validate raw signal and create CivilizationSignal."""
        # Required fields
        required = ["name", "value", "unit", "domain"]
        for field in required:
            if field not in raw:
                raise ValueError(f"Missing required field: {field}")
        
        # Generate signal ID
        signal_id = self._generate_signal_id(raw, source_id)
        
        # Generate provenance hash
        provenance_hash = hashlib.sha256(
            f"{source_id}|{raw['name']}|{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()
        
        return CivilizationSignal(
            signal_id=signal_id,
            domain=raw["domain"],
            name=raw["name"],
            value=raw["value"],
            unit=raw["unit"],
            timestamp=datetime.utcnow(),
            source=source_id,
            provenance_hash=provenance_hash,
        )
    
    def _generate_signal_id(self, raw: Dict[str, Any], source_id: str) -> str:
        """Generate deterministic signal ID."""
        content = f"{source_id}|{raw['name']}|{raw['value']}|{raw['unit']}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def interpret(self, *args, **kwargs) -> None:
        """
        FORBIDDEN: Interpret signals.
        
        Signals are raw observations — interpretation is not permitted.
        """
        raise SignalInterpretationError(
            "Signal interpretation is forbidden. "
            "Signals are raw observations, not interpretations."
        )
    
    def aggregate(self, *args, **kwargs) -> None:
        """
        FORBIDDEN: Aggregate signals.
        
        Aggregation implies interpretation.
        """
        raise SignalInterpretationError(
            "Signal aggregation is forbidden. "
            "Only raw observations are permitted."
        )
    
    def influence(self, *args, **kwargs) -> None:
        """
        FORBIDDEN: Influence through signals.
        
        Signals are read-only — no influence on observed systems.
        """
        raise SignalInfluenceError(
            "Influencing through signals is forbidden. "
            "Signals are awareness without influence."
        )
    
    def send_data(self, *args, **kwargs) -> None:
        """
        FORBIDDEN: Send data to observed systems.
        
        Data flows IN only.
        """
        raise SignalInfluenceError(
            "Sending data to observed systems is forbidden. "
            "Signal flow is read-only, inbound only."
        )
    
    def get_signals(self, domain: Optional[str] = None) -> List[CivilizationSignal]:
        """Get loaded signals (read-only copy)."""
        if domain:
            return [s for s in self._loaded_signals if s.domain == domain]
        return list(self._loaded_signals)
    
    @property
    def load_count(self) -> int:
        """Total signals loaded."""
        return self._load_count
