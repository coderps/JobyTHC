import structlog

logger = structlog.get_logger()


async def handle_inventory_updated(event: dict) -> None:
    logger.info(
        "inventory_observed_update",
        workorder_id=event.get("workorder_id"),
        order_id=event.get("order_id"),
        sku=event.get("sku"),
        quantity_added=event.get("quantity_added"),
    )


async def handle_assembly_job_requested(event: dict) -> None:
    logger.info(
        "assembly_observed_request",
        workorder_id=event.get("workorder_id"),
        order_id=event.get("order_id"),
        sku=event.get("sku"),
        quantity=event.get("quantity"),
    )