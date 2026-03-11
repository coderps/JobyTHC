import asyncio
import random

import structlog

from contracts.common import EventMetadata
from contracts.cnc_events import (
    CncJobRequestedEvent,
    CncJobStartedEvent,
    CncJobCompletedEvent,
)
from infrastructure.publisher import publisher
from observability.demo_log import demo_step

logger = structlog.get_logger()


class CncSimulator:
    async def handle_cnc_job_requested(self, raw_event: dict) -> None:
        event = CncJobRequestedEvent.model_validate(raw_event)
        demo_step(
            step="CNC_PROCESSING_STARTED",
            workorder_id=event.workorder_id,
            order_id=event.order_id,
            sku=event.sku,
            quantity=event.quantity,
            attempt=event.attempt,
            extra={"machine_id": event.target_machine},
        )

        logger.info(
            "cnc_job_received",
            workorder_id=event.workorder_id,
            quantity=event.quantity,
            machine=event.target_machine,
            attempt=event.attempt,
        )

        await publisher.publish(
            "cnc.job.started",
            CncJobStartedEvent(
                metadata=EventMetadata(
                    event_type="cnc.job.started",
                    correlation_id=event.metadata.correlation_id,
                ),
                workorder_id=event.workorder_id,
                order_id=event.order_id,
                sku=event.sku,
                quantity=event.quantity,
                machine_id=event.target_machine,
                attempt=event.attempt,
            ),
        )

        duration_seconds = random.randint(2, 4)
        logger.info(
            "cnc_processing",
            workorder_id=event.workorder_id,
            sleep_seconds=duration_seconds,
            attempt=event.attempt,
        )

        await asyncio.sleep(duration_seconds)

        await publisher.publish(
            "cnc.job.completed",
            CncJobCompletedEvent(
                metadata=EventMetadata(
                    event_type="cnc.job.completed",
                    correlation_id=event.metadata.correlation_id,
                ),
                workorder_id=event.workorder_id,
                order_id=event.order_id,
                sku=event.sku,
                quantity=event.quantity,
                machine_id=event.target_machine,
                duration_seconds=duration_seconds,
                attempt=event.attempt,
            ),
        )

        logger.info(
            "cnc_job_completed",
            workorder_id=event.workorder_id,
            quantity=event.quantity,
            machine=event.target_machine,
            attempt=event.attempt,
        )

        demo_step(
            step="CNC_PROCESSING_COMPLETED",
            workorder_id=event.workorder_id,
            order_id=event.order_id,
            sku=event.sku,
            quantity=event.quantity,
            attempt=event.attempt,
            extra={"machine_id": event.target_machine, "duration_seconds": duration_seconds},
        )


cnc_simulator = CncSimulator()