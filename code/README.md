
# MES Orchestration PoC (Event‑Driven Manufacturing Simulation)

This repository contains a **Proof of Concept (PoC)** for an **MES (Manufacturing Execution System) orchestration layer** built using an **event‑driven architecture with NATS JetStream**.

The goal of this project is to demonstrate how MES can coordinate multiple manufacturing systems (ERP, CNC, Quality, Assembly, Inventory) **without tight coupling**, using events.

The surrounding systems are **simulated**, while the **MES orchestration logic is the real PoC implementation**.

---

# Architecture Overview

The system follows an **event-driven architecture**.

Systems involved:

- ERP (simulated)
- MES (PoC implementation)
- CNC Machines (simulated)
- Quality Inspection (simulated)
- Inventory/WMS (simulated)
- Assembly Line (simulated)

Communication happens through **NATS JetStream**.

Example flow:

ERP → `order.created` → MES  
MES → `cnc.job.requested` → CNC  
CNC → `cnc.job.completed` → MES  
MES → `quality.inspection.requested` → Quality  
Quality → `quality.inspection.completed` → MES  

MES decision:

PASS → `wms.inventory.update` → `assembly.job.requested`  
FAIL → `cnc.job.requested` (rework)

---

# Project Structure

```
code/

README.md
requirements.txt

main.py
Entry point. Connects to NATS and starts the orchestrator.

config/
Configuration such as NATS URL and runtime settings.
    settings.py

contracts/
Event contract definitions.
    cnc_events.py      → CNC machine event contracts
    common.py          → Common event structures
    order_events.py    → Order-related event contracts
    quality_events.py  → Quality inspection event contracts

domain/
Domain models and events.
    events.py          → Core domain events

infrastructure/
Messaging integration.
    nats.py            → NATS connection manager
    streams.py         → JetStream stream definitions
    publisher.py       → Event publishing helper
    subscribers.py     → Event subscription wrapper

mes/
Core MES logic.
    handlers.py        → Event handlers
    models.py          → Data models
    service.py         → Orchestration logic
    store.py           → Data storage utilities
    utils.py           → Utility functions
    orchestrators/
        cnc_orchestrator.py      → CNC job orchestration
        order_orchestrator.py    → Order processing orchestration
        quality_orchestrator.py  → Quality inspection orchestration

observability/
Logging helpers.
    demo_log.py        → Human readable timeline logs

simulators/
Simulated factory systems.
    cnc_simulator.py
    downstream_observers.py
    quality_simulator.py

tests/
Test scenarios and publishers.
    test_publish.py
    test_scenarios.py
```

---

# Why This Structure

The repository separates **infrastructure**, **domain logic**, and **simulated systems**.

Infrastructure layer:
- messaging
- streams
- publishers
- subscribers

MES layer:
- business orchestration
- workorder lifecycle
- routing logic

Simulators:
- CNC machine behavior
- quality inspection results
- processing delays

This separation keeps the PoC **clean and easy to reason about**.

---

# Workorder Lifecycle

Simplified lifecycle:

ORDER_RECEIVED  
→ WORKORDER_CREATED  
→ CNC_REQUESTED  
→ CNC_COMPLETED  
→ QUALITY_REQUESTED  
→ QUALITY_RESULT  

If PASS:

inventory update → assembly request

If FAIL:

rework → CNC_REQUESTED again

Example:

Order quantity = 2

Quality result:

1 PASS  
1 FAIL  

MES forwards 1 to assembly and sends 1 for rework.

---

# Setup

## Requirements

- Docker
- Python v3.13+

```bash
curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh
python3 -V
```

---

# Start NATS JetStream

Run NATS using Docker:

```bash
docker run -d --name nats-jetstream -p 4222:4222 -p 8222:8222 -v nats-data:/data nats:latest -js -sd /data
```

Ports:

4222 → NATS client port  
8222 → monitoring UI

---

# Install Python Dependencies

```bash
pip install -r requirements.txt
```

Example requirements:

```
nats-py
pydantic
structlog
```

---

# Run the MES Orchestrator

Start the orchestrator:

```bash
python main.py
```

Startup actions:

1. Connect to NATS
2. Reset JetStream streams (dev mode, prod will have persistent streams)
3. Create streams
4. Start subscribers
5. Start simulators and orchestrators

---

# Run Test Scenarios

In a second terminal run:

```bash
python tests/test_scenarios.py partial_rework
```

This tests rework workflow with a 2-unit batch where 1 unit passes quality and 1 fails, triggering rework of the failed unit which then passes.

Other scenarios:

- `single_unit`: Tests simple single-unit manufacturing flow with no rework required.
- `larger_batch`: Tests batch processing with 4 units where all pass quality inspection on first attempt.
- `high_priority`: Tests high-priority order processing with 2 units that trigger quality rework.
- `low_priority`: Tests low-priority order processing with 3 units that pass quality without rework.
- `mixed_priority`: Tests concurrent processing of HIGH and MEDIUM priority orders running in parallel.
- `second_order_parallel`: Tests rapid sequential orders (2 units with rework + 3 units passing) processing simultaneously.
- `bulk_processing`: Tests larger batch manufacturing with 5 units in a single CNC and quality cycle.
- `multi_parallel`: Tests concurrent processing of 3 orders with varying quantities (2, 1, and 3 units) submitted nearly simultaneously.
- `stress_test`: Tests system load with 5 orders of mixed quantities submitted rapidly to validate queue capacity and stability.

> NOTE: **You need to observe logs for the results**.

---

# Viewing the Results

The easiest way:

```bash
python main.py > mes_run.log
```

Then run a scenario.

Search for:

```
demo_timeline
```

Example output:

ORDER_CREATED_RECEIVED  
WORKORDER_CREATED  
CNC_JOB_DISPATCHED  
CNC_PROCESSING_STARTED  
CNC_PROCESSING_COMPLETED  
QUALITY_COMPLETED  
REWORK_REQUESTED  
CNC_JOB_DISPATCHED  
QUALITY_COMPLETED  
WORKORDER_COMPLETED

This shows the complete orchestration flow.

> **Note:** For better traceability, we plan to implement trace_ids in the future, but for this PoC it's a bit too much. We could also use some built-in Python libraries (for example, OpenTelemetry with Jaeger exporter).

---

# Key Concepts Demonstrated

- Event-driven orchestration
- Loose coupling between systems
- Partial manufacturing success handling
- Rework logic
- Observable workflows

---

# Limitations (Intentional)

This is a PoC.

Simplifications:

- no database (in-memory store)
- simulated machines
- simulated ERP/WMS
- no physical device integrations
- no distributed tracing (trace_ids) - planned for future but too much for PoC; could use Python libraries like OpenTelemetry with Jaeger exporter

The focus is **MES orchestration**.

---

# Possible Extensions

Future improvements:

- PostgreSQL persistence
- device integration
- workflow engine
- metrics and monitoring
- dead letter queues
- retry policies
- better traceabilty

---

Author: Prakhar Saxena
