# Logging
"""Structured logging for CONTINUUM."""

import json
from datetime import datetime


class Logger:
    """Structured logger."""
    
    def __init__(self, component: str):
        self._component = component
    
    def info(self, message: str, **kwargs) -> None:
        self._log("INFO", message, kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        self._log("WARNING", message, kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        self._log("ERROR", message, kwargs)
    
    def _log(self, level: str, message: str, extra: dict) -> None:
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "component": self._component,
            "message": message,
            **extra
        }
        print(json.dumps(entry))
