from datetime import datetime
from uuid import uuid4

from pydantic import BaseModel, Field


def new_event_id() -> str:
    return f"evt-{uuid4().hex[:12]}"


def utc_now() -> datetime:
    return datetime.utcnow()


class EventMetadata(BaseModel):
    event_type: str
    event_id: str = Field(default_factory=new_event_id)
    timestamp: datetime = Field(default_factory=utc_now)
    correlation_id: str