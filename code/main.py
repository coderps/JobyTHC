import asyncio
import structlog

from infrastructure.nats import nats_connection
from infrastructure.streams import JetStreamStreamManager
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

logger = structlog.get_logger()


async def main() -> None:
    await nats_connection.connect()

    stream_manager = JetStreamStreamManager()
    await stream_manager.reset_streams()
    await stream_manager.ensure_streams()

    subscriber = JetStreamSubscriber()

    logger.info("mes_poc_started_clean")

    await asyncio.gather(
        # MES
        subscriber.subscribe("order.created", "mes-order-created", handle_order_created),
        subscriber.subscribe("cnc.job.completed", "mes-cnc-completed", handle_cnc_job_completed),
        subscriber.subscribe(
            "quality.inspection.completed",
            "mes-quality-completed",
            handle_quality_inspection_completed,
        ),

        # Simulated external systems
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

        # Observers for demo logs
        subscriber.subscribe(
            "inventory.updated",
            "obs-inventory-updated",
            handle_inventory_updated,
        ),
        subscriber.subscribe(
            "assembly.job.requested",
            "obs-assembly-requested",
            handle_assembly_job_requested,
        ),
    )


if __name__ == "__main__":
    asyncio.run(main())