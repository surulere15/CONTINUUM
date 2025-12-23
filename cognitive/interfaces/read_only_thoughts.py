"""
Read-Only Thought Interface

Safe inspection of cognition. No command injection or feedback loops.

COGNITIVE MODULE - No imports from execution/agents/kernel/governance.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional, List
from enum import Enum


class ThoughtAccessLevel(Enum):
    """Access levels for thought inspection."""
    INSPECT = "inspect"
    DEBUG = "debug"
    AUDIT = "audit"


@dataclass(frozen=True)
class ThoughtSnapshot:
    """
    Read-only snapshot of cognitive state.
    
    Cannot be used to inject commands or create feedback.
    """
    snapshot_id: str
    timestamp: datetime
    active_concepts: tuple
    active_relations: tuple
    current_constraints: tuple
    processing_status: str


@dataclass(frozen=True)
class ThoughtQuery:
    """
    Query for thought inspection.
    
    Queries are read-only — no side effects.
    """
    query_id: str
    query_type: str
    parameters: dict
    access_level: ThoughtAccessLevel


@dataclass(frozen=True)
class ThoughtQueryResult:
    """Result of thought query."""
    query_id: str
    result: Any
    accessed_at: datetime


class CommandInjectionError(Exception):
    """Raised when command injection is attempted."""
    pass


class FeedbackLoopError(Exception):
    """Raised when feedback loop is attempted."""
    pass


class ReadOnlyThoughts:
    """
    Safe read-only interface to cognition.
    
    Allows:
    - Inspection
    - Debugging
    - Auditing
    
    Disallows:
    - Command injection
    - Feedback loops
    - Memory writes
    - Execution triggers
    """
    
    def __init__(self, cognition_core=None, representation_space=None):
        """
        Initialize with references to cognitive components.
        
        All references are read-only.
        """
        self._core = cognition_core
        self._space = representation_space
        self._query_log: List[ThoughtQuery] = []
    
    def snapshot(self) -> ThoughtSnapshot:
        """
        Take a snapshot of current cognitive state.
        
        Returns read-only snapshot — no modification possible.
        """
        import hashlib
        
        snapshot_id = hashlib.sha256(
            f"snapshot:{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()[:16]
        
        # Get concepts if space available
        concepts = ()
        relations = ()
        if self._space:
            concepts = tuple(self._space._concepts.keys())
            relations = tuple(self._space._relations.keys())
        
        # Get constraints if core available
        constraints = ()
        status = "unknown"
        if self._core:
            if hasattr(self._core, '_constraints') and self._core._constraints:
                constraints = self._core._constraints.get_active_constraints()
            status = self._core.status.value if hasattr(self._core, 'status') else "unknown"
        
        return ThoughtSnapshot(
            snapshot_id=snapshot_id,
            timestamp=datetime.utcnow(),
            active_concepts=concepts,
            active_relations=relations,
            current_constraints=constraints,
            processing_status=status,
        )
    
    def query(self, query: ThoughtQuery) -> ThoughtQueryResult:
        """
        Execute read-only query.
        
        Args:
            query: Query to execute
            
        Returns:
            Query result
        """
        self._query_log.append(query)
        
        result = None
        
        if query.query_type == "status":
            result = self.snapshot()
        elif query.query_type == "concepts":
            if self._space:
                result = list(self._space._concepts.values())
            else:
                result = []
        elif query.query_type == "constraints":
            if self._core and self._core._constraints:
                result = self._core._constraints.get_active_constraints()
            else:
                result = ()
        else:
            result = {"error": f"Unknown query type: {query.query_type}"}
        
        return ThoughtQueryResult(
            query_id=query.query_id,
            result=result,
            accessed_at=datetime.utcnow(),
        )
    
    def inject_command(self, *args, **kwargs) -> None:
        """
        FORBIDDEN: Inject commands into cognition.
        """
        raise CommandInjectionError(
            "Command injection is forbidden. "
            "This interface is read-only."
        )
    
    def create_feedback_loop(self, *args, **kwargs) -> None:
        """
        FORBIDDEN: Create feedback loops.
        """
        raise FeedbackLoopError(
            "Feedback loops are forbidden. "
            "Cognition cannot be influenced through inspection."
        )
    
    def write_memory(self, *args, **kwargs) -> None:
        """
        FORBIDDEN: Write to memory.
        """
        raise CommandInjectionError(
            "Memory writes are forbidden through inspection interface."
        )
    
    def trigger_execution(self, *args, **kwargs) -> None:
        """
        FORBIDDEN: Trigger execution.
        """
        raise CommandInjectionError(
            "Execution triggers are forbidden. "
            "Cognition cannot initiate actions."
        )
    
    def get_query_log(self) -> List[ThoughtQuery]:
        """Get query history (for auditing)."""
        return list(self._query_log)
