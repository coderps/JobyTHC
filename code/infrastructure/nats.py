"""NATS Connection Management Module

This module manages the connection to a NATS server with JetStream capabilities.
It provides a singleton instance that maintains the connection state and provides
access to both the core NATS client and the JetStream context for pub/sub operations.
"""
import asyncio
from nats.aio.client import Client as NATS
from nats.js import JetStreamContext
import structlog

from config.settings import settings

logger = structlog.get_logger()


class NatsConnection:
    """Manages the lifecycle of a NATS/JetStream connection.
    
    This class handles connecting to a NATS server with automatic reconnection,
    and provides access to the JetStream context for event streaming operations.
    
    Attributes:
        nc: The NATS client connection (None until connect() is called)
        js: The JetStream context for pub/sub operations (None until connect() is called)
    """
    def __init__(self):
        # Core NATS client instance
        self.nc: NATS | None = None
        # JetStream context for publish/subscribe operations
        self.js: JetStreamContext | None = None

    async def connect(self):
        """Establish a connection to the NATS server.
        
        Creates a new NATS client, connects to the configured NATS server,
        and initializes the JetStream context. Includes automatic reconnection
        with exponential backoff.
        """
        logger.info("connecting_to_nats", url=settings.NATS_URL)

        # Instantiate the NATS client
        self.nc = NATS()

        # Connect to NATS server with automatic reconnection enabled
        await self.nc.connect(
            servers=[settings.NATS_URL],
            name=settings.NATS_CLIENT_NAME,
            reconnect_time_wait=2,
            max_reconnect_attempts=-1,
        )

        # Initialize JetStream context for streaming operations
        self.js = self.nc.jetstream()

        logger.info("nats_connected")

    async def close(self):
        """Close the NATS connection gracefully.
        
        Drains all pending operations and closes the connection cleanly.
        """
        if self.nc:
            # Drain: wait for all pending operations to complete
            await self.nc.drain()
            # Close the connection
            await self.nc.close()
            logger.info("nats_connection_closed")


# Singleton instance of NatsConnection used throughout the application
nats_connection = NatsConnection()