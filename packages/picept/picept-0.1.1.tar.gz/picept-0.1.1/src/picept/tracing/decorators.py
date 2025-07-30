
import contextlib
import functools
import inspect
from typing import Optional, Iterator, Any

from opentelemetry.util.types import Attributes

from ..context import get_tracer_or_none

@contextlib.contextmanager
def start_span(
    name: str, 
    *, 
    record_exception: bool = True, 
    attributes: Optional[Attributes] = None
) -> Iterator[Optional[Any]]:
    """
    Context manager for creating and managing a trace span.
    
    Example:
    ```python
    import picept
    
    picept.init(trace_id="my-project")
    
    def complex_operation():
        with picept.start_span("Data preparation"):
            # Your code here
            pass
    ```
    
    Args:
        name: The name of the span
        record_exception: Whether to record exceptions that occur within the span
        attributes: Additional attributes to associate with the span
    """
    tracer = get_tracer_or_none()
    if tracer is None:
        yield None
        return
        
    with tracer.start_as_current_span(
        name,
        record_exception=record_exception,
        attributes=attributes,
    ) as span:
        yield span

def traced(
    span_name: Optional[str] = None,
    *,
    log_args: bool = True,
    log_results: bool = True, 
    log_exceptions: bool = True,
    attributes: Optional[Attributes] = None,
    **kwargs: Any,
):
    """
    Decorator to trace function execution by recording a span.
        
    Example:
    ```python
    import picept
    
    picept.init(trace_id="my-project")
    
    @picept.traced()
    def process_input(user_query):
        # Your code gets automatically traced
        return "processed: " + user_query
    ```
    
    Args:
        span_name: Custom name for the span (defaults to function name)
        log_args: Whether to log function arguments
        log_results: Whether to log function return value
        log_exceptions: Whether to log exceptions
        attributes: Additional attributes to attach to the span
    """
    
    def decorator(func):
        name = span_name or func.__qualname__
        
        @functools.wraps(func)
        def wrapper_sync(*f_args, **f_kwargs):
            tracer = get_tracer_or_none()
            if tracer is None:
                return func(*f_args, **f_kwargs)
            
            with tracer.start_as_current_span(name, attributes=attributes):
                return func(*f_args, **f_kwargs)
        
        @functools.wraps(func)
        async def wrapper_async(*f_args, **f_kwargs):
            tracer = get_tracer_or_none()
            if tracer is None:
                return await func(*f_args, **f_kwargs)
            
            with tracer.start_as_current_span(name, attributes=attributes):
                return await func(*f_args, **f_kwargs)
        
        if inspect.iscoroutinefunction(func):
            wrapper_async._picept_traced = True
            return wrapper_async
        else:
            wrapper_sync._picept_traced = True
            return wrapper_sync
    
    return decorator