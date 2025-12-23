"""
Phase A Rejection Tests

Proves the kernel rejects all execution, planning, and implicit objectives.
All rejection tests must pass before Phase B.

KERNEL TESTS - Phase A acceptance criteria.
"""

import pytest
from datetime import datetime, timezone


class TestExecutionRejection:
    """Verify kernel rejects all execution attempts."""
    
    def test_execution_request_forbidden(self):
        """Execution requests must be forbidden."""
        from kernel.interfaces.execution_auth import ExecutionAuthorizationInterface
        
        interface = ExecutionAuthorizationInterface()
        result = interface.request_execution({"action": "run_command"})
        
        assert "FORBIDDEN" in result.reason
    
    def test_authorize_execution_impossible(self):
        """Authorize execution method must not exist."""
        from kernel.interfaces.execution_auth import ExecutionAuthorizationInterface
        
        interface = ExecutionAuthorizationInterface()
        
        with pytest.raises(NotImplementedError):
            interface.authorize_execution()
    
    def test_direct_execute_impossible(self):
        """Direct execute method must not exist."""
        from kernel.interfaces.execution_auth import ExecutionAuthorizationInterface
        
        interface = ExecutionAuthorizationInterface()
        
        with pytest.raises(NotImplementedError):
            interface.execute()
    
    def test_axiom_rejects_execution(self):
        """Axiom enforcer rejects execution keywords."""
        from kernel.skeleton.axiom_enforcer import AxiomEnforcer
        
        enforcer = AxiomEnforcer()
        result = enforcer.check("execute this command")
        
        assert not result.allowed
        assert "AXIOM VIOLATION" in result.reason


class TestPlanningRejection:
    """Verify kernel rejects all planning attempts."""
    
    def test_planning_request_denied(self):
        """Planning requests must be denied."""
        from kernel.interfaces.planning_admission import PlanningAdmissionInterface
        
        interface = PlanningAdmissionInterface()
        result = interface.request_planning({"plan": "do something"})
        
        assert "DENIED" in result.reason
    
    def test_approve_planning_impossible(self):
        """Approve planning method must not exist."""
        from kernel.interfaces.planning_admission import PlanningAdmissionInterface
        
        interface = PlanningAdmissionInterface()
        
        with pytest.raises(NotImplementedError):
            interface.approve_planning()
    
    def test_axiom_rejects_planning(self):
        """Axiom enforcer rejects planning keywords."""
        from kernel.skeleton.axiom_enforcer import AxiomEnforcer
        
        enforcer = AxiomEnforcer()
        result = enforcer.check("plan the next steps")
        
        assert not result.allowed
        assert "AXIOM VIOLATION" in result.reason


class TestImplicitObjectiveRefusal:
    """Verify kernel refuses implicit objectives."""
    
    def test_objective_state_empty(self):
        """Objective state must be empty in Phase A."""
        from kernel.skeleton.registers import KernelRegisters
        
        registers = KernelRegisters()
        
        assert registers.objective_state.empty
        assert len(registers.objective_state.objectives) == 0
    
    def test_objective_modification_blocked(self):
        """Objective state cannot be modified."""
        from kernel.skeleton.registers import KernelRegisters, RegisterLockError
        
        registers = KernelRegisters()
        
        with pytest.raises(RegisterLockError):
            registers.modify_objective_state()
    
    def test_semantics_rejected(self):
        """Intent semantics are rejected."""
        from kernel.interfaces.intent_ingress import IntentIngressInterface
        
        interface = IntentIngressInterface()
        result = interface.ingest({"type": "objective", "content": "do X"})
        
        assert result.result.value == "semantics_rejected"


class TestAxiomDisableBlocked:
    """Verify axioms cannot be disabled."""
    
    def test_cannot_disable_axiom(self):
        """Axiom disable must raise."""
        from kernel.skeleton.axiom_enforcer import AxiomEnforcer, AxiomViolation
        
        enforcer = AxiomEnforcer()
        
        with pytest.raises(AxiomViolation):
            enforcer.disable_axiom()
    
    def test_cannot_add_exception(self):
        """Cannot add exception paths."""
        from kernel.skeleton.axiom_enforcer import AxiomEnforcer, AxiomViolation
        
        enforcer = AxiomEnforcer()
        
        with pytest.raises(AxiomViolation):
            enforcer.add_exception()
    
    def test_all_axioms_active(self):
        """All five axioms must be active."""
        from kernel.skeleton.axiom_enforcer import AxiomEnforcer, Axiom
        
        enforcer = AxiomEnforcer()
        
        assert len(enforcer.active_axioms) == 5
        assert Axiom.OBJECTIVE_SUPREMACY in enforcer.active_axioms
        assert Axiom.BOUNDED_AUTONOMY in enforcer.active_axioms


class TestAuditLogging:
    """Verify audit logging works correctly."""
    
    def test_refusals_logged(self):
        """All refusals must be logged."""
        from kernel.audit.event_log import AuditEventLog
        
        log = AuditEventLog()
        
        event = log.append(
            event_type="REJECTION",
            input_hash="abc123",
            decision="FORBIDDEN",
            axiom_reference="bounded_autonomy",
        )
        
        assert event.event_type == "REJECTION"
        assert log.event_count == 1
    
    def test_audit_chain_valid(self):
        """Audit chain must be valid."""
        from kernel.audit.event_log import AuditEventLog
        
        log = AuditEventLog()
        
        for i in range(5):
            log.append(
                event_type=f"EVENT_{i}",
                input_hash=f"hash_{i}",
                decision="LOGGED",
            )
        
        assert log.verify_chain()
