import asyncio
import json
from datetime import datetime, UTC

from nats.aio.client import Client as NATS


async def main():
    nc = NATS()
    await nc.connect("nats://localhost:4222")
    js = nc.jetstream()

    payload = {
        "metadata": {
            "event_type": "order.created",
            "event_id": "evt-001",
            "timestamp": datetime.now(UTC).isoformat(),
            "correlation_id": "corr-ORD-001",
        },
        "order": {
            "order_id": "ORD-001",
            "priority": "HIGH",
            "due_date": "2026-03-14T12:00:00Z",
        },
        "product": {
            "sku": "ObjA",
            "quantity": 2,
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
            "reserved_parts": [
                {"part_id": "RM-AL-001", "qty": 2}
            ],
            "missing_parts": [],
        },
    }

    await js.publish("order.created", json.dumps(payload).encode())
    print("order.created published")

    await nc.close()


asyncio.run(main())