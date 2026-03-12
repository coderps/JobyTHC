"""Order Orchestrator Module

This module handles the orchestration of manufacturing work orders created from incoming orders.
It manages the initial work order creation and CNC job dispatch workflow.
"""
import random
import structlog
from observability.demo_log import demo_step
from contracts.common import EventMetadata
from contracts.order_events import OrderCreatedEvent
from contracts.cnc_events import CncJobRequestedEvent
from infrastructure.publisher import publisher
from mes.models import WorkOrder
from mes.store import mes_store
from mes.utils import new_workorder_id, set_status

logger = structlog.get_logger()


class OrderOrchestrator:
    """Orchestrates the creation and dispatch of work orders from incoming orders.
    
    Handles the initial stages of manufacturing flow:
    1. Creates a new work order from an order
    2. Saves it to the store
    3. Publishes workorder.created event
    4. Dispatches initial CNC job request
    """

    async def handle_order_created(self, raw_event: dict) -> None:
        """Handle an incoming order creation event.
        
        Creates a new manufacturing work order, saves it, and initiates the
        CNC machining workflow by publishing a CNC job request.
        
        Args:
            raw_event: The raw OrderCreatedEvent payload as a dictionary
        """
        # Validate and parse the incoming event
        event = OrderCreatedEvent.model_validate(raw_event)
        demo_step(
            step="ORDER_CREATED_RECEIVED",
            order_id=event.order.order_id,
            sku=event.product.sku,
            quantity=event.product.quantity,
        )

        # Create a new work order with initial state
        workorder = WorkOrder(
            workorder_id=new_workorder_id(),
            order_id=event.order.order_id,
            sku=event.product.sku,
            target_quantity=event.product.quantity,
            passed_quantity=0,
            failed_quantity=0,
            remaining_quantity=event.product.quantity,
            routing=event.manufacturing.routing,
            reserved_parts=[part.model_dump() for part in event.inventory_reservation.reserved_parts],
            status="CNC_REQUESTED",
            rework_count=0,
            max_rework_attempts=2,
        )
        # Persist the new work order
        mes_store.save(workorder)

        logger.info(
            "mes_workorder_created",
            workorder_id=workorder.workorder_id,
            order_id=workorder.order_id,
            sku=workorder.sku,
            target_quantity=workorder.target_quantity,
        )

        # Publish workorder.created event for downstream listeners
        await publisher.publish(
            "mes.workorder.created",
            {
                "workorder_id": workorder.workorder_id,
                "order_id": workorder.order_id,
                "sku": workorder.sku,
                "target_quantity": workorder.target_quantity,
                "status": workorder.status,
            },
        )

        demo_step(
            step="WORKORDER_CREATED",
            workorder_id=workorder.workorder_id,
            order_id=workorder.order_id,
            sku=workorder.sku,
            quantity=workorder.target_quantity,
            status=workorder.status,
        )

        # Dispatch initial CNC job request for this work order
        await self._dispatch_cnc_job(workorder, event.metadata.correlation_id, attempt=1)

    async def _dispatch_cnc_job(self, workorder: WorkOrder, correlation_id: str, attempt: int) -> None:
        """Dispatch a CNC job request for the work order.
        
        Publishes a CNC job request to start machining of the work order.
        
        Args:
            workorder: The WorkOrder to machine
            correlation_id: The correlation ID from the original order event
            attempt: The attempt number (1 for initial, >1 for rework)
        """
        # Publish CNC job request event
        await publisher.publish(
            "cnc.job.requested",
            CncJobRequestedEvent(
                metadata=EventMetadata(
                    event_type="cnc.job.requested",
                    correlation_id=correlation_id,
                ),
                workorder_id=workorder.workorder_id,
                order_id=workorder.order_id,
                sku=workorder.sku,
                quantity=workorder.remaining_quantity,
                # Randomly select from 3 CNC machines
                # In a real system, this would be based on scheduling logic and machine availability
                target_machine=f"CNC-{random.randint(1, 3):02d}",
                attempt=attempt,
            ),
        )

        logger.info(
            "mes_cnc_job_dispatched",
            workorder_id=workorder.workorder_id,
            quantity=workorder.remaining_quantity,
            attempt=attempt,
        )

        demo_step(
            step="CNC_JOB_DISPATCHED",
            workorder_id=workorder.workorder_id,
            order_id=workorder.order_id,
            sku=workorder.sku,
            quantity=workorder.remaining_quantity,
            attempt=attempt,
        )


# Singleton instance
order_orchestrator = OrderOrchestrator()
