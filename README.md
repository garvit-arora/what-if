# THREAD

**Break a moment. Explore the consequences.**

THREAD is a graph-native counterfactual and decision-impact engine being built for the Relate by Neo4j Hackathon. It preserves an immutable baseline, applies explicit interventions in isolated scenarios, and explains every calculated graph change.

## Current state

Milestone 2 is operational: a 22-event Napoleonic-era graph seeds idempotently into Relate, FastAPI exposes the graph, and an isolated scenario can remove the Coup of 18 Brumaire and return a persisted semantic graph diff. No alternate database or mock fallback is used.

## Verify Relate on Windows

```powershell
python -m pip install -r requirements-dev.txt
$env:PYTHONPATH = "services/api"
python scripts/verify_relate.py
```

The script creates `data/verify_thread.rl`, writes nodes and a relationship with parameterized Cypher inside an explicit transaction, closes the store, reopens it, and asserts the persisted result.

Example query used by the proof:

```cypher
MATCH (e:Event {id: $id})-[:PART_OF]->(w:World)
RETURN e.name AS event, w.name AS world
```

See `docs/RESEARCH.md` and `docs/IMPLEMENTATION_PLAN.md` for verified constraints and the active build sequence.

## Run the historical intervention

```powershell
$env:PYTHONPATH = ".vendor;services/api"
python scripts/seed_history.py
python -m uvicorn app.main:app --port 8000 --workers 1
```

Create a scenario with `POST /api/v1/scenarios`, add `REMOVE_EVENT` for `event_coup_18_brumaire_1799`, then call `/simulate`. Interactive OpenAPI documentation is at `http://127.0.0.1:8000/docs`.

Run the real-store test suite:

```powershell
$env:PYTHONPATH = ".vendor;services/api"
python -m pytest services/api/tests -q
```
