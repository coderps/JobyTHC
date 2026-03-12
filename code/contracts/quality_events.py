"""
Quality Events Module

This module defines Pydantic models for quality-related events in the manufacturing system.
It includes event contracts for quality inspection requests and completion results.
"""
from typing import Literal
from pydantic import BaseModel
from contracts.common import EventMetadata


class QualityInspectionRequestedEvent(BaseModel):
    """Event published when a quality inspection is requested for a work order.
    
    Attributes:
        metadata: Event tracking metadata (event_id, timestamp, correlation_id, etc.)
        workorder_id: Unique identifier for the manufacturing work order
        order_id: The original customer order this work order belongs to
        sku: Stock keeping unit (product identifier)
        quantity: Number of units to inspect
        attempt: Attempt number (1 for initial, >1 for rework inspection attempts)
    """
    metadata: EventMetadata
    workorder_id: str
    order_id: str
    sku: str
    quantity: int
    attempt: int


class FailureReason(BaseModel):
    """Model representing a quality failure reason and the quantity affected.
    
    Attributes:
        qty: Number of units that failed for this specific reason
        reason: Description of the quality issue or defect found
    """
    qty: int
    reason: str


class QualityInspectionCompletedEvent(BaseModel):
    """Event published when a quality inspection is completed for a work order.
    
    Contains the inspection results including passed/failed quantities and detailed
    failure reasons for parts that did not meet quality standards.
    
    Attributes:
        metadata: Event tracking metadata (event_id, timestamp, correlation_id, etc.)
        workorder_id: Unique identifier for the manufacturing work order
        order_id: The original customer order this work order belongs to
        sku: Stock keeping unit (product identifier)
        inspected_quantity: Total number of units that were inspected
        passed_quantity: Number of units that passed quality inspection
        failed_quantity: Number of units that failed quality inspection
        disposition: Overall inspection result (PASS: all units passed, FAIL: all units failed, PARTIAL_REWORK: requires rework)
        failure_reasons: List of specific failure reasons identified during inspection
        attempt: Attempt number (1 for initial, >1 for rework inspection attempts)
    """
    metadata: EventMetadata
    workorder_id: str
    order_id: str
    sku: str
    inspected_quantity: int
    passed_quantity: int
    failed_quantity: int
    disposition: Literal["PASS", "FAIL", "PARTIAL_REWORK"]
    failure_reasons: list[FailureReason]
    attempt: int