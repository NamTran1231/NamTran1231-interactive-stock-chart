"""[P04] Data Simulator — Deterministic OHLCV Generator & Replay Source (Easy).

Run tests:
    pytest -m p04

Design Pattern — Factory Method (Creational):
    `ReplayDataSource.from_csv(path)` and `ReplayDataSource.from_synthetic(...)`
    are idiomatic Python Factory Methods (`@classmethod`) so callers (`MainWindow`,
    CLI) construct a replay source without wiring CSV/simulator details directly.

Problem:
    1. `generate_synthetic_candles(...)`: deterministically generate `count`
       valid random-walk OHLCV `Candle`s using an isolated `random.Random(seed)`
       instance (never mutate global `random` state).
    2. `ReplayDataSource`: stream candles one-by-one for replay controls and
       support updating the forming candle or appending a new candle in O(1).

Constraints:
    - `generate_synthetic_candles`:
      - `count`: real `int >= 0` (reject `bool`/non-`int` with `TypeError`,
        `< 0` with `ValueError`). `count == 0` returns `[]`.
      - `interval_sec`: real `int > 0` (`TypeError` / `ValueError`).
      - `start_price`: finite float `> 0` (`TypeError` / `ValueError`).
      - Output timestamps must equal `start_ts + i * interval_sec`; all candles
        must satisfy `Candle` invariants with positive prices.
    - `ReplayDataSource`:
      - Copies input sequence on `__init__` so external mutations do not leak.
      - `from_csv(path)` loads candles via `load_candles(path)` and returns a
        new `ReplayDataSource`.
      - `from_synthetic(...)` builds candles via `generate_synthetic_candles(...)`
        and returns a new `ReplayDataSource`.
      - `step()` returns next `Candle` and advances cursor, or `None` at end.
      - `progress` returns `(cursor, len(candles))`.
      - `replace_or_append(candle)`:
        - Same timestamp as last candle -> replaces last, returns `("replaced", idx)`.
        - Empty or strictly newer timestamp -> appends, returns `("appended", idx)`.
        - Older timestamp than last -> raises `ValueError`.

Example:
    >>> src = ReplayDataSource.from_synthetic(5, seed=7)
    >>> c0 = src.step()
    >>> c0 is not None and src.progress == (1, 5)
    True
"""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

from src.core.candle import Candle


def generate_synthetic_candles(
    count: int,
    seed: int = 42,
    start_ts: int = 1700000000,
    interval_sec: int = 60,
    start_price: float = 100.0,
) -> list[Candle]:
    """Generate `count` deterministic, valid OHLCV candles in O(N)."""
    raise NotImplementedError("TODO(P04): implement generate_synthetic_candles")


class ReplayDataSource:
    """Sequential candle replay cursor with Factory Methods and O(1) upsert."""

    def __init__(self, candles: Sequence[Candle]) -> None:
        """Initialize replay source from a shallow copy of `candles` at cursor 0."""
        raise NotImplementedError("TODO(P04): implement ReplayDataSource.__init__")

    @classmethod
    def from_csv(cls, path: str | Path) -> ReplayDataSource:
        """Factory Method: build a `ReplayDataSource` from a CSV file via `load_candles`."""
        raise NotImplementedError("TODO(P04): implement ReplayDataSource.from_csv")

    @classmethod
    def from_synthetic(
        cls,
        count: int,
        seed: int = 42,
        start_ts: int = 1700000000,
        interval_sec: int = 60,
        start_price: float = 100.0,
    ) -> ReplayDataSource:
        """Factory Method: build a `ReplayDataSource` from synthetic random-walk candles."""
        raise NotImplementedError("TODO(P04): implement ReplayDataSource.from_synthetic")

    def has_next(self) -> bool:
        """Return True if at least one unplayed candle remains (O(1))."""
        raise NotImplementedError("TODO(P04): implement ReplayDataSource.has_next")

    def step(self) -> Candle | None:
        """Return the next candle and advance cursor, or None if exhausted (O(1))."""
        raise NotImplementedError("TODO(P04): implement ReplayDataSource.step")

    def reset(self) -> None:
        """Reset replay cursor back to 0 (O(1))."""
        raise NotImplementedError("TODO(P04): implement ReplayDataSource.reset")

    @property
    def progress(self) -> tuple[int, int]:
        """Return `(current_cursor, total_candles)` (O(1))."""
        raise NotImplementedError("TODO(P04): implement ReplayDataSource.progress")

    @property
    def candles(self) -> list[Candle]:
        """Return a shallow copy of all underlying candles."""
        raise NotImplementedError("TODO(P04): implement ReplayDataSource.candles")

    def replace_or_append(self, candle: Candle) -> tuple[str, int]:
        """Replace last candle on equal timestamp, append if newer, raise ValueError if older (O(1))."""
        raise NotImplementedError("TODO(P04): implement ReplayDataSource.replace_or_append")
