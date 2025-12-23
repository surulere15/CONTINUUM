"""
Determinism Guarantees

Given identical inputs, the kernel produces identical outputs bit-for-bit.
No randomness. No heuristics. No probabilistic logic.

KERNEL SKELETON - Phase A. Zero autonomy.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, List, Tuple
import hashlib


class DeterminismViolation(Exception):
    """Raised when determinism is violated."""
    pass


@dataclass(frozen=True)
class DeterminismProof:
    """
    Proof that a computation was deterministic.
    
    Contains input and output hashes for verification.
    """
    input_hash: str
    output_hash: str
    computation_id: str
    verified_at: datetime
    reproducible: bool


class DeterminismGuarantee:
    """
    Ensures kernel operations are deterministic.
    
    Requirements:
    - No randomness
    - No heuristics
    - No probabilistic logic
    - Identical inputs → identical outputs (bit-for-bit)
    
    This is mandatory for Phase A completion.
    """
    
    def __init__(self):
        """Initialize determinism checker."""
        self._computation_log: List[DeterminismProof] = []
    
    def verify_determinism(
        self,
        computation_fn,
        input_data: Any,
        num_runs: int = 3,
    ) -> DeterminismProof:
        """
        Verify a computation is deterministic.
        
        Runs the computation multiple times and verifies
        identical outputs.
        
        Args:
            computation_fn: Function to verify
            input_data: Input to the function
            num_runs: Number of verification runs
            
        Returns:
            DeterminismProof
            
        Raises:
            DeterminismViolation: If outputs differ
        """
        input_hash = self._hash(input_data)
        outputs = []
        
        for _ in range(num_runs):
            result = computation_fn(input_data)
            output_hash = self._hash(result)
            outputs.append(output_hash)
        
        # Check all outputs are identical
        if len(set(outputs)) != 1:
            raise DeterminismViolation(
                f"Non-deterministic computation detected. "
                f"Outputs: {outputs}"
            )
        
        computation_id = hashlib.sha256(
            f"{input_hash}|{outputs[0]}".encode()
        ).hexdigest()[:16]
        
        proof = DeterminismProof(
            input_hash=input_hash,
            output_hash=outputs[0],
            computation_id=computation_id,
            verified_at=datetime.utcnow(),
            reproducible=True,
        )
        
        self._computation_log.append(proof)
        return proof
    
    def check_no_randomness(self, code_module) -> bool:
        """
        Check that a module uses no randomness.
        
        Inspects for random imports and calls.
        """
        import inspect
        source = inspect.getsource(code_module)
        
        random_patterns = [
            "import random",
            "from random",
            "random.",
            "np.random",
            "torch.rand",
            "uuid4()",
            "secrets.",
        ]
        
        for pattern in random_patterns:
            if pattern in source:
                return False
        
        return True
    
    def check_no_heuristics(self, code_module) -> bool:
        """
        Check that a module uses no heuristics.
        
        Looks for heuristic indicators.
        """
        import inspect
        source = inspect.getsource(code_module)
        
        heuristic_patterns = [
            "heuristic",
            "approximate",
            "best_effort",
            "fuzzy",
            "probabilistic",
        ]
        
        source_lower = source.lower()
        for pattern in heuristic_patterns:
            if pattern in source_lower:
                return False
        
        return True
    
    def _hash(self, data: Any) -> str:
        """Compute deterministic hash of data."""
        return hashlib.sha256(str(data).encode()).hexdigest()
    
    def get_proofs(self) -> List[DeterminismProof]:
        """Get all determinism proofs."""
        return list(self._computation_log)


def assert_deterministic(fn):
    """
    Decorator to assert a function is deterministic.
    
    Wraps function and verifies consistent outputs.
    """
    _cache = {}
    
    def wrapper(*args, **kwargs):
        # Create cache key from args
        key = hashlib.sha256(str((args, kwargs)).encode()).hexdigest()
        
        result = fn(*args, **kwargs)
        result_hash = hashlib.sha256(str(result).encode()).hexdigest()
        
        if key in _cache:
            if _cache[key] != result_hash:
                raise DeterminismViolation(
                    f"Function {fn.__name__} produced different output for same input"
                )
        else:
            _cache[key] = result_hash
        
        return result
    
    return wrapper
