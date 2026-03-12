"""
This module defines the event handlers for the manufacturing execution system (MES).
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