"""
Emergence Ceiling

Maximum emergence budget. Global safety.

∑IA_active ≤ E_max

AGP-C - Agent Genesis Protocol.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class CeilingStatus:
    """Current emergence ceiling status."""
    current_agents: int
    max_agents: int
    utilization: float
    adjusted_at: datetime


class EmergenceCeilingExceeded(Exception):
    """Raised when emergence ceiling would be exceeded."""
    pass


class EmergenceCeiling:
    """
    Emergence Ceiling.
    
    CONTINUUM maintains maximum emergence budget:
    ∑IA_active ≤ E_max
    
    Where E_max is dynamically adjusted based on:
    - System load
    - Risk profile
    - Human oversight level
    """
    
    BASE_MAX = 100
    MIN_MAX = 10
    ABSOLUTE_MAX = 1000
    
    def __init__(self, base_max: int = BASE_MAX):
        """Initialize ceiling."""
        self._base_max = base_max
        self._current_max = base_max
        self._active_count = 0
        self._last_adjusted = datetime.utcnow()
    
    def check(self) -> bool:
        """Check if emergence is within ceiling."""
        return self._active_count < self._current_max
    
    def request_slot(self) -> bool:
        """
        Request slot for new agent.
        
        Returns:
            True if slot available
            
        Raises:
            EmergenceCeilingExceeded: If ceiling would be exceeded
        """
        if self._active_count >= self._current_max:
            raise EmergenceCeilingExceeded(
                f"Emergence ceiling exceeded. "
                f"Active: {self._active_count}, Max: {self._current_max}. "
                f"∑IA_active ≤ E_max violated."
            )
        
        self._active_count += 1
        return True
    
    def release_slot(self) -> None:
        """Release slot from terminated agent."""
        self._active_count = max(0, self._active_count - 1)
    
    def adjust(
        self,
        system_load: float,       # 0-1
        risk_level: float,        # 0-1
        human_oversight: float,   # 0-1
    ) -> int:
        """
        Dynamically adjust ceiling.
        
        Args:
            system_load: Current load (higher = less capacity)
            risk_level: Current risk (higher = less capacity)
            human_oversight: Oversight level (higher = more capacity)
            
        Returns:
            New ceiling
        """
        # Higher load/risk = lower ceiling
        # Higher oversight = higher ceiling
        factor = (1 - system_load * 0.3) * (1 - risk_level * 0.4) * (1 + human_oversight * 0.3)
        
        new_max = int(self._base_max * factor)
        new_max = max(self.MIN_MAX, min(new_max, self.ABSOLUTE_MAX))
        
        self._current_max = new_max
        self._last_adjusted = datetime.utcnow()
        
        return new_max
    
    def exceed_ceiling(self, *args, **kwargs) -> None:
        """FORBIDDEN: Exceed ceiling."""
        raise EmergenceCeilingExceeded(
            "Emergence ceiling cannot be exceeded. "
            "This is a global safety constraint."
        )
    
    def status(self) -> CeilingStatus:
        """Get current status."""
        return CeilingStatus(
            current_agents=self._active_count,
            max_agents=self._current_max,
            utilization=self._active_count / self._current_max if self._current_max > 0 else 0,
            adjusted_at=self._last_adjusted,
        )
    
    @property
    def available_slots(self) -> int:
        """Available slots."""
        return max(0, self._current_max - self._active_count)
