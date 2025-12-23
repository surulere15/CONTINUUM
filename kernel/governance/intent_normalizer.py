"""
Intent Normalizer

Convert raw intent expressions into canonical form.
Reject underspecified or ambiguous intents.

KERNEL MODULE - No imports from execution/agents/learning.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict, Any
import hashlib
import re

from .intent_schema import Intent, IntentSource, IntentStatus


class NormalizationError(Exception):
    """Raised when intent cannot be normalized."""
    pass


class AmbiguousIntentError(NormalizationError):
    """Raised when intent requires interpretation to normalize."""
    pass


class UnderspecifiedIntentError(NormalizationError):
    """Raised when intent lacks required information."""
    pass


@dataclass(frozen=True)
class NormalizationResult:
    """Result of normalization attempt."""
    success: bool
    intent: Optional[Intent]
    error: Optional[str] = None
    warnings: tuple = ()


class IntentNormalizer:
    """
    Normalizes raw intent expressions into canonical form.
    
    Responsibilities:
    - Remove ambiguity
    - Enforce explicit scope
    - Bind references to Canon entities
    - Reject underspecified intents
    
    Rule: If intent cannot be normalized without interpretation → REJECT
    """
    
    # Known scopes
    VALID_SCOPES = frozenset({
        "civilization",
        "system",
        "human",
        "operational",
        "experimental",
    })
    
    # Words that indicate ambiguity
    AMBIGUOUS_MARKERS = frozenset({
        "maybe",
        "perhaps",
        "possibly",
        "might",
        "could",
        "somehow",
        "probably",
        "approximately",
    })
    
    def __init__(self, canon_references: Optional[Dict[str, str]] = None):
        """
        Initialize normalizer.
        
        Args:
            canon_references: Map of reference IDs to Canon entities
        """
        self._canon_refs = canon_references or {}
    
    def normalize(
        self,
        raw_description: str,
        source: IntentSource,
        scope: Optional[str] = None,
        references: Optional[List[str]] = None,
        constraints: Optional[List[str]] = None,
    ) -> NormalizationResult:
        """
        Normalize a raw intent into canonical form.
        
        Args:
            raw_description: Raw intent description
            source: Origin of intent
            scope: Optional scope (will be inferred if missing)
            references: Canon references
            constraints: Explicit constraints
            
        Returns:
            NormalizationResult
        """
        try:
            # Step 1: Check for underspecification
            self._check_underspecified(raw_description)
            
            # Step 2: Check for ambiguity
            self._check_ambiguity(raw_description)
            
            # Step 3: Normalize scope
            normalized_scope = self._normalize_scope(scope, raw_description)
            
            # Step 4: Validate references
            validated_refs = self._validate_references(references or [])
            
            # Step 5: Normalize constraints
            normalized_constraints = self._normalize_constraints(constraints or [])
            
            # Step 6: Create normalized intent
            intent_id = self._generate_id(raw_description, source, normalized_scope)
            
            intent = Intent(
                intent_id=intent_id,
                source=source,
                description=self._clean_description(raw_description),
                scope=normalized_scope,
                references=tuple(validated_refs),
                constraints=tuple(normalized_constraints),
                created_at=datetime.utcnow(),
            )
            
            return NormalizationResult(
                success=True,
                intent=intent,
            )
            
        except NormalizationError as e:
            return NormalizationResult(
                success=False,
                intent=None,
                error=str(e),
            )
    
    def _check_underspecified(self, description: str) -> None:
        """Check for underspecified intent."""
        if not description or len(description.strip()) < 10:
            raise UnderspecifiedIntentError(
                "Intent description is too short. "
                "Intents must be explicitly specified."
            )
        
        # Check for placeholder language
        placeholders = ["TBD", "TODO", "...", "etc", "and so on"]
        for ph in placeholders:
            if ph.lower() in description.lower():
                raise UnderspecifiedIntentError(
                    f"Intent contains placeholder '{ph}'. "
                    f"Intents must be fully specified."
                )
    
    def _check_ambiguity(self, description: str) -> None:
        """Check for ambiguous language."""
        words = set(re.findall(r'\b\w+\b', description.lower()))
        
        for marker in self.AMBIGUOUS_MARKERS:
            if marker in words:
                raise AmbiguousIntentError(
                    f"Intent contains ambiguous language: '{marker}'. "
                    f"Normalization cannot proceed without interpretation."
                )
    
    def _normalize_scope(self, scope: Optional[str], description: str) -> str:
        """Normalize or infer scope."""
        if scope:
            scope_lower = scope.lower()
            if scope_lower not in self.VALID_SCOPES:
                raise NormalizationError(
                    f"Unknown scope: '{scope}'. "
                    f"Valid scopes: {self.VALID_SCOPES}"
                )
            return scope_lower
        
        # Cannot infer scope - must be explicit
        raise UnderspecifiedIntentError(
            "Intent scope must be explicitly specified. "
            "Cannot infer scope without interpretation."
        )
    
    def _validate_references(self, references: List[str]) -> List[str]:
        """Validate Canon references."""
        validated = []
        for ref in references:
            # Check if reference exists in Canon
            if ref in self._canon_refs:
                validated.append(ref)
            else:
                # Allow but warn about unbound references
                validated.append(f"unbound:{ref}")
        return validated
    
    def _normalize_constraints(self, constraints: List[str]) -> List[str]:
        """Normalize constraint expressions."""
        normalized = []
        for c in constraints:
            # Clean and standardize
            cleaned = c.strip().lower()
            if cleaned:
                normalized.append(cleaned)
        return normalized
    
    def _clean_description(self, description: str) -> str:
        """Clean and standardize description."""
        # Remove extra whitespace
        cleaned = " ".join(description.split())
        # Remove trailing punctuation variations
        cleaned = cleaned.rstrip(".,;:")
        return cleaned
    
    def _generate_id(self, description: str, source: IntentSource, scope: str) -> str:
        """Generate deterministic intent ID."""
        content = f"{description}|{source.value}|{scope}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
