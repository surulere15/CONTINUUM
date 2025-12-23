# Tracing
"""Distributed tracing for CONTINUUM."""


class Tracer:
    """Distributed tracing."""
    
    def start_span(self, name: str, parent_id: str = None) -> str:
        import uuid
        return str(uuid.uuid4())
    
    def end_span(self, span_id: str) -> None:
        pass
    
    def add_event(self, span_id: str, event: str) -> None:
        pass
