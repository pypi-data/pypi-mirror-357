# OpenTelemetry Custom Distribution

## Overview

This documentation provides comprehensive guidance for implementing a custom OpenTelemetry distribution in Python applications. The custom distribution enables automatic instrumentation of applications without requiring code modifications, while providing extensive customization capabilities for sampling strategies, span processing, and metric export configurations.

## Project Architecture

The distribution follows a modular architecture with the following components:

**Core Module Structure:**
- Distribution configuration module for TracerProvider and MeterProvider setup
- Custom sampler implementation for intelligent span filtering
- Span processor for runtime span attribute modification
- Metric exporter for customized metric handling and export

**Application Integration:**
- Seamless integration with Flask web framework
- MySQL database instrumentation support
- Extensible support for additional auto-instrumented libraries

## File Structure

The project follows a standardized directory layout:

```
otel_custom_distro/
├── ndotel/                      # Custom OpenTelemetry components directory
│   ├── __init__.py             # Package initialization file
│   ├── distro.py               # Main distribution configuration module
│   ├── sampler.py              # Custom sampling logic implementation
│   ├── NDspanProcessor.py      # Span processing and modification logic
│   └── metric_exporter.py      # Custom metric export functionality
├── app.py                      # Example Flask application file
├── pyproject.toml              # Build configuration and entry points
├── setup.cfg                   # Legacy build configuration for older pip versions
└── README.md                   # Project documentation
```

**Directory Descriptions:**

- **ndotel/**: Contains all custom OpenTelemetry component implementations
- **__init__.py**: Enables the ndotel directory to function as a Python package
- **distro.py**: Central configuration file that orchestrates TracerProvider and MeterProvider setup
- **sampler.py**: Implements custom sampling strategies for span filtering
- **NDspanProcessor.py**: Handles span modification and attribute injection
- **metric_exporter.py**: Manages custom metric export destinations and formatting
- **app.py**: Sample application demonstrating auto-instrumentation capabilities
- **pyproject.toml**: Defines build requirements and OpenTelemetry distribution entry points
- **setup.cfg**: Legacy configuration file providing backward compatibility for older pip versions
- **README.md**: Comprehensive documentation and usage instructions

## Installation and Setup

### Prerequisites Installation

Install the required OpenTelemetry packages and dependencies:

```bash
pip install opentelemetry-distro==0.54b1 opentelemetry-sdk==1.33.1 opentelemetry-instrumentation-flask==0.54b1 opentelemetry-instrumentation-mysql==0.54b1 Flask==2.0.2 Flask-MySQLdb==0.2.0
```

**Description:** This command installs the OpenTelemetry SDK, instrumentation libraries for Flask and MySQL, along with the necessary web framework dependencies.

### Distribution Installation

Install the custom distribution in development mode:

```bash
pip install -e .
```

**Description:** Installs the custom distribution package in editable mode, allowing for real-time development and testing without reinstallation.

## Configuration Management

### Environment Variables

Configure the distribution behavior using the following environment variables:

```bash
export OTEL_PYTHON_DISTRO=otel_custom_distro
export OTEL_TRACES_EXPORTER=console
export OTEL_METRICS_EXPORTER=none
export OTEL_SERVICE_NAME=flask-mysql-app
```

**Variable Descriptions:**

- `OTEL_PYTHON_DISTRO`: Specifies the custom distribution name for OpenTelemetry to load
- `OTEL_TRACES_EXPORTER`: Defines the trace export destination (console, OTLP, etc.)
- `OTEL_METRICS_EXPORTER`: Configures metric export behavior (none, OTLP, etc.)
- `OTEL_SERVICE_NAME`: Sets the service identifier in telemetry data

### Build Configuration

The distribution requires proper entry point configuration in `pyproject.toml`:

```toml
[project.entry-points."opentelemetry_distro"]
otel_custom_distro = "ndotel.distro:CustomDistro"
```

**Description:** This configuration registers the custom distribution with OpenTelemetry's plugin system, enabling automatic discovery and loading.

## Application Execution

### Auto-Instrumentation Command

Execute applications with automatic instrumentation:

```bash
opentelemetry-instrument python app.py
```

**Description:** This command launches the Python application with OpenTelemetry auto-instrumentation enabled, automatically detecting and instrumenting supported libraries and frameworks.

### Advanced Execution Options

For applications requiring specific configuration:

```bash
opentelemetry-instrument --traces_exporter console --metrics_exporter none python app.py
```

**Description:** Provides command-line override options for exporter configuration, allowing runtime customization without environment variable modification.

## Component Descriptions

### Custom Sampler

The custom sampler implements intelligent span filtering based on configurable rules. It evaluates incoming spans and determines whether to sample, record, or drop them based on attributes such as endpoint patterns, request types, or custom business logic.

**Key Features:**
- Health check endpoint filtering
- Configurable sampling rates
- Context-aware decision making
- Performance optimization for high-traffic applications

### Span Processor

The span processor provides runtime span modification capabilities, allowing for dynamic attribute injection, span name modification, and custom metadata addition.

**Capabilities:**
- Environment-specific attribute injection
- Dynamic span enrichment
- Custom business context addition
- Compliance and security attribute handling

### Metric Exporter

The custom metric exporter handles the export and processing of application metrics, providing flexibility in destination configuration and data format transformation.

**Features:**
- Console output for development
- File-based export for analysis
- Custom formatting and aggregation
- Integration with external monitoring systems

## Monitoring and Observability

### Trace Analysis

The distribution generates comprehensive trace data for:
- HTTP request/response cycles
- Database query execution
- Inter-service communication
- Custom business operations

### Metric Collection

Automated metric collection includes:
- Request latency and throughput
- Database connection pool statistics
- Custom application metrics
- Resource utilization data

## Troubleshooting

### Common Issues

**Distribution Not Loading:**
Verify the entry point configuration in `pyproject.toml` and ensure the package is properly installed.

**Missing Instrumentation:**
Check that all required instrumentation packages are installed and compatible versions are used.

**Configuration Conflicts:**
Review environment variable settings and ensure no conflicting configurations exist.

### Diagnostic Commands

Verify installation status:
```bash
pip list | grep opentelemetry
```

**Description:** Lists all installed OpenTelemetry packages and their versions for troubleshooting compatibility issues.

Check distribution registration:
```bash
python -c "import pkg_resources; print([ep.name for ep in pkg_resources.iter_entry_points('opentelemetry_distro')])"
```

**Description:** Verifies that the custom distribution is properly registered and discoverable by OpenTelemetry.
