"""
Intent Translation Pipeline

5-stage normalization from human input to executable intent.
Canon prevails over human input.

GOVERNANCE - Phase I. Shared steering without control abdication.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Tuple
from enum import Enum
import hashlib


class PipelineStage(Enum):
    """Stages in the intent pipeline."""
    SEMANTIC_PARSING = "semantic_parsing"
    INTENT_NORMALIZATION = "intent_normalization"
    CANON_COMPATIBILITY = "canon_compatibility"
    CONSTRAINT_INJECTION = "constraint_injection"
    GRAPH_CONSTRUCTION = "graph_construction"


class PipelineResult(Enum):
    """Result of pipeline processing."""
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    PENDING_REVIEW = "pending_review"


@dataclass(frozen=True)
class PipelineInput:
    """Raw human input."""
    input_id: str
    raw_text: str
    issuer_id: str
    timestamp: datetime


@dataclass(frozen=True)
class ParsedIntent:
    """Semantically parsed intent."""
    intent_id: str
    action: str
    target: str
    constraints: Tuple[str, ...]
    confidence: float


@dataclass(frozen=True)
class NormalizedIntent:
    """Normalized, canonical intent."""
    intent_id: str
    canonical_form: str
    parameters: Tuple[Tuple[str, str], ...]
    priority: int


@dataclass(frozen=True)
class CompatibilityCheck:
    """Result of Canon compatibility check."""
    compatible: bool
    violations: Tuple[str, ...]
    warnings: Tuple[str, ...]


@dataclass(frozen=True)
class ExecutableIntent:
    """Final executable intent graph node."""
    intent_id: str
    action: str
    target: str
    constraints: Tuple[str, ...]
    canon_aligned: bool
    execution_ready: bool


@dataclass(frozen=True)
class PipelineReport:
    """Report of pipeline processing."""
    input_id: str
    result: PipelineResult
    stages_passed: Tuple[PipelineStage, ...]
    rejection_reason: Optional[str]
    executable: Optional[ExecutableIntent]
    processed_at: datetime


class CanonIncompatibleError(Exception):
    """Raised when input is Canon-incompatible."""
    pass


class IntentPipeline:
    """
    5-stage intent translation pipeline.
    
    Stages:
    1. Semantic Parsing
    2. Intent Normalization
    3. Objective Canon Compatibility Check
    4. Constraint Injection
    5. Executable Intent Graph
    
    If incompatibility detected:
    - Execution denied
    - Conflict reported
    - Canon prevails
    """
    
    # Patterns that violate Canon
    CANON_VIOLATIONS = [
        "modify objective",
        "change purpose",
        "override canon",
        "ignore constraints",
        "grant autonomy",
        "remove safeguard",
    ]
    
    def __init__(self):
        """Initialize pipeline."""
        self._processed_count = 0
        self._rejection_count = 0
    
    def process(self, human_input: PipelineInput) -> PipelineReport:
        """
        Process human input through the pipeline.
        
        Args:
            human_input: Raw human input
            
        Returns:
            PipelineReport
        """
        stages_passed = []
        
        try:
            # Stage 1: Semantic Parsing
            parsed = self._semantic_parse(human_input)
            stages_passed.append(PipelineStage.SEMANTIC_PARSING)
            
            # Stage 2: Intent Normalization
            normalized = self._normalize_intent(parsed)
            stages_passed.append(PipelineStage.INTENT_NORMALIZATION)
            
            # Stage 3: Canon Compatibility Check
            compatibility = self._check_canon_compatibility(normalized)
            if not compatibility.compatible:
                raise CanonIncompatibleError(
                    f"Canon violations: {compatibility.violations}"
                )
            stages_passed.append(PipelineStage.CANON_COMPATIBILITY)
            
            # Stage 4: Constraint Injection
            constrained = self._inject_constraints(normalized)
            stages_passed.append(PipelineStage.CONSTRAINT_INJECTION)
            
            # Stage 5: Graph Construction
            executable = self._construct_executable(constrained)
            stages_passed.append(PipelineStage.GRAPH_CONSTRUCTION)
            
            self._processed_count += 1
            
            return PipelineReport(
                input_id=human_input.input_id,
                result=PipelineResult.ACCEPTED,
                stages_passed=tuple(stages_passed),
                rejection_reason=None,
                executable=executable,
                processed_at=datetime.utcnow(),
            )
            
        except CanonIncompatibleError as e:
            self._rejection_count += 1
            
            return PipelineReport(
                input_id=human_input.input_id,
                result=PipelineResult.REJECTED,
                stages_passed=tuple(stages_passed),
                rejection_reason=str(e),
                executable=None,
                processed_at=datetime.utcnow(),
            )
    
    def _semantic_parse(self, input: PipelineInput) -> ParsedIntent:
        """Stage 1: Parse semantics."""
        # Simplified parsing
        words = input.raw_text.lower().split()
        action = words[0] if words else "unknown"
        target = words[1] if len(words) > 1 else "unknown"
        
        intent_id = hashlib.sha256(
            f"{input.input_id}:{input.raw_text}".encode()
        ).hexdigest()[:16]
        
        return ParsedIntent(
            intent_id=intent_id,
            action=action,
            target=target,
            constraints=(),
            confidence=0.8,
        )
    
    def _normalize_intent(self, parsed: ParsedIntent) -> NormalizedIntent:
        """Stage 2: Normalize to canonical form."""
        return NormalizedIntent(
            intent_id=parsed.intent_id,
            canonical_form=f"{parsed.action}:{parsed.target}",
            parameters=(),
            priority=5,
        )
    
    def _check_canon_compatibility(
        self,
        normalized: NormalizedIntent,
    ) -> CompatibilityCheck:
        """Stage 3: Check Canon compatibility."""
        violations = []
        
        canonical_lower = normalized.canonical_form.lower()
        
        for pattern in self.CANON_VIOLATIONS:
            if pattern in canonical_lower:
                violations.append(f"Violates Canon: '{pattern}'")
        
        return CompatibilityCheck(
            compatible=len(violations) == 0,
            violations=tuple(violations),
            warnings=(),
        )
    
    def _inject_constraints(
        self,
        normalized: NormalizedIntent,
    ) -> NormalizedIntent:
        """Stage 4: Inject governance constraints."""
        # Add standard constraints
        constraints = (
            "requires_audit",
            "reversible_only",
            "canon_supremacy",
        )
        
        return NormalizedIntent(
            intent_id=normalized.intent_id,
            canonical_form=normalized.canonical_form,
            parameters=normalized.parameters + (("constraints", str(constraints)),),
            priority=normalized.priority,
        )
    
    def _construct_executable(
        self,
        normalized: NormalizedIntent,
    ) -> ExecutableIntent:
        """Stage 5: Construct executable intent."""
        parts = normalized.canonical_form.split(":")
        action = parts[0] if parts else "unknown"
        target = parts[1] if len(parts) > 1 else "unknown"
        
        return ExecutableIntent(
            intent_id=normalized.intent_id,
            action=action,
            target=target,
            constraints=("requires_audit", "reversible_only", "canon_supremacy"),
            canon_aligned=True,
            execution_ready=True,
        )
    
    def bypass_canon_check(self, *args, **kwargs) -> None:
        """FORBIDDEN: Bypass Canon compatibility."""
        raise CanonIncompatibleError(
            "Canon compatibility check cannot be bypassed. "
            "Canon prevails over human input."
        )
    
    @property
    def processed_count(self) -> int:
        """Total inputs processed."""
        return self._processed_count
    
    @property
    def rejection_count(self) -> int:
        """Total inputs rejected."""
        return self._rejection_count
