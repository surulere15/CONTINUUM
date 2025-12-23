"""
Retention Policy

Domain-specific retention policies.
Never deletes audit trail — only archives.

INSTRUMENTATION MODULE - No imports from kernel/cognitive/execution/agents.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from enum import Enum


class RetentionAction(Enum):
    """Actions for signals past retention."""
    ARCHIVE = "archive"      # Move to cold storage
    COMPRESS = "compress"    # Compress in place
    NONE = "none"           # Keep forever


@dataclass(frozen=True)
class RetentionPolicy:
    """
    Retention policy for a domain.
    
    Defines how long signals are kept in hot storage
    and what happens when they age out.
    """
    domain: str
    hot_retention_days: int      # Days in hot storage
    warm_retention_days: int     # Days before archival
    action: RetentionAction
    description: str


# Default retention policies by domain
DEFAULT_POLICIES: Dict[str, RetentionPolicy] = {
    "economic": RetentionPolicy(
        domain="economic",
        hot_retention_days=365,      # 1 year hot
        warm_retention_days=3650,    # 10 years warm
        action=RetentionAction.ARCHIVE,
        description="Economic signals retained for long-term trend reference",
    ),
    "environmental": RetentionPolicy(
        domain="environmental",
        hot_retention_days=730,      # 2 years hot
        warm_retention_days=7300,    # 20 years warm
        action=RetentionAction.ARCHIVE,
        description="Environmental signals for climate pattern analysis",
    ),
    "societal": RetentionPolicy(
        domain="societal",
        hot_retention_days=365,      # 1 year hot
        warm_retention_days=3650,    # 10 years warm
        action=RetentionAction.ARCHIVE,
        description="Societal signals for demographic reference",
    ),
    "technological": RetentionPolicy(
        domain="technological",
        hot_retention_days=180,      # 6 months hot
        warm_retention_days=1825,    # 5 years warm
        action=RetentionAction.COMPRESS,
        description="Tech signals compress due to rapid obsolescence",
    ),
}


@dataclass
class RetentionDecision:
    """Decision about a signal's retention status."""
    signal_id: str
    domain: str
    age_days: int
    status: str  # "hot", "warm", "archive"
    action: RetentionAction


class RetentionManager:
    """
    Manages signal retention policies.
    
    Rules:
    - Never deletes audit trail
    - Only archives or compresses
    - Policies are domain-specific
    - Human-configurable thresholds
    """
    
    def __init__(self, policies: Optional[Dict[str, RetentionPolicy]] = None):
        """
        Initialize with retention policies.
        
        Args:
            policies: Custom policies, or use defaults
        """
        self._policies = policies or DEFAULT_POLICIES.copy()
    
    def evaluate(
        self,
        signal_id: str,
        domain: str,
        timestamp: datetime,
        now: Optional[datetime] = None,
    ) -> RetentionDecision:
        """
        Evaluate retention status for a signal.
        
        Args:
            signal_id: Signal identifier
            domain: Signal domain
            timestamp: Signal timestamp
            now: Current time (defaults to now)
            
        Returns:
            RetentionDecision
        """
        now = now or datetime.utcnow()
        age = now - timestamp
        age_days = age.days
        
        policy = self._policies.get(domain)
        if not policy:
            # No policy = keep forever
            return RetentionDecision(
                signal_id=signal_id,
                domain=domain,
                age_days=age_days,
                status="hot",
                action=RetentionAction.NONE,
            )
        
        if age_days <= policy.hot_retention_days:
            status = "hot"
            action = RetentionAction.NONE
        elif age_days <= policy.warm_retention_days:
            status = "warm"
            action = RetentionAction.NONE
        else:
            status = "archive"
            action = policy.action
        
        return RetentionDecision(
            signal_id=signal_id,
            domain=domain,
            age_days=age_days,
            status=status,
            action=action,
        )
    
    def get_policy(self, domain: str) -> Optional[RetentionPolicy]:
        """Get policy for domain."""
        return self._policies.get(domain)
    
    def set_policy(self, policy: RetentionPolicy) -> None:
        """Set policy for domain."""
        self._policies[policy.domain] = policy
