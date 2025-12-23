"""
Superfluid Router

Work flows around failures. Blocked agent ≠ blocked system.

EFAP-C - Execution Fabric & Agent Physics.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Set
from enum import Enum


class RouteStatus(Enum):
    """Route status."""
    AVAILABLE = "available"
    DEGRADED = "degraded"
    BLOCKED = "blocked"


@dataclass
class Route:
    """A route for work flow."""
    route_id: str
    agent_ids: List[str]
    status: RouteStatus
    failed_agents: Set[str]


@dataclass
class RoutingDecision:
    """Decision on work routing."""
    work_id: str
    route_id: str
    agent_id: str
    rerouted: bool
    original_agent: Optional[str]
    decided_at: datetime


class SuperfluidRouter:
    """
    Superfluid Router.
    
    Law 5: Work flows around failures.
    Blocked agent ≠ blocked system.
    
    Like a superfluid: work flows without turbulence.
    """
    
    def __init__(self):
        """Initialize router."""
        self._routes: Dict[str, Route] = {}
        self._decisions: List[RoutingDecision] = []
        self._route_count = 0
    
    def create_route(
        self,
        agent_ids: List[str],
    ) -> Route:
        """Create a route with multiple agents."""
        route_id = f"route_{self._route_count}"
        self._route_count += 1
        
        route = Route(
            route_id=route_id,
            agent_ids=agent_ids,
            status=RouteStatus.AVAILABLE,
            failed_agents=set(),
        )
        
        self._routes[route_id] = route
        return route
    
    def route(
        self,
        work_id: str,
        route_id: str,
        preferred_agent: Optional[str] = None,
    ) -> RoutingDecision:
        """
        Route work to an agent.
        
        Automatically reroutes around failures.
        
        Args:
            work_id: Work to route
            route_id: Route to use
            preferred_agent: Preferred agent (may be unavailable)
            
        Returns:
            RoutingDecision
        """
        if route_id not in self._routes:
            raise ValueError(f"Route '{route_id}' not found")
        
        route = self._routes[route_id]
        
        # Find available agent
        available = [
            aid for aid in route.agent_ids
            if aid not in route.failed_agents
        ]
        
        if not available:
            raise ValueError(
                f"No available agents on route '{route_id}'. "
                f"Failed: {route.failed_agents}"
            )
        
        # Check if preferred is available
        if preferred_agent and preferred_agent in available:
            selected = preferred_agent
            rerouted = False
        else:
            selected = available[0]
            rerouted = preferred_agent is not None
        
        decision = RoutingDecision(
            work_id=work_id,
            route_id=route_id,
            agent_id=selected,
            rerouted=rerouted,
            original_agent=preferred_agent if rerouted else None,
            decided_at=datetime.utcnow(),
        )
        
        self._decisions.append(decision)
        return decision
    
    def mark_failed(self, route_id: str, agent_id: str) -> None:
        """Mark agent as failed on route."""
        if route_id in self._routes:
            route = self._routes[route_id]
            route.failed_agents.add(agent_id)
            
            # Update route status
            available = len(route.agent_ids) - len(route.failed_agents)
            if available == 0:
                route.status = RouteStatus.BLOCKED
            elif available < len(route.agent_ids) / 2:
                route.status = RouteStatus.DEGRADED
    
    def recover(self, route_id: str, agent_id: str) -> None:
        """Recover a failed agent."""
        if route_id in self._routes:
            route = self._routes[route_id]
            route.failed_agents.discard(agent_id)
            
            # Update status
            if not route.failed_agents:
                route.status = RouteStatus.AVAILABLE
            else:
                route.status = RouteStatus.DEGRADED
    
    def get_reroute_count(self) -> int:
        """Count of rerouted decisions."""
        return sum(1 for d in self._decisions if d.rerouted)
