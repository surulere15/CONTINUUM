"""
Reasoning Router

Routes tasks to appropriate reasoning primitives.
Static, rule-based routing. No adaptive learning.

COGNITIVE MODULE - No imports from execution/agents/kernel/governance.
"""

from dataclasses import dataclass
from typing import Dict, Optional, List, Callable
from enum import Enum


class ReasoningType(Enum):
    """Types of reasoning primitives."""
    DEDUCTION = "deduction"
    INDUCTION = "induction"
    ABDUCTION = "abduction"
    ANALOGY = "analogy"
    COMPARISON = "comparison"
    CONSISTENCY = "consistency"
    DECOMPOSITION = "decomposition"
    ABSTRACTION = "abstraction"


@dataclass(frozen=True)
class RoutingRule:
    """
    Static routing rule.
    
    Rules are defined at configuration time, not runtime.
    No adaptive routing based on performance.
    """
    pattern: str
    target_type: ReasoningType
    priority: int
    description: str


@dataclass(frozen=True)
class RoutingDecision:
    """Result of routing decision."""
    reasoning_type: ReasoningType
    rule_applied: str
    confidence: float


class AdaptiveRoutingError(Exception):
    """Raised when adaptive routing is attempted."""
    pass


class ReasoningRouter:
    """
    Routes reasoning tasks to appropriate primitives.
    
    Properties:
    - Static, rule-based routing
    - No model selection based on performance
    - No adaptive routing
    - No learning from outcomes
    
    Routing decisions are deterministic given the same input.
    """
    
    # Default routing rules (static)
    DEFAULT_RULES: List[RoutingRule] = [
        RoutingRule("logic:*", ReasoningType.DEDUCTION, 1, "Logical queries use deduction"),
        RoutingRule("pattern:*", ReasoningType.INDUCTION, 2, "Pattern queries use induction"),
        RoutingRule("explain:*", ReasoningType.ABDUCTION, 3, "Explanation queries use abduction"),
        RoutingRule("compare:*", ReasoningType.COMPARISON, 4, "Comparison queries"),
        RoutingRule("check:*", ReasoningType.CONSISTENCY, 5, "Consistency checks"),
        RoutingRule("decompose:*", ReasoningType.DECOMPOSITION, 6, "Decomposition tasks"),
        RoutingRule("abstract:*", ReasoningType.ABSTRACTION, 7, "Abstraction tasks"),
        RoutingRule("*", ReasoningType.DEDUCTION, 100, "Default to deduction"),
    ]
    
    def __init__(self, rules: Optional[List[RoutingRule]] = None):
        """
        Initialize router with static rules.
        
        Args:
            rules: Custom routing rules, or use defaults
        """
        self._rules = sorted(
            rules or self.DEFAULT_RULES,
            key=lambda r: r.priority
        )
        self._routing_history: List[RoutingDecision] = []
    
    def route(self, task_descriptor: str) -> RoutingDecision:
        """
        Route a task to a reasoning type.
        
        Routing is purely pattern-based, no performance consideration.
        
        Args:
            task_descriptor: Description of the reasoning task
            
        Returns:
            RoutingDecision
        """
        for rule in self._rules:
            if self._matches(task_descriptor, rule.pattern):
                decision = RoutingDecision(
                    reasoning_type=rule.target_type,
                    rule_applied=rule.description,
                    confidence=1.0,  # Static rules have full confidence
                )
                self._routing_history.append(decision)
                return decision
        
        # Should never reach here if rules include catch-all
        return RoutingDecision(
            reasoning_type=ReasoningType.DEDUCTION,
            rule_applied="fallback",
            confidence=0.5,
        )
    
    def _matches(self, descriptor: str, pattern: str) -> bool:
        """Check if descriptor matches pattern."""
        if pattern == "*":
            return True
        
        if pattern.endswith("*"):
            prefix = pattern[:-1]
            return descriptor.lower().startswith(prefix.lower())
        
        return descriptor.lower() == pattern.lower()
    
    def update_based_on_performance(self, *args, **kwargs) -> None:
        """
        FORBIDDEN: Adaptive routing based on performance.
        
        This method exists only to explicitly prevent this operation.
        """
        raise AdaptiveRoutingError(
            "Adaptive routing is forbidden. "
            "Routing rules are static and defined at configuration time. "
            "No learning from outcomes is permitted."
        )
    
    def add_dynamic_rule(self, *args, **kwargs) -> None:
        """
        FORBIDDEN: Dynamic rule addition.
        
        Rules must be defined at configuration time.
        """
        raise AdaptiveRoutingError(
            "Dynamic rule addition is forbidden. "
            "All routing rules must be static."
        )
    
    def get_rules(self) -> List[RoutingRule]:
        """Get all routing rules (read-only)."""
        return list(self._rules)
    
    def get_history(self) -> List[RoutingDecision]:
        """Get routing history (read-only, for debugging)."""
        return list(self._routing_history)
