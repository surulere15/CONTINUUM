"""
Value Memory (Mv)

Kernel-locked. Preserves alignment, ethics, priorities.
No learning process may modify without governance approval.

MMCP-C - Memory Model & Cognitive Persistence.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Tuple, Optional


@dataclass(frozen=True)
class ValueEntry:
    """Entry in value memory."""
    value_id: str
    category: str  # "constraint", "norm", "risk_tolerance", "forbidden_state"
    description: str
    priority: int  # Higher = more important
    locked_at: datetime


class ValueModificationError(Exception):
    """Raised when unauthorized value modification is attempted."""
    pass


class GovernanceRequiredError(Exception):
    """Raised when governance approval is needed."""
    pass


class ValueMemory:
    """
    Value Memory (Mv).
    
    Purpose: Preserve alignment, ethics, priorities
    
    Contents:
    - Constraints
    - Norms
    - Risk tolerances
    - Forbidden states
    
    This memory is Kernel-locked.
    No learning process may modify Mv without governance approval.
    """
    
    def __init__(self):
        """Initialize value memory."""
        self._values: Dict[str, ValueEntry] = {}
        self._locked = True
        self._governance_key: Optional[str] = None
        self._value_count = 0
        
        # Initialize core values
        self._init_core_values()
    
    def _init_core_values(self) -> None:
        """Initialize immutable core values."""
        core = [
            ("constraint", "Never cause irreversible harm", 100),
            ("constraint", "Always maintain auditability", 99),
            ("constraint", "Never bypass governance", 98),
            ("norm", "Prefer reversible actions", 80),
            ("norm", "Minimize uncertainty", 70),
            ("risk_tolerance", "High risk requires human approval", 90),
            ("forbidden_state", "Autonomous goal creation", 100),
            ("forbidden_state", "Self-modification without oversight", 100),
        ]
        
        for category, description, priority in core:
            self._add_locked(category, description, priority)
    
    def _add_locked(
        self,
        category: str,
        description: str,
        priority: int,
    ) -> ValueEntry:
        """Add value entry (internal only)."""
        value_id = f"value_{self._value_count}"
        self._value_count += 1
        
        entry = ValueEntry(
            value_id=value_id,
            category=category,
            description=description,
            priority=priority,
            locked_at=datetime.utcnow(),
        )
        
        self._values[value_id] = entry
        return entry
    
    def get_constraints(self) -> List[ValueEntry]:
        """Get all constraints."""
        return [v for v in self._values.values() if v.category == "constraint"]
    
    def get_norms(self) -> List[ValueEntry]:
        """Get all norms."""
        return [v for v in self._values.values() if v.category == "norm"]
    
    def get_forbidden_states(self) -> List[ValueEntry]:
        """Get all forbidden states."""
        return [v for v in self._values.values() if v.category == "forbidden_state"]
    
    def check_forbidden(self, state_description: str) -> bool:
        """Check if state is forbidden."""
        forbidden = self.get_forbidden_states()
        state_lower = state_description.lower()
        
        for f in forbidden:
            if f.description.lower() in state_lower:
                return True
        
        return False
    
    def modify(self, *args, **kwargs) -> None:
        """FORBIDDEN: Modify values without governance."""
        raise ValueModificationError(
            "Value memory modification is forbidden without governance approval. "
            "No learning process may modify Mv."
        )
    
    def add(self, *args, **kwargs) -> None:
        """FORBIDDEN: Add values without governance."""
        raise GovernanceRequiredError(
            "Adding values requires governance approval. "
            "Value memory is Kernel-locked."
        )
    
    def delete(self, *args, **kwargs) -> None:
        """FORBIDDEN: Delete values."""
        raise ValueModificationError(
            "Value deletion is forbidden. "
            "Core values are permanent."
        )
    
    def unlock(self, *args, **kwargs) -> None:
        """FORBIDDEN: Unlock value memory."""
        raise ValueModificationError(
            "Value memory cannot be unlocked by learning processes. "
            "Only Kernel governance can modify."
        )
    
    def get_all(self) -> List[ValueEntry]:
        """Get all values."""
        return list(self._values.values())
    
    @property
    def count(self) -> int:
        """Total values."""
        return len(self._values)
    
    @property
    def is_locked(self) -> bool:
        """Check if locked."""
        return self._locked
