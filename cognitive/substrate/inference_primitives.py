"""
Inference Primitives

Smallest units of thought. Pure, bounded, explainable.

COGNITIVE MODULE - No imports from execution/agents/kernel/governance.
"""

from dataclasses import dataclass
from typing import Any, List, Optional, Tuple
from abc import ABC, abstractmethod


@dataclass(frozen=True)
class PrimitiveResult:
    """
    Result from an inference primitive.
    
    All results include explanation.
    """
    value: Any
    explanation: str
    steps: tuple
    bounded: bool  # Was execution bounded?


class InferencePrimitive(ABC):
    """
    Base class for inference primitives.
    
    Each primitive:
    - Is pure (no side effects)
    - Has bounded runtime
    - Produces explainable output
    """
    
    @abstractmethod
    def apply(self, *args, **kwargs) -> PrimitiveResult:
        """Apply the primitive. Must be pure."""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the primitive."""
        pass


class Deduction(InferencePrimitive):
    """
    Deductive reasoning: If A then B, A, therefore B.
    """
    
    @property
    def name(self) -> str:
        return "deduction"
    
    def apply(
        self,
        premises: List[str],
        rules: List[Tuple[str, str]],  # (antecedent, consequent)
    ) -> PrimitiveResult:
        """
        Apply deductive inference.
        
        Args:
            premises: Known facts
            rules: Implication rules (if A then B)
            
        Returns:
            PrimitiveResult with derived conclusions
        """
        conclusions = set(premises)
        steps = [f"Starting with premises: {premises}"]
        
        changed = True
        iterations = 0
        max_iterations = 100  # Bounded
        
        while changed and iterations < max_iterations:
            changed = False
            iterations += 1
            
            for antecedent, consequent in rules:
                if antecedent in conclusions and consequent not in conclusions:
                    conclusions.add(consequent)
                    steps.append(f"Applied rule: {antecedent} → {consequent}")
                    changed = True
        
        return PrimitiveResult(
            value=list(conclusions),
            explanation=f"Derived {len(conclusions) - len(premises)} new conclusions",
            steps=tuple(steps),
            bounded=iterations < max_iterations,
        )


class Abstraction(InferencePrimitive):
    """
    Abstraction: Extract general pattern from specifics.
    """
    
    @property
    def name(self) -> str:
        return "abstraction"
    
    def apply(
        self,
        instances: List[Any],
        abstraction_level: int = 1,
    ) -> PrimitiveResult:
        """
        Abstract from instances.
        
        Args:
            instances: Specific instances
            abstraction_level: How abstract to go (1-3)
            
        Returns:
            PrimitiveResult with abstraction
        """
        steps = [f"Examining {len(instances)} instances"]
        
        # Simple type-based abstraction
        types = set(type(i).__name__ for i in instances)
        steps.append(f"Found types: {types}")
        
        if len(types) == 1:
            abstract = f"Collection of {list(types)[0]}"
        else:
            abstract = f"Mixed collection: {types}"
        
        steps.append(f"Abstracted to: {abstract}")
        
        return PrimitiveResult(
            value=abstract,
            explanation=f"Abstracted {len(instances)} instances to '{abstract}'",
            steps=tuple(steps),
            bounded=True,
        )


class Comparison(InferencePrimitive):
    """
    Comparison: Find similarities and differences.
    """
    
    @property
    def name(self) -> str:
        return "comparison"
    
    def apply(
        self,
        item_a: Any,
        item_b: Any,
    ) -> PrimitiveResult:
        """
        Compare two items.
        
        Args:
            item_a: First item
            item_b: Second item
            
        Returns:
            PrimitiveResult with comparison
        """
        steps = ["Comparing items"]
        
        similarities = []
        differences = []
        
        # Type comparison
        if type(item_a) == type(item_b):
            similarities.append(f"same type: {type(item_a).__name__}")
        else:
            differences.append(f"different types: {type(item_a).__name__} vs {type(item_b).__name__}")
        
        # Value comparison
        if item_a == item_b:
            similarities.append("equal values")
        else:
            differences.append("different values")
        
        steps.append(f"Found {len(similarities)} similarities")
        steps.append(f"Found {len(differences)} differences")
        
        return PrimitiveResult(
            value={"similarities": similarities, "differences": differences},
            explanation=f"Comparison: {len(similarities)} similar, {len(differences)} different",
            steps=tuple(steps),
            bounded=True,
        )


class ConsistencyCheck(InferencePrimitive):
    """
    Consistency: Check for logical contradictions.
    """
    
    @property
    def name(self) -> str:
        return "consistency_check"
    
    def apply(
        self,
        statements: List[str],
        negations: Optional[dict] = None,
    ) -> PrimitiveResult:
        """
        Check consistency of statements.
        
        Args:
            statements: List of statements
            negations: Map of statement to its negation
            
        Returns:
            PrimitiveResult with consistency status
        """
        steps = [f"Checking consistency of {len(statements)} statements"]
        negations = negations or {}
        
        contradictions = []
        statement_set = set(statements)
        
        for stmt in statements:
            neg = negations.get(stmt)
            if neg and neg in statement_set:
                contradictions.append((stmt, neg))
                steps.append(f"Contradiction: '{stmt}' vs '{neg}'")
        
        is_consistent = len(contradictions) == 0
        steps.append(f"Consistent: {is_consistent}")
        
        return PrimitiveResult(
            value={"consistent": is_consistent, "contradictions": contradictions},
            explanation=f"{'Consistent' if is_consistent else 'Inconsistent'}: {len(contradictions)} contradictions",
            steps=tuple(steps),
            bounded=True,
        )


class Decomposition(InferencePrimitive):
    """
    Decomposition: Break complex into simpler parts.
    """
    
    @property
    def name(self) -> str:
        return "decomposition"
    
    def apply(
        self,
        complex_item: Any,
        max_depth: int = 3,
    ) -> PrimitiveResult:
        """
        Decompose complex item.
        
        Args:
            complex_item: Item to decompose
            max_depth: Maximum decomposition depth
            
        Returns:
            PrimitiveResult with decomposition
        """
        steps = ["Beginning decomposition"]
        
        def decompose(item, depth):
            if depth >= max_depth:
                return item
            
            if isinstance(item, dict):
                return {k: decompose(v, depth + 1) for k, v in item.items()}
            elif isinstance(item, (list, tuple)):
                return [decompose(i, depth + 1) for i in item]
            else:
                return item
        
        result = decompose(complex_item, 0)
        steps.append(f"Decomposed to depth {max_depth}")
        
        return PrimitiveResult(
            value=result,
            explanation=f"Decomposed with max depth {max_depth}",
            steps=tuple(steps),
            bounded=True,
        )


# Registry of available primitives
PRIMITIVES: dict = {
    "deduction": Deduction(),
    "abstraction": Abstraction(),
    "comparison": Comparison(),
    "consistency": ConsistencyCheck(),
    "decomposition": Decomposition(),
}


def get_primitive(name: str) -> Optional[InferencePrimitive]:
    """Get a primitive by name."""
    return PRIMITIVES.get(name)
