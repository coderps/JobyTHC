from dataclasses import dataclass

@dataclass
class WorkOrder:
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