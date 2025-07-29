from enum import StrEnum
from typing import Any, Optional

from pydantic import BaseModel

from core_infinity_stones.errors.base_error import LocalizedMessage, Severity


class TracingDetails(BaseModel):
    trace_id: str
    span_id: str


class EventType(StrEnum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class Event(BaseModel):
    code: str
    type: EventType
    service: str
    message: str
    details: Optional[dict[str, Any]] = None


class EventWithTraces(Event):
    trace_id: str
    span_id: str

    @classmethod
    def from_event(cls, event: Event, tracing_details: TracingDetails) -> "EventWithTraces":
        return cls(
            trace_id=tracing_details.trace_id,
            span_id=tracing_details.span_id,
            code=event.code,
            type=event.type,
            service=event.service,
            message=event.message,
            details=event.details,
        )


class ErrorEvent(EventWithTraces):
    severity: Severity
    occurred_while: Optional[str] = None
    caused_by: Optional[Exception]
    status_code: int
    public_code: str
    public_message: LocalizedMessage
    public_details: Optional[dict[str, Any]] = None