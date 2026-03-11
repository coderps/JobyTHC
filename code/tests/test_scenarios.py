import asyncio
import json
import sys
from datetime import UTC, datetime

from nats.aio.client import Client as NATS


def base_order_payload(order_id: str, sku: str, quantity: int) -> dict:
    return {
        "metadata": {
            "event_type": "order.created",
            "event_id": f"evt-{order_id.lower()}",
            "timestamp": datetime.now(UTC).isoformat(),
            "correlation_id": f"corr-{order_id}",
        },
        "order": {
            "order_id": order_id,
            "priority": "HIGH",
            "due_date": "2026-03-14T12:00:00Z",
        },
        "product": {
            "sku": sku,
            "quantity": quantity,
            "unit_of_measure": "EA",
        },
        "manufacturing": {
            "routing": ["machining", "quality", "assembly"],
            "requires_cnc": True,
            "part_family": "BRACKET",
            "revision": "A",
        },
        "inventory_reservation": {
            "availability_status": "AVAILABLE",
            "reservation_status": "RESERVED",
            "reservation_expires_at": "2026-03-11T18:00:00Z",
            "reserved_parts": [{"part_id": "RM-AL-001", "qty": quantity}],
            "missing_parts": [],
        },
    }


async def publish_order(payload: dict) -> None:
    nc = NATS()
    await nc.connect("nats://localhost:4222")
    js = nc.jetstream()
    await js.publish("order.created", json.dumps(payload).encode())
    print(f"published order.created for {payload['order']['order_id']}")
    await nc.close()


async def main() -> None:
    scenario = sys.argv[1] if len(sys.argv) > 1 else "partial_rework"

    if scenario == "partial_rework":
        payload = base_order_payload("ORD-001", "ObjA", 2)

    elif scenario == "single_unit":
        payload = base_order_payload("ORD-002", "ObjB", 1)

    elif scenario == "larger_batch":
        payload = base_order_payload("ORD-003", "ObjC", 4)

    elif scenario == "second_order_parallel":
        payload1 = base_order_payload("ORD-004", "ObjD", 2)
        payload2 = base_order_payload("ORD-005", "ObjE", 3)
        await publish_order(payload1)
        await asyncio.sleep(1)
        await publish_order(payload2)
        return

    else:
        raise ValueError(f"Unknown scenario: {scenario}")

    await publish_order(payload)


if __name__ == "__main__":
    asyncio.run(main())