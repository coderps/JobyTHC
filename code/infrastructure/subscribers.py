"""JetStream Event Subscriber Module

This module provides functionality to subscribe to NATS JetStream subjects
and process incoming events. It handles message acknowledgment, error handling,
and structured logging for event consumption.
"""
import json
import structlog

from nats.js.api import ConsumerConfig, DeliverPolicy, AckPolicy
from infrastructure.nats import nats_connection

logger = structlog.get_logger()


class JetStreamSubscriber:
    """Subscribes to NATS JetStream subjects and processes events.
    
    Creates durable consumers that deliver all messages with explicit
    acknowledgment. Failed messages are negatively acknowledged (nack'ed)
    for redelivery.
    """
    async def subscribe(self, subject: str, durable: str, handler) -> None:
        """Subscribe to a subject and process incoming events.
        
        Creates a durable subscription that will deliver all historical and future
        messages, with explicit acknowledgment required for each message.
        
        Args:
            subject: The NATS subject pattern to subscribe to (e.g., "order.*")
            durable: Unique durable consumer name for this subscription
            handler: Async callable that processes each event payload
            
        Raises:
            RuntimeError: If JetStream is not initialized
        """
        if nats_connection.js is None:
            raise RuntimeError("JetStream is not initialized")

        logger.info("creating_subscription", subject=subject, durable=durable)

        # Create a subscription with explicit acknowledgment and historical message delivery
        sub = await nats_connection.js.subscribe(
            subject=subject,
            durable=durable,
            config=ConsumerConfig(
                deliver_policy=DeliverPolicy.ALL,  # Deliver all messages from the stream
                ack_policy=AckPolicy.EXPLICIT,  # Require explicit acknowledgment
            ),
            manual_ack=True,  # Handle acknowledgment manually
        )

        logger.info("subscription_created", subject=subject, durable=durable)

        # Process messages as they arrive
        async for msg in sub.messages:
            try:
                # Decode and parse the JSON payload
                payload = json.loads(msg.data.decode())
                logger.info(
                    "event_received",
                    subject=msg.subject,
                    event_type=payload.get("metadata", {}).get("event_type"),
                    correlation_id=payload.get("metadata", {}).get("correlation_id"),
                )

                # Call the event handler
                await handler(payload)

                # Acknowledge successful processing
                await msg.ack()
                logger.info("event_acked", subject=msg.subject, durable=durable)

            except Exception as exc:
                # Log the error and negatively acknowledge for redelivery
                logger.exception(
                    "event_processing_failed",
                    subject=msg.subject,
                    durable=durable,
                    error=str(exc),
                )
                await msg.nak()