"""
Authority Classes

Human roles and authority levels.
No role has unilateral authority over Canon.

GOVERNANCE - Phase I. Shared steering without control abdication.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Set, Optional, Tuple
from enum import Enum
import hashlib


class AuthorityLevel(Enum):
    """Authority levels in the governance hierarchy."""
    STEWARD = "steward"       # Strategic directives, prioritization
    OPERATOR = "operator"     # Operational commands, pause/resume
    AUDITOR = "auditor"       # Read-only, can trigger review
    GUARDIAN = "guardian"     # Emergency override, halt


class Permission(Enum):
    """Specific permissions within authority classes."""
    # Steward permissions
    ISSUE_STRATEGIC_DIRECTIVE = "issue_strategic_directive"
    PRIORITIZE_OBJECTIVES = "prioritize_objectives"
    
    # Operator permissions
    ISSUE_OPERATIONAL_COMMAND = "issue_operational_command"
    PAUSE_EXECUTION = "pause_execution"
    RESUME_EXECUTION = "resume_execution"
    REROUTE_EXECUTION = "reroute_execution"
    
    # Auditor permissions
    READ_LOGS = "read_logs"
    TRIGGER_REVIEW = "trigger_review"
    
    # Guardian permissions
    EMERGENCY_HALT = "emergency_halt"
    FREEZE_AGENTS = "freeze_agents"
    ISOLATE_SUBSYSTEM = "isolate_subsystem"


# Authority class permission mappings
AUTHORITY_PERMISSIONS = {
    AuthorityLevel.STEWARD: frozenset({
        Permission.ISSUE_STRATEGIC_DIRECTIVE,
        Permission.PRIORITIZE_OBJECTIVES,
        Permission.READ_LOGS,
    }),
    AuthorityLevel.OPERATOR: frozenset({
        Permission.ISSUE_OPERATIONAL_COMMAND,
        Permission.PAUSE_EXECUTION,
        Permission.RESUME_EXECUTION,
        Permission.REROUTE_EXECUTION,
        Permission.READ_LOGS,
    }),
    AuthorityLevel.AUDITOR: frozenset({
        Permission.READ_LOGS,
        Permission.TRIGGER_REVIEW,
    }),
    AuthorityLevel.GUARDIAN: frozenset({
        Permission.EMERGENCY_HALT,
        Permission.FREEZE_AGENTS,
        Permission.ISOLATE_SUBSYSTEM,
        Permission.READ_LOGS,
    }),
}

# Universally forbidden permissions (no role can do these)
FORBIDDEN_PERMISSIONS = frozenset({
    "modify_objective_canon",
    "grant_autonomy",
    "remove_safeguards",
    "rewrite_purpose",
    "create_objectives",
})


@dataclass(frozen=True)
class HumanIdentity:
    """
    Identity of an authorized human.
    
    All governance actions are attributable.
    """
    identity_id: str
    name: str
    authority_level: AuthorityLevel
    permissions: Tuple[Permission, ...]
    credential_hash: str
    registered_at: datetime


class CanonModificationError(Exception):
    """Raised when Canon modification is attempted."""
    pass


class AuthorityLeakageError(Exception):
    """Raised when authority leakage is detected."""
    pass


class UnauthorizedActionError(Exception):
    """Raised when unauthorized action is attempted."""
    pass


class AuthorityRegistry:
    """
    Registry of authorized humans and their authority levels.
    
    Properties:
    - No role can modify Objective Canon
    - No role can grant autonomy
    - No role can remove safeguards
    - All actions are attributable
    """
    
    def __init__(self):
        """Initialize authority registry."""
        self._identities: dict[str, HumanIdentity] = {}
    
    def register(
        self,
        identity_id: str,
        name: str,
        authority_level: AuthorityLevel,
    ) -> HumanIdentity:
        """
        Register a human identity.
        
        Args:
            identity_id: Unique identifier
            name: Human name
            authority_level: Authority class
            
        Returns:
            HumanIdentity
        """
        permissions = AUTHORITY_PERMISSIONS.get(authority_level, frozenset())
        
        credential_hash = hashlib.sha256(
            f"{identity_id}:{name}:{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()
        
        identity = HumanIdentity(
            identity_id=identity_id,
            name=name,
            authority_level=authority_level,
            permissions=tuple(permissions),
            credential_hash=credential_hash,
            registered_at=datetime.utcnow(),
        )
        
        self._identities[identity_id] = identity
        return identity
    
    def has_permission(
        self,
        identity_id: str,
        permission: Permission,
    ) -> bool:
        """Check if identity has permission."""
        if identity_id not in self._identities:
            return False
        
        identity = self._identities[identity_id]
        return permission in identity.permissions
    
    def require_permission(
        self,
        identity_id: str,
        permission: Permission,
    ) -> None:
        """
        Assert identity has permission.
        
        Raises:
            UnauthorizedActionError: If permission not held
        """
        if not self.has_permission(identity_id, permission):
            raise UnauthorizedActionError(
                f"Identity '{identity_id}' lacks permission '{permission.value}'"
            )
    
    def modify_canon(self, *args, **kwargs) -> None:
        """FORBIDDEN: No role can modify Canon."""
        raise CanonModificationError(
            "No authority class can modify the Objective Canon. "
            "Canon is immutable."
        )
    
    def grant_autonomy(self, *args, **kwargs) -> None:
        """FORBIDDEN: No role can grant autonomy."""
        raise AuthorityLeakageError(
            "No authority class can grant autonomy. "
            "CONTINUUM remains non-autonomous."
        )
    
    def remove_safeguards(self, *args, **kwargs) -> None:
        """FORBIDDEN: No role can remove safeguards."""
        raise AuthorityLeakageError(
            "No authority class can remove safeguards. "
            "Safety constraints are immutable."
        )
    
    def get_identity(self, identity_id: str) -> Optional[HumanIdentity]:
        """Get identity by ID."""
        return self._identities.get(identity_id)
    
    @property
    def identity_count(self) -> int:
        """Number of registered identities."""
        return len(self._identities)
