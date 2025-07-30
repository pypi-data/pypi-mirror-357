"""Custom span processor for Picept attributes"""

from typing import Optional
from opentelemetry import context as context_api
from opentelemetry.sdk.trace import Span, SpanProcessor

from ..context import PiceptScope

class PiceptAttributesSpanProcessor(SpanProcessor):
    """
    Processor that adds Picept-specific attributes to all spans.
    
    This ensures every span gets tagged with your custom identifiers:
    project-id, experiment-id, user-id, session-id, config-id, context-id, api-key
    """
    
    def __init__(self, scope: PiceptScope, api_key: Optional[str] = None):
        self.scope = scope
        self.api_key = api_key  # Store API key for adding to spans
    
    def on_start(self, span: Span, parent_context: Optional[context_api.Context] = None) -> None:
        """Called when a span starts - adds our custom attributes"""
        attributes = self.scope.as_attributes()
        if attributes:  # Only set if we have attributes
            span.set_attributes(attributes)
        
        # Add API key to every span for authentication
        if self.api_key:
            span.set_attribute("picept.api_key", self.api_key)
            
        super().on_start(span, parent_context)
    
    def on_end(self, span: Span) -> None:
        """Called when span ends - no action needed"""
        super().on_end(span)
    
    def shutdown(self) -> None:
        """Shutdown the processor"""
        super().shutdown()
    
    def force_flush(self, timeout_millis: int = 30000) -> bool:
        """Force flush - no action needed"""
        return True