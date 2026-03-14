# Joby Manufacturing Execution System (MES) - Take-Home Challenge

## Overview

This project is a **Proof of Concept (PoC)** for a **Manufacturing Execution System (MES) built using event-driven architecture**. The MES orchestrates multiple manufacturing systems (ERP, CNC, Quality, Assembly, Inventory) without tight coupling, using **NATS JetStream** for asynchronous, persistent event streaming.

The surrounding systems (ERP, CNC, Quality, Assembly, Inventory) are **simulated** to demonstrate how the MES coordinates their workflows. The **MES orchestration logic is the core real implementation** being showcased in this PoC.

---

## Project Goals

✅ Demonstrate event-driven architecture for manufacturing systems  
✅ Show MES orchestration without tight coupling  
✅ Provide scalable pattern for multi-system coordination  
✅ Include comprehensive documentation and logging  
✅ Enable scenario-based testing of complex workflows  

---

## What Is Being Done

### Manufacturing Workflow Orchestration

The MES acts as a central orchestrator that coordinates a manufacturing order from creation to fulfillment:

1. **Order Reception** - An order arrives via ERP system
2. **Job Routing** - MES routes work to appropriate machines and systems based on order specifications
3. **CNC Processing** - CNC machines process jobs (simulated with success/failure scenarios)
4. **Quality Inspection** - Completed jobs undergo quality checks
5. **Inventory Management** - Upon passing quality, inventory is updated and next stages trigger
6. **Rework Handling** - Failed quality checks trigger rework requests back to CNC
7. **Assembly Coordination** - Final assembly stages are coordinated after passing all checkpoints

### Key Features

- **Event-Driven Architecture**: All system communication happens through events published to NATS JetStream streams
- **Loose Coupling**: Systems only need to know event schemas, not implementation details
- **Persistent Streaming**: JetStream provides message durability and replay capability
- **Scalable Pattern**: New systems can subscribe to events without modifying existing code
- **Observability**: Structured logging tracks the entire workflow with event timestamps and correlations
- **Scenario-Based Testing**: Test scenarios can simulate complex manufacturing workflows

For detailed code structure and architecture information, see [code/README.md](code/README.md).

---

## Technology Stack

- **Language**: Python 3.13
- **Message Queue**: NATS with JetStream for durable event streaming
- **Data Validation**: Pydantic for type-safe event contracts
- **Logging**: structlog for structured, contextual logging
- **Testing**: custom scenario runners
- **Async**: asyncio for non-blocking I/O operations

---

## AI as a Collaborative Tool

During development, AI was leveraged as a collaborative partner to accelerate iteration:

- **Architecture Discussions**: Used AI to explore event-driven architecture trade-offs and validate component design decisions
- **Code Scaffolding**: Directed AI to generate boilerplate for infrastructure (NATS, streams, publishers) and event contracts, then refined based on requirements
- **Pattern Development**: Worked with AI to establish consistent patterns for event handlers, orchestration logic, and state management
- **Documentation**: Collaborated on comprehensive docstrings and comments to ensure code clarity
- **Testing**: Created test scenarios with AI assistance to cover multiple order workflows and edge cases
- **Iteration**: Used AI feedback to optimize async patterns, error handling, and logging structure

The key was maintaining direction. AI served as an intelligent autocomplete and validation partner, increasing development velocity without compromising design ownership.

---

## Running the Project

### Prerequisites

- Docker
- Python v3.13+

```bash
curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh
docker run -d --name nats-jetstream -p 4222:4222 -p 8222:8222 -v nats-data:/data nats:latest -js -sd /data
python3 -V
pip install -r code/requirements.txt
```

### Start the MES

```bash
cd code
python main.py
```

This starts:
- NATS connection to JetStream
- MES service listening for order events
- CNC, Quality, and Assembly simulators
- Observability/logging system

### Run Test Scenarios

```bash
cd code
python tests/test_scenarios.py first_order_simple
python tests/test_scenarios.py second_order_parallel
python tests/test_scenarios.py third_order_rework_scenario
```

---

## Key Design Decisions

For detailed architectural decisions, see [docs/ADRs/](docs/ADRs/).

---

## Future Enhancements

- Distributed MES instances with event sourcing
- Event replay and audit trails
- Advanced scheduling algorithms
- Machine learning for predictive maintenance integration
- Kubernetes deployment with proper message queue clustering

---

## Documentation

- **Technical Details**: See [code/README.md](code/README.md)
- **Architecture Decisions**: See [docs/PoC-Scope-MES-Orchestration.md](docs/PoC-Scope-MES-Orchestration.md)
- **ADRs**: See [docs/ADRs/](docs/ADRs/) for Architecture Decision Records
- **Challenge Details**: See [Software_Engineering_Lead-Take_home_challenge.pdf](docs/Software_Engineering_Lead-Take_home_challenge.pdf)
- **NATS JetStream**: [official-docs](https://docs.nats.io/nats-concepts/jetstream)