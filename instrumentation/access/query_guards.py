"""
Query Guards

Rate limiting and scope enforcement for signal access.
Prevents exfiltration patterns and abuse.

INSTRUMENTATION MODULE - No imports from kernel/cognitive/execution/agents.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, Optional
from enum import Enum


class GuardViolation(Exception):
    """Raised when query violates guards."""
    pass


class ViolationType(Enum):
    """Types of guard violations."""
    RATE_LIMIT = "rate_limit"
    SCOPE_VIOLATION = "scope_violation"
    EXFILTRATION_PATTERN = "exfiltration_pattern"
    FORBIDDEN_OPERATION = "forbidden_operation"


@dataclass
class GuardResult:
    """Result of guard check."""
    allowed: bool
    violation_type: Optional[ViolationType] = None
    reason: Optional[str] = None
    retry_after_seconds: Optional[int] = None


@dataclass
class RateLimitConfig:
    """Rate limit configuration."""
    requests_per_minute: int
    requests_per_hour: int
    max_results_per_query: int


# Default rate limits
DEFAULT_RATE_LIMITS = RateLimitConfig(
    requests_per_minute=60,
    requests_per_hour=1000,
    max_results_per_query=1000,
)


class QueryGuards:
    """
    Guard layer for signal queries.
    
    Protections:
    - Rate limiting
    - Scope enforcement (no cross-domain)
    - Exfiltration detection
    - Forbidden operation blocking
    
    Forbidden Operations:
    - Cross-domain aggregation
    - Computing scores or indices
    - Triggering actions
    - Modifying signals
    """
    
    def __init__(self, config: Optional[RateLimitConfig] = None):
        """
        Initialize guards.
        
        Args:
            config: Rate limit configuration
        """
        self._config = config or DEFAULT_RATE_LIMITS
        self._request_log: Dict[str, list] = {}  # client_id -> timestamps
    
    def check_rate_limit(self, client_id: str) -> GuardResult:
        """
        Check if client is within rate limits.
        
        Args:
            client_id: Client identifier
            
        Returns:
            GuardResult
        """
        now = datetime.utcnow()
        
        if client_id not in self._request_log:
            self._request_log[client_id] = []
        
        # Clean old entries
        cutoff_hour = now - timedelta(hours=1)
        self._request_log[client_id] = [
            ts for ts in self._request_log[client_id]
            if ts > cutoff_hour
        ]
        
        timestamps = self._request_log[client_id]
        
        # Check per-minute limit
        minute_ago = now - timedelta(minutes=1)
        recent_minute = sum(1 for ts in timestamps if ts > minute_ago)
        if recent_minute >= self._config.requests_per_minute:
            return GuardResult(
                allowed=False,
                violation_type=ViolationType.RATE_LIMIT,
                reason=f"Rate limit exceeded: {recent_minute}/{self._config.requests_per_minute} per minute",
                retry_after_seconds=60,
            )
        
        # Check per-hour limit
        if len(timestamps) >= self._config.requests_per_hour:
            return GuardResult(
                allowed=False,
                violation_type=ViolationType.RATE_LIMIT,
                reason=f"Rate limit exceeded: {len(timestamps)}/{self._config.requests_per_hour} per hour",
                retry_after_seconds=3600,
            )
        
        # Record this request
        self._request_log[client_id].append(now)
        
        return GuardResult(allowed=True)
    
    def check_scope(self, domains_requested: list) -> GuardResult:
        """
        Check if query scope is valid.
        
        Cross-domain queries are forbidden.
        """
        if len(domains_requested) > 1:
            return GuardResult(
                allowed=False,
                violation_type=ViolationType.SCOPE_VIOLATION,
                reason="Cross-domain queries are forbidden. Query one domain at a time.",
            )
        
        return GuardResult(allowed=True)
    
    def check_forbidden_operations(self, operation: str) -> GuardResult:
        """
        Check if operation is forbidden.
        
        Forbidden:
        - aggregate
        - score
        - index
        - optimize
        - trigger
        - modify
        - delete
        """
        forbidden = {
            "aggregate", "score", "index", "compute",
            "optimize", "trigger", "modify", "delete",
            "update", "average", "sum", "trend",
        }
        
        if operation.lower() in forbidden:
            return GuardResult(
                allowed=False,
                violation_type=ViolationType.FORBIDDEN_OPERATION,
                reason=f"Operation '{operation}' is forbidden. Signals are read-only facts.",
            )
        
        return GuardResult(allowed=True)
    
    def check_exfiltration(
        self,
        client_id: str,
        result_count: int,
        time_window_seconds: int = 3600,
    ) -> GuardResult:
        """
        Detect potential data exfiltration patterns.
        
        Flags excessive data retrieval.
        """
        # Simple heuristic: flag if requesting too much data
        if result_count > self._config.max_results_per_query:
            return GuardResult(
                allowed=False,
                violation_type=ViolationType.EXFILTRATION_PATTERN,
                reason=f"Result count {result_count} exceeds limit {self._config.max_results_per_query}",
            )
        
        return GuardResult(allowed=True)
    
    def full_check(
        self,
        client_id: str,
        domains: list,
        operation: str,
        result_count: int = 0,
    ) -> GuardResult:
        """
        Run all guard checks.
        
        Returns first failing check or success.
        """
        # Rate limit
        result = self.check_rate_limit(client_id)
        if not result.allowed:
            return result
        
        # Scope
        result = self.check_scope(domains)
        if not result.allowed:
            return result
        
        # Forbidden operations
        result = self.check_forbidden_operations(operation)
        if not result.allowed:
            return result
        
        # Exfiltration
        if result_count > 0:
            result = self.check_exfiltration(client_id, result_count)
            if not result.allowed:
                return result
        
        return GuardResult(allowed=True)
