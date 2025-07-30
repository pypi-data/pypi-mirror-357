"""
Tests for the Cobli JSON logging formatter.
"""

import json
import logging
import os
from unittest.mock import patch, MagicMock

from cobli_logging import JsonFormatter, configure_logging, get_logger


class TestJsonFormatter:
    """Test cases for JsonFormatter."""

    def test_basic_log_formatting(self):
        """Test basic log record formatting."""
        formatter = JsonFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)
        log_data = json.loads(result)

        assert log_data["level"] == "INFO"
        assert log_data["message"] == "Test message"
        assert "timestamp" in log_data
        assert log_data["timestamp"].endswith("Z")

    def test_custom_fields(self):
        """Test that custom fields are included in the custom section."""
        formatter = JsonFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.user_id = 123
        record.action = "login"

        result = formatter.format(record)
        log_data = json.loads(result)

        assert "custom" in log_data
        assert log_data["custom"]["user_id"] == 123
        assert log_data["custom"]["action"] == "login"

    def test_thread_name_included(self):
        """Test that non-main thread names are included."""
        formatter = JsonFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.threadName = "WorkerThread"

        result = formatter.format(record)
        log_data = json.loads(result)

        assert log_data["thread_name"] == "WorkerThread"

    def test_main_thread_not_included(self):
        """Test that MainThread name is not included."""
        formatter = JsonFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.threadName = "MainThread"

        result = formatter.format(record)
        log_data = json.loads(result)

        assert "thread_name" not in log_data

    @patch("cobli_logging.formatter.tracer")
    def test_datadog_integration(self, mock_tracer):
        """Test Datadog trace context integration."""
        mock_context = MagicMock()
        mock_context.trace_id = 123456789
        mock_context.span_id = 987654321
        mock_tracer.current_trace_context.return_value = mock_context

        formatter = JsonFormatter(service_name="test-service", version="1.0.0")
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)
        log_data = json.loads(result)

        assert "dd" in log_data
        assert log_data["dd"]["trace_id"] == "123456789"
        assert log_data["dd"]["span_id"] == "987654321"
        assert log_data["dd"]["service"] == "test-service"
        assert log_data["dd"]["version"] == "1.0.0"

    def test_exception_formatting(self):
        """Test that exceptions are properly formatted."""
        formatter = JsonFormatter()

        try:
            raise ValueError("Test exception")
        except ValueError:
            import sys

            exc_info = sys.exc_info()
            record = logging.LogRecord(
                name="test",
                level=logging.ERROR,
                pathname="test.py",
                lineno=1,
                msg="An error occurred",
                args=(),
                exc_info=exc_info,
            )

        result = formatter.format(record)
        log_data = json.loads(result)

        assert "stack_trace" in log_data
        assert "ValueError: Test exception" in log_data["stack_trace"]


class TestConfigurationFunctions:
    """Test cases for configuration utilities."""

    def test_configure_logging(self):
        """Test logger configuration."""
        logger = configure_logging(service_name="test-service", log_level="DEBUG")

        assert logger.level == logging.DEBUG
        assert len(logger.handlers) == 1
        assert isinstance(logger.handlers[0].formatter, JsonFormatter)

    def test_get_logger(self):
        """Test get_logger convenience function."""
        logger = get_logger(service_name="test-service")

        assert logger.name == "test-service"
        assert len(logger.handlers) == 1
        assert isinstance(logger.handlers[0].formatter, JsonFormatter)

    @patch.dict(os.environ, {"DD_SERVICE": "env-service", "LOG_LEVEL": "WARNING"})
    def test_environment_variable_usage(self):
        """Test that environment variables are used when parameters are not provided."""
        logger = get_logger()

        assert logger.name == "env-service"
        assert logger.level == logging.WARNING

    def test_no_duplicate_handlers(self):
        """Test that configure_logging multiple times doesn't create duplicates."""
        logger_name = "test-no-duplicates"

        logger1 = configure_logging(logger_name=logger_name)
        assert len(logger1.handlers) == 1

        logger2 = configure_logging(logger_name=logger_name)
        assert len(logger2.handlers) == 1
        assert logger1 is logger2  # Same logger instance
