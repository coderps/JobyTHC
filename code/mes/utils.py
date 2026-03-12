"""MES Utility Functions Module

This module provides shared utility functions used across the MES orchestration system.
It includes helpers for work order ID generation, status management, and common operations.
"""
import uuid
import structlog

logger = structlog.get_logger()


def new_workorder_id() -> str:
    """Generate a new unique work order identifier.
    
    Creates a work order ID with a human-readable prefix and a random hex suffix.
    This logic currently does not guarantee uniqueness across the system but is sufficient for this simulation.
    
    Returns:
        A work order ID in the format "WO-{random_hex}" (e.g., "WO-A1B2C3D4")
    """
    return f"WO-{uuid.uuid4().hex[:8].upper()}"


def set_status(workorder, new_status: str) -> None:
    """Update a work order's status with logging.
    
    Changes the work order status and logs the transition for observability.
    
    Args:
        workorder: The WorkOrder object to update
        new_status: The new status value
    """
    old_status = workorder.status
    workorder.status = new_status
    logger.info(
        "workorder_state_changed",
        workorder_id=workorder.workorder_id,
        order_id=workorder.order_id,
        sku=workorder.sku,
        from_status=old_status,
        to_status=new_status,
    )
