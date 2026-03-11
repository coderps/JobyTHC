from mes.service import mes_service


async def handle_order_created(event: dict) -> None:
    await mes_service.handle_order_created(event)


async def handle_cnc_job_completed(event: dict) -> None:
    await mes_service.handle_cnc_job_completed(event)


async def handle_quality_inspection_completed(event: dict) -> None:
    await mes_service.handle_quality_inspection_completed(event)