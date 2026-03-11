import random
import uuid

import structlog
from observability.demo_log import demo_step
from contracts.common import EventMetadata
from contracts.order_events import OrderCreatedEvent
from contracts.cnc_events import CncJobRequestedEvent, CncJobCompletedEvent
from contracts.quality_events import (
    QualityInspectionRequestedEvent,
    QualityInspectionCompletedEvent,
)
from infrastructure.publisher import publisher
from mes.models import WorkOrder
from mes.store import mes_store

logger = structlog.get_logger()


class MesOrchestratorService:
    def _set_status(self, workorder, new_status: str) -> None:
        old_status = workorder.status
        workorder.status = new_status
        logger.info(
            "workorder_state_changed",
            workorder_id=workorder.workorder_id,
            order_id=workorder.order_id,
            sku=workorder.sku,
            from_status=old_status,
            to_status=new_status,
        )

    async def handle_order_created(self, raw_event: dict) -> None:
        event = OrderCreatedEvent.model_validate(raw_event)
        demo_step(
            step="ORDER_CREATED_RECEIVED",
            order_id=event.order.order_id,
            sku=event.product.sku,
            quantity=event.product.quantity,
        )

        workorder = WorkOrder(
            workorder_id=self._new_workorder_id(),
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
        mes_store.save(workorder)

        logger.info(
            "mes_workorder_created",
            workorder_id=workorder.workorder_id,
            order_id=workorder.order_id,
            sku=workorder.sku,
            target_quantity=workorder.target_quantity,
        )

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
                quantity=workorder.remaining_quantity,
                target_machine=f"CNC-{random.randint(1, 3):02d}",
                attempt=1,
            ),
        )

        logger.info(
            "mes_cnc_job_dispatched",
            workorder_id=workorder.workorder_id,
            quantity=workorder.remaining_quantity,
            attempt=1,
        )

        demo_step(
            step="CNC_JOB_DISPATCHED",
            workorder_id=workorder.workorder_id,
            order_id=workorder.order_id,
            sku=workorder.sku,
            quantity=workorder.remaining_quantity,
            attempt=1,
        )

    async def handle_cnc_job_completed(self, raw_event: dict) -> None:
        event = CncJobCompletedEvent.model_validate(raw_event)
        workorder = mes_store.get(event.workorder_id)
        self._set_status(workorder, "QUALITY_REQUESTED")

        logger.info(
            "mes_quality_requested",
            workorder_id=workorder.workorder_id,
            quantity=event.quantity,
            attempt=event.attempt,
        )

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

    async def handle_quality_inspection_completed(self, raw_event: dict) -> None:
        event = QualityInspectionCompletedEvent.model_validate(raw_event)
        workorder = mes_store.get(event.workorder_id)

        workorder.passed_quantity += event.passed_quantity
        workorder.failed_quantity += event.failed_quantity
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

        if event.passed_quantity > 0:
            await publisher.publish(
                "inventory.updated",
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

        if workorder.passed_quantity >= workorder.target_quantity:
            self._set_status(workorder, "COMPLETED")

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
            return

        if event.failed_quantity > 0 and workorder.rework_count < workorder.max_rework_attempts:
            workorder.rework_count += 1
            self._set_status(workorder, "REWORK_REQUESTED")

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
            return

        if workorder.remaining_quantity > 0:
            self._set_status(workorder, "FAILED")

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

    def _new_workorder_id(self) -> str:
        return f"WO-{uuid.uuid4().hex[:8].upper()}"


mes_service = MesOrchestratorService()