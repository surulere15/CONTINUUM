"""
Resource Arbiter

Compute allocation. Resources serve goals, not agents.

ORCHESTRATION - Phase II.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum


class ResourceType(Enum):
    """Types of resources."""
    COMPUTE = "compute"
    MEMORY = "memory"
    NETWORK = "network"
    STORAGE = "storage"
    MODEL_INFERENCE = "model_inference"


@dataclass
class ResourceQuota:
    """Resource quota for a goal."""
    goal_id: str
    resource_type: ResourceType
    allocated: float
    used: float
    limit: float


@dataclass
class ResourceAllocation:
    """An active resource allocation."""
    allocation_id: str
    goal_id: str
    agent_id: Optional[str]
    resource_type: ResourceType
    amount: float
    allocated_at: datetime


class ResourceExhaustedError(Exception):
    """Raised when resources exhausted."""
    pass


class UnauthorizedAllocationError(Exception):
    """Raised when allocation unauthorized."""
    pass


class ResourceArbiter:
    """
    Resource Arbiter.
    
    Allocates compute resources.
    Resources serve goals, not agents directly.
    """
    
    DEFAULT_LIMITS = {
        ResourceType.COMPUTE: 100.0,
        ResourceType.MEMORY: 1000.0,
        ResourceType.NETWORK: 50.0,
        ResourceType.STORAGE: 500.0,
        ResourceType.MODEL_INFERENCE: 100.0,
    }
    
    def __init__(self):
        """Initialize arbiter."""
        self._quotas: Dict[str, Dict[ResourceType, ResourceQuota]] = {}
        self._allocations: Dict[str, ResourceAllocation] = {}
        self._allocation_count = 0
    
    def create_quota(
        self,
        goal_id: str,
        limits: Optional[Dict[ResourceType, float]] = None,
    ) -> Dict[ResourceType, ResourceQuota]:
        """Create quotas for a goal."""
        limits = limits or self.DEFAULT_LIMITS
        
        quotas = {}
        for rtype, limit in limits.items():
            quotas[rtype] = ResourceQuota(
                goal_id=goal_id,
                resource_type=rtype,
                allocated=0.0,
                used=0.0,
                limit=limit,
            )
        
        self._quotas[goal_id] = quotas
        return quotas
    
    def allocate(
        self,
        goal_id: str,
        resource_type: ResourceType,
        amount: float,
        agent_id: Optional[str] = None,
    ) -> ResourceAllocation:
        """
        Allocate resources for a goal.
        
        Args:
            goal_id: Goal requesting resources
            resource_type: Type of resource
            amount: Amount to allocate
            agent_id: Optional agent
            
        Returns:
            ResourceAllocation
        """
        if goal_id not in self._quotas:
            raise UnauthorizedAllocationError(
                f"No quota for goal '{goal_id}'. "
                f"Create quota first."
            )
        
        quota = self._quotas[goal_id].get(resource_type)
        if not quota:
            raise UnauthorizedAllocationError(
                f"No quota for resource type {resource_type.value}."
            )
        
        if quota.allocated + amount > quota.limit:
            raise ResourceExhaustedError(
                f"Resource limit exceeded for {resource_type.value}. "
                f"Allocated: {quota.allocated}, Requested: {amount}, Limit: {quota.limit}"
            )
        
        allocation_id = f"alloc_{self._allocation_count}"
        self._allocation_count += 1
        
        allocation = ResourceAllocation(
            allocation_id=allocation_id,
            goal_id=goal_id,
            agent_id=agent_id,
            resource_type=resource_type,
            amount=amount,
            allocated_at=datetime.utcnow(),
        )
        
        quota.allocated += amount
        self._allocations[allocation_id] = allocation
        
        return allocation
    
    def release(self, allocation_id: str) -> None:
        """Release an allocation."""
        if allocation_id not in self._allocations:
            return
        
        alloc = self._allocations.pop(allocation_id)
        
        if alloc.goal_id in self._quotas:
            quota = self._quotas[alloc.goal_id].get(alloc.resource_type)
            if quota:
                quota.allocated = max(0, quota.allocated - alloc.amount)
    
    def unlimited_allocation(self, *args, **kwargs) -> None:
        """FORBIDDEN: Unlimited allocation."""
        raise ResourceExhaustedError(
            "Unlimited allocation is forbidden. "
            "All resources have quotas."
        )
    
    def get_usage(self, goal_id: str) -> Dict[ResourceType, float]:
        """Get resource usage for goal."""
        if goal_id not in self._quotas:
            return {}
        
        return {
            rtype: quota.allocated
            for rtype, quota in self._quotas[goal_id].items()
        }
