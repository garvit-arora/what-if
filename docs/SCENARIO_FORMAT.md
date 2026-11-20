# Scenario format

A `Scenario` links to an immutable baseline `World` with `DERIVED_FROM`. An `Intervention` is linked with `MODIFIES`; a `SimulationRun` stores the versioned, deterministic result and links back to the scenario. All three persist in Relate.

Diff items use stable application IDs and semantic instructions:

- `CUT_THREAD`: intervention makes a relationship absent in the branch.
- `DIM_DEPENDENCY`: a declared prerequisite is unsatisfied or indeterminate.
- Updated nodes carry prior/new states and machine-readable reason codes.

The backend returns semantics, evidence IDs, mechanism IDs, and explanations. It deliberately returns no colors, coordinates, or rendering objects.

