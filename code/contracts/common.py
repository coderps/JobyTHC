"""
Common event contract definitions and utilities.

This module defines the base metadata structure that all events must include
for proper traceability, correlation, and audit logging across the event-driven
messaging system.
"""
from datetime import datetime
from uuid import uuid4
from pydantic import BaseModel, Field


def new_event_id() -> str:
    """Generate a unique event identifier in the format evt-<12-char-hex>."""
    return f"evt-{uuid4().hex[:12]}"


def utc_now() -> datetime:
    """Get the current UTC timestamp."""
    return datetime.utcnow()


class EventMetadata(BaseModel):
    """Metadata that accompanies every event in the system for traceability.
    
    Attributes:
        event_type: The type/category of event (e.g., 'order.created', 'cnc.job.requested')
        event_id: Unique identifier for this specific event instance
        timestamp: UTC timestamp when the event was created
        correlation_id: ID used to track related events in the same business transaction
    """
    event_type: str
    event_id: str = Field(default_factory=new_event_id)
    timestamp: datetime = Field(default_factory=utc_now)
    correlation_id: str