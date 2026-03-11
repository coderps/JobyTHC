import structlog

logger = structlog.get_logger()


async def handle_order_accepted(event):
    order_id = event["order_id"]

    logger.info(
        "mes_creating_workorder",
        order_id=order_id
    )

    # later:
    # emit inventory.check.requested