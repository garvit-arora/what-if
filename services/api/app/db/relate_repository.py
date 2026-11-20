from __future__ import annotations
import queue, threading
from concurrent.futures import Future
from pathlib import Path
from typing import Any, Callable, TypeVar
import relate
T = TypeVar("T")

class RelateRepository:
    """A serialized Relate connection owned by one dedicated thread."""
    def __init__(self, path: str | Path) -> None:
        self.path = str(path); Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self._jobs: queue.Queue = queue.Queue(); self._ready: Future = Future()
        self._thread = threading.Thread(target=self._run, name="thread-relate", daemon=True)
        self._thread.start(); self._ready.result(timeout=10)
    def _run(self) -> None:
        try: connection = relate.connect(self.path); self._ready.set_result(None)
        except BaseException as exc: self._ready.set_exception(exc); return
        while True:
            function, args, future = self._jobs.get()
            if function is None: connection.close(); future.set_result(None); return
            try: future.set_result(function(connection, *args))
            except BaseException as exc: future.set_exception(exc)
    def _submit(self, function: Callable[..., T], *args: Any) -> T:
        if not self._thread.is_alive(): raise RuntimeError("Relate repository is closed")
        future: Future = Future(); self._jobs.put((function, args, future)); return future.result(timeout=30)
    @staticmethod
    def _execute(connection: Any, query: str, params: dict[str, Any]) -> list[dict[str, Any]]:
        return [dict(row) for row in connection.execute(query, params).fetchall()]
    def execute(self, query: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        return self._submit(self._execute, query, params or {})
    @staticmethod
    def _transaction(connection: Any, statements: list[tuple[str, dict[str, Any]]]) -> None:
        previous = connection.autocommit; connection.autocommit = False
        try:
            for query, params in statements: connection.execute(query, params)
            connection.commit()
        except Exception: connection.rollback(); raise
        finally: connection.autocommit = previous
    def transaction(self, statements: list[tuple[str, dict[str, Any]]]) -> None: self._submit(self._transaction, statements)
    def close(self) -> None:
        if self._thread.is_alive():
            future: Future = Future(); self._jobs.put((None, (), future)); future.result(timeout=10); self._thread.join(timeout=10)
    def __enter__(self) -> "RelateRepository": return self
    def __exit__(self, *_: object) -> None: self.close()
