# ndotel/distro.py - Configuration via environment variables
from opentelemetry.distro import BaseDistro
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, BatchSpanProcessor
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry import trace
from .NDspanProcessor import NDSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from .sampler import MySampler
import logging
import os

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class NDCustomDistro(BaseDistro):
    """Enhanced custom distro with environment variable configuration"""
    
    def _configure(self, **kwargs):
        logger.info("Configuring MyCustomDistro")
        
        # Check if we already have a tracer provider
        current_provider = trace.get_tracer_provider()
        
        # Only proceed if we have a ProxyTracerProvider
        if "ProxyTracerProvider" not in str(type(current_provider)):
            return
        
        # Get configuration from environment variables
        service_name = os.getenv("OTEL_SERVICE_NAME", "flask-app")
        otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
        otlp_protocol = os.getenv("OTEL_EXPORTER_OTLP_PROTOCOL", "http/protobuf")
        
        # Create resource
        resource = Resource.create({
            SERVICE_NAME: service_name,
            "service.version": "1.0.0",
            "service.instance.id": "instance-1",
            "deployment.environment": os.getenv("DEPLOYMENT_ENVIRONMENT", "development")
        })
        
        # Create custom tracer provider
        tracer_provider = TracerProvider(
            resource=resource,
            sampler=MySampler()
        )
        
        # Add processors
        tracer_provider.add_span_processor(NDSpanProcessor())
        
        tracer_provider.add_span_processor(
            BatchSpanProcessor(ConsoleSpanExporter())
        )
        
        # Configure OTLP exporter if endpoint is provided
        if otlp_endpoint:
            try:
                otlp_exporter = OTLPSpanExporter(
                    endpoint=otlp_endpoint,
                    # Add protocol-specific configuration if needed
                )
                tracer_provider.add_span_processor(
                    BatchSpanProcessor(otlp_exporter)
                )
            except Exception as e:
                logger.error(f"Failed to configure OTLP exporter: {e}")
        
        # Set the tracer provider
        try:
            trace.set_tracer_provider(tracer_provider)
        except Exception as e:
            logger.error(f"TracerProvider setup error: {e}")
            return
        
def create_distro():
    """Factory function that reads from environment variables"""
    return NDCustomDistro()
