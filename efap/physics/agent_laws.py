"""
Agent Laws

5 execution laws - non-negotiable.

EFAP-C - Execution Fabric & Agent Physics.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Tuple
from enum import Enum


class LawViolation(Enum):
    """Types of law violations."""
    FREE_WORK = "law_1_free_work"
    UNDECLARED_EFFECT = "law_2_undeclared_effect"
    NONDETERMINISTIC = "law_3_nondeterministic"
    BOUNDED_AUTONOMY = "law_4_bounded_autonomy"
    ROUTING_FAILURE = "law_5_superfluid"


@dataclass(frozen=True)
class LawCheck:
    """Result of law enforcement check."""
    law_number: int
    law_name: str
    passed: bool
    violation: Optional[LawViolation]
    description: str


class Law1Violation(Exception):
    """Law 1: No Free Work."""
    pass


class Law2Violation(Exception):
    """Law 2: No Side Effects Without Declaration."""
    pass


class Law3Violation(Exception):
    """Law 3: Deterministic Execution."""
    pass


class Law4Violation(Exception):
    """Law 4: Bounded Autonomy."""
    pass


class Law5Violation(Exception):
    """Law 5: Superfluid Routing."""
    pass


class AgentLaws:
    """
    The 5 Execution Laws.
    
    These are non-negotiable.
    
    Law 1 — No Free Work: ∀W, ∃G: W ≺ G
    Law 2 — No Side Effects Without Declaration
    Law 3 — Deterministic Execution
    Law 4 — Bounded Autonomy
    Law 5 — Superfluid Routing
    """
    
    @staticmethod
    def check_law_1(work_id: str, goal_id: Optional[str]) -> LawCheck:
        """
        Law 1: No Free Work.
        
        ∀W, ∃G: W ≺ G
        No work exists without purpose.
        """
        if not goal_id:
            raise Law1Violation(
                f"Work '{work_id}' has no goal. "
                f"Law 1: ∀W, ∃G: W ≺ G"
            )
        
        return LawCheck(
            law_number=1,
            law_name="No Free Work",
            passed=True,
            violation=None,
            description="Work has valid goal",
        )
    
    @staticmethod
    def check_law_2(
        has_effect: bool,
        effect_declared: bool,
        reversibility_stated: bool,
    ) -> LawCheck:
        """
        Law 2: No Side Effects Without Declaration.
        
        If effect(W) ≠ ∅, then:
        - Effect must be declared
        - Reversibility must be stated
        """
        if has_effect and not effect_declared:
            raise Law2Violation(
                "Side effect not declared. "
                "Law 2: All effects must be declared."
            )
        
        if has_effect and not reversibility_stated:
            raise Law2Violation(
                "Reversibility not stated. "
                "Law 2: Reversibility must be declared."
            )
        
        return LawCheck(
            law_number=2,
            law_name="No Undeclared Effects",
            passed=True,
            violation=None,
            description="Effects properly declared",
        )
    
    @staticmethod
    def check_law_3(
        output_1: str,
        output_2: str,
    ) -> LawCheck:
        """
        Law 3: Deterministic Execution.
        
        Given same input/work/environment, result must be equivalent.
        Nondeterminism is treated as failure.
        """
        if output_1 != output_2:
            raise Law3Violation(
                "Nondeterministic output detected. "
                "Law 3: Execution must be deterministic."
            )
        
        return LawCheck(
            law_number=3,
            law_name="Deterministic Execution",
            passed=True,
            violation=None,
            description="Output is deterministic",
        )
    
    @staticmethod
    def check_law_4(
        agent_spawning: bool = False,
        goal_modification: bool = False,
        direct_memory_access: bool = False,
        kernel_override: bool = False,
    ) -> LawCheck:
        """
        Law 4: Bounded Autonomy.
        
        Agents cannot:
        - Spawn new agents
        - Modify goals
        - Access memory directly
        - Override Kernel decisions
        """
        violations = []
        
        if agent_spawning:
            violations.append("agent spawning")
        if goal_modification:
            violations.append("goal modification")
        if direct_memory_access:
            violations.append("direct memory access")
        if kernel_override:
            violations.append("kernel override")
        
        if violations:
            raise Law4Violation(
                f"Bounded autonomy violated: {violations}. "
                f"Law 4: Agents have strict limits."
            )
        
        return LawCheck(
            law_number=4,
            law_name="Bounded Autonomy",
            passed=True,
            violation=None,
            description="Agent within bounds",
        )
    
    @staticmethod
    def check_law_5(
        work_blocked: bool,
        system_blocked: bool,
    ) -> LawCheck:
        """
        Law 5: Superfluid Routing.
        
        Work units flow around failures.
        Blocked agent ≠ blocked system.
        """
        if work_blocked and system_blocked:
            raise Law5Violation(
                "System blocked due to agent failure. "
                "Law 5: Work must flow around failures."
            )
        
        return LawCheck(
            law_number=5,
            law_name="Superfluid Routing",
            passed=True,
            violation=None,
            description="Work flowing correctly",
        )
