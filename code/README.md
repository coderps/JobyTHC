
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

PASS → `inventory.update` → `assembly.job.requested`  
FAIL → `cnc.job.requested` (rework)

---

# Project Structure

```
code/

main.py
Entry point. Connects to NATS and starts the orchestrator.

config/
Configuration such as NATS URL and runtime settings.

infrastructure/
Messaging integration.
    nats.py           → NATS connection manager
    streams.py        → JetStream stream definitions
    publisher.py      → event publishing helper
    subscribers.py    → event subscription wrapper

mes/
Core MES logic.
    models.py         → event models
    workorder.py      → workorder state
    service.py        → orchestration logic
    handlers.py       → event handlers

simulators/
Simulated factory systems.
    cnc_simulator.py
    quality_simulator.py

observability/
Logging helpers.
    demo_log.py       → human readable timeline logs

tests/
Scenario publishers used to trigger workflows.
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

Python 3.11+  
Docker

---

# Start NATS JetStream

Run NATS using Docker:

```
docker run -d   --name nats-jetstream   -p 4222:4222   -p 8222:8222   -v nats-data:/data   nats:latest   -js -sd /data
```

Ports:

4222 → NATS client port  
8222 → monitoring UI

---

# Install Python Dependencies

```
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

```
python main.py
```

Startup actions:

1. Connect to NATS
2. Reset JetStream streams (dev mode)
3. Create streams
4. Start subscribers
5. Start simulators

---

# Run Test Scenarios

In a second terminal run:

```
python tests/test_scenarios.py partial_rework
```

Other scenarios:

```
python tests/test_scenarios.py single_unit
python tests/test_scenarios.py larger_batch
python tests/test_scenarios.py parallel_orders
```

---

# Viewing the Results

The easiest way:

```
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

---

# Key Concepts Demonstrated

Event-driven orchestration

Loose coupling between systems

Partial manufacturing success handling

Rework logic

Observable workflows

---

# Limitations (Intentional)

This is a PoC.

Simplifications:

- no database
- simulated machines
- simulated ERP/WMS
- no physical device integrations

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

---

Author: Prakhar Saxena
