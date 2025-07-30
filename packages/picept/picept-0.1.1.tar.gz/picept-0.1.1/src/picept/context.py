"""Context management for Picept tracing"""

import dataclasses
from typing import Optional
from contextvars import ContextVar
from opentelemetry import trace

@dataclasses.dataclass
class PiceptScope:
    """Stores Picept-specific context attributes"""
    project_id: Optional[str] = None
    experiment_id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    config_id: Optional[str] = None
    context_id: Optional[str] = None
    
    def as_attributes(self) -> dict[str, str]:
        """Convert to OpenTelemetry attributes"""
        attrs = {}
        if self.project_id:
            attrs["picept.project_id"] = self.project_id
        if self.experiment_id:
            attrs["picept.experiment_id"] = self.experiment_id
        if self.user_id:
            attrs["picept.user_id"] = self.user_id
        if self.session_id:
            attrs["picept.session_id"] = self.session_id
        if self.config_id:
            attrs["picept.config_id"] = self.config_id
        if self.context_id:
            attrs["picept.context_id"] = self.context_id
        return attrs

# Global context storage
_PICEPT_CONTEXT: ContextVar[Optional[PiceptScope]] = ContextVar('picept_context', default=None)

def set_context(scope: PiceptScope) -> None:
    """Set the current Picept context"""
    _PICEPT_CONTEXT.set(scope)

def get_context() -> Optional[PiceptScope]:
    """Get the current Picept context"""
    return _PICEPT_CONTEXT.get()

def get_tracer_or_none():
    """Get current tracer if available"""
    try:
        return trace.get_tracer("picept.sdk")
    except:
        return None
    
    