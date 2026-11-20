# THREAD research notes

Last verified: 2026-11-21.

## Relate

- The official package is `relate-db`; the Python import is `relate`. The package installed and exercised on this Windows x64 / Python 3.14 environment is 1.2.0 (an abi3 wheel).
- `relate.connect(database: str = ":memory:", namespace: str = "neo4j", read_only: bool = False)` returns a DB-API-style connection. The verified connection methods include `execute`, `cursor`, `commit`, `rollback`, `flush`, and `close`.
- Parameters use `$name` in Cypher and a Python mapping in `execute(query, params)`.
- A path ending in `.rl` selects a portable single-file persistent store. The whole graph and indexes are loaded into memory.
- Only one process may open a persistent store for writing. A `.rl` file cannot be opened by a side reader while its writer holds it. THREAD therefore owns one connection in one API process and serializes access.
- Transactions are single-level; there are no savepoints. Conflicting element writes fail rather than being silently retried.
- Relate supports Cypher 25 but is not a Neo4j server and must not be assumed to provide APOC or GDS.
- Relate is Apache-2.0 licensed.

## Initial engineering decisions

- Use a single `.rl` demo store, one FastAPI worker, and a repository guarded by a process-local re-entrant lock.
- Keep simulation algorithms deterministic and domain logic outside Cypher. Relate is the connected-data source of truth; Python evaluates explicit causal mechanism rules.
- Store scenario deltas rather than copying the baseline graph.
- Use NetworkX only for numerical flow algorithms; historical propagation uses a small explicit rule evaluator so its semantics are inspectable.

## Primary sources

- Relate installation: https://relatedb.ai/docs/get-started/install/
- Python embedding: https://relatedb.ai/docs/guides/embed/python/
- Limitations: https://relatedb.ai/docs/reference/limitations/
- Cypher differences: https://relatedb.ai/docs/reference/cypher/differences-from-neo4j/
- Store layouts: https://relatedb.ai/docs/guides/storage/choose-a-store-layout/
- Repository: https://github.com/relatedb/relate
- Hackathon: https://relate.devpost.com/
- Rules: https://relate.devpost.com/rules

## Still to verify

The hackathon rules, frontend library versions/licenses, index syntax, and historical-source dataset are Phase 0 work still in progress. No unverified claim is relied on by the first persistence proof.

## Milestone 2 verification

Relate 1.2.0 was exercised directly for `MERGE`, parameterized property updates, transactional multi-statement imports, traversal, persistence, and concurrent request serialization. Official documentation confirms one writer per store and single-level transactions. THREAD now uses a dedicated owner thread rather than sharing a connection across FastAPI execution contexts.

Historical source review used the Wikidata record for the Coup of 18 Brumaire and Château de Versailles pages documenting that the coup overthrew the Directory, established Napoleon as First Consul, and preceded the Empire. Counterfactual necessity beyond those documented facts remains labeled as a model assumption.

