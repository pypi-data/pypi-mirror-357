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
    message: Optional[str] = None
    details: Optional[dict[str, Any]] = None


class EventWithTracesDetails(BaseModel):
    trace_id: str
    span_id: str
    type: EventType
    service: str
    url: Optional[str] = None
    client_platform: Optional[str] = None
    code: str
    message: Optional[str] = None
    details: Optional[dict[str, Any]] = None

    @classmethod
    def from_event(
        cls,
        event: Event,
        tracing_details: TracingDetails,
        type: EventType,
        service: str,
        url: Optional[str],
        client_platform: Optional[str]
    ) -> "EventWithTracesDetails":
        return cls(
            trace_id=tracing_details.trace_id,
            span_id=tracing_details.span_id,
            type=type,
            service=service,
            url=url,
            client_platform=client_platform,
            code=event.code,
            message=event.message,
            details=event.details,
        )


class ErrorEvent(BaseModel):
    trace_id: str
    span_id: str
    type: EventType
    service: str
    url: Optional[str] = None
    client_platform: Optional[str] = None
    severity: Severity
    code: str
    message: str
    details: Optional[dict[str, Any]] = None
    occurred_while: Optional[str] = None
    caused_by: Optional[str] = None
    status_code: int
    public_code: str
    public_message: LocalizedMessage
    public_details: Optional[dict[str, Any]] = None