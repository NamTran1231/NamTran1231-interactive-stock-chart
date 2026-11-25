"""Segment tree for candle range statistics and point updates."""

from collections.abc import Sequence

from src.algorithms.range_stats import RangeStats
from src.core.candle import Candle


def _merge(left: RangeStats | None, right: RangeStats | None) -> RangeStats | None:
    """Combine two disjoint ranges; None contributes no candles."""
    if left is None:
        return right
    if right is None:
        return left
    return RangeStats(
        min(left.min_low, right.min_low),
        max(left.max_high, right.max_high),
        left.volume_sum + right.volume_sum,
    )


class SegmentTree:
    """Snapshot candle statistics in O(N) build time and O(N) storage."""

    def __init__(self, candles: Sequence[Candle]) -> None:
        self._count = len(candles)
        self._timestamps = tuple(candle.timestamp for candle in candles)
        self._capacity = 1
        while self._capacity < self._count:
            self._capacity *= 2

        # Index 1 is the root; leaves start at capacity. Extra leaves stay empty.
        self._nodes: list[RangeStats | None] = [None] * (2 * self._capacity)
        for index, candle in enumerate(candles, start=self._capacity):
            self._nodes[index] = RangeStats(candle.low, candle.high, candle.volume)
        for index in range(self._capacity - 1, 0, -1):
            self._refresh_parent(index)

    def _refresh_parent(self, index: int) -> None:
        self._nodes[index] = _merge(self._nodes[2 * index], self._nodes[2 * index + 1])

    def update(self, index: int, candle: Candle) -> None:
        """Replace one candle's statistics in O(log N) time and O(1) extra space.

        Raise IndexError for an invalid index or ValueError if the timestamp changes.
        """
        if not 0 <= index < self._count:
            raise IndexError(f"Invalid candle index {index} for {self._count} candles")
        if candle.timestamp != self._timestamps[index]:
            raise ValueError("A point update must preserve the candle timestamp")

        node = self._capacity + index
        self._nodes[node] = RangeStats(candle.low, candle.high, candle.volume)
        while node > 1:
            node //= 2
            self._refresh_parent(node)

    def query(self, left: int, right: int) -> RangeStats | None:
        """Summarize [left, right) in O(log N) time and O(1) extra space.

        Return None for an empty range and raise IndexError for invalid bounds.
        """
        if not 0 <= left <= right <= self._count:
            raise IndexError(f"Invalid candle range [{left}, {right}) for {self._count} candles")
        left += self._capacity
        right += self._capacity
        result = None
        while left < right:
            # Take unmatched boundary nodes before moving to the parent level.
            if left % 2:
                result = _merge(result, self._nodes[left])
                left += 1
            if right % 2:
                right -= 1
                result = _merge(result, self._nodes[right])
            left //= 2
            right //= 2
        return result
