# Cobli Logging Formatter

A structured JSON logging formatter with Datadog integration for Python applications.

## Features

- **Structured JSON Logging**: Outputs logs in a consistent JSON format
- **Datadog Integration**: Automatically includes trace and span IDs from Datadog APM
- **Timezone Aware**: Timestamps in UTC with ISO 8601 format
- **Custom Fields Support**: Automatically captures and includes custom log fields
- **Thread Information**: Includes thread names for multi-threaded applications
- **Exception Handling**: Captures and formats stack traces
- **Environment Configuration**: Uses environment variables for service metadata

## Installation

## Using uv (recommended)

```bash
uv add cobli-logging-formatter
```

## Using pip

```bash
pip install cobli-logging-formatter
```

## Quick Start

### Option 1: Use the preconfigured logger

```python
from cobli_logging import get_logger

logger = get_logger()
logger.info("Hello, world!")
logger.error("Something went wrong", extra={"user_id": 123, "action": "login"})
```

### Option 2: Use just the formatter

```python
import logging
from cobli_logging import JsonFormatter

logger = logging.getLogger("my-service")
handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)

logger.info("Hello, world!")
```

### Option 3: Use the configuration helper

```python
from cobli_logging import configure_logging

# Configure with default settings
configure_logging()

# Or with custom settings
configure_logging(
    service_name="my-custom-service",
    log_level="DEBUG",
    propagate=True
)

import logging
logger = logging.getLogger("my-custom-service")
logger.info("Configured logger ready!")
```

## Configuration

The formatter uses the following environment variables:

- `DD_SERVICE`: Service name for Datadog (optional)
- `DD_VERSION`: Service version for Datadog (optional)
- `LOG_LEVEL`: Logging level (default: "INFO")

## Output Format

```json
{
  "timestamp": "2025-06-05T10:30:00Z",
  "level": "INFO",
  "message": "User logged in successfully",
  "thread_name": "WorkerThread-1",
  "dd": {
    "trace_id": "1234567890123456789",
    "span_id": "987654321",
    "service": "user-service",
    "version": "1.2.3"
  },
  "custom": {
    "user_id": 123,
    "action": "login",
    "ip_address": "192.168.1.1"
  },
  "stack_trace": "Traceback (most recent call last):\n..."
}
```

## Development

## Quick start with Makefile

This project uses a comprehensive Makefile for all development tasks:

```bash
# Complete development setup
make dev-setup

# Run all quality checks (format, lint, test)
make check

# Run tests with coverage
make test-cov

# Build the package
make build

# Run examples
make examples

# See all available commands
make help
```

## License

MIT License
