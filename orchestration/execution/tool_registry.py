"""
Tool Registry

Tool management. Tools are capabilities with constraints.

ORCHESTRATION - Phase II.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Dict, List, Optional, Set, Tuple
from enum import Enum


class ToolCategory(Enum):
    """Tool categories."""
    READ = "read"          # Read-only operations
    WRITE = "write"        # Writes data
    EXECUTE = "execute"    # Executes code
    NETWORK = "network"    # Network operations
    SYSTEM = "system"      # System operations


class ToolRisk(Enum):
    """Tool risk levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True)
class Tool:
    """A registered tool."""
    tool_id: str
    name: str
    description: str
    category: ToolCategory
    risk: ToolRisk
    permissions_required: Tuple[str, ...]
    reversible: bool


class ToolNotFoundError(Exception):
    """Raised when tool not found."""
    pass


class ToolUnauthorizedError(Exception):
    """Raised when tool use unauthorized."""
    pass


class ToolRegistry:
    """
    Tool Registry.
    
    Manages available tools.
    Tools have:
    - Categories
    - Risk levels
    - Permission requirements
    """
    
    def __init__(self):
        """Initialize registry."""
        self._tools: Dict[str, Tool] = {}
        self._tool_count = 0
        
        # Register default tools
        self._register_defaults()
    
    def _register_defaults(self) -> None:
        """Register default tools."""
        defaults = [
            ("read_file", "Read a file", ToolCategory.READ, ToolRisk.LOW, ("read",), True),
            ("write_file", "Write a file", ToolCategory.WRITE, ToolRisk.MEDIUM, ("write",), True),
            ("execute_code", "Execute code", ToolCategory.EXECUTE, ToolRisk.HIGH, ("execute",), False),
            ("http_request", "Make HTTP request", ToolCategory.NETWORK, ToolRisk.MEDIUM, ("network",), True),
            ("query_database", "Query database", ToolCategory.READ, ToolRisk.LOW, ("read", "database"), True),
        ]
        
        for name, desc, cat, risk, perms, rev in defaults:
            self.register(name, desc, cat, risk, perms, rev)
    
    def register(
        self,
        name: str,
        description: str,
        category: ToolCategory,
        risk: ToolRisk,
        permissions: Tuple[str, ...],
        reversible: bool,
    ) -> Tool:
        """Register a tool."""
        tool_id = f"tool_{self._tool_count}"
        self._tool_count += 1
        
        tool = Tool(
            tool_id=tool_id,
            name=name,
            description=description,
            category=category,
            risk=risk,
            permissions_required=permissions,
            reversible=reversible,
        )
        
        self._tools[name] = tool
        return tool
    
    def get(self, name: str) -> Tool:
        """Get a tool by name."""
        if name not in self._tools:
            raise ToolNotFoundError(f"Tool '{name}' not registered.")
        return self._tools[name]
    
    def authorize(
        self,
        tool_name: str,
        agent_permissions: Set[str],
    ) -> bool:
        """
        Check if agent is authorized to use tool.
        
        Args:
            tool_name: Tool to check
            agent_permissions: Agent's permissions
            
        Returns:
            True if authorized
        """
        tool = self.get(tool_name)
        required = set(tool.permissions_required)
        
        if not required.issubset(agent_permissions):
            raise ToolUnauthorizedError(
                f"Agent lacks permissions for tool '{tool_name}'. "
                f"Required: {required}, Has: {agent_permissions}"
            )
        
        return True
    
    def list_by_category(self, category: ToolCategory) -> List[Tool]:
        """List tools by category."""
        return [t for t in self._tools.values() if t.category == category]
    
    def list_by_risk(self, max_risk: ToolRisk) -> List[Tool]:
        """List tools up to risk level."""
        return [
            t for t in self._tools.values()
            if t.risk.value <= max_risk.value
        ]
    
    @property
    def count(self) -> int:
        """Total registered tools."""
        return len(self._tools)
