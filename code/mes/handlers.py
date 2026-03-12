"""MES Event Handlers Module

This module contains event handlers for the Manufacturing Execution System (MES).
It routes incoming events from various sources (orders, CNC, quality) to the
MES service for orchestration and processing.
"""
from mes.service import mes_service


async def handle_order_created(event: dict) -> None:
    """Handle an order creation event.
    
    Called when a new order is created in the system. Triggers MES orchestration
    to plan and schedule the manufacturing work.
    
    Args:
        event: The OrderCreatedEvent payload as a dictionary
    """
    await mes_service.handle_order_created(event)


async def handle_cnc_job_completed(event: dict) -> None:
    """Handle a CNC job completion event.
    
    Called when a CNC machining operation completes for a work order.
    Advances the work order through its manufacturing workflow.
    
    Args:
        event: The CncJobCompletedEvent payload as a dictionary
    """
    await mes_service.handle_cnc_job_completed(event)


async def handle_quality_inspection_completed(event: dict) -> None:
    """Handle a quality inspection completion event.
    
    Called when a quality inspection is completed for a work order.
    Determines whether to pass, fail, or schedule rework based on inspection results.
    
    Args:
        event: The QualityInspectionCompletedEvent payload as a dictionary
    """
    await mes_service.handle_quality_inspection_completed(event)