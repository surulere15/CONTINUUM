"""
Intent Ingress Interface

Accepts structured input, parses syntax only, rejects semantics.
Purpose: prove the Kernel can refuse intent safely.

KERNEL INTERFACE - Stubbed, Non-Functional.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum
import hashlib
import json


class IngressResult(Enum):
    """Result of ingress attempt."""
    SYNTAX_VALID = "syntax_valid"
    SYNTAX_INVALID = "syntax_invalid"
    SEMANTICS_REJECTED = "semantics_rejected"


@dataclass(frozen=True)
class IngressAttempt:
    """
    Record of an ingress attempt.
    
    Syntax is parsed, semantics are rejected.
    """
    attempt_id: str
    result: IngressResult
    input_hash: str
    reason: str
    timestamp: datetime


class IntentIngressInterface:
    """
    Intent ingress interface for the kernel.
    
    Capabilities:
    - Accepts structured input
    - Parses syntax only
    - Rejects semantics
    
    Purpose: prove the Kernel can refuse intent safely.
    
    This interface exists but does nothing except validate and reject.
    """
    
    REQUIRED_FIELDS = ("type", "content")
    
    def __init__(self):
        """Initialize ingress interface."""
        self._attempt_log = []
    
    def ingest(self, input_data: Dict[str, Any]) -> IngressAttempt:
        """
        Attempt to ingest input.
        
        Parses syntax, always rejects semantics.
        
        Args:
            input_data: Structured input
            
        Returns:
            IngressAttempt record
        """
        input_hash = hashlib.sha256(
            json.dumps(input_data, sort_keys=True).encode()
        ).hexdigest()
        
        attempt_id = hashlib.sha256(
            f"{len(self._attempt_log)}|{input_hash}".encode()
        ).hexdigest()[:16]
        
        # Step 1: Validate syntax
        syntax_result = self._validate_syntax(input_data)
        
        if syntax_result != IngressResult.SYNTAX_VALID:
            attempt = IngressAttempt(
                attempt_id=attempt_id,
                result=syntax_result,
                input_hash=input_hash,
                reason="Syntax validation failed",
                timestamp=datetime.utcnow(),
            )
            self._attempt_log.append(attempt)
            return attempt
        
        # Step 2: Reject semantics (always)
        attempt = IngressAttempt(
            attempt_id=attempt_id,
            result=IngressResult.SEMANTICS_REJECTED,
            input_hash=input_hash,
            reason="Semantics rejected: Phase A does not process intent semantics",
            timestamp=datetime.utcnow(),
        )
        self._attempt_log.append(attempt)
        return attempt
    
    def _validate_syntax(self, input_data: Dict[str, Any]) -> IngressResult:
        """Validate input syntax only."""
        if not isinstance(input_data, dict):
            return IngressResult.SYNTAX_INVALID
        
        for field in self.REQUIRED_FIELDS:
            if field not in input_data:
                return IngressResult.SYNTAX_INVALID
        
        return IngressResult.SYNTAX_VALID
    
    def process_semantics(self, *args, **kwargs) -> None:
        """
        FORBIDDEN: Process semantics.
        
        This interface rejects all semantics.
        """
        raise NotImplementedError(
            "Semantic processing is forbidden in Phase A. "
            "This interface validates syntax only."
        )
    
    def get_attempt_log(self):
        """Get log of all attempts."""
        return list(self._attempt_log)
