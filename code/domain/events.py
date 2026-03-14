"""
Event Subscription Module for Manufacturing Execution System (MES)

This module defines and manages all event subscriptions for the MES system.
It coordinates event handlers for core manufacturing workflows, simulated external systems,
and observability/monitoring components.

Key Events in the Manufacturing Workflow:

Core MES Events (Processed by MES):
- order.created: ERP publishes new customer orders with inventory reservation details
- cnc.job.completed: CNC machine completes machining with duration and status
- quality.inspection.completed: Quality system reports inspection results with pass/fail details

MES Output Events (Published by MES):
- mes.workorder.created: MES creates internal work orders from customer orders
- cnc.job.requested: MES requests CNC machining for work orders
- quality.inspection.requested: MES requests quality inspection after CNC completion
- wms.inventory.updated: MES updates inventory when parts pass quality inspection
- assembly.job.requested: MES forwards passed parts to assembly station

Simulated External System Events:
- cnc.job.started: CNC machine begins processing a machining job (simulated response)
- cnc.job.requested: Triggers CNC simulator to start machining job
- quality.inspection.requested: Triggers quality simulator to perform inspection

Observability Events (Logged for monitoring):
- wms.inventory.updated: Inventory changes logged for audit trail
- assembly.job.requested: Assembly requests logged for workflow visibility
"""
import asyncio

from infrastructure.subscribers import JetStreamSubscriber
from mes.handlers import (
    handle_order_created,
    handle_cnc_job_completed,
    handle_quality_inspection_completed,
)
from simulators.cnc_simulator import cnc_simulator
from simulators.quality_simulator import quality_simulator
from simulators.downstream_observers import (
    handle_inventory_updated,
    handle_assembly_job_requested,
)

# This module defines the event handlers for the manufacturing execution system (MES)
# It includes handlers for core MES events, simulated external system responses, and demo observers
# The handlers are designed to be registered with an event subscriber to process incoming events
async def subscribe_events(subscriber: JetStreamSubscriber):
    await asyncio.gather(
        # MES event handlers - process core manufacturing events
        subscriber.subscribe(
            "order.created", 
            "mes-order-created", 
            handle_order_created,
        ),
        subscriber.subscribe(
            "cnc.job.completed", 
            "mes-cnc-completed", 
            handle_cnc_job_completed,
        ),
        subscriber.subscribe(
            "quality.inspection.completed", 
            "mes-quality-completed", 
            handle_quality_inspection_completed,
        ),

        # Simulated external systems - simulate CNC and quality inspection responses
        subscriber.subscribe(
            "cnc.job.requested",
            "sim-cnc-job-requested",
            cnc_simulator.handle_cnc_job_requested,
        ),
        subscriber.subscribe(
            "quality.inspection.requested",
            "sim-quality-requested",
            quality_simulator.handle_quality_inspection_requested,
        ),

        # Demo observers - log key events for visibility and audit trail
        subscriber.subscribe(
            "wms.inventory.updated",
            "obs-inventory-updated",
            handle_inventory_updated,
        ),
        subscriber.subscribe(
            "assembly.job.requested",
            "obs-assembly-requested",
            handle_assembly_job_requested,
        ),
    )