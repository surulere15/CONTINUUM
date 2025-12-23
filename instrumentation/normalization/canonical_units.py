"""
Canonical Units

Normalizes units to standard forms for comparability.
No aggregation, no indices, no derived metrics.

INSTRUMENTATION MODULE - No imports from kernel/cognitive/execution/agents.
"""

from dataclasses import dataclass
from typing import Dict, Optional, Tuple
from enum import Enum


class UnitSystem(Enum):
    """Standard unit systems."""
    SI = "si"
    IMPERIAL = "imperial"
    CUSTOM = "custom"


@dataclass(frozen=True)
class CanonicalUnit:
    """A canonical unit definition."""
    name: str
    symbol: str
    system: UnitSystem
    domain: str


# Canonical units by domain
CANONICAL_UNITS: Dict[str, Dict[str, CanonicalUnit]] = {
    "economic": {
        "currency": CanonicalUnit("US Dollar", "USD", UnitSystem.CUSTOM, "economic"),
        "rate": CanonicalUnit("Percent", "percent", UnitSystem.CUSTOM, "economic"),
        "count": CanonicalUnit("Count", "count", UnitSystem.CUSTOM, "economic"),
    },
    "environmental": {
        "temperature": CanonicalUnit("Celsius", "celsius", UnitSystem.SI, "environmental"),
        "concentration": CanonicalUnit("Parts Per Million", "ppm", UnitSystem.CUSTOM, "environmental"),
        "distance": CanonicalUnit("Millimeter", "mm", UnitSystem.SI, "environmental"),
        "area": CanonicalUnit("Square Kilometer", "km2", UnitSystem.SI, "environmental"),
    },
    "societal": {
        "count": CanonicalUnit("Count", "count", UnitSystem.CUSTOM, "societal"),
        "rate": CanonicalUnit("Percent", "percent", UnitSystem.CUSTOM, "societal"),
        "time": CanonicalUnit("Years", "years", UnitSystem.CUSTOM, "societal"),
    },
    "technological": {
        "compute": CanonicalUnit("FLOPS", "flops", UnitSystem.CUSTOM, "technological"),
        "bandwidth": CanonicalUnit("Gigabits Per Second", "gbps", UnitSystem.CUSTOM, "technological"),
        "power": CanonicalUnit("Watts", "watts", UnitSystem.SI, "technological"),
        "count": CanonicalUnit("Count", "count", UnitSystem.CUSTOM, "technological"),
    },
}

# Unit conversion factors to canonical
CONVERSIONS: Dict[str, Tuple[str, float]] = {
    # Temperature
    "fahrenheit": ("celsius", lambda f: (f - 32) * 5/9),
    "kelvin": ("celsius", lambda k: k - 273.15),
    
    # Currency (placeholder - would need real-time rates)
    "eur": ("USD", 1.10),
    "gbp": ("USD", 1.27),
    
    # Distance
    "m": ("mm", 1000),
    "cm": ("mm", 10),
    "km": ("mm", 1_000_000),
    "inches": ("mm", 25.4),
    
    # Bandwidth
    "mbps": ("gbps", 0.001),
    "tbps": ("gbps", 1000),
    
    # Compute
    "tflops": ("flops", 1e12),
    "pflops": ("flops", 1e15),
}


class UnitNormalizer:
    """
    Normalizes signal units to canonical forms.
    
    Rules:
    - Pure unit conversion only
    - No aggregation
    - No indices or composite metrics
    - Preserves original value if no conversion available
    """
    
    def normalize(
        self,
        value: float,
        from_unit: str,
        domain: str,
    ) -> Tuple[float, str]:
        """
        Normalize a value to canonical units.
        
        Args:
            value: Original value
            from_unit: Original unit
            domain: Signal domain
            
        Returns:
            Tuple of (normalized_value, canonical_unit)
        """
        from_unit_lower = from_unit.lower()
        
        # Check if conversion exists
        if from_unit_lower in CONVERSIONS:
            target_unit, conversion = CONVERSIONS[from_unit_lower]
            if callable(conversion):
                normalized = conversion(value)
            else:
                normalized = value * conversion
            return normalized, target_unit
        
        # No conversion needed - return as-is
        return value, from_unit
    
    def is_canonical(self, unit: str, domain: str) -> bool:
        """Check if unit is already canonical for domain."""
        domain_units = CANONICAL_UNITS.get(domain, {})
        return any(cu.symbol.lower() == unit.lower() for cu in domain_units.values())
