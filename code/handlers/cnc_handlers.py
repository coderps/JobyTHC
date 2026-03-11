import structlog

logger = structlog.get_logger()


async def handle_cnc_completed(event):
    workorder_id = event["workorder_id"]

    logger.info(
        "cnc_completed_trigger_quality",
        workorder_id=workorder_id
    )

    # later:
    # emit quality.inspection.requested