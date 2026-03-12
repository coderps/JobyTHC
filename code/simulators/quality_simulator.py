"""Quality Inspection Simulator Module

This module simulates a quality inspection station that validates machined parts.
It listens for quality inspection requests, simulates the inspection process, and
publishes quality inspection completion events with pass/fail results.

Used for testing and demonstration of the manufacturing workflow without real quality controls.
"""
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
    """Simulates a quality inspection station that validates machined parts.
    
    This simulator handles quality inspection requests by:
    1. Logging the inspection received
    2. Simulating inspection processing (random delay between 1-3 seconds)
    3. Determining pass/fail results based on configured rules:
       - On first attempt with 2+ units: 1 unit fails (triggers rework), rest pass (PARTIAL_REWORK)
       - Otherwise: all units pass (PASS)
    4. Publishing quality inspection completed event with results
    
    This allows testing the end-to-end manufacturing workflow including rework scenarios.
    """

    async def handle_quality_inspection_requested(self, raw_event: dict) -> None:
        """Handle a quality inspection request and simulate the inspection process.
        
        Simulates the complete lifecycle of a quality inspection:
        1. Receives and logs inspection request
        2. Sleeps to simulate inspection (1-3 seconds)
        3. Determines inspection results based on attempt number and quantity
        4. Publishes inspection completed event with results
        
        The simulation is designed to test rework scenarios:
        - First inspection attempt: 1 unit fails if quantity >= 2 (triggers rework)
        - Subsequent attempts: all units pass (successful rework)
        
        Args:
            raw_event: The QualityInspectionRequestedEvent payload as a dictionary
        """
        # Validate and parse the incoming quality inspection request
        event = QualityInspectionRequestedEvent.model_validate(raw_event)

        # Log the inspection request received
        logger.info(
            "quality_inspection_received",
            workorder_id=event.workorder_id,
            quantity=event.quantity,
            attempt=event.attempt,
        )

        # Simulate inspection time with random duration (1-3 seconds)
        duration_seconds = random.randint(1, 3)
        logger.info(
            "quality_processing",
            workorder_id=event.workorder_id,
            sleep_seconds=duration_seconds,
            attempt=event.attempt,
        )

        # Sleep to simulate actual inspection time
        await asyncio.sleep(duration_seconds)

        # Determine inspection results based on attempt number and quantity
        # On first attempt with 2+ units, simulate a defect that triggers rework
        if event.attempt == 1 and event.quantity >= 2:
            # First attempt: 1 unit fails due to out-of-tolerance diameter
            passed_quantity = event.quantity - 1
            failed_quantity = 1
            disposition = "PARTIAL_REWORK"
            failure_reasons = [
                FailureReason(qty=1, reason="diameter_out_of_tolerance")
            ]
        else:
            # Subsequent attempts or single-unit orders: all units pass
            passed_quantity = event.quantity
            failed_quantity = 0
            disposition = "PASS"
            failure_reasons = []

        # Publish quality inspection completed event with results
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

        # Log inspection completion with results
        logger.info(
            "quality_inspection_completed",
            workorder_id=event.workorder_id,
            inspected_quantity=event.quantity,
            passed_quantity=passed_quantity,
            failed_quantity=failed_quantity,
            disposition=disposition,
            attempt=event.attempt,
        )

        # Log demo step for demonstration purposes
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


# Singleton instance of QualitySimulator used throughout the application
quality_simulator = QualitySimulator()