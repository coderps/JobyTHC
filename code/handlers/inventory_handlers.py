import structlog

logger = structlog.get_logger()


async def handle_inventory_reserved(event):
    order_id = event["order_id"]

    logger.info(
        "inventory_reserved_starting_cnc",
        order_id=order_id
    )

    # later:
    # emit cnc.job.requested