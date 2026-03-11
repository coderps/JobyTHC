import structlog

logger = structlog.get_logger()


def demo_step(
    step: str,
    workorder_id: str | None = None,
    order_id: str | None = None,
    sku: str | None = None,
    quantity: int | None = None,
    attempt: int | None = None,
    status: str | None = None,
    extra: dict | None = None,
) -> None:
    payload = {
        "step": step,
        "workorder_id": workorder_id,
        "order_id": order_id,
        "sku": sku,
        "quantity": quantity,
        "attempt": attempt,
        "status": status,
    }

    if extra:
        payload.update(extra)

    logger.info("demo_timeline", **{k: v for k, v in payload.items() if v is not None})