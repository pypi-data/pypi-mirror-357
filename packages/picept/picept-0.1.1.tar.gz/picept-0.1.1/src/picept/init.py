"""Picept initialization"""

from typing import Optional, List, Any
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from .context import PiceptScope, set_context
from .tracing.tracer import PiceptAttributesSpanProcessor

def _auto_detect_integrations() -> List[Any]:
    available_integrations = []
    
    # Try Anthropic
    try:
        from openinference.instrumentation.anthropic import AnthropicInstrumentor
        available_integrations.append(AnthropicInstrumentor())
        print("   🤖 Auto-detected: AnthropicInstrumentor")
    except ImportError:
        pass
    
    # Try OpenAI  
    try:
        from openinference.instrumentation.openai import OpenAIInstrumentor
        available_integrations.append(OpenAIInstrumentor())
        print("   🤖 Auto-detected: OpenAIInstrumentor")
    except ImportError:
        pass
        
    # Try LangChain
    try:
        from openinference.instrumentation.langchain import LangChainInstrumentor
        available_integrations.append(LangChainInstrumentor())
        print("   🤖 Auto-detected: LangChainInstrumentor")
    except ImportError:
        pass
    
    if available_integrations:
        print(f"🎯 Auto-detected {len(available_integrations)} integrations")
    else:
        print("🔍 No auto-instrumentable libraries found")
        
    return available_integrations

# endpoint: str = "http://localhost:4318/v1/traces", # local developemnts 

def init(
    project_id: Optional[str] = None,
    experiment_id: Optional[str] = None,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    config_id: Optional[str] = None,
    context_id: Optional[str] = None,
    endpoint: str ="http://api.picept.ai:4318/v1/traces",
    api_key: Optional[str] = None,
    integrations: Optional[List[Any]] = None,
    auto_instrument: bool = True,
) -> None:
    """
    Initialize Picept tracing
    
    Args:
        project_id: Project name identifier
        experiment_id: Experiment identifier  
        user_id: User identifier
        session_id: Session identifier
        config_id: Configuration identifier
        context_id: Context identifier
        endpoint: OTLP endpoint for traces
        api_key: API key for authentication
        integrations: List of OpenTelemetry instrumentors
        auto_instrument: Whether to auto-detect and apply integrations
    """
    # Create context 
    scope = PiceptScope(
        project_id=project_id,
        experiment_id=experiment_id,
        user_id=user_id,
        session_id=session_id,
        config_id=config_id,
        context_id=context_id,
    )
    set_context(scope)
    
    # Setup OpenTelemetry
    provider = TracerProvider()
    
    # Add our custom span processor with API key
    provider.add_span_processor(PiceptAttributesSpanProcessor(scope, api_key))
    
    # Add OTLP exporter if endpoint provided
    if endpoint:
        headers = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
            print(f"🔑 EXPORTER DEBUG: Using API key {api_key[:8]}...")
            print(f"🔑 HEADERS DEBUG: {headers}")
        
        exporter = OTLPSpanExporter(
            endpoint=endpoint, 
            headers=headers,
            timeout=30
        )
        provider.add_span_processor(BatchSpanProcessor(exporter))
        
    trace.set_tracer_provider(provider)
    
    # Auto-detect integrations if none provided and auto_instrument is True
    if integrations is None and auto_instrument:
        integrations = _auto_detect_integrations()
    
    # Apply integrations
    if integrations:
        print(f"🔧 Applying {len(integrations)} integrations...")
        for integration in integrations:
            try:
                if hasattr(integration, 'instrument'):
                    integration_name = integration.__class__.__name__
                    print(f"   ✅ Instrumenting: {integration_name}")
                    integration.instrument()
                else:
                    print(f"   ⚠️ Skipping invalid integration: {integration}")
            except Exception as e:
                print(f"   ❌ Failed to instrument {integration}: {e}")
    else:
        print("🔧 No integrations provided")

    print(f"✅ Picept initialized with context: {scope}")