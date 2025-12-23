"""
Environmental Signal Adapter

Maps external environmental data to internal signal form.
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
class EnvironmentalDataPoint:
    """Raw environmental data point from external source."""
    metric: str
    value: float
    unit: str
    location: str
    source: str
    collected_at: datetime
    sensor_id: Optional[str] = None


class EnvironmentalAdapter:
    """
    Adapter for environmental signals.
    
    Supported metrics:
    - CO2 concentration (ppm)
    - Temperature (celsius)
    - Biodiversity indices
    - Air quality indices
    - Sea level measurements
    
    Rules:
    - No spatial averaging
    - No trend calculation
    - No anomaly detection
    - Raw sensor values only
    """
    
    SUPPORTED_METRICS = {
        "co2": "CO2 Concentration",
        "temperature": "Temperature",
        "biodiversity": "Biodiversity Index",
        "air_quality": "Air Quality Index",
        "sea_level": "Sea Level",
        "rainfall": "Rainfall",
        "humidity": "Humidity",
        "particulate_matter": "Particulate Matter",
    }
    
    def __init__(self, provenance_registry):
        self._provenance_registry = provenance_registry
    
    def adapt(self, data: EnvironmentalDataPoint) -> Optional[CivilizationSignal]:
        """Convert environmental data point to CivilizationSignal."""
        metric_key = data.metric.lower().replace(" ", "_")
        if metric_key not in self.SUPPORTED_METRICS:
            return None
        
        # Determine collection method
        method = CollectionMethod.SENSOR if data.sensor_id else CollectionMethod.REPORTED
        
        # Create provenance
        provenance = Provenance(
            source_id=f"env_{data.source}_{data.sensor_id or 'manual'}",
            source_name=data.source,
            collection_method=method,
            update_cadence="realtime" if data.sensor_id else "daily",
            confidence=0.95 if data.sensor_id else 0.8,
            collected_at=data.collected_at,
        )
        prov_hash = self._provenance_registry.register(provenance)
        
        # Generate signal ID
        content = f"{data.metric}|{data.value}|{data.location}|{data.collected_at.isoformat()}"
        signal_id = hashlib.sha256(content.encode()).hexdigest()[:16]
        
        return CivilizationSignal(
            signal_id=signal_id,
            domain="environmental",
            name=f"{self.SUPPORTED_METRICS[metric_key]}_{data.location}",
            value=data.value,
            unit=data.unit,
            timestamp=data.collected_at,
            source=data.source,
            provenance_hash=prov_hash,
        )
