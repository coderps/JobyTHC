from typing import Literal

from pydantic import BaseModel

from contracts.common import EventMetadata


class ReservedPart(BaseModel):
    part_id: str
    qty: int


class MissingPart(BaseModel):
    part_id: str
    qty: int


class OrderInfo(BaseModel):
    order_id: str
    priority: Literal["LOW", "MEDIUM", "HIGH"]
    due_date: str


class ProductInfo(BaseModel):
    sku: str
    quantity: int
    unit_of_measure: str = "EA"


class ManufacturingInfo(BaseModel):
    routing: list[str]
    requires_cnc: bool = True
    part_family: str
    revision: str


class InventoryReservationInfo(BaseModel):
    availability_status: Literal["AVAILABLE", "PARTIAL_AVAILABLE", "UNAVAILABLE"]
    reservation_status: Literal["RESERVED", "PARTIALLY_RESERVED", "NOT_RESERVED"]
    reservation_expires_at: str
    reserved_parts: list[ReservedPart]
    missing_parts: list[MissingPart]


class OrderCreatedEvent(BaseModel):
    metadata: EventMetadata
    order: OrderInfo
    product: ProductInfo
    manufacturing: ManufacturingInfo
    inventory_reservation: InventoryReservationInfo