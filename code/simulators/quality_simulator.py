import asyncio
import random

import structlog

from contracts.common import EventMetadata
from contracts.quality_events import (
    QualityInspectionRequestedEvent,
    QualityInspectionCompletedEvent,
    FailureReason,
)
from infrastructure.publisher import publisher
from observability.demo_log import demo_step

logger = structlog.get_logger()


class QualitySimulator:
    async def handle_quality_inspection_requested(self, raw_event: dict) -> None:
        event = QualityInspectionRequestedEvent.model_validate(raw_event)

        logger.info(
            "quality_inspection_received",
            workorder_id=event.workorder_id,
            quantity=event.quantity,
            attempt=event.attempt,
        )

        duration_seconds = random.randint(1, 3)
        logger.info(
            "quality_processing",
            workorder_id=event.workorder_id,
            sleep_seconds=duration_seconds,
            attempt=event.attempt,
        )

        await asyncio.sleep(duration_seconds)

        if event.attempt == 1 and event.quantity >= 2:
            passed_quantity = event.quantity - 1
            failed_quantity = 1
            disposition = "PARTIAL_REWORK"
            failure_reasons = [
                FailureReason(qty=1, reason="diameter_out_of_tolerance")
            ]
        else:
            passed_quantity = event.quantity
            failed_quantity = 0
            disposition = "PASS"
            failure_reasons = []

        await publisher.publish(
            "quality.inspection.completed",
            QualityInspectionCompletedEvent(
                metadata=EventMetadata(
                    event_type="quality.inspection.completed",
                    correlation_id=event.metadata.correlation_id,
                ),
                workorder_id=event.workorder_id,
                order_id=event.order_id,
                sku=event.sku,
                inspected_quantity=event.quantity,
                passed_quantity=passed_quantity,
                failed_quantity=failed_quantity,
                disposition=disposition,
                failure_reasons=failure_reasons,
                attempt=event.attempt,
            ),
        )

        logger.info(
            "quality_inspection_completed",
            workorder_id=event.workorder_id,
            inspected_quantity=event.quantity,
            passed_quantity=passed_quantity,
            failed_quantity=failed_quantity,
            disposition=disposition,
            attempt=event.attempt,
        )

        demo_step(
            step="QUALITY_COMPLETED",
            workorder_id=event.workorder_id,
            order_id=event.order_id,
            sku=event.sku,
            quantity=event.quantity,
            attempt=event.attempt,
            extra={
                "passed_quantity": passed_quantity,
                "failed_quantity": failed_quantity,
                "disposition": disposition,
            },
        )


quality_simulator = QualitySimulator()