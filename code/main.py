"""
Main entry point for the event-driven MES (Manufacturing Execution System) orchestration.

This module sets up the event streaming infrastructure and subscribes to various
domain events across the system, including MES processing, external system simulators,
and observation/logging handlers.
"""
import asyncio
import structlog

from infrastructure.nats import nats_connection
from infrastructure.streams import JetStreamStreamManager
from infrastructure.subscribers import JetStreamSubscriber
from domain.events import subscribe_events

logger = structlog.get_logger()


async def main() -> None:
    """Initialize event streaming infrastructure and subscribe to all event handlers."""
    # Connect to NATS server
    await nats_connection.connect()

    # Initialize and reset JetStream streams to ensure clean state
    stream_manager = JetStreamStreamManager()
    await stream_manager.reset_streams()
    await stream_manager.ensure_streams()

    # Create subscriber for event-driven message handling
    subscriber = JetStreamSubscriber()

    logger.info("mes_poc_started_clean")

    # Subscribe to all event topics and run event handlers concurrently
    await subscribe_events(subscriber)


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())