"""Manufacturing System Test Scenarios

This module provides test scenarios to validate the manufacturing execution system (MES).
Each scenario simulates different manufacturing workflows including:
- Single unit orders
- Batch orders
- Parallel order processing
- Rework scenarios
- Various priority levels

Run scenarios with: python test_scenarios.py <scenario_name>

Available scenarios:
  - partial_rework: 2 units triggering quality rework
  - single_unit: 1 unit (no rework)
  - larger_batch: 4 units (no rework)
  - high_priority: 2 units with HIGH priority
  - low_priority: 3 units with LOW priority
  - mixed_priority: Two orders with different priorities in parallel
  - second_order_parallel: 2 orders (2+3 units) in quick succession
  - bulk_processing: 5 units testing batch processing
  - multi_parallel: 3 orders simultaneously
  - stress_test: 5 orders in rapid succession
"""
import asyncio
import json
import sys
from datetime import UTC, datetime

from nats.aio.client import Client as NATS


def base_order_payload(order_id: str, sku: str, quantity: int, priority: str = "HIGH") -> dict:
    """Create a base order payload with common fields.
    
    Args:
        order_id: Unique order identifier (e.g., "ORD-001")
        sku: Product SKU/identifier (e.g., "ObjA")
        quantity: Number of units to manufacture
        priority: Order priority level (LOW, MEDIUM, HIGH)
        
    Returns:
        A dictionary representing an OrderCreatedEvent payload
    """
    return {
        # Event metadata for tracking and correlation
        "metadata": {
            "event_type": "order.created",
            "event_id": f"evt-{order_id.lower()}",
            "timestamp": datetime.now(UTC).isoformat(),
            "correlation_id": f"corr-{order_id}",
        },
        # Order information
        "order": {
            "order_id": order_id,
            "priority": priority,
            "due_date": "2026-03-14T12:00:00Z",
        },
        # Product details
        "product": {
            "sku": sku,
            "quantity": quantity,
            "unit_of_measure": "EA",
        },
        # Manufacturing specifications
        "manufacturing": {
            "routing": ["machining", "quality", "assembly"],
            "requires_cnc": True,
            "part_family": "BRACKET",
            "revision": "A",
        },
        # Inventory reservation status
        "inventory_reservation": {
            "availability_status": "AVAILABLE",
            "reservation_status": "RESERVED",
            "reservation_expires_at": "2026-03-11T18:00:00Z",
            "reserved_parts": [{"part_id": "RM-AL-001", "qty": quantity}],
            "missing_parts": [],
        },
    }


async def publish_order(payload: dict) -> None:
    """Publish an order to the NATS message broker.
    
    Connects to NATS, publishes the order event to the order.created subject,
    and logs the publication.
    
    Args:
        payload: The OrderCreatedEvent payload to publish
    """
    # Connect to NATS
    nc = NATS()
    await nc.connect("nats://localhost:4222")
    js = nc.jetstream()
    
    # Publish the order event
    await js.publish("order.created", json.dumps(payload).encode())
    print(f"published order.created for {payload['order']['order_id']}")
    
    # Close connection
    await nc.close()


async def scenario_partial_rework() -> None:
    """Scenario: Partial Rework
    
    Tests the rework workflow with a 2-unit batch:
    - First quality inspection: 1 unit passes, 1 fails
    - Triggers rework of failed unit
    - Rework attempt: all units pass
    - Workflow completes with all units passed
    """
    print("\n=== Running: Partial Rework Scenario ===")
    payload = base_order_payload("ORD-001", "ObjA", 2)
    await publish_order(payload)


async def scenario_single_unit() -> None:
    """Scenario: Single Unit
    
    Tests simple single-unit manufacturing:
    - 1 unit enters CNC machining
    - Quality inspection passes immediately (no rework)
    - Completes without requiring rework
    """
    print("\n=== Running: Single Unit Scenario ===")
    payload = base_order_payload("ORD-002", "ObjB", 1)
    await publish_order(payload)


async def scenario_larger_batch() -> None:
    """Scenario: Larger Batch
    
    Tests batch processing with 4 units:
    - All units manufactured via CNC
    - Quality inspection: all pass (4 units)
    - No rework required
    - Order completes after first pass
    """
    print("\n=== Running: Larger Batch Scenario ===")
    payload = base_order_payload("ORD-003", "ObjC", 4)
    await publish_order(payload)


async def scenario_high_priority() -> None:
    """Scenario: High Priority Order
    
    Tests high-priority order processing:
    - 2-unit order with HIGH priority
    - Triggers quality rework scenario
    - Tests priority handling in scheduling
    """
    print("\n=== Running: High Priority Order Scenario ===")
    payload = base_order_payload("ORD-006", "ObjF", 2, priority="HIGH")
    await publish_order(payload)


async def scenario_low_priority() -> None:
    """Scenario: Low Priority Order
    
    Tests low-priority order processing:
    - 3-unit order with LOW priority
    - Single quality pass (no rework)
    - Tests priority-based workflow handling
    """
    print("\n=== Running: Low Priority Order Scenario ===")
    payload = base_order_payload("ORD-007", "ObjG", 3, priority="LOW")
    await publish_order(payload)


