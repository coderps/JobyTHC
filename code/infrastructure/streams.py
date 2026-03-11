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
    name: str
    subjects: Sequence[str]
    description: str


class JetStreamStreamManager:
    def __init__(self) -> None:
        self._streams: list[StreamDefinition] = [
            StreamDefinition(
                name="ORDERS",
                subjects=["order.*"],
                description="Order lifecycle events from ERP",
            ),
            StreamDefinition(
                name="INVENTORY",
                subjects=["inventory.*"],
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
        if nats_connection.js is None:
            raise RuntimeError("JetStream is not initialized. Connect to NATS first.")

        for stream in self._streams:
            try:
                await nats_connection.js.delete_stream(stream.name)
                logger.info("stream_deleted", stream=stream.name)
            except NotFoundError:
                logger.info("stream_not_found_on_delete", stream=stream.name)

    async def ensure_streams(self) -> None:
        if nats_connection.js is None:
            raise RuntimeError("JetStream is not initialized. Connect to NATS first.")

        for stream in self._streams:
            await self._ensure_stream(stream)

    async def _ensure_stream(self, stream: StreamDefinition) -> None:
        assert nats_connection.js is not None

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

        config = StreamConfig(
            name=stream.name,
            description=stream.description,
            subjects=list(stream.subjects),
            retention=RetentionPolicy.LIMITS,
            max_msgs=-1,
            max_bytes=-1,
            max_age=0,
            storage=StorageType.FILE,
            num_replicas=1,
        )

        await nats_connection.js.add_stream(config=config)

        logger.info(
            "stream_created",
            stream=stream.name,
            subjects=list(stream.subjects),
        )