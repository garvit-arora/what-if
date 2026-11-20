from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "services" / "api"))

from app.db.relate_repository import RelateRepository


def verify(path: Path) -> None:
    if path.exists():
        path.unlink()

    with RelateRepository(path) as repo:
        repo.execute(
            "CREATE (w:World {id: $id, name: $name})",
            {"id": "world_demo", "name": "THREAD verification world"},
        )
        repo.transaction([
            (
                "MATCH (w:World {id: $world_id}) "
                "CREATE (e:Event {id: $event_id, name: $name}), "
                "(e)-[:PART_OF]->(w)",
                {"world_id": "world_demo", "event_id": "event_demo", "name": "Verified event"},
            )
        ])

    with RelateRepository(path) as reopened:
        rows = reopened.execute(
            "MATCH (e:Event {id: $id})-[:PART_OF]->(w:World) "
            "RETURN e.name AS event, w.name AS world",
            {"id": "event_demo"},
        )
        assert rows == [{"event": "Verified event", "world": "THREAD verification world"}], rows

    print(f"Relate persistence verified: {path}")
    print("Parameterized query, transaction, close, reopen, and relationship read all passed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", type=Path, default=ROOT / "data" / "verify_thread.rl")
    verify(parser.parse_args().database)

