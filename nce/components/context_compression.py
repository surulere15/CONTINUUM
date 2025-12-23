"""
Context Compression Engine (CCE)

Prevents cognitive overload and drift via salience scoring and temporal decay.

NCE COMPONENT - Neural Continuum Engine.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Tuple
import math


@dataclass(frozen=True)
class CompressedContext:
    """
    Compressed context field.
    
    C'_t = compress(C_t, α, β)
    
    Where:
    - α = relevance weight
    - β = recency weight
    """
    context_id: str
    entries: Tuple[Tuple[str, float], ...]  # (content, score)
    original_size: int
    compressed_size: int
    alpha: float
    beta: float
    compressed_at: datetime


class ContextCompressionEngine:
    """
    Context Compression Engine (CCE).
    
    Purpose: Prevent cognitive overload and drift.
    
    Mechanism:
    - Salience scoring
    - Temporal decay
    - Intent relevance weighting
    
    C'_t = compress(C_t, α, β)
    """
    
    DEFAULT_ALPHA = 0.6  # Relevance weight
    DEFAULT_BETA = 0.4   # Recency weight
    
    def __init__(
        self,
        alpha: float = DEFAULT_ALPHA,
        beta: float = DEFAULT_BETA,
    ):
        """
        Initialize compression engine.
        
        Args:
            alpha: Relevance weight
            beta: Recency weight
        """
        self._alpha = alpha
        self._beta = beta
        self._compressions: List[CompressedContext] = []
    
    def compress(
        self,
        entries: List[Tuple[str, datetime]],
        intent: str,
        target_size: int,
    ) -> CompressedContext:
        """
        Compress context entries.
        
        Args:
            entries: List of (content, timestamp)
            intent: Current intent for relevance
            target_size: Target compressed size
            
        Returns:
            CompressedContext
        """
        now = datetime.utcnow()
        scored = []
        
        for content, timestamp in entries:
            # Calculate relevance score (simplified)
            relevance = self._calculate_relevance(content, intent)
            
            # Calculate recency score
            age = (now - timestamp).total_seconds()
            recency = math.exp(-age / 3600)  # Decay over hours
            
            # Combined score
            score = self._alpha * relevance + self._beta * recency
            scored.append((content, score))
        
        # Sort by score descending
        scored.sort(key=lambda x: x[1], reverse=True)
        
        # Select top entries up to target size
        selected = []
        current_size = 0
        for content, score in scored:
            if current_size + len(content) > target_size:
                break
            selected.append((content, score))
            current_size += len(content)
        
        original_size = sum(len(c) for c, _ in entries)
        
        compressed = CompressedContext(
            context_id=f"compressed_{len(self._compressions)}",
            entries=tuple(selected),
            original_size=original_size,
            compressed_size=current_size,
            alpha=self._alpha,
            beta=self._beta,
            compressed_at=now,
        )
        
        self._compressions.append(compressed)
        return compressed
    
    def _calculate_relevance(self, content: str, intent: str) -> float:
        """Calculate relevance to intent (simplified)."""
        # Simplified: check for word overlap
        content_words = set(content.lower().split())
        intent_words = set(intent.lower().split())
        
        overlap = len(content_words & intent_words)
        total = len(intent_words) or 1
        
        return min(1.0, overlap / total)
    
    @property
    def alpha(self) -> float:
        """Relevance weight."""
        return self._alpha
    
    @property
    def beta(self) -> float:
        """Recency weight."""
        return self._beta
    
    @property
    def compression_count(self) -> int:
        """Total compressions performed."""
        return len(self._compressions)
