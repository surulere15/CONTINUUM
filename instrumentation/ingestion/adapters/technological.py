"""
Technological Signal Adapter

Maps external technological data to internal signal form.
No aggregation, smoothing, forecasts, or enrichment.

INSTRUMENTATION MODULE - No imports from kernel/cognitive/execution/agents.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import hashlib

from ..schema.signal_base import CivilizationSignal
from ..schema.provenance import Provenance, CollectionMethod


@dataclass
class TechnologicalDataPoint:
    """Raw technological data point from external source."""
    metric: str
    value: float
    unit: str
    technology: str
    region: Optional[str]
    source: str
    collected_at: datetime


class TechnologicalAdapter:
    """
    Adapter for technological signals.
    
    Supported metrics:
    - Compute capacity
    - Network bandwidth
    - Technology adoption rates
    - Energy consumption
    - Research output
    
    Rules:
    - No capability projections
    - No growth rate calculations
    - No comparative rankings
    - Raw measurements only
    """
    
    SUPPORTED_METRICS = {
        "compute_capacity": "Compute Capacity",
        "bandwidth": "Network Bandwidth",
        "adoption_rate": "Technology Adoption",
        "energy_consumption": "Energy Consumption",
        "research_publications": "Research Publications",
        "patent_filings": "Patent Filings",
        "internet_penetration": "Internet Penetration",
        "mobile_subscriptions": "Mobile Subscriptions",
    }
    
    def __init__(self, provenance_registry):
        self._provenance_registry = provenance_registry
    
    def adapt(self, data: TechnologicalDataPoint) -> Optional[CivilizationSignal]:
        """Convert technological data point to CivilizationSignal."""
        metric_key = data.metric.lower().replace(" ", "_")
        if metric_key not in self.SUPPORTED_METRICS:
            return None
        
        # Create provenance
        provenance = Provenance(
            source_id=f"tech_{data.source}",
            source_name=data.source,
            collection_method=CollectionMethod.REPORTED,
            update_cadence="quarterly",
            confidence=0.8,
            collected_at=data.collected_at,
        )
        prov_hash = self._provenance_registry.register(provenance)
        
        # Generate signal ID
        region_str = data.region or "global"
        content = f"{data.metric}|{data.value}|{data.technology}|{region_str}"
        signal_id = hashlib.sha256(content.encode()).hexdigest()[:16]
        
        return CivilizationSignal(
            signal_id=signal_id,
            domain="technological",
            name=f"{self.SUPPORTED_METRICS[metric_key]}_{data.technology}",
            value=data.value,
            unit=data.unit,
            timestamp=data.collected_at,
            source=data.source,
            provenance_hash=prov_hash,
        )
