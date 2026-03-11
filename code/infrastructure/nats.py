import asyncio
from nats.aio.client import Client as NATS
from nats.js import JetStreamContext
import structlog

from config.settings import settings

logger = structlog.get_logger()


class NatsConnection:
    def __init__(self):
        self.nc: NATS | None = None
        self.js: JetStreamContext | None = None

    async def connect(self):
        logger.info("connecting_to_nats", url=settings.NATS_URL)

        self.nc = NATS()

        await self.nc.connect(
            servers=[settings.NATS_URL],
            name=settings.NATS_CLIENT_NAME,
            reconnect_time_wait=2,
            max_reconnect_attempts=-1,
        )

        self.js = self.nc.jetstream()

        logger.info("nats_connected")

    async def close(self):
        if self.nc:
            await self.nc.drain()
            await self.nc.close()
            logger.info("nats_connection_closed")


nats_connection = NatsConnection()