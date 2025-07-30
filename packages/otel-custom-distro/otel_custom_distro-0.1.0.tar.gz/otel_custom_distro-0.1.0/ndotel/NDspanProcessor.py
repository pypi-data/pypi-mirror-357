

from opentelemetry.sdk.trace import SpanProcessor
from opentelemetry.trace import Span, SpanKind
from typing import Optional
import time

class NDSpanProcessor(SpanProcessor):
    """Custom span processor with improved database span handling"""
    
    def on_start(self, span: Span, parent_context=None) -> None:
        """Called when a span is started"""
        # Add custom attributes

        span.set_attribute("custom.processor", "NDSpanProcessor")
        span.set_attribute("custom.timestamp", int(time.time()))
        span.set_attribute("custom.environment", "development")
        
        # Cavisson attributes
        span.set_attribute("cav.TR", "111")
        span.set_attribute("cav.tier", "Jatin")
        span.set_attribute("cav.server", "Random")
        span.set_attribute("cav.instance", "Python")
        
        
        # Detect database spans early
        db_system = span.attributes.get("db.system", "").lower()
        if db_system:
            span.set_attribute("custom.span_type", "database")
            if db_system == "mongodb":
                span.set_attribute("custom.db.type", "mongodb")
            elif db_system in ["mysql", "postgresql"]:
                span.set_attribute("custom.db.type", "sql")
            elif db_system == "redis":
                span.set_attribute("custom.db.type", "redis")

    def on_end(self, span: Span) -> None:
        """Enhanced span processing with better database support"""

        duration_ms = (span.end_time - span.start_time) / 1_000_000
        

        # First check for database spans (they may not always be CLIENT kind)
        db_system = span.attributes.get("db.system", "").lower()
        if db_system:
            self._process_db_span(span, db_system)
        elif span.kind == SpanKind.SERVER:
            self._process_http_span(span)

    def _process_db_span(self, span: Span, db_system: str):
        """Process all database spans"""
        
        # Common attributes
        db_name = span.attributes.get("db.name", "NA")
        operation = span.attributes.get("db.statement", 
                      span.attributes.get("db.operation", "NA"))
        user = span.attributes.get("db.user", "NA")
        
        # Host detection
        host = (span.attributes.get("net.peer.name") or 
               span.attributes.get("server.address") or 
               span.attributes.get("net.peer.ip") or 
               "NA")
        
        # Port detection
        port = (span.attributes.get("net.peer.port") or 
               span.attributes.get("server.port") or 
               "NA")

        if db_system == "mysql"or db_system == "postgresql":
            backend_name = f"NA|{host}|{port}|NA|mysql|{db_name}|NA|NA|NA|NA|NA"
            
        elif db_system == "mongodb":
            backend_name = f"NA|{host}|{port}|NA|MONGODB|{db_name}|NA|NA|NA|NA|NA"

        elif db_system == "redis":
            backend_name = f"NA|{host}|{port}|NA|redis|{db_name}|NA|NA|NA|NA|NA"
            #span.set_attribute("backend_name", backend_name)

    def _process_http_span(self, span: Span):
        """Process HTTP server spans"""
        
        # Print headers if available
        req_headers = {k: v for k, v in span.attributes.items() 
                      if k.startswith('http.request.header.')}
        if req_headers:
            print("\n   Request Headers:")
            for k, v in req_headers.items():
                print(f"     {k[20:]}: {v}")
                
        resp_headers = {k: v for k, v in span.attributes.items() 
                       if k.startswith('http.response.header.')}
        if resp_headers:
            print("\n   Response Headers:")
            for k, v in resp_headers.items():
                print(f"     {k[21:]}: {v}")

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        return True
        
    def shutdown(self) -> None:
        print("🛑 Custom Span Processor: Shutting down")
