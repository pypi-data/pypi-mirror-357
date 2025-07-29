from logging import Logger as NativeLogger
from typing import Callable

from core_infinity_stones.errors.base_error import HttpError
from core_infinity_stones.logging.schemas import (
    ErrorEvent,
    Event,
    EventType,
    EventWithTraces,
    TracingDetails,
)


class Logger:
    def __init__(
        self,
        service_name: str,
        tracing_details_resolver: Callable[[], TracingDetails],
        logger: NativeLogger,
    ):
        self.service_name = service_name
        self.tracing_details_resolver = tracing_details_resolver
        self.logger = logger

    def info(self, event: Event) -> None:
        tracing_details = self.tracing_details_resolver()
        self.logger.info(EventWithTraces.from_event(event, tracing_details))

    def warning(self, event: Event) -> None:
        tracing_details = self.tracing_details_resolver()
        self.logger.info(EventWithTraces.from_event(event, tracing_details))

    def error(self, error: HttpError) -> None:
        tracing_details = self.tracing_details_resolver()

        self.logger.error(
            ErrorEvent(
                trace_id=tracing_details.trace_id,
                span_id=tracing_details.span_id,
                code=error.debug_details.debug_code,
                type=EventType.ERROR,
                service=self.service_name,
                message=error.debug_details.debug_message,
                details=error.debug_details.debug_details,
                severity=error.debug_details.severity,
                occurred_while=error.debug_details.occurred_while,
                caused_by=error.debug_details.caused_by,
                status_code=error.public_details.status_code,
                public_code=error.public_details.code,
                public_message=error.public_details.message,
                public_details=error.public_details.details,
            )
        )