"""
MES Models

This module defines the data models used in the Manufacturing Execution System (MES).
These models represent the core entities and their states during manufacturing processes.
"""

from dataclasses import dataclass


@dataclass
class WorkOrder:
    """Represents a manufacturing work order in the MES system.

    A work order encapsulates all the information needed to execute a manufacturing job,
    including quantities, routing, parts reservation, and quality tracking.

    Attributes:
        workorder_id: Unique identifier for this work order
        order_id: Identifier of the parent order from ERP system
        sku: Stock Keeping Unit - the product being manufactured
        target_quantity: Total quantity required to be produced
        passed_quantity: Quantity that has passed quality inspection
        failed_quantity: Quantity that has failed quality inspection
        remaining_quantity: Quantity still remaining to be processed
        routing: List of manufacturing steps or machine identifiers
        reserved_parts: List of parts reserved for this work order (dict format for flexibility)
        status: Current status of the work order (e.g., 'pending', 'in_progress', 'completed')
        rework_count: Number of times this work order has been reworked
        max_rework_attempts: Maximum allowed rework attempts before escalation
    """
    workorder_id: str
    order_id: str
    sku: str
    target_quantity: int
    passed_quantity: int
    failed_quantity: int
    remaining_quantity: int
    routing: list[str]
    reserved_parts: list[dict]
    status: str
    rework_count: int
    max_rework_attempts: int