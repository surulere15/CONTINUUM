"""
Societal Signal Adapter

Maps external societal data to internal signal form.
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
class SocietalDataPoint:
    """Raw societal data point from external source."""
    indicator: str
    value: float
    unit: str
    region: str
    demographic: Optional[str]
    source: str
    collected_at: datetime


class SocietalAdapter:
    """
    Adapter for societal signals.
    
    Supported indicators:
    - Population counts
    - Health statistics
    - Education metrics
    - Life expectancy
    - Literacy rates
    
    Rules:
    - No demographic weighting
    - No composite indices
    - No quality-of-life scores
    - Raw counts/rates only
    """
    
    SUPPORTED_INDICATORS = {
        "population": "Population",
        "life_expectancy": "Life Expectancy",
        "literacy_rate": "Literacy Rate",
        "infant_mortality": "Infant Mortality Rate",
        "education_enrollment": "Education Enrollment",
        "healthcare_access": "Healthcare Access",
        "poverty_rate": "Poverty Rate",
        "gini_coefficient": "Gini Coefficient",
    }
    
    def __init__(self, provenance_registry):
        self._provenance_registry = provenance_registry
    
    def adapt(self, data: SocietalDataPoint) -> Optional[CivilizationSignal]:
        """Convert societal data point to CivilizationSignal."""
        indicator_key = data.indicator.lower().replace(" ", "_")
        if indicator_key not in self.SUPPORTED_INDICATORS:
            return None
        
        # Create provenance
        provenance = Provenance(
            source_id=f"societal_{data.source}",
            source_name=data.source,
            collection_method=CollectionMethod.ADMINISTRATIVE,
            update_cadence="annual",
            confidence=0.85,
            collected_at=data.collected_at,
            notes=f"Demographic: {data.demographic}" if data.demographic else None,
        )
        prov_hash = self._provenance_registry.register(provenance)
        
        # Generate signal ID
        demo_str = data.demographic or "all"
        content = f"{data.indicator}|{data.value}|{data.region}|{demo_str}"
        signal_id = hashlib.sha256(content.encode()).hexdigest()[:16]
        
        name_suffix = f"_{data.demographic}" if data.demographic else ""
        
        return CivilizationSignal(
            signal_id=signal_id,
            domain="societal",
            name=f"{self.SUPPORTED_INDICATORS[indicator_key]}_{data.region}{name_suffix}",
            value=data.value,
            unit=data.unit,
            timestamp=data.collected_at,
            source=data.source,
            provenance_hash=prov_hash,
        )
