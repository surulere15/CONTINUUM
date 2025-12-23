"""
Kernel Entrypoint

Main entry point for the CONTINUUM kernel.
Initializes all kernel subsystems and provides the primary interface.

KERNEL MODULE - Human-written, no AI-generated code permitted.
"""

from pathlib import Path
from typing import Optional
from datetime import datetime

from .state.kernel_state import KernelState, KernelStatus
from .state.audit_log import AuditLog, AuditEventType, AuditSeverity
from .governance.intent_validator import IntentValidator, Intent, ValidationResult
from .governance.conflict_resolver import ConflictResolver, Conflict, Resolution
from .governance.objective_persistence import ObjectivePersistence
from .governance.rollback_controller import RollbackController


class ContinuumKernel:
    """
    Main kernel class for CONTINUUM.
    
    This is the primary interface to kernel functionality.
    All governance operations flow through this class.
    """
    
    def __init__(self, kernel_path: Path):
        """
        Initialize CONTINUUM kernel.
        
        Args:
            kernel_path: Path to kernel directory
        """
        self._kernel_path = kernel_path
        self._state: Optional[KernelState] = None
        self._audit_log: Optional[AuditLog] = None
        self._intent_validator: Optional[IntentValidator] = None
        self._conflict_resolver: Optional[ConflictResolver] = None
        self._persistence: Optional[ObjectivePersistence] = None
        self._rollback: Optional[RollbackController] = None
        self._initialized = False
    
    def initialize(self) -> bool:
        """
        Initialize all kernel subsystems.
        
        Returns:
            True if initialization successful
        """
        try:
            # Initialize state manager
            self._state = KernelState(self._kernel_path)
            if not self._state.initialize():
                return False
            
            # Initialize audit log
            audit_path = self._kernel_path / "logs"
            audit_path.mkdir(parents=True, exist_ok=True)
            self._audit_log = AuditLog(audit_path)
            
            # Initialize governance components
            self._intent_validator = IntentValidator(
                axioms=self._state.axioms,
                canon=self._state.canon
            )
            
            lattices = self._state.canon.get('priority_lattices', {})
            self._conflict_resolver = ConflictResolver(lattices)
            
            # Initialize persistence
            persistence_path = self._kernel_path / "persistence"
            persistence_path.mkdir(parents=True, exist_ok=True)
            self._persistence = ObjectivePersistence(persistence_path)
            
            # Initialize rollback controller
            checkpoint_path = self._kernel_path / "checkpoints"
            checkpoint_path.mkdir(parents=True, exist_ok=True)
            self._rollback = RollbackController(checkpoint_path)
            
            # Create initial checkpoint
            initial_state = {
                "axioms": list(self._state.axioms.keys()),
                "canon": list(self._state.canon.keys()),
                "timestamp": datetime.utcnow().isoformat()
            }
            checkpoint_id = self._rollback.checkpoint(
                state=initial_state,
                description="Kernel initialization",
                created_by="kernel"
            )
            self._state.set_last_checkpoint(checkpoint_id)
            
            # Log successful initialization
            self._audit_log.log(
                event_type=AuditEventType.CHECKPOINT_CREATED,
                severity=AuditSeverity.INFO,
                actor="kernel",
                action="initialize",
                outcome="success",
                context={"checkpoint_id": checkpoint_id}
            )
            
            self._initialized = True
            return True
            
        except Exception as e:
            # Log initialization failure
            if self._audit_log:
                self._audit_log.log(
                    event_type=AuditEventType.SAFE_MODE_ENTERED,
                    severity=AuditSeverity.CRITICAL,
                    actor="kernel",
                    action="initialize",
                    outcome="failed",
                    context={"error": str(e)}
                )
            return False
    
    def validate_intent(self, intent: Intent) -> ValidationResult:
        """
        Validate an intent against governance rules.
        
        Args:
            intent: Intent to validate
            
        Returns:
            ValidationResult with status and explanation
        """
        if not self._initialized:
            raise RuntimeError("Kernel not initialized")
        
        result = self._intent_validator.validate(intent)
        
        # Log validation
        event_type = (
            AuditEventType.INTENT_VALIDATED 
            if result.status.value == "approved"
            else AuditEventType.INTENT_REJECTED
        )
        
        self._audit_log.log(
            event_type=event_type,
            severity=AuditSeverity.INFO,
            actor=intent.source,
            action=f"validate_intent:{intent.action_type}",
            target=intent.target,
            outcome=result.status.value,
            context={"intent_id": intent.id}
        )
        
        return result
    
    def resolve_conflicts(self, conflicts: list) -> list:
        """
        Resolve conflicts between objectives or constraints.
        
        Args:
            conflicts: List of Conflict objects
            
        Returns:
            List of Resolution objects
        """
        if not self._initialized:
            raise RuntimeError("Kernel not initialized")
        
        resolutions = self._conflict_resolver.resolve(conflicts)
        
        # Log each resolution
        for resolution in resolutions:
            self._audit_log.log(
                event_type=AuditEventType.CONFLICT_RESOLVED,
                severity=AuditSeverity.INFO,
                actor="kernel",
                action="resolve_conflict",
                target=resolution.conflict_id,
                outcome=resolution.method.value,
                context={"requires_escalation": resolution.requires_escalation}
            )
        
        return resolutions
    
    def create_checkpoint(self, description: str, actor: str) -> str:
        """
        Create a checkpoint of current kernel state.
        
        Args:
            description: Human-readable description
            actor: Who is creating the checkpoint
            
        Returns:
            Checkpoint ID
        """
        if not self._initialized:
            raise RuntimeError("Kernel not initialized")
        
        state = {
            "axioms": list(self._state.axioms.keys()),
            "canon": list(self._state.canon.keys()),
            "snapshot": self._state.get_snapshot().__dict__
        }
        
        checkpoint_id = self._rollback.checkpoint(state, description, actor)
        self._state.set_last_checkpoint(checkpoint_id)
        
        self._audit_log.log(
            event_type=AuditEventType.CHECKPOINT_CREATED,
            severity=AuditSeverity.INFO,
            actor=actor,
            action="create_checkpoint",
            outcome="success",
            context={"checkpoint_id": checkpoint_id, "description": description}
        )
        
        return checkpoint_id
    
    def rollback_to(self, checkpoint_id: str, actor: str) -> bool:
        """
        Rollback kernel state to a checkpoint.
        
        Args:
            checkpoint_id: ID of checkpoint to restore
            actor: Who is initiating the rollback
            
        Returns:
            True if rollback successful
        """
        if not self._initialized:
            raise RuntimeError("Kernel not initialized")
        
        result = self._rollback.rollback(checkpoint_id)
        
        self._audit_log.log(
            event_type=AuditEventType.ROLLBACK_EXECUTED,
            severity=AuditSeverity.WARNING,
            actor=actor,
            action="rollback",
            target=checkpoint_id,
            outcome=result.status.value,
            context={"changes_reverted": result.changes_reverted}
        )
        
        return result.status.value == "success"
    
    def shutdown(self, reason: str, actor: str) -> None:
        """
        Initiate kernel shutdown.
        
        Args:
            reason: Reason for shutdown
            actor: Who is initiating shutdown
        """
        if self._state:
            self._state.shutdown(reason)
        
        if self._audit_log:
            self._audit_log.log(
                event_type=AuditEventType.SHUTDOWN_INITIATED,
                severity=AuditSeverity.WARNING,
                actor=actor,
                action="shutdown",
                outcome="initiated",
                context={"reason": reason}
            )
    
    @property
    def status(self) -> KernelStatus:
        """Get current kernel status."""
        if not self._state:
            return KernelStatus.SHUTDOWN
        return self._state.status
    
    @property
    def is_initialized(self) -> bool:
        """Check if kernel is initialized."""
        return self._initialized


# Module-level initialization
def create_kernel(kernel_path: Path) -> ContinuumKernel:
    """
    Create and initialize a CONTINUUM kernel instance.
    
    Args:
        kernel_path: Path to kernel directory
        
    Returns:
        Initialized ContinuumKernel
    """
    kernel = ContinuumKernel(kernel_path)
    kernel.initialize()
    return kernel
