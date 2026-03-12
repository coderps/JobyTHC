"""CNC Job Orchestrator Module

This module handles the orchestration of CNC job completion events.
It routes completed CNC jobs to quality inspection for verification.
"""
import structlog
from contracts.common import EventMetadata
from contracts.cnc_events import CncJobCompletedEvent
from contracts.quality_events import QualityInspectionRequestedEvent
from infrastructure.publisher import publisher
from mes.store import mes_store
from mes.utils import set_status

logger = structlog.get_logger()


class CncOrchestrator:
    """Orchestrates the workflow after CNC machining completes.
    
    Routes completed CNC jobs to quality inspection for verification.
    Maintains the flow: CNC_REQUESTED -> QUALITY_REQUESTED -> quality inspection
    """

    async def handle_cnc_job_completed(self, raw_event: dict) -> None:
        """Handle a CNC job completion event.
        
        When CNC machining completes for a work order, this handler:
        1. Updates the work order status to QUALITY_REQUESTED
        2. Publishes a quality inspection request
        
        Args:
            raw_event: The raw CncJobCompletedEvent payload as a dictionary
        """
        # Validate and parse the incoming event
        event = CncJobCompletedEvent.model_validate(raw_event)
        
        # Retrieve the work order from store
        workorder = mes_store.get(event.workorder_id)
        
        # Update status to indicate quality inspection is next
        set_status(workorder, "QUALITY_REQUESTED")

        logger.info(
            "mes_quality_requested",
            workorder_id=workorder.workorder_id,
            quantity=event.quantity,
            attempt=event.attempt,
        )

        # Request quality inspection for the machined parts
        await publisher.publish(
            "quality.inspection.requested",
            QualityInspectionRequestedEvent(
                metadata=EventMetadata(
                    event_type="quality.inspection.requested",
                    correlation_id=event.metadata.correlation_id,
                ),
                workorder_id=workorder.workorder_id,
                order_id=workorder.order_id,
                sku=workorder.sku,
                quantity=event.quantity,
                attempt=event.attempt,
            ),
        )


# Singleton instance
cnc_orchestrator = CncOrchestrator()
