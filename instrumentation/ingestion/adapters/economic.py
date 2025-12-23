"""
Economic Signal Adapter

Maps external economic data to internal signal form.
No aggregation, smoothing, forecasts, or enrichment.

INSTRUMENTATION MODULE - No imports from kernel/cognitive/execution/agents.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional

from ..schema.signal_base import CivilizationSignal
from ..schema.provenance import Provenance, CollectionMethod


@dataclass
class EconomicDataPoint:
    """Raw economic data point from external source."""
    indicator: str
    value: float
    currency: Optional[str]
    region: str
    period: str
    source: str
    collected_at: datetime


class EconomicAdapter:
    """
    Adapter for economic signals.
    
    Supported indicators:
    - GDP (gross domestic product)
    - Inflation rate
    - Employment rate
    - Interest rates
    - Trade balance
    
    Rules:
    - No aggregation across regions
    - No seasonality adjustment
    - No forecasting
    - Raw values only
    """
    
    SUPPORTED_INDICATORS = {
        "gdp": "GDP",
        "inflation": "Inflation Rate",
        "employment": "Employment Rate",
        "interest_rate": "Interest Rate",
        "trade_balance": "Trade Balance",
        "unemployment": "Unemployment Rate",
        "cpi": "Consumer Price Index",
    }
    
    def __init__(self, provenance_registry):
        self._provenance_registry = provenance_registry
    
    def adapt(self, data: EconomicDataPoint) -> Optional[CivilizationSignal]:
        """
        Convert economic data point to CivilizationSignal.
        
        Args:
            data: Raw economic data point
            
        Returns:
            CivilizationSignal or None if indicator not supported
        """
        indicator_key = data.indicator.lower().replace(" ", "_")
        if indicator_key not in self.SUPPORTED_INDICATORS:
            return None
        
        # Create provenance record
        provenance = Provenance(
            source_id=f"economic_{data.source}",
            source_name=data.source,
            collection_method=CollectionMethod.ADMINISTRATIVE,
            update_cadence=self._infer_cadence(data.period),
            confidence=0.9,  # Official statistics typically high confidence
            collected_at=data.collected_at,
        )
        prov_hash = self._provenance_registry.register(provenance)
        
        # Determine unit
        unit = data.currency if data.currency else "percent"
        if indicator_key in ("gdp", "trade_balance"):
            unit = data.currency or "USD"
        
        # Generate signal ID
        import hashlib
        content = f"{data.indicator}|{data.value}|{data.region}|{data.period}"
        signal_id = hashlib.sha256(content.encode()).hexdigest()[:16]
        
        return CivilizationSignal(
            signal_id=signal_id,
            domain="economic",
            name=f"{self.SUPPORTED_INDICATORS[indicator_key]}_{data.region}",
            value=data.value,
            unit=unit,
            timestamp=data.collected_at,
            source=data.source,
            provenance_hash=prov_hash,
        )
    
    def _infer_cadence(self, period: str) -> str:
        """Infer update cadence from period string."""
        period_lower = period.lower()
        if "daily" in period_lower:
            return "daily"
        elif "weekly" in period_lower:
            return "weekly"
        elif "monthly" in period_lower:
            return "monthly"
        elif "quarterly" in period_lower or "q" in period_lower:
            return "quarterly"
        elif "annual" in period_lower or "yearly" in period_lower:
            return "annual"
        return "unknown"
