"""[P07] SegmentTree — O(log N) OHLCV Range Query & Dynamic Append (Hard).

Run tests:
    pytest -m p07

Problem:
    Implement `scan_range` (O(N) brute-force oracle) and `SegmentTree`
    (O(log N) range query / point update, amortized O(log N) dynamic append)
    computing `(min_low, max_high, volume_sum)` over half-open intervals
    `[left, right)`.

Constraints:
    - Half-open intervals `[left, right)` cover indices `left <= i < right`.
    - `query(left, right)` and `scan_range(candles, left, right)`:
      - Clamp bounds to `[0, len]`. Return `None` if empty or `l >= r`.
      - `SegmentTree.query` must match `scan_range` on any size (including
        empty, 1, and non-power-of-2 sizes) in O(log N).
    - `update(index, candle)`: O(log N). Raises `IndexError` if `index` is out
      of `[0, len)` (reject `bool` with `TypeError` or `IndexError`).
    - `append(candle)`: O(log N) amortized; grows capacity automatically past
      power-of-2 boundaries (`0 -> 1 -> 2 -> 4 -> 8 -> ...`).
    - `get_candle(index)`: O(1); raises `IndexError` if out of `[0, len)`.
    - Construction `SegmentTree(candles)`: O(N); supports `None` or `[]`.

Example:
    >>> st = SegmentTree(candles)
    >>> st.query(10, 50) == scan_range(candles, 10, 50)
    True
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from src.core.candle import Candle


@dataclass(frozen=True, slots=True)
class RangeStats:
    """Aggregated OHLCV statistics over a candle index interval `[left, right)`."""

    min_low: float
    max_high: float
    volume_sum: float


def scan_range(candles: Sequence[Candle], left: int, right: int) -> RangeStats | None:
    """Linear O(N) oracle returning `RangeStats` over `[left, right)`, or None if empty."""
    raise NotImplementedError("TODO(P07): implement scan_range")


class SegmentTree:
    """Dynamic Segment Tree supporting O(log N) OHLCV range stats, update, and append."""

    def __init__(self, candles: Sequence[Candle] | None = None) -> None:
        """Build segment tree from optional initial `candles` in O(N)."""
        raise NotImplementedError("TODO(P07): implement SegmentTree.__init__")

    def query(self, left: int, right: int) -> RangeStats | None:
        """Query `(min_low, max_high, volume_sum)` over half-open `[left, right)` in O(log N)."""
        raise NotImplementedError("TODO(P07): implement SegmentTree.query")

    def update(self, index: int, candle: Candle) -> None:
        """Replace candle at `index` and update aggregates in O(log N); IndexError if invalid."""
        raise NotImplementedError("TODO(P07): implement SegmentTree.update")

    def append(self, candle: Candle) -> None:
        """Append a new candle, growing capacity dynamically in O(log N) amortized."""
        raise NotImplementedError("TODO(P07): implement SegmentTree.append")

    def __len__(self) -> int:
        """Return number of candles stored in the tree (O(1))."""
        raise NotImplementedError("TODO(P07): implement SegmentTree.__len__")

    def get_candle(self, index: int) -> Candle:
        """Return candle at `index` (O(1)); raise IndexError if out of bounds."""
        raise NotImplementedError("TODO(P07): implement SegmentTree.get_candle")
