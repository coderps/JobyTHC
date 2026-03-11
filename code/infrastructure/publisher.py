import json
import structlog
from pydantic import BaseModel

from infrastructure.nats import nats_connection

logger = structlog.get_logger()


class EventPublisher:
    async def publish(self, subject: str, payload: dict | BaseModel) -> None:
        if nats_connection.js is None:
            raise RuntimeError("JetStream is not initialized")

        if isinstance(payload, BaseModel):
            body = payload.model_dump(mode="json")
        else:
            body = payload

        encoded = json.dumps(body).encode()
        await nats_connection.js.publish(subject, encoded)

        metadata = body.get("metadata", {}) if isinstance(body, dict) else {}
        logger.info(
            "event_published",
            subject=subject,
            event_type=metadata.get("event_type"),
            correlation_id=metadata.get("correlation_id"),
        )


publisher = EventPublisher()