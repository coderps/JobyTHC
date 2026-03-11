from typing import Literal

from pydantic import BaseModel

from contracts.common import EventMetadata


class QualityInspectionRequestedEvent(BaseModel):
    metadata: EventMetadata
    workorder_id: str
    order_id: str
    sku: str
    quantity: int
    attempt: int


class FailureReason(BaseModel):
    qty: int
    reason: str


class QualityInspectionCompletedEvent(BaseModel):
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