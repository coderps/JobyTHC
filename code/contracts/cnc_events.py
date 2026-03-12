"""
Event contracts for CNC (Computer Numeric Control) machine operations.

Defines the structure of events related to CNC job lifecycle:
- Requests to perform CNC operations (machining)
- Notifications that a job has started
- Completion events with duration and status
"""
from typing import Literal
from pydantic import BaseModel
from contracts.common import EventMetadata


class CncJobRequestedEvent(BaseModel):
    """Event published when a CNC job is requested for a work order.
    
    Attributes:
        metadata: Event tracking metadata (event_id, timestamp, correlation_id, etc.)
        workorder_id: Unique identifier for this manufacturing work order
        order_id: The original customer order this work order belongs to
        sku: Stock keeping unit (product identifier)
        quantity: Number of units to machine
        routing_step: Manufacturing step (currently only 'machining' supported)
        target_machine: Specific CNC machine identifier (e.g., 'CNC-01')
        attempt: Attempt number (1 for initial, >1 for rework attempts)
    """
    metadata: EventMetadata
    workorder_id: str
    order_id: str
    sku: str
    quantity: int
    routing_step: Literal["machining"] = "machining"
    target_machine: str
    attempt: int


class CncJobStartedEvent(BaseModel):
    """Event published when a CNC machine starts processing a job.
    
    Attributes:
        metadata: Event tracking metadata
        workorder_id: Reference to the work order being processed
        order_id: Reference to the original customer order
        sku: Product identifier
        quantity: Number of units being machined
        machine_id: The CNC machine that started processing
        attempt: Attempt number for this job
    """
    metadata: EventMetadata
    workorder_id: str
    order_id: str
    sku: str
    quantity: int
    machine_id: str
    attempt: int


class CncJobCompletedEvent(BaseModel):
    """Event published when a CNC job completes successfully.
    
    Attributes:
        metadata: Event tracking metadata
        workorder_id: Reference to the completed work order
        order_id: Reference to the original customer order
        sku: Product identifier
        quantity: Number of units completed
        machine_id: The CNC machine that completed the job
        duration_seconds: Time elapsed from start to completion
        attempt: Attempt number for this job
    """
    metadata: EventMetadata
    workorder_id: str
    order_id: str
    sku: str
    quantity: int
    machine_id: str
    duration_seconds: int
    attempt: int