"""
JSON Formatter for structured logging with Datadog integration.
"""

import os
import logging
import json
import datetime
import traceback
from typing import Dict, Any, Optional

from ddtrace import tracer


class JsonFormatter(logging.Formatter):
    """
    A custom JSON formatter that outputs structured logs with Datadog integration.

    Features:
    - ISO 8601 timestamps in UTC
    - Datadog trace and span ID integration
    - Custom field support
    - Thread information
    - Exception stack traces
    """

    def __init__(
        self, service_name: Optional[str] = None, version: Optional[str] = None
    ):
        """
        Initialize the JSON formatter.

        Args:
            service_name: Override for DD_SERVICE environment variable
            version: Override for DD_VERSION environment variable
        """
        super().__init__()
        self.dd_service = service_name or os.environ.get("DD_SERVICE")
        self.dd_version = version or os.environ.get("DD_VERSION")

    def format(self, record: logging.LogRecord) -> str:
        """
        Format a log record as a JSON string.

        Args:
            record: The log record to format

        Returns:
            A JSON-formatted string representation of the log record
        """
        timestamp_str = datetime.datetime.fromtimestamp(
            record.created, tz=datetime.timezone.utc
        ).isoformat()
        if timestamp_str.endswith("+00:00"):
            timestamp_str = timestamp_str[:-6] + "Z"

        log_record = {
            "timestamp": timestamp_str,
            "level": record.levelname,
            "message": record.getMessage(),
        }

        # Add thread information if not main thread
        if record.threadName and record.threadName != "MainThread":
            log_record["thread_name"] = record.threadName

        # Add Datadog information
        dd_info = self._get_datadog_info()
        if dd_info:
            log_record["dd"] = dd_info

        # Add custom fields
        custom_data = self._extract_custom_fields(record, log_record)
        if custom_data:
            log_record["custom"] = custom_data

        # Add stack trace if exception occurred
        if record.exc_info and record.exc_info is not True:
            exc_type, exc_value, exc_tb = record.exc_info
            log_record["stack_trace"] = "".join(
                traceback.format_exception(exc_type, exc_value, exc_tb)
            )
        elif record.exc_info is True:
            # Handle case where exc_info=True but no exception info available
            log_record["stack_trace"] = traceback.format_exc()

        return json.dumps(log_record, default=str)

    def _get_datadog_info(self) -> Dict[str, Any]:
        """Extract Datadog trace information."""
        dd_info = {}

        # Get trace context from ddtrace
        trace_context = tracer.current_trace_context()
        if trace_context:
            if trace_context.trace_id is not None:
                dd_info["trace_id"] = str(trace_context.trace_id)
            if trace_context.span_id is not None:
                dd_info["span_id"] = str(trace_context.span_id)

        # Add service metadata
        if self.dd_service:
            dd_info["service"] = self.dd_service
        if self.dd_version:
            dd_info["version"] = self.dd_version

        # Clean out None values
        return {k: v for k, v in dd_info.items() if v is not None}

    def _extract_custom_fields(
        self, record: logging.LogRecord, log_record: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract custom fields from the log record."""
        custom_data = {}

        # Standard LogRecord attributes that should not be duplicated
        base_handled_keys = {
            "args",
            "asctime",
            "created",
            "exc_info",
            "exc_text",
            "filename",
            "funcName",
            "levelname",
            "levelno",
            "lineno",
            "module",
            "msecs",
            "message",
            "msg",
            "name",
            "pathname",
            "process",
            "processName",
            "relativeCreated",
            "stack_info",
            "thread",
            "threadName",
            # Datadog injected top-level keys
            "dd.env",
            "dd.service",
            "dd.span_id",
            "dd.trace_id",
            "dd.version",
            "lambda_request_id",
        }

        current_log_record_keys = set(log_record.keys())
        record_dict = record.__dict__

        for key in record_dict:
            if key not in base_handled_keys and key not in current_log_record_keys:
                custom_data[key] = record_dict[key]

        return custom_data
