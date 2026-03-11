import json
import structlog

from nats.js.api import ConsumerConfig, DeliverPolicy, AckPolicy
from infrastructure.nats import nats_connection

logger = structlog.get_logger()


class JetStreamSubscriber:
    async def subscribe(self, subject: str, durable: str, handler) -> None:
        if nats_connection.js is None:
            raise RuntimeError("JetStream is not initialized")

        logger.info("creating_subscription", subject=subject, durable=durable)

        sub = await nats_connection.js.subscribe(
            subject=subject,
            durable=durable,
            config=ConsumerConfig(
                deliver_policy=DeliverPolicy.ALL,
                ack_policy=AckPolicy.EXPLICIT,
            ),
            manual_ack=True,
        )

        logger.info("subscription_created", subject=subject, durable=durable)

        async for msg in sub.messages:
            try:
                payload = json.loads(msg.data.decode())
                logger.info(
                    "event_received",
                    subject=msg.subject,
                    event_type=payload.get("metadata", {}).get("event_type"),
                    correlation_id=payload.get("metadata", {}).get("correlation_id"),
                )

                await handler(payload)

                await msg.ack()
                logger.info("event_acked", subject=msg.subject, durable=durable)

            except Exception as exc:
                logger.exception(
                    "event_processing_failed",
                    subject=msg.subject,
                    durable=durable,
                    error=str(exc),
                )
                await msg.nak()