# Architecture

```text
Next.js web app
      |
FastAPI /api/v1
      |
application services ---- deterministic causal evaluator
      |                   deterministic network-flow adapter
serialized repository
      |
Relate embedded store (data/thread.rl)
```

The baseline world is immutable. A scenario records interventions and simulation runs as graph entities linked back to the baseline. Evaluation produces explicit statuses and an explanation trace. The web client animates the returned diff; it never invents affected edges.

Relate access stays in one API process and one application worker. A dedicated executor thread owns the connection for its entire lifetime; all requests submit serialized jobs to it. FastAPI startup opens and seeds the store, and shutdown closes it. This satisfies connection thread ownership as well as the single-writer store constraint.

Scenarios are graph deltas: `Scenario -[:DERIVED_FROM]-> World`, `Scenario -[:MODIFIES]-> Intervention`, and `SimulationRun -[:DERIVED_FROM]-> Scenario`. Baseline events are never deleted by simulation.

