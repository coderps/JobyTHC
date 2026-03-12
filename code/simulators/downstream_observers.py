"""Downstream Event Observers Module

This module contains observer handlers for downstream manufacturing events.
These observers provide observability into key system events like inventory updates
and assembly job requests by logging them in a structured format.

These are "observer" or "monitor" handlers that don't modify state but provide
visibility into the system's operation for debugging and monitoring purposes.
"""
import structlog

logger = structlog.get_logger()


async def handle_inventory_updated(event: dict) -> None:
    """Handle an inventory update event.
    
    Logs when inventory has been updated due to quality inspection completion.
    This provides visibility into inventory changes throughout the manufacturing process.
    
    Args:
        event: The inventory.updated event payload as a dictionary with keys:
            - workorder_id: The work order ID
            - order_id: The original order ID
            - sku: The product SKU
            - quantity_added: Number of units added to inventory
    """
    # Log the inventory update event with relevant details for observability
    logger.info(
        "inventory_observed_update",
        workorder_id=event.get("workorder_id"),
        order_id=event.get("order_id"),
        sku=event.get("sku"),
        quantity_added=event.get("quantity_added"),
    )


async def handle_assembly_job_requested(event: dict) -> None:
    """Handle an assembly job request event.
    
    Logs when parts are forwarded to the assembly station after passing quality inspection.
    This provides visibility into parts moving through the manufacturing workflow.
    
    Args:
        event: The assembly.job.requested event payload as a dictionary with keys:
            - workorder_id: The work order ID
            - order_id: The original order ID
            - sku: The product SKU
            - quantity: Number of units being sent to assembly
    """
    # Log the assembly job request event with relevant details for observability
    logger.info(
        "assembly_observed_request",
        workorder_id=event.get("workorder_id"),
        order_id=event.get("order_id"),
        sku=event.get("sku"),
        quantity=event.get("quantity"),
    )