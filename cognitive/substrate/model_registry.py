"""
Model Registry

Tracks available models, their capabilities, and routes requests
to appropriate model endpoints.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum


class ModelCapability(Enum):
    """Capabilities a model can have."""
    TEXT_GENERATION = "text_generation"
    REASONING = "reasoning"
    CODE = "code"
    VISION = "vision"
    EMBEDDING = "embedding"


@dataclass
class ModelInfo:
    """Information about a registered model."""
    id: str
    name: str
    version: str
    capabilities: List[ModelCapability]
    context_window: int
    cost_per_token: float
    latency_ms: int
    endpoint: str
    is_available: bool


class ModelRegistry:
    """
    Registry of available models and their capabilities.
    """
    
    def __init__(self):
        """Initialize empty registry."""
        self._models: Dict[str, ModelInfo] = {}
    
    def register(self, model: ModelInfo) -> None:
        """Register a model."""
        self._models[model.id] = model
    
    def get(self, model_id: str) -> Optional[ModelInfo]:
        """Get model by ID."""
        return self._models.get(model_id)
    
    def find_by_capability(
        self,
        capability: ModelCapability,
        min_context: int = 0
    ) -> List[ModelInfo]:
        """Find models with specific capability."""
        return [
            m for m in self._models.values()
            if capability in m.capabilities
            and m.context_window >= min_context
            and m.is_available
        ]
    
    def list_all(self) -> List[ModelInfo]:
        """List all registered models."""
        return list(self._models.values())
    
    def set_availability(self, model_id: str, available: bool) -> None:
        """Update model availability status."""
        if model_id in self._models:
            self._models[model_id].is_available = available
