"""Event Publisher Module

This module provides functionality to publish events to NATS JetStream.
It handles serialization of Pydantic models and raw dictionaries, and logs
event publication with metadata tracking for observability.
"""
import json
import structlog
from pydantic import BaseModel

from infrastructure.nats import nats_connection

logger = structlog.get_logger()


class EventPublisher:
    """Publishes events to NATS JetStream subjects.
    
    Handles serialization of both Pydantic models and raw dictionaries,
    and provides structured logging for event publication tracking.
    """
    async def publish(self, subject: str, payload: dict | BaseModel) -> None:
        """Publish an event to a NATS JetStream subject.
        
        Serializes the payload (converting Pydantic models to JSON-compatible dicts),
        encodes it as JSON bytes, and publishes to the specified subject.
        
        Args:
            subject: The NATS subject to publish to (e.g., "order.created")
            payload: The event payload as either a Pydantic BaseModel or dict
            
        Raises:
            RuntimeError: If JetStream is not initialized
        """
        if nats_connection.js is None:
            raise RuntimeError("JetStream is not initialized")

        # Convert Pydantic models to JSON-serializable dictionaries
        if isinstance(payload, BaseModel):
            body = payload.model_dump(mode="json")
        else:
            body = payload

        # Encode the body as JSON bytes for NATS transmission
        encoded = json.dumps(body).encode()
        # Publish to JetStream
        await nats_connection.js.publish(subject, encoded)

        # Extract metadata for structured logging
        metadata = body.get("metadata", {}) if isinstance(body, dict) else {}
        logger.info(
            "event_published",
            subject=subject,
            event_type=metadata.get("event_type"),
            correlation_id=metadata.get("correlation_id"),
        )


# Singleton instance of EventPublisher used throughout the application
publisher = EventPublisher()