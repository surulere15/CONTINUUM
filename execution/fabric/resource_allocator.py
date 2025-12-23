"""
Resource Allocator

Manages resource pools and allocation for task execution.
"""

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class ResourceRequest:
    cpu: float  # cores
    memory: int  # MB
    network: bool
    gpu: int  # count


@dataclass  
class ResourceAllocation:
    request_id: str
    granted: ResourceRequest
    expires_at: Optional[float]


class ResourceAllocator:
    """Manages resource allocation."""
    
    def __init__(self, total_resources: Dict):
        self._total = total_resources
        self._allocated: Dict[str, ResourceRequest] = {}
    
    def allocate(self, request_id: str, request: ResourceRequest) -> Optional[ResourceAllocation]:
        """Allocate resources."""
        if self._can_allocate(request):
            self._allocated[request_id] = request
            return ResourceAllocation(
                request_id=request_id,
                granted=request,
                expires_at=None
            )
        return None
    
    def release(self, request_id: str) -> bool:
        """Release allocated resources."""
        if request_id in self._allocated:
            del self._allocated[request_id]
            return True
        return False
    
    def _can_allocate(self, request: ResourceRequest) -> bool:
        """Check if resources are available."""
        used_cpu = sum(r.cpu for r in self._allocated.values())
        used_memory = sum(r.memory for r in self._allocated.values())
        
        return (
            used_cpu + request.cpu <= self._total.get("cpu", 0) and
            used_memory + request.memory <= self._total.get("memory", 0)
        )
    
    def get_available(self) -> Dict:
        """Get available resources."""
        used_cpu = sum(r.cpu for r in self._allocated.values())
        used_memory = sum(r.memory for r in self._allocated.values())
        
        return {
            "cpu": self._total.get("cpu", 0) - used_cpu,
            "memory": self._total.get("memory", 0) - used_memory
        }
