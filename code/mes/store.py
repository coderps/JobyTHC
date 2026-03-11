from mes.models import WorkOrder


class InMemoryMesStore:
    def __init__(self) -> None:
        self.workorders: dict[str, WorkOrder] = {}

    def save(self, workorder: WorkOrder) -> None:
        self.workorders[workorder.workorder_id] = workorder

    def get(self, workorder_id: str) -> WorkOrder:
        return self.workorders[workorder_id]


mes_store = InMemoryMesStore()