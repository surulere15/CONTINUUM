"""
Economic Metrics

Tracks economic indicators relevant to civilization objectives.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime


@dataclass
class EconomicSignal:
    name: str
    value: float
    unit: str
    source: str
    timestamp: datetime
    confidence: float


class EconomicMetrics:
    """Collects and processes economic signals."""
    
    def __init__(self):
        self._signals: List[EconomicSignal] = []
    
    def record(self, signal: EconomicSignal) -> None:
        """Record an economic signal."""
        self._signals.append(signal)
    
    def get_latest(self, name: str) -> Optional[EconomicSignal]:
        """Get latest value for a metric."""
        for s in reversed(self._signals):
            if s.name == name:
                return s
        return None
    
    def compute_composite_index(self) -> float:
        """Compute composite economic health index."""
        # TODO: Implement composite calculation
        return 0.0
