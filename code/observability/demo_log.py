"""Demo Timeline Logging Module

This module provides observability into the manufacturing workflow for demonstration purposes.
It logs significant workflow steps to help visualize and track the progression of orders
through the system from creation to completion.

The demo_step function creates a human-readable timeline of key events in the manufacturing process,
making it easy to understand the flow of work and identify bottlenecks or issues.
"""
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
    """Log a significant step in the manufacturing workflow timeline.
    
    Creates a structured log entry for a workflow milestone, making it easy to trace
    the progression of orders through the system. Used for demonstration and debugging.
    
    Parameters:
        step: The name of the workflow step (e.g., "ORDER_CREATED_RECEIVED", "CNC_PROCESSING_STARTED")
        workorder_id: Unique identifier for the manufacturing work order
        order_id: The original customer order ID this work order belongs to
        sku: Product SKU being manufactured
        quantity: Number of units in this step
        attempt: The attempt number for rework scenarios
        status: Current status of the work order (e.g., "CNC_REQUESTED", "COMPLETED")
        extra: Dictionary of additional key-value pairs to include in the log
    """
    # Build the base payload with core fields
    payload = {
        "step": step,
        "workorder_id": workorder_id,
        "order_id": order_id,
        "sku": sku,
        "quantity": quantity,
        "attempt": attempt,
        "status": status,
    }

    # Add any extra fields provided (e.g., machine_id, duration_seconds)
    if extra:
        payload.update(extra)

    # Log the step with only non-None values to keep logs clean and focused
    logger.info("demo_timeline", **{k: v for k, v in payload.items() if v is not None})