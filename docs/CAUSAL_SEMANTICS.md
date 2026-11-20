# Causal semantics

- `ALL`: every listed prerequisite is required by that mechanism.
- `ANY`: at least one listed prerequisite is required.
- Multiple mechanisms producing the same event are alternative support pathways.
- `PRECEDED` carries chronology only.
- Failure of a documented declared rule is `dependency_disrupted`.
- Failure of a counterfactual model assumption is `indeterminate`; it does not assert that the historical event could not occur by another unknown route.
- Removed baseline events are `directly_intervened` in the branch only.

Evaluation is sorted, bounded, and deterministic. Cycles terminate at a fixed point or fail at a safety bound. Unknown real-world causal pathways are not silently invented.

