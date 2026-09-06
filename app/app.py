from flask import Flask, request, g
from prometheus_client import (
    Counter,
    Histogram,
    generate_latest,
    CONTENT_TYPE_LATEST,
)
import time
import logging
from opentelemetry.sdk.resources import Resource
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    ConsoleSpanExporter,
    SimpleSpanProcessor,
)
from opentelemetry.instrumentation.flask import FlaskInstrumentor


# --------------------------------------------------
# OpenTelemetry tracing
# --------------------------------------------------

resource = Resource.create(
    {
        "service.name": "devops-platform",
        "service.version": "3.0.0",
        "deployment.environment": "development",
    }
)

trace_provider = TracerProvider(
    resource=resource
)

trace_provider.add_span_processor(
    SimpleSpanProcessor(
        ConsoleSpanExporter()
    )
)

trace.set_tracer_provider(trace_provider)


# --------------------------------------------------
# Logging
# --------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

logger = logging.getLogger(__name__)


# --------------------------------------------------
# Flask application
# --------------------------------------------------

app = Flask(__name__)

# Automatically create OpenTelemetry spans
# for incoming Flask HTTP requests.
FlaskInstrumentor().instrument_app(app)


# --------------------------------------------------
# Prometheus metrics
# --------------------------------------------------

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "status"],
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
)


# --------------------------------------------------
# Request timing
# --------------------------------------------------

@app.before_request
def before_request():
    g.start_time = time.time()


@app.after_request
def after_request(response):
    duration = time.time() - g.start_time

    # Prometheus counter
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.path,
        status=response.status_code,
    ).inc()

    # Prometheus histogram
    REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=request.path,
    ).observe(duration)

    # Application log
    logger.info(
        "request method=%s path=%s status=%s duration=%.4fs",
        request.method,
        request.path,
        response.status_code,
        duration,
    )

    return response


# --------------------------------------------------
# Application routes
# --------------------------------------------------

@app.route("/")
def hello():
    return "DevOps Platform v3 is running!"


# --------------------------------------------------
# Prometheus metrics endpoint
# --------------------------------------------------

@app.route("/metrics")
def metrics():
    return generate_latest(), 200, {
        "Content-Type": CONTENT_TYPE_LATEST
    }


# --------------------------------------------------
# Start application
# --------------------------------------------------

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
    )