"""JetStream Stream Management Module

This module manages the creation and configuration of NATS JetStream streams.
Streams define the subjects they consume from and their retention/storage policies.
This module ensures that required streams exist on startup and can reset them for testing.

Checkout domain/events.py for event subscription and handling logic that interacts with these streams.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import structlog
from nats.js.api import StreamConfig, RetentionPolicy, StorageType
from nats.js.errors import NotFoundError

from infrastructure.nats import nats_connection

logger = structlog.get_logger()


@dataclass(frozen=True)
class StreamDefinition:
    """Definition of a JetStream stream configuration.
    
    Attributes:
        name: Unique name for the stream (e.g., "ORDERS", "CNC")
        subjects: List of NATS subjects this stream subscribes to (supports wildcards)
        description: Human-readable description of the stream's purpose
    """
    name: str
    subjects: Sequence[str]
    description: str


class JetStreamStreamManager:
    """Manages the lifecycle and configuration of JetStream streams.
    
    Creates and maintains streams for different event categories (orders, inventory,
    CNC, quality, etc.). Supports resetting streams for testing and ensuring they
    exist with proper configuration.
    """
    def __init__(self) -> None:
        """Initialize the stream manager with predefined stream configurations."""
        # List of stream definitions for different event categories
        self._streams: list[StreamDefinition] = [
            StreamDefinition(
                name="ORDERS",
                subjects=["order.*"],
                description="Order lifecycle events from ERP",
            ),
            StreamDefinition(
                name="INVENTORY",
                subjects=["wms.inventory.*"],
                description="Inventory events",
            ),
            StreamDefinition(
                name="MES",
                subjects=["mes.>"],
                description="MES orchestration events",
            ),
            StreamDefinition(
                name="CNC",
                subjects=["cnc.job.*"],
                description="CNC job events",
            ),
            StreamDefinition(
                name="QUALITY",
                subjects=["quality.>"],
                description="Quality events",
            ),
            StreamDefinition(
                name="ASSEMBLY",
                subjects=["assembly.job.*"],
                description="Assembly events",
            ),
        ]

    async def reset_streams(self) -> None:
        """Delete all streams. Useful for testing and resetting state.
        
        Raises:
            RuntimeError: If JetStream is not initialized
        """
        if nats_connection.js is None:
            raise RuntimeError("JetStream is not initialized. Connect to NATS first.")

        # Delete each stream, ignoring NotFoundError if stream doesn't exist
        for stream in self._streams:
            try:
                await nats_connection.js.delete_stream(stream.name)
                logger.info("stream_deleted", stream=stream.name)
            except NotFoundError:
                logger.info("stream_not_found_on_delete", stream=stream.name)

    async def ensure_streams(self) -> None:
        """Create all required streams if they don't already exist.
        
        Called during application startup to ensure all event streams are available.
        
        Raises:
            RuntimeError: If JetStream is not initialized
        """
        if nats_connection.js is None:
            raise RuntimeError("JetStream is not initialized. Connect to NATS first.")

        # Ensure each stream exists with proper configuration
        for stream in self._streams:
            await self._ensure_stream(stream)

    async def _ensure_stream(self, stream: StreamDefinition) -> None:
        """Create a stream if it doesn't exist, or verify existing stream.
        
        Args:
            stream: The StreamDefinition to create or verify
        """
        assert nats_connection.js is not None

        # Check if stream already exists
        try:
            existing = await nats_connection.js.stream_info(stream.name)
            logger.info(
                "stream_already_exists",
                stream=stream.name,
                subjects=existing.config.subjects,
            )
            return
        except NotFoundError:
            logger.info(
                "stream_not_found_creating",
                stream=stream.name,
                subjects=list(stream.subjects),
            )

        # Create stream configuration with file-based storage and limit-based retention
        config = StreamConfig(
            name=stream.name,
            description=stream.description,
            subjects=list(stream.subjects),
            retention=RetentionPolicy.LIMITS,  # Retention based on message/byte/age limits
            max_msgs=-1,  # No limit on message count
            max_bytes=-1,  # No limit on total bytes
            max_age=0,  # Messages never expire by age
            storage=StorageType.FILE,  # Persist to disk
            num_replicas=1,  # Single replica (non-clustered)
        )

        # Create the stream
        await nats_connection.js.add_stream(config=config)

        logger.info(
            "stream_created",
            stream=stream.name,
            subjects=list(stream.subjects),
        )