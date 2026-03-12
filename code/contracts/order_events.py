"""
Order Events Module

This module defines Pydantic models for order-related events in the manufacturing system.
It includes event contracts for order creation and related inventory/manufacturing information.
"""
from typing import Literal
from pydantic import BaseModel
from contracts.common import EventMetadata


class ReservedPart(BaseModel):
    """Model representing a part that has been successfully reserved for an order.
    
    Attributes:
        part_id: Unique identifier for the part
        qty: Quantity of the part that was reserved
    """
    part_id: str
    qty: int


class MissingPart(BaseModel):
    """Model representing a part that could not be fully reserved due to insufficient inventory.
    
    Attributes:
        part_id: Unique identifier for the part
        qty: Quantity of the part that is missing or unavailable
    """
    part_id: str
    qty: int


class OrderInfo(BaseModel):
    """Core information about an order.
    
    Attributes:
        order_id: Unique identifier for the order
        priority: Priority level determining scheduling and fulfillment order (LOW, MEDIUM, HIGH)
        due_date: Expected delivery or completion date for the order
    """
    order_id: str
    priority: Literal["LOW", "MEDIUM", "HIGH"]
    due_date: str


class ProductInfo(BaseModel):
    """Details about the product being ordered.
    
    Attributes:
        sku: Stock Keeping Unit - unique product identifier
        quantity: Number of units ordered
        unit_of_measure: Unit of measure (default: "EA" for each/units)
    """
    sku: str
    quantity: int
    unit_of_measure: str = "EA"


class ManufacturingInfo(BaseModel):
    """Manufacturing specifications and routing information for the product.
    
    Attributes:
        routing: List of manufacturing steps/operations required
        requires_cnc: Whether the product requires CNC (Computer Numerical Control) machining
        part_family: Product family classification for grouping similar parts
        revision: Design revision number for version control
    """
    routing: list[str]
    requires_cnc: bool = True
    part_family: str
    revision: str


class InventoryReservationInfo(BaseModel):
    """Inventory reservation status and details for the order.
    
    Attributes:
        availability_status: Overall availability status of required inventory (AVAILABLE, PARTIAL_AVAILABLE, UNAVAILABLE)
        reservation_status: Whether inventory has been reserved (RESERVED, PARTIALLY_RESERVED, NOT_RESERVED)
        reservation_expires_at: Timestamp when this reservation will expire if not converted to actual allocation
        reserved_parts: List of parts successfully reserved for this order
        missing_parts: List of parts that could not be reserved due to insufficient inventory
    """
    availability_status: Literal["AVAILABLE", "PARTIAL_AVAILABLE", "UNAVAILABLE"]
    reservation_status: Literal["RESERVED", "PARTIALLY_RESERVED", "NOT_RESERVED"]
    reservation_expires_at: str
    reserved_parts: list[ReservedPart]
    missing_parts: list[MissingPart]


class OrderCreatedEvent(BaseModel):
    """Event emitted when a new order is created in the system.
    
    This is the primary event that triggers the order fulfillment workflow,
    including inventory reservation, manufacturing planning, and CNC routing.
    
    Attributes:
        metadata: Standard event metadata (timestamp, source, event ID, etc.)
        order: Core order information
        product: Product details for this order
        manufacturing: Manufacturing specifications and routing for the product
        inventory_reservation: Inventory reservation status and details
    """
    metadata: EventMetadata
    order: OrderInfo
    product: ProductInfo
    manufacturing: ManufacturingInfo
    inventory_reservation: InventoryReservationInfo