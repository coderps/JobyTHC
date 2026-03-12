"""Quality Inspection Orchestrator Module

This module handles the orchestration of quality inspection completion events.
It's the most complex orchestrator, managing multiple branching paths:
- Forward passed parts to assembly and inventory
- Schedule rework for failed parts
- Handle work order completion or failure
"""
import random
import structlog
from observability.demo_log import demo_step
from contracts.common import EventMetadata
from contracts.cnc_events import CncJobRequestedEvent
from contracts.quality_events import QualityInspectionCompletedEvent
from infrastructure.publisher import publisher
from mes.store import mes_store
from mes.utils import set_status

logger = structlog.get_logger()


class QualityOrchestrator:
    """Orchestrates quality inspection results and downstream actions.
    
    Handles the quality inspection completion workflow with multiple decision paths:
    - If parts passed: forward to assembly and update inventory
    - If work order complete: publish completion event
    - If rework needed: schedule CNC rework
    - If max rework exceeded: mark work order as failed
    """

    async def handle_quality_inspection_completed(self, raw_event: dict) -> None:
        """Handle a quality inspection completion event.
        
        Coordinates multiple actions based on inspection results:
        1. Updates work order with inspection results
        2. Routes passed parts to assembly
        3. Manages rework scheduling
        4. Handles completion or failure scenarios
        
        Args:
            raw_event: The raw QualityInspectionCompletedEvent payload as a dictionary
        """
        # Validate and parse the incoming event
        event = QualityInspectionCompletedEvent.model_validate(raw_event)
        
        # Retrieve the work order from store
        workorder = mes_store.get(event.workorder_id)

        # Update work order quantities based on inspection results
        workorder.passed_quantity += event.passed_quantity
        workorder.failed_quantity += event.failed_quantity
        # Calculate remaining quantity to reach target
        workorder.remaining_quantity = workorder.target_quantity - workorder.passed_quantity

        logger.info(
            "mes_quality_result_received",
            workorder_id=workorder.workorder_id,
            inspected_quantity=event.inspected_quantity,
            passed_quantity=event.passed_quantity,
            failed_quantity=event.failed_quantity,
            total_passed=workorder.passed_quantity,
            total_failed=workorder.failed_quantity,
            remaining_quantity=workorder.remaining_quantity,
            attempt=event.attempt,
        )

        demo_step(
            step="QUALITY_RESULT_EVALUATED",
            workorder_id=workorder.workorder_id,
            order_id=workorder.order_id,
            sku=workorder.sku,
            attempt=event.attempt,
            extra={
                "inspected_quantity": event.inspected_quantity,
                "passed_quantity": event.passed_quantity,
                "failed_quantity": event.failed_quantity,
                "total_passed": workorder.passed_quantity,
                "remaining_quantity": workorder.remaining_quantity,
                "disposition": event.disposition,
            },
        )

        # Branch 1: Handle passed parts (if any)
        if event.passed_quantity > 0:
            await self._handle_passed_parts(workorder, event)

        # Branch 2: Check if work order is complete
        if workorder.passed_quantity >= workorder.target_quantity:
            await self._handle_workorder_completed(workorder)
            return

        # Branch 3: Handle failed parts and rework scheduling
        if event.failed_quantity > 0 and workorder.rework_count < workorder.max_rework_attempts:
            await self._handle_rework_scheduling(workorder, event)
            return

        # Branch 4: Handle failure (no more rework attempts)
        if workorder.remaining_quantity > 0:
            await self._handle_workorder_failed(workorder)

    async def _handle_passed_parts(self, workorder, event: QualityInspectionCompletedEvent) -> None:
        """Handle workflow for parts that passed quality inspection.
        
        Updates inventory and routes parts to assembly for further processing.
        
        Args:
            workorder: The WorkOrder containing passed parts
            event: The quality inspection completion event
        """
        # Publish inventory update for passed parts
        await publisher.publish(
            "wms.inventory.updated",
            {
                "workorder_id": workorder.workorder_id,
                "order_id": workorder.order_id,
                "sku": workorder.sku,
                "quantity_added": event.passed_quantity,
            },
        )

        logger.info(
            "mes_inventory_updated",
            workorder_id=workorder.workorder_id,
            quantity_added=event.passed_quantity,
        )

        # Route passed parts to assembly station
        await publisher.publish(
            "assembly.job.requested",
            {
                "workorder_id": workorder.workorder_id,
                "order_id": workorder.order_id,
                "sku": workorder.sku,
                "quantity": event.passed_quantity,
            },
        )

        logger.info(
            "mes_forwarded_to_assembly",
            workorder_id=workorder.workorder_id,
            quantity=event.passed_quantity,
        )

        demo_step(
            step="ASSEMBLY_FORWARDED",
            workorder_id=workorder.workorder_id,
            order_id=workorder.order_id,
            sku=workorder.sku,
            quantity=event.passed_quantity,
        )

    async def _handle_workorder_completed(self, workorder) -> None:
        """Handle workflow when work order reaches target quantity.
        
        Marks work order as completed and publishes completion event.
        
        Args:
            workorder: The completed WorkOrder
        """
        set_status(workorder, "COMPLETED")

        # Publish workorder completion event
        await publisher.publish(
            "mes.workorder.completed",
            {
                "workorder_id": workorder.workorder_id,
                "order_id": workorder.order_id,
                "sku": workorder.sku,
                "target_quantity": workorder.target_quantity,
                "passed_quantity": workorder.passed_quantity,
            },
        )

        demo_step(
            step="WORKORDER_COMPLETED",
            workorder_id=workorder.workorder_id,
            order_id=workorder.order_id,
            sku=workorder.sku,
            quantity=workorder.passed_quantity,
            status=workorder.status,
        )

        logger.info(
            "mes_workorder_completed",
            workorder_id=workorder.workorder_id,
            target_quantity=workorder.target_quantity,
            passed_quantity=workorder.passed_quantity,
        )

    async def _handle_rework_scheduling(self, workorder, event: QualityInspectionCompletedEvent) -> None:
        """Handle workflow for scheduling rework of failed parts.
        
        Increments rework count and dispatches a new CNC job for failed parts,
        unless maximum rework attempts have been exceeded.
        
        Args:
            workorder: The WorkOrder with failed parts to rework
            event: The quality inspection completion event
        """
        # Increment rework attempt counter
        workorder.rework_count += 1
        set_status(workorder, "REWORK_REQUESTED")

        # Publish rework request event
        await publisher.publish(
            "mes.rework.requested",
            {
                "workorder_id": workorder.workorder_id,
                "failed_quantity": event.failed_quantity,
                "rework_count": workorder.rework_count,
            },
        )

        logger.info(
            "mes_rework_requested",
            workorder_id=workorder.workorder_id,
            failed_quantity=event.failed_quantity,
            rework_count=workorder.rework_count,
        )

        demo_step(
            step="REWORK_REQUESTED",
            workorder_id=workorder.workorder_id,
            order_id=workorder.order_id,
            sku=workorder.sku,
            quantity=event.failed_quantity,
            attempt=workorder.rework_count + 1,
        )

        # Dispatch new CNC job for rework
        await publisher.publish(
            "cnc.job.requested",
            CncJobRequestedEvent(
                metadata=EventMetadata(
                    event_type="cnc.job.requested",
                    correlation_id=event.metadata.correlation_id,
                ),
                workorder_id=workorder.workorder_id,
                order_id=workorder.order_id,
                sku=workorder.sku,
                quantity=event.failed_quantity,
                # Randomly select from 3 CNC machines
                target_machine=f"CNC-{random.randint(1, 3):02d}",
                attempt=workorder.rework_count + 1,
            ),
        )

        logger.info(
            "mes_cnc_rework_dispatched",
            workorder_id=workorder.workorder_id,
            quantity=event.failed_quantity,
            attempt=workorder.rework_count + 1,
        )

    async def _handle_workorder_failed(self, workorder) -> None:
        """Handle workflow when work order fails (rework exhausted).
        
        Marks work order as failed after maximum rework attempts exceeded.
        
        Args:
            workorder: The failed WorkOrder
        """
        set_status(workorder, "FAILED")

        # Publish workorder failure event
        await publisher.publish(
            "mes.workorder.failed",
            {
                "workorder_id": workorder.workorder_id,
                "order_id": workorder.order_id,
                "sku": workorder.sku,
                "passed_quantity": workorder.passed_quantity,
                "failed_quantity": workorder.failed_quantity,
                "remaining_quantity": workorder.remaining_quantity,
            },
        )

        logger.info(
            "mes_workorder_failed",
            workorder_id=workorder.workorder_id,
            remaining_quantity=workorder.remaining_quantity,
        )


# Singleton instance
quality_orchestrator = QualityOrchestrator()
