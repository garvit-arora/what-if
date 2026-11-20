# Technical decisions

## TD-001 — Relate is mandatory

There is no silent mock or alternate database. Startup failures are surfaced.

## TD-002 — Delta scenarios

Baseline facts remain unchanged. Interventions and results are stored as deltas linked to a scenario, enabling reset and comparison.

## TD-003 — Explicit grouped causes

Causal mechanisms declare `ALL` (jointly required) or `ANY` (independent sufficient pathways). A chronological `PRECEDED` edge never implies invalidation.

## TD-004 — Determinism

Stable IDs, sorted traversal, bounded fixed-point evaluation, and versioned rules make identical inputs reproducible.

