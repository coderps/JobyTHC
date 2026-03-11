from typing import Literal

from pydantic import BaseModel

from contracts.common import EventMetadata


class CncJobRequestedEvent(BaseModel):
    metadata: EventMetadata
    workorder_id: str
    order_id: str
    sku: str
    quantity: int
    routing_step: Literal["machining"] = "machining"
    target_machine: str
    attempt: int


class CncJobStartedEvent(BaseModel):
    metadata: EventMetadata
    workorder_id: str
    order_id: str
    sku: str
    quantity: int
    machine_id: str
    attempt: int


class CncJobCompletedEvent(BaseModel):
    metadata: EventMetadata
    workorder_id: str
    order_id: str
    sku: str
    quantity: int
    machine_id: str
    duration_seconds: int
    attempt: int