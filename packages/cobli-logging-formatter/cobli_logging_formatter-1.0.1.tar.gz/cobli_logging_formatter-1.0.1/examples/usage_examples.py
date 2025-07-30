"""
Example usage of the Cobli logging formatter.
"""

import os
import logging
from cobli_logging import JsonFormatter, configure_logging, get_logger

# Set up environment variables for demonstration
os.environ["DD_SERVICE"] = "example-service"
os.environ["DD_VERSION"] = "1.0.0"
os.environ["LOG_LEVEL"] = "INFO"


def example_with_preconfigured_logger():
    """Example using the preconfigured logger."""
    print("=== Example 1: Using get_logger() ===")

    logger = get_logger()

    logger.info("Application started")
    logger.warning("This is a warning message")
    logger.error("An error occurred", extra={"user_id": 123, "action": "login"})

    try:
        raise ValueError("Something went wrong")
    except ValueError:
        logger.exception("Exception caught")


def example_with_custom_configuration():
    """Example using custom configuration."""
    print("\n=== Example 2: Using configure_logging() with custom settings ===")

    logger = configure_logging(
        service_name="custom-service",
        version="2.0.0",
        log_level="DEBUG",
        logger_name="my-custom-logger",
    )

    logger.debug("Debug message")
    logger.info(
        "Custom configured logger",
        extra={
            "request_id": "req-123",
            "user_agent": "Mozilla/5.0",
            "ip_address": "192.168.1.1",
        },
    )


def example_with_formatter_only():
    """Example using just the formatter."""
    print("\n=== Example 3: Using JsonFormatter directly ===")

    logger = logging.getLogger("manual-config")
    logger.setLevel(logging.INFO)

    # Remove any existing handlers
    for handler in list(logger.handlers):
        logger.removeHandler(handler)

    # Create and configure handler with our formatter
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter(service_name="manual-service", version="3.0.0"))
    logger.addHandler(handler)
    logger.propagate = False

    logger.info("Manually configured logger")
    logger.error(
        "Error with custom data",
        extra={
            "error_code": "E001",
            "service_module": "authentication",
            "retry_count": 3,
        },
    )


def example_in_different_thread():
    """Example showing thread information."""
    import threading
    import time

    print("\n=== Example 4: Multi-threaded logging ===")

    logger = get_logger(service_name="threaded-service")

    def worker_function(worker_id):
        logger.info(f"Worker {worker_id} started", extra={"worker_id": worker_id})
        time.sleep(0.1)
        logger.info(
            f"Worker {worker_id} completed",
            extra={"worker_id": worker_id, "duration_ms": 100},
        )

    # Create and start multiple threads
    threads = []
    for i in range(3):
        thread = threading.Thread(target=worker_function, args=(i,), name=f"Worker-{i}")
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()


if __name__ == "__main__":
    example_with_preconfigured_logger()
    example_with_custom_configuration()
    example_with_formatter_only()
    example_in_different_thread()

    print("\n=== All examples completed ===")
