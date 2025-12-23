"""
Canon Errors

Explicit failure types for Objective Canon operations.
No generic exceptions allowed — all failures must be typed.

KERNEL MODULE - Human-written, no AI-generated code permitted.
"""


class CanonError(Exception):
    """Base class for all canon errors."""
    pass


class CanonSchemaViolation(CanonError):
    """
    Raised when an objective does not conform to the required schema.
    
    Examples:
    - Missing required field
    - Invalid field type
    - Invalid scope value
    - Invalid priority value
    """
    
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"Schema violation in '{field}': {message}")


class AxiomConflictError(CanonError):
    """
    Raised when an objective conflicts with a kernel axiom.
    
    Every rejection must reference the specific axiom violated.
    """
    
    def __init__(self, objective_id: str, axiom_id: str, reason: str):
        self.objective_id = objective_id
        self.axiom_id = axiom_id
        self.reason = reason
        super().__init__(
            f"Objective '{objective_id}' conflicts with axiom '{axiom_id}': {reason}"
        )


class ObjectiveAmbiguityError(CanonError):
    """
    Raised when an objective is ambiguous or self-referential.
    
    Examples:
    - Circular dependency between objectives
    - Self-referential termination condition
    - Undefined scope reference
    """
    
    def __init__(self, objective_id: str, ambiguity: str):
        self.objective_id = objective_id
        self.ambiguity = ambiguity
        super().__init__(f"Objective '{objective_id}' is ambiguous: {ambiguity}")


class UnauthorizedCanonMutation(CanonError):
    """
    Raised when an attempt is made to modify existing canon.
    
    Canon is append-only. Modifications require:
    - New objective ID
    - Supersession reference to old objective
    - Full audit trail
    """
    
    def __init__(self, objective_id: str, attempted_action: str):
        self.objective_id = objective_id
        self.attempted_action = attempted_action
        super().__init__(
            f"Unauthorized mutation of '{objective_id}': {attempted_action}. "
            "Canon is immutable. Create a superseding objective instead."
        )


class PersistenceIntegrityError(CanonError):
    """
    Raised when canon storage integrity is compromised.
    
    Examples:
    - Checksum mismatch
    - Missing content for hash
    - Corrupted storage
    """
    
    def __init__(self, objective_id: str, expected_hash: str, actual_hash: str):
        self.objective_id = objective_id
        self.expected_hash = expected_hash
        self.actual_hash = actual_hash
        super().__init__(
            f"Integrity failure for '{objective_id}': "
            f"expected hash '{expected_hash[:16]}...', got '{actual_hash[:16]}...'"
        )


class CanonHashMismatchError(CanonError):
    """
    Raised when the canon hash does not match kernel state.
    
    This is a CRITICAL error. The kernel must HALT.
    """
    
    def __init__(self, expected_hash: str, actual_hash: str):
        self.expected_hash = expected_hash
        self.actual_hash = actual_hash
        super().__init__(
            f"CRITICAL: Canon hash mismatch. Expected '{expected_hash[:16]}...', "
            f"got '{actual_hash[:16]}...'. Kernel must HALT."
        )


class ExecutionSemanticsError(CanonError):
    """
    Raised when an objective contains execution-like language.
    
    Objectives describe WHAT must be preserved, not HOW.
    Forbidden verbs: execute, optimize, control, implement, trigger, run, invoke.
    """
    
    def __init__(self, objective_id: str, forbidden_term: str, context: str):
        self.objective_id = objective_id
        self.forbidden_term = forbidden_term
        self.context = context
        super().__init__(
            f"Objective '{objective_id}' contains execution semantics: "
            f"'{forbidden_term}' in '{context}'. Objectives must be declarative."
        )
