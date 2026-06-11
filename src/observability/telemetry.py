from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
import functools
import time
import logging

tracer_provider = None
_initialized = False


def initialize_telemetry(
    service_name: str = "complianceiq", otlp_endpoint: str = None
) -> None:
    """
    Set up OpenTelemetry. Call once at startup.
    Gracefully does nothing if endpoint not configured.
    """
    global tracer_provider, _initialized
    if _initialized:
        return

    resource = Resource.create(
        {
            "service.name": service_name,
            "service.version": "1.0.0",
            "deployment.environment": "hackathon",
            "complianceiq.track": "reasoning-agents",
            "complianceiq.hackathon": "agents-league-aisf-2026",
        }
    )

    tracer_provider = TracerProvider(resource=resource)

    if otlp_endpoint:
        exporter = OTLPSpanExporter(endpoint=otlp_endpoint)
        tracer_provider.add_span_processor(BatchSpanProcessor(exporter))
        logging.info(f"OpenTelemetry initialized. Exporting to: {otlp_endpoint}")
    else:
        logging.info("OpenTelemetry initialized (no export endpoint — local only)")

    trace.set_tracer_provider(tracer_provider)
    HTTPXClientInstrumentor().instrument()  # Auto-instrument HTTP calls
    _initialized = True


def get_tracer(name: str) -> trace.Tracer:
    """Get a tracer instance. Initializes with defaults if not yet set up."""
    if not _initialized:
        initialize_telemetry()
    return trace.get_tracer(name)


def trace_agent(agent_name: str):
    """
    Decorator for agent methods. Creates a span with agent metadata.
    Usage: @trace_agent("Scanner Agent")
    """

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            tracer = get_tracer(f"complianceiq.{agent_name.lower().replace(' ', '_')}")
            with tracer.start_as_current_span(agent_name) as span:
                span.set_attribute("agent.name", agent_name)
                mock_mode = getattr(args[0], "mock_mode", False) if args else False
                span.set_attribute("agent.mock_mode", mock_mode)
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    span.set_attribute("agent.status", "success")
                    span.set_attribute(
                        "agent.duration_ms", int((time.time() - start_time) * 1000)
                    )
                    return result
                except Exception as e:
                    span.set_attribute("agent.status", "error")
                    span.set_attribute("agent.error", str(e))
                    span.record_exception(e)
                    raise

        return wrapper

    return decorator


def trace_foundry_iq_query(query_type: str):
    """Decorator for Foundry IQ queries. Records query type and citation count."""

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            tracer = get_tracer("complianceiq.foundry_iq")
            with tracer.start_as_current_span(f"foundry_iq.{query_type}") as span:
                span.set_attribute("foundry_iq.query_type", query_type)
                start_time = time.time()
                result = await func(*args, **kwargs)
                span.set_attribute(
                    "foundry_iq.duration_ms", int((time.time() - start_time) * 1000)
                )
                if isinstance(result, dict) and "citations" in result:
                    span.set_attribute(
                        "foundry_iq.citations_returned",
                        len(result.get("citations", [])),
                    )
                return result

        return wrapper

    return decorator
