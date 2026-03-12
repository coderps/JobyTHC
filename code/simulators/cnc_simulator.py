"""CNC Simulator Module

This module simulates a CNC (Computer Numerical Control) machine that processes manufacturing jobs.
It listens for CNC job requests, simulates the machining process, and publishes job completion events.
Used for testing and demonstration of the manufacturing workflow without real hardware.
"""
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
    """Simulates a CNC machine processing manufacturing jobs.
    
    This simulator handles CNC job requests by:
    1. Publishing a job started event
    2. Simulating processing (random delay between 2-4 seconds)
    3. Publishing a job completed event
    
    This allows testing the end-to-end manufacturing workflow without actual hardware.
    """

    async def handle_cnc_job_requested(self, raw_event: dict) -> None:
        """Handle a CNC job request and simulate the machining process.
        
        Simulates the complete lifecycle of a CNC machining job:
        1. Logs the job received
        2. Publishes job started event
        3. Sleeps to simulate processing (2-4 seconds)
        4. Publishes job completed event
        
        Args:
            raw_event: The CncJobRequestedEvent payload as a dictionary
        """
        # Validate and parse the incoming CNC job request
        event = CncJobRequestedEvent.model_validate(raw_event)
        
        # Log demo step for demonstration purposes
        demo_step(
            step="CNC_PROCESSING_STARTED",
            workorder_id=event.workorder_id,
            order_id=event.order_id,
            sku=event.sku,
            quantity=event.quantity,
            attempt=event.attempt,
            extra={"machine_id": event.target_machine},
        )

        # Log the job receipt
        logger.info(
            "cnc_job_received",
            workorder_id=event.workorder_id,
            quantity=event.quantity,
            machine=event.target_machine,
            attempt=event.attempt,
        )

        # Publish job started event to indicate machining has begun
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

        # Simulate machining time with random duration (2-4 seconds)
        duration_seconds = random.randint(2, 4)
        logger.info(
            "cnc_processing",
            workorder_id=event.workorder_id,
            sleep_seconds=duration_seconds,
            attempt=event.attempt,
        )

        # Sleep to simulate actual machining time
        await asyncio.sleep(duration_seconds)

        # Publish job completed event with results
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

        # Log job completion
        logger.info(
            "cnc_job_completed",
            workorder_id=event.workorder_id,
            quantity=event.quantity,
            machine=event.target_machine,
            attempt=event.attempt,
        )

        # Log demo step for demonstration purposes
        demo_step(
            step="CNC_PROCESSING_COMPLETED",
            workorder_id=event.workorder_id,
            order_id=event.order_id,
            sku=event.sku,
            quantity=event.quantity,
            attempt=event.attempt,
            extra={"machine_id": event.target_machine, "duration_seconds": duration_seconds},
        )


# Singleton instance of CncSimulator used throughout the application
cnc_simulator = CncSimulator()