async def scenario_mixed_priority_parallel() -> None:
    """Scenario: Mixed Priority Orders in Parallel
    
    Tests concurrent processing of different priority levels:
    - HIGH priority order (2 units) - enters queue first
    - MEDIUM priority order (2 units) - enters queue second
    - Tests scheduler handling of mixed priorities
    - Both orders process concurrently
    """
    print("\n=== Running: Mixed Priority Parallel Scenario ===")
    payload1 = base_order_payload("ORD-008", "ObjH", 2, priority="HIGH")
    payload2 = base_order_payload("ORD-009", "ObjI", 2, priority="MEDIUM")
    
    await publish_order(payload1)
    await asyncio.sleep(0.5)  # Small delay between orders
    await publish_order(payload2)


async def scenario_second_order_parallel() -> None:
    """Scenario: Second Order Parallel
    
    Tests rapid sequential orders:
    - ORD-004: 2 units (triggers rework)
    - 1 second delay
    - ORD-005: 3 units (passes quality)
    - Both orders process in parallel
    - Tests queue handling and concurrency
    """
    print("\n=== Running: Second Order Parallel Scenario ===")
    payload1 = base_order_payload("ORD-004", "ObjD", 2)
    payload2 = base_order_payload("ORD-005", "ObjE", 3)
    
    await publish_order(payload1)
    await asyncio.sleep(1)  # 1 second between orders
    await publish_order(payload2)


async def scenario_bulk_processing() -> None:
    """Scenario: Bulk Processing
    
    Tests larger batch manufacturing:
    - 5-unit order
    - Single CNC and quality cycle
    - Tests batch processing efficiency
    """
    print("\n=== Running: Bulk Processing Scenario ===")
    payload = base_order_payload("ORD-010", "ObjJ", 5)
    await publish_order(payload)


async def scenario_multi_parallel() -> None:
    """Scenario: Multiple Orders in Parallel
    
    Tests concurrent processing of 3 orders:
    - ORD-011: 2 units (triggers rework)
    - ORD-012: 1 unit (simple)
    - ORD-013: 3 units (simple)
    - All enter system nearly simultaneously
    - Tests system capacity with concurrent jobs
    """
    print("\n=== Running: Multiple Parallel Orders Scenario ===")
    payload1 = base_order_payload("ORD-011", "ObjK", 2)
    payload2 = base_order_payload("ORD-012", "ObjL", 1)
    payload3 = base_order_payload("ORD-013", "ObjM", 3)
    
    await publish_order(payload1)
    await asyncio.sleep(0.3)
    await publish_order(payload2)
    await asyncio.sleep(0.3)
    await publish_order(payload3)


async def scenario_stress_test() -> None:
    """Scenario: Stress Test
    
    Tests system under load with rapid order submission:
    - 5 orders submitted in rapid succession
    - Mixed quantities (1-4 units per order)
    - Tests message queue capacity
    - Tests CNC machine scheduling under load
    - Tests system stability with concurrent processing
    
    Expected behavior:
    - All orders should eventually complete
    - Some may queue if resources are busy
    - Quality rework orders should still trigger correctly
    """
    print("\n=== Running: Stress Test Scenario ===")
    orders = [
        base_order_payload("ORD-014", "ObjN", 2),
        base_order_payload("ORD-015", "ObjO", 1),
        base_order_payload("ORD-016", "ObjP", 3),
        base_order_payload("ORD-017", "ObjQ", 2),
        base_order_payload("ORD-018", "ObjR", 4),
    ]
    
    for i, payload in enumerate(orders):
        await publish_order(payload)
        if i < len(orders) - 1:  # Small delay between orders, not after last
            await asyncio.sleep(0.2)


async def main() -> None:
    """Main entry point for test scenario execution.
    
    Reads scenario name from command-line arguments and executes the
    corresponding test scenario.
    
    Usage:
        python test_scenarios.py <scenario_name>
        
    If no scenario specified, defaults to 'partial_rework'.
    """
    # Get scenario name from command line arguments
    scenario = sys.argv[1] if len(sys.argv) > 1 else "partial_rework"

    # Map scenario names to their handler functions
    scenarios = {
        "partial_rework": scenario_partial_rework,
        "single_unit": scenario_single_unit,
        "larger_batch": scenario_larger_batch,
        "high_priority": scenario_high_priority,
        "low_priority": scenario_low_priority,
        "mixed_priority": scenario_mixed_priority_parallel,
        "second_order_parallel": scenario_second_order_parallel,
        "bulk_processing": scenario_bulk_processing,
        "multi_parallel": scenario_multi_parallel,
        "stress_test": scenario_stress_test,
    }

    # Execute the requested scenario, or show error if unknown
    if scenario in scenarios:
        await scenarios[scenario]()
    else:
        print(f"Unknown scenario: {scenario}")
        print(f"Available scenarios: {', '.join(scenarios.keys())}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())