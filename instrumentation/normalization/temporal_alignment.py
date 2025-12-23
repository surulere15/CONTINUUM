"""
Temporal Alignment

Aligns signal timestamps to UTC for comparability.
No rolling averages, no trend calculation, no forecasting.

INSTRUMENTATION MODULE - No imports from kernel/cognitive/execution/agents.
"""

from datetime import datetime, timezone, timedelta
from typing import Optional
import re


class TemporalAlignmentError(Exception):
    """Raised when timestamp cannot be aligned."""
    pass


class TemporalAligner:
    """
    Aligns timestamps to UTC.
    
    Rules:
    - All timestamps normalized to UTC
    - No rolling averages
    - No trend calculations
    - No time series aggregation
    - Pure timestamp conversion only
    """
    
    # Common timezone offsets
    TIMEZONE_OFFSETS = {
        "EST": timedelta(hours=-5),
        "EDT": timedelta(hours=-4),
        "CST": timedelta(hours=-6),
        "CDT": timedelta(hours=-5),
        "MST": timedelta(hours=-7),
        "MDT": timedelta(hours=-6),
        "PST": timedelta(hours=-8),
        "PDT": timedelta(hours=-7),
        "UTC": timedelta(hours=0),
        "GMT": timedelta(hours=0),
        "CET": timedelta(hours=1),
        "CEST": timedelta(hours=2),
        "JST": timedelta(hours=9),
    }
    
    def align(self, timestamp: datetime, source_tz: Optional[str] = None) -> datetime:
        """
        Align timestamp to UTC.
        
        Args:
            timestamp: Original timestamp
            source_tz: Source timezone name (if not in timestamp)
            
        Returns:
            Timestamp in UTC
        """
        # If already has timezone info
        if timestamp.tzinfo is not None:
            return timestamp.astimezone(timezone.utc)
        
        # Try to parse source timezone
        if source_tz:
            source_tz_upper = source_tz.upper()
            if source_tz_upper in self.TIMEZONE_OFFSETS:
                offset = self.TIMEZONE_OFFSETS[source_tz_upper]
                tz = timezone(offset)
                localized = timestamp.replace(tzinfo=tz)
                return localized.astimezone(timezone.utc)
        
        # Assume UTC if no timezone info
        return timestamp.replace(tzinfo=timezone.utc)
    
    def align_iso(self, iso_string: str) -> datetime:
        """
        Align ISO format timestamp string to UTC.
        
        Handles various ISO 8601 formats.
        """
        # Handle Z suffix
        if iso_string.endswith('Z'):
            iso_string = iso_string[:-1] + '+00:00'
        
        try:
            dt = datetime.fromisoformat(iso_string)
            return self.align(dt)
        except ValueError as e:
            raise TemporalAlignmentError(f"Cannot parse timestamp: {iso_string}") from e
    
    def is_utc(self, timestamp: datetime) -> bool:
        """Check if timestamp is in UTC."""
        if timestamp.tzinfo is None:
            return False
        return timestamp.tzinfo == timezone.utc or timestamp.utcoffset() == timedelta(0)
    
    def to_epoch(self, timestamp: datetime) -> float:
        """Convert timestamp to Unix epoch (seconds since 1970-01-01 UTC)."""
        utc_ts = self.align(timestamp)
        return utc_ts.timestamp()
    
    def from_epoch(self, epoch: float) -> datetime:
        """Convert Unix epoch to UTC datetime."""
        return datetime.fromtimestamp(epoch, tz=timezone.utc)
