"""
Execution Channel

Constrained pathway for work flow.

EFAP-C - Execution Fabric & Agent Physics.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Set
from enum import Enum


class ChannelType(Enum):
    """Types of execution channels."""
    API = "api"
    GUI = "gui"
    COMPUTE = "compute"
    DATA = "data"
    NETWORK = "network"


class ChannelState(Enum):
    """Channel state."""
    OPEN = "open"
    THROTTLED = "throttled"
    BLOCKED = "blocked"
    CLOSED = "closed"


@dataclass
class Channel:
    """
    Execution channel.
    
    Channels enforce:
    - Rate limits
    - Permissions
    - Isolation
    """
    channel_id: str
    channel_type: ChannelType
    state: ChannelState
    rate_limit: int          # Max ops per second
    current_rate: int
    permissions: Set[str]
    isolated: bool


@dataclass
class ChannelTransmission:
    """A transmission through a channel."""
    transmission_id: str
    channel_id: str
    work_id: str
    transmitted_at: datetime


class RateLimitError(Exception):
    """Raised when rate limit exceeded."""
    pass


class ChannelPermissionError(Exception):
    """Raised when permission denied."""
    pass


class ExecutionChannel:
    """
    Execution Channel Manager.
    
    Constrained pathways for work flow.
    Enforces rate limits, permissions, isolation.
    """
    
    DEFAULT_RATE_LIMIT = 100  # ops/sec
    
    def __init__(self):
        """Initialize channel manager."""
        self._channels: Dict[str, Channel] = {}
        self._transmissions: List[ChannelTransmission] = []
        self._channel_count = 0
        self._transmission_count = 0
        
        # Create default channels
        self._init_channels()
    
    def _init_channels(self) -> None:
        """Initialize default channels."""
        defaults = [
            (ChannelType.API, {"read", "write", "network"}),
            (ChannelType.GUI, {"read", "interact"}),
            (ChannelType.COMPUTE, {"execute", "compute"}),
            (ChannelType.DATA, {"read", "write"}),
        ]
        
        for ctype, perms in defaults:
            self.create(ctype, perms)
    
    def create(
        self,
        channel_type: ChannelType,
        permissions: Set[str],
        rate_limit: int = DEFAULT_RATE_LIMIT,
    ) -> Channel:
        """Create a channel."""
        channel_id = f"channel_{self._channel_count}"
        self._channel_count += 1
        
        channel = Channel(
            channel_id=channel_id,
            channel_type=channel_type,
            state=ChannelState.OPEN,
            rate_limit=rate_limit,
            current_rate=0,
            permissions=permissions,
            isolated=True,
        )
        
        self._channels[channel_id] = channel
        return channel
    
    def transmit(
        self,
        channel_id: str,
        work_id: str,
        required_permissions: Set[str],
    ) -> ChannelTransmission:
        """
        Transmit work through channel.
        
        Args:
            channel_id: Channel to use
            work_id: Work to transmit
            required_permissions: Required permissions
            
        Returns:
            ChannelTransmission
        """
        if channel_id not in self._channels:
            raise ValueError(f"Channel '{channel_id}' not found")
        
        channel = self._channels[channel_id]
        
        # Check state
        if channel.state == ChannelState.CLOSED:
            raise ValueError("Channel is closed")
        
        # Check rate limit
        if channel.current_rate >= channel.rate_limit:
            raise RateLimitError(
                f"Rate limit exceeded on channel '{channel_id}'. "
                f"Limit: {channel.rate_limit}"
            )
        
        # Check permissions
        if not required_permissions.issubset(channel.permissions):
            missing = required_permissions - channel.permissions
            raise ChannelPermissionError(
                f"Permission denied. Missing: {missing}"
            )
        
        channel.current_rate += 1
        
        transmission_id = f"tx_{self._transmission_count}"
        self._transmission_count += 1
        
        transmission = ChannelTransmission(
            transmission_id=transmission_id,
            channel_id=channel_id,
            work_id=work_id,
            transmitted_at=datetime.utcnow(),
        )
        
        self._transmissions.append(transmission)
        return transmission
    
    def reset_rates(self) -> None:
        """Reset all channel rates (called periodically)."""
        for channel in self._channels.values():
            channel.current_rate = 0
    
    def get_by_type(self, channel_type: ChannelType) -> Optional[Channel]:
        """Get channel by type."""
        for channel in self._channels.values():
            if channel.channel_type == channel_type:
                return channel
        return None
    
    @property
    def open_count(self) -> int:
        """Open channels."""
        return sum(1 for c in self._channels.values() if c.state == ChannelState.OPEN)
