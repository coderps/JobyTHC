
# ADR-004: Quality Results Published as Events

**Status:** Accepted  
**Date:** 2026-03-10

---

## Context

After CNC machines complete machining operations, produced parts must be inspected by a **Quality system** to ensure they meet required tolerances and specifications.

Inspection outcomes determine the next step in the manufacturing workflow:

- **PASSED** → the part proceeds to Assembly
- **FAILED (reworkable)** → the part must be reprocessed
- **FAILED (scrap)** → a new production cycle must be initiated

Several systems need access to inspection results:

- MES must decide whether to continue the workflow or trigger rework
- Analytics systems may track defect rates
- Monitoring systems may evaluate machine performance
- Traceability systems may store inspection history

A direct integration between Quality and MES (or Quality and CNC) would tightly couple the systems and limit the ability for other consumers to access inspection data.

---

## Decision

Quality inspection results will be **published as events** to the **NATS JetStream event bus**.

Systems that require inspection information subscribe to these events.

Primary consumer:

- **MES** – determines next workflow step (assembly or rework)

Possible additional consumers:

- Production analytics
- Machine performance monitoring
- Manufacturing traceability systems

This approach ensures that inspection data is available to all relevant systems without introducing tight coupling.

---

## Event Flow

```mermaid
flowchart LR

CNC -->|cnc.job.completed| NATS[(NATS JetStream)]
NATS --> |quality.inspection.requested| Quality

MES -->|assembly.job.requested| NATS
MES -->|cnc.job.retry_requested| CNC

Quality -->|quality.inspection.completed| NATS
NATS --> |Inspection Results| MES

NATS -->|Out for Assembly| Assembly
```

---

## Example Event: Quality Inspection

```json
{
  "event_type": "quality.inspection.completed",
  "work_order_id": "WO-501",
  "produced_part_id": "PART-9001",
  "result": "FAILED",
  "disposition": "SCRAP",
  "reason": "diameter_out_of_tolerance",
  "timestamp": "2026-03-10T10:25:12Z"
}
```

---

## Alternatives Considered

### Direct Quality → MES Integration

Quality systems could directly notify MES of inspection results.

Pros:

- simple integration
- low latency communication

Cons:

- tight coupling between Quality and MES
- difficult to add additional consumers of inspection data

### Quality → CNC Feedback Loop

Inspection results could be sent directly to the CNC system to trigger retries.

Pros:

- immediate machine-level feedback

Cons:

- CNC systems are not responsible for workflow orchestration
- production state becomes fragmented across systems

### MES Pulling Inspection Results

MES could periodically query the Quality system for inspection results.

Pros:

- simple architecture

Cons:

- inefficient polling
- delayed response to inspection outcomes

---

## Consequences

### Positive

- Loose coupling between Quality and other manufacturing systems
- Inspection data becomes reusable across multiple consumers
- Supports analytics, monitoring, and traceability
- Fits naturally within the event-driven architecture

### Negative

- Event-driven systems introduce eventual consistency
- Requires reliable event delivery and monitoring
- Debugging may require tracing events across multiple systems

---

## Notes

Publishing inspection outcomes as events allows the manufacturing system to remain modular and scalable.

MES remains responsible for workflow orchestration, while Quality systems focus exclusively on inspection and validation responsibilities.